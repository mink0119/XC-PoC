#!/usr/bin/env python3
"""Local BOLA traffic runner against Pet Shop only.

Sends ordinary API traffic that matches the agreed scenarios. Labels
(expected=benign|bola) are computed locally from bola_model — the server
response is never annotated for detection.

operator_code in JWT is optional (--operator-code / --no-operator-code):
  off = current world (no operator identity in token; FP risk for XC)
  on  = future token with operator_code claim
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

DEFAULT_CYCLIC_IDS = 264
MAX_CYCLIC_IDS = 500


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
    operator_code_enabled: bool,
):
    rows.append({
        "scenario": scenario,
        "expected": expected,
        "method": method,
        "path": path,
        "status": status,
        "source_ip": source_ip,
        "operator_code": operator_code,
        "operator_code_enabled": operator_code_enabled,
        "customer_id": customer_id,
        "issued_at": issued_at,
        "owner_customer_id": owner_customer_id,
        "notes": notes,
    })


def get_private(session, base, token, path, source_ip):
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


def op_code(enabled: bool, code: str) -> str | None:
    return code if enabled else None


def run_catalog(session, base, rows, count: int, operator_code_enabled: bool):
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
            operator_code_enabled=operator_code_enabled,
        )


def run_self_orders(session, base, rows, operator_code_enabled: bool):
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
        operator_code_enabled=operator_code_enabled,
    )


def run_cyclic_operator(
    session,
    base,
    rows,
    sample: int,
    id_count: int,
    operator_code_enabled: bool,
):
    """Cyclic multi-account. id_count selects how many assigned IDs to rotate (1..500)."""
    if id_count < 1 or id_count > MAX_CYCLIC_IDS:
        raise SystemExit(f"--cyclic-ids 는 1..{MAX_CYCLIC_IDS} 범위여야 합니다")
    code = "OP_CYCLE_A" if id_count <= 264 else "OP_LARGE"
    # Prefer contiguous 1..N for adjustable count (matches OP_LARGE pool).
    assigned = list(range(1, id_count + 1))
    # 1 IP when stressing scale; 2 IPs for the classic 264-style pattern.
    ips = ["203.0.113.50"] if id_count > 264 else ["203.0.113.10", "203.0.113.11"]
    token_op = op_code(operator_code_enabled, code)
    for i in range(sample):
        customer_id = assigned[i % len(assigned)]
        source_ip = ips[i % len(ips)]
        token = issue(session, base, customer_id, token_op)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        status, _body = get_private(session, base, token, path, source_ip)
        record(
            rows,
            scenario="operator_cyclic",
            expected=bola_model.expected_label(customer_id, token_op, owner),
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=token_op,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=(
                f"순환형 멀티계정 id_count={id_count}, "
                f"operator_code={'on' if operator_code_enabled else 'off'}"
            ),
            operator_code_enabled=operator_code_enabled,
        )


def run_fixed_operator(session, base, rows, sample: int, operator_code_enabled: bool):
    code = "OP_FIXED_A"
    meta = bola_model.OPERATORS[code]
    customer_id = meta["customer_ids"][0]
    ips = meta["shared_ips"]
    token_op = op_code(operator_code_enabled, code)
    for i in range(sample):
        source_ip = ips[i % len(ips)]
        token = issue(session, base, customer_id, token_op)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        status, _body = get_private(session, base, token, path, source_ip)
        record(
            rows,
            scenario="operator_fixed",
            expected=bola_model.expected_label(customer_id, token_op, owner),
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=token_op,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes="고정형: ID 고정, 소스 IP 변경",
            operator_code_enabled=operator_code_enabled,
        )


def run_access_token_reissue(session, base, rows, operator_code_enabled: bool):
    code = "OP_FIXED_B"
    customer_id = bola_model.OPERATORS[code]["customer_ids"][0]
    order_id = bola_model.order_id_for(customer_id, 0)
    owner = bola_model.customer_id_for_order(order_id)
    path = f"/api/v1/orders/{order_id}"
    token_op = op_code(operator_code_enabled, code)
    day0 = int(datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc).timestamp())
    tokens = []
    for day_offset in (0, 1, 2):
        issued_at = day0 + day_offset * bola_model.ACCESS_TOKEN_TTL_SEC
        token = issue(session, base, customer_id, token_op, issued_at=issued_at)
        tokens.append(token)
        status, _body = get_private(session, base, token, path, "198.51.100.10")
        record(
            rows,
            scenario="access_token_reissue",
            expected=bola_model.expected_label(customer_id, token_op, owner),
            method="GET",
            path=path,
            status=status,
            source_ip="198.51.100.10",
            operator_code=token_op,
            customer_id=customer_id,
            issued_at=issued_at,
            owner_customer_id=owner,
            notes="24h access_token 재발급 (iat/exp만 변경)",
            operator_code_enabled=operator_code_enabled,
        )
    if len(set(tokens)) != 3:
        raise SystemExit("access_token_reissue 는 일자마다 다른 accessToken 이어야 합니다")


def run_cross_customer_bola(session, base, rows, operator_code_enabled: bool):
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
            operator_code_enabled=operator_code_enabled,
        )


def run_id_enumeration(session, base, rows, count: int, operator_code_enabled: bool):
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
            operator_code_enabled=operator_code_enabled,
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
    "cross_customer_bola",
    "id_enumeration",
)


def run_selected(session, base, rows, name: str, args, operator_code_enabled: bool):
    if name == "public_catalog":
        run_catalog(session, base, rows, args.catalog, operator_code_enabled)
    elif name == "self_order":
        run_self_orders(session, base, rows, operator_code_enabled)
    elif name == "operator_cyclic":
        run_cyclic_operator(
            session, base, rows, args.cyclic, args.cyclic_ids, operator_code_enabled
        )
    elif name == "operator_fixed":
        run_fixed_operator(session, base, rows, args.fixed, operator_code_enabled)
    elif name == "access_token_reissue":
        run_access_token_reissue(session, base, rows, operator_code_enabled)
    elif name == "cross_customer_bola":
        run_cross_customer_bola(session, base, rows, operator_code_enabled)
    elif name == "id_enumeration":
        run_id_enumeration(session, base, rows, args.enum, operator_code_enabled)
    else:
        raise SystemExit(f"알 수 없는 시나리오: {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Pet Shop BOLA scenario runner",
        epilog="GUI: http://<petshop-host>/lab  |  docs: ../docs/SCENARIOS.md",
    )
    parser.add_argument("--base", default="http://192.168.47.81", help="Pet Shop base URL")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=SCENARIOS,
        help="실행할 시나리오 (여러 번 지정 가능). 생략 시 전체",
    )
    parser.add_argument("--list", action="store_true", help="시나리오 이름만 출력")
    parser.add_argument(
        "--operator-code",
        dest="operator_code_enabled",
        action="store_true",
        default=False,
        help="JWT에 operator_code 포함 (미래형 토큰)",
    )
    parser.add_argument(
        "--no-operator-code",
        dest="operator_code_enabled",
        action="store_false",
        help="JWT에 operator_code 없음 (현재형, 기본값)",
    )
    parser.add_argument("--catalog", type=int, default=30, help="공개 카탈로그 요청 수")
    parser.add_argument("--cyclic", type=int, default=40, help="순환형 샘플 요청 수")
    parser.add_argument(
        "--cyclic-ids",
        type=int,
        default=DEFAULT_CYCLIC_IDS,
        help=f"순환에 쓸 계정 수 1..{MAX_CYCLIC_IDS} (기본 {DEFAULT_CYCLIC_IDS})",
    )
    parser.add_argument("--fixed", type=int, default=16, help="고정형 샘플 수")
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
        run_selected(session, args.base, rows, name, args, args.operator_code_enabled)

    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(rows)
    summary["operator_code_enabled"] = args.operator_code_enabled
    summary["cyclic_ids"] = args.cyclic_ids
    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out_path), "summary": summary}, ensure_ascii=False, indent=2))

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
