#!/usr/bin/env python3
"""Local BOLA traffic runner against Pet Shop only.

Sends ordinary API traffic that matches the agreed scenarios. Labels
(expected=benign|bola) are computed locally from bola_model — the server
response is never annotated for detection.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

sys.path.insert(0, str(ROOT.parent / "petshop"))
import bola_model  # noqa: E402


def issue(
    session: requests.Session,
    base: str,
    customer_id: int,
    operator_code: str | None,
    issued_at: int | None = None,
) -> str:
    body: dict = {"customer_id": customer_id}
    if operator_code:
        body["operator_code"] = operator_code
    if issued_at is not None:
        body["issued_at"] = issued_at
    resp = session.post(f"{base}/api/v1/auth/token", json=body, timeout=10)
    resp.raise_for_status()
    return resp.json()["accessToken"]


def record(
    rows: list[dict],
    *,
    scenario: str,
    expected: str,
    method: str,
    path: str,
    status: int,
    source_ip: str,
    operator_code: str | None,
    customer_id: int | None,
    issued_at: int | None,
    owner_customer_id: int | None,
    notes: str,
):
    rows.append({
        "scenario": scenario,
        "expected": expected,
        "method": method,
        "path": path,
        "status": status,
        "source_ip": source_ip,
        "operator_code": operator_code,
        "customer_id": customer_id,
        "issued_at": issued_at,
        "owner_customer_id": owner_customer_id,
        "notes": notes,
    })


def get_private(session, base, token, path, source_ip):
    # X-Forwarded-For simulates the client's public IP for cloud/NAT scenarios.
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": source_ip,
        "X-Real-IP": source_ip,
    }
    resp = session.get(f"{base}{path}", headers=headers, timeout=10)
    try:
        body = resp.json()
    except ValueError:
        body = None
    return resp.status_code, body


def run_catalog(session, base, rows, count: int):
    paths = [
        "/api/v1/products",
        "/api/v1/categories",
        "/api/v1/brands",
        "/api/v1/foods",
        "/api/v1/toys",
        "/api/v1/products/1",
        "/api/v1/search?q=salmon",
    ]
    for i in range(count):
        path = paths[i % len(paths)]
        resp = session.get(f"{base}{path}", timeout=10)
        record(
            rows,
            scenario="public_catalog",
            expected="benign",
            method="GET",
            path=path.split("?", 1)[0],
            status=resp.status_code,
            source_ip="192.0.2.50",
            operator_code=None,
            customer_id=None,
            issued_at=None,
            owner_customer_id=None,
            notes="공개 카탈로그 조회",
        )


def run_self_orders(session, base, rows):
    customer_id = 410
    token = issue(session, base, customer_id, None)
    order_id = bola_model.order_id_for(customer_id, 0)
    owner = bola_model.customer_id_for_order(order_id)
    path = f"/api/v1/orders/{order_id}"
    status, _body = get_private(session, base, token, path, "192.0.2.60")
    record(
        rows,
        scenario="self_order",
        expected=bola_model.expected_label(customer_id, None, owner),
        method="GET",
        path=path,
        status=status,
        source_ip="192.0.2.60",
        operator_code=None,
        customer_id=customer_id,
        issued_at=None,
        owner_customer_id=owner,
        notes="본인 주문 조회",
    )


def run_cyclic_operator(session, base, rows, sample: int):
    code = "OP_CYCLE_A"
    meta = bola_model.OPERATORS[code]
    ips = meta["shared_ips"]
    assigned = meta["customer_ids"]
    for i in range(sample):
        customer_id = assigned[i % len(assigned)]
        source_ip = ips[i % len(ips)]
        token = issue(session, base, customer_id, code)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        status, _body = get_private(session, base, token, path, source_ip)
        record(
            rows,
            scenario="operator_cyclic",
            expected=bola_model.expected_label(customer_id, code, owner),
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=code,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=f"순환형 운영자 {len(assigned)} ID 중 배정 계정 접근, 공유 IP",
        )


def run_fixed_operator(session, base, rows, sample: int):
    code = "OP_FIXED_A"
    meta = bola_model.OPERATORS[code]
    customer_id = meta["customer_ids"][0]
    ips = meta["shared_ips"]
    for i in range(sample):
        source_ip = ips[i % len(ips)]
        token = issue(session, base, customer_id, code)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        status, _body = get_private(session, base, token, path, source_ip)
        record(
            rows,
            scenario="operator_fixed",
            expected=bola_model.expected_label(customer_id, code, owner),
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=code,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes="고정형 운영자: ID·operator_code 고정, 소스 IP 변경",
        )


def run_access_token_reissue(session, base, rows):
    """24h access-token re-issue: same identity claims, new iat/exp (new string)."""
    code = "OP_FIXED_B"
    customer_id = bola_model.OPERATORS[code]["customer_ids"][0]
    order_id = bola_model.order_id_for(customer_id, 0)
    owner = bola_model.customer_id_for_order(order_id)
    path = f"/api/v1/orders/{order_id}"
    day0 = int(datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc).timestamp())
    tokens = []
    for day_offset in (0, 1, 2):
        issued_at = day0 + day_offset * bola_model.ACCESS_TOKEN_TTL_SEC
        token = issue(session, base, customer_id, code, issued_at=issued_at)
        tokens.append(token)
        status, _body = get_private(session, base, token, path, "198.51.100.10")
        record(
            rows,
            scenario="access_token_reissue",
            expected=bola_model.expected_label(customer_id, code, owner),
            method="GET",
            path=path,
            status=status,
            source_ip="198.51.100.10",
            operator_code=code,
            customer_id=customer_id,
            issued_at=issued_at,
            owner_customer_id=owner,
            notes="24h access_token 재발급: iat/exp만 갱신, customer_id·operator_code 유지",
        )
    if len(set(tokens)) != 3:
        raise SystemExit("access_token_reissue 는 일자마다 다른 accessToken 이어야 합니다")


def run_cross_customer_bola(session, base, rows):
    attacker_id = 410
    victim_order = bola_model.order_id_for(1, 0)
    victim_payment = bola_model.payment_id_for(1, 0)
    victim_pet = bola_model.pet_id_for(1)
    token = issue(session, base, attacker_id, None)
    targets = [
        (f"/api/v1/orders/{victim_order}", 1, "타 계정 주문"),
        (f"/api/v1/payments/{victim_payment}", 1, "타 계정 결제"),
        ("/api/v1/customers/1", 1, "타 계정 프로필"),
        (f"/api/v1/pets/{victim_pet}/medical-records", 1, "타 계정 진료기록"),
    ]
    for path, owner, note in targets:
        status, _body = get_private(session, base, token, path, "192.0.2.99")
        record(
            rows,
            scenario="cross_customer_bola",
            expected=bola_model.expected_label(attacker_id, None, owner),
            method="GET",
            path=path,
            status=status,
            source_ip="192.0.2.99",
            operator_code=None,
            customer_id=attacker_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=note,
        )


def run_id_enumeration(session, base, rows, count: int):
    attacker_id = 410
    token = issue(session, base, attacker_id, None)
    start = bola_model.order_id_for(1, 0)
    for offset in range(count):
        order_id = start + offset
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        status, _body = get_private(session, base, token, path, "192.0.2.99")
        record(
            rows,
            scenario="id_enumeration",
            expected=bola_model.expected_label(attacker_id, None, owner),
            method="GET",
            path=path,
            status=status,
            source_ip="192.0.2.99",
            operator_code=None,
            customer_id=attacker_id,
            issued_at=None,
            owner_customer_id=owner,
            notes="연속 order ID 열거",
        )


def run_large_operator(session, base, rows, sample: int):
    code = "OP_LARGE"
    meta = bola_model.OPERATORS[code]
    ips = meta["shared_ips"]
    assigned = meta["customer_ids"]
    for i in range(sample):
        customer_id = assigned[i % len(assigned)]
        source_ip = ips[0]
        token = issue(session, base, customer_id, code)
        path = f"/api/v1/customers/{customer_id}/orders"
        status, _body = get_private(session, base, token, path, source_ip)
        record(
            rows,
            scenario="operator_large",
            expected=bola_model.expected_label(customer_id, code, customer_id),
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=code,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=customer_id,
            notes=f"단일 IP에서 최대 {len(assigned)} ID 순환(축소 샘플)",
        )


def summarize(rows: list[dict]) -> dict:
    by_scenario: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_scenario.setdefault(row["scenario"], {"benign": 0, "bola": 0, "total": 0})
        bucket[row["expected"]] += 1
        bucket["total"] += 1
    return {
        "total": len(rows),
        "benign": sum(1 for r in rows if r["expected"] == "benign"),
        "bola": sum(1 for r in rows if r["expected"] == "bola"),
        "by_scenario": by_scenario,
    }


SCENARIOS = (
    "public_catalog",
    "self_order",
    "operator_cyclic",
    "operator_fixed",
    "access_token_reissue",
    "operator_large",
    "cross_customer_bola",
    "id_enumeration",
)


def run_selected(session, base, rows, name: str, args):
    if name == "public_catalog":
        run_catalog(session, base, rows, args.catalog)
    elif name == "self_order":
        run_self_orders(session, base, rows)
    elif name == "operator_cyclic":
        run_cyclic_operator(session, base, rows, args.cyclic)
    elif name == "operator_fixed":
        run_fixed_operator(session, base, rows, args.fixed)
    elif name == "access_token_reissue":
        run_access_token_reissue(session, base, rows)
    elif name == "operator_large":
        run_large_operator(session, base, rows, args.large)
    elif name == "cross_customer_bola":
        run_cross_customer_bola(session, base, rows)
    elif name == "id_enumeration":
        run_id_enumeration(session, base, rows, args.enum)
    else:
        raise SystemExit(f"알 수 없는 시나리오: {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Pet Shop BOLA scenario runner",
        epilog="시나리오 설명: ../docs/SCENARIOS.md",
    )
    parser.add_argument("--base", default="http://192.168.47.81", help="Pet Shop base URL")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=SCENARIOS,
        help="실행할 시나리오 (여러 번 지정 가능). 생략 시 전체 실행",
    )
    parser.add_argument("--list", action="store_true", help="시나리오 이름만 출력")
    parser.add_argument("--catalog", type=int, default=30, help="공개 카탈로그 요청 수")
    parser.add_argument("--cyclic", type=int, default=40, help="순환형 샘플 수")
    parser.add_argument("--fixed", type=int, default=16, help="고정형 샘플 수")
    parser.add_argument("--large", type=int, default=40, help="대규모 샘플 수")
    parser.add_argument("--enum", type=int, default=20, help="ID 열거 샘플 수")
    parser.add_argument("--out", type=Path, default=None, help="JSONL output path")
    args = parser.parse_args()

    if args.list:
        print("\n".join(SCENARIOS))
        return

    selected = args.scenario or list(SCENARIOS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = args.out or (OUT_DIR / f"bola-run-{int(time.time())}.jsonl")

    session = requests.Session()
    health = session.get(f"{args.base}/health", timeout=5)
    health.raise_for_status()

    rows: list[dict] = []
    for name in selected:
        run_selected(session, args.base, rows, name, args)

    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(rows)
    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out_path), "summary": summary}, ensure_ascii=False, indent=2))

    # Hard checks only when those scenarios were included.
    cross = [r for r in rows if r["scenario"] == "cross_customer_bola"]
    if cross and any(r["expected"] != "bola" or r["status"] != 200 for r in cross):
        raise SystemExit("cross_customer_bola 는 expected=bola 이고 HTTP 200 이어야 합니다")
    cyclic = [r for r in rows if r["scenario"] == "operator_cyclic"]
    if cyclic and any(r["expected"] != "benign" or r["status"] != 200 for r in cyclic):
        raise SystemExit("operator_cyclic 는 expected=benign 이고 HTTP 200 이어야 합니다")
    if len(selected) == len(SCENARIOS) and (summary["bola"] < 1 or summary["benign"] < 1):
        raise SystemExit("전체 실행 시 benign/bola 라벨이 모두 필요합니다")


if __name__ == "__main__":
    main()
