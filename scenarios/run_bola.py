#!/usr/bin/env python3
"""Local BOLA traffic runner against Pet Shop only.

Three scenarios only:
  normal_orders   — customer_id N → GET /orders/N   (benign), ≥50 distinct XFF
  attack_orders   — customer_id N → GET /orders/M≠N (bola),   ≥50 distinct XFF
  operator_orders — pool of customer IDs, each hits own order, shared IP count

Labels (expected=benign|bola) are local only — never written into API responses.
operator_code in JWT is optional and does not change ownership labels.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

from http_log import ExchangeLogger, header_map

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

sys.path.insert(0, str(ROOT.parent / "petshop"))
import bola_model  # noqa: E402

DEFAULT_USERS = 50
MAX_USERS = bola_model.CUSTOMER_COUNT
DEFAULT_ROUNDS = 1
MAX_ROUNDS = 500
DEFAULT_OPERATOR_SHARED_IPS = 1
MAX_OPERATOR_SHARED_IPS = 16
DEFAULT_OPERATOR_CUSTOMERS = 50
DEFAULT_OPERATOR_REQUESTS = 50

SCENARIOS = (
    "normal_orders",
    "attack_orders",
    "operator_orders",
)


def user_source_ip(customer_id: int) -> str:
    """Normal/attack: customer_id → distinct stable XFF (1:1)."""
    slot = max(1, int(customer_id)) - 1
    a = slot % 508
    if a < 254:
        return f"198.51.100.{a + 1}"
    return f"203.0.113.{(a - 254) + 1}"


def operator_shared_ips(count: int = DEFAULT_OPERATOR_SHARED_IPS) -> list[str]:
    if count < 1 or count > MAX_OPERATOR_SHARED_IPS:
        raise SystemExit(f"--operator-shared-ips 는 1..{MAX_OPERATOR_SHARED_IPS} 범위여야 합니다")
    return [f"203.0.113.{200 + i}" for i in range(int(count))]


def mismatched_order_id(customer_id: int, user_count: int) -> int:
    """Always a different order id than customer_id (ring among 1..user_count)."""
    if user_count < 2:
        raise SystemExit("attack_orders 는 계정 수가 2 이상이어야 합니다")
    other = (customer_id % user_count) + 1
    if other == customer_id:
        other = 1 if customer_id != 1 else 2
    return other


class Ctx:
    def __init__(
        self,
        session: requests.Session,
        base: str,
        logger: ExchangeLogger,
        *,
        enforce_ownership: bool = False,
    ):
        self.session = session
        self.base = base.rstrip("/")
        self.logger = logger
        self.enforce_ownership = enforce_ownership
        self.scenario: str | None = None

    def exchange(
        self,
        method: str,
        path: str,
        *,
        headers: dict | None = None,
        json_body=None,
        expected: str | None = None,
        meta: dict | None = None,
    ):
        url = path if path.startswith("http") else self.base + path
        req_headers = dict(headers or {})
        req_headers["X-Enforce-Ownership"] = "1" if self.enforce_ownership else "0"
        resp = self.session.request(
            method,
            url,
            headers=req_headers,
            json=json_body,
            timeout=10,
        )
        try:
            resp_body = resp.json()
        except ValueError:
            resp_body = resp.text[:4000] if resp.text else None
        self.logger.add(
            scenario=self.scenario,
            expected=expected,
            method=method,
            url=url,
            request_headers=req_headers,
            request_body=json_body,
            status=resp.status_code,
            response_headers=header_map(resp.headers),
            response_body=resp_body,
            meta=meta,
        )
        return resp, resp_body


def issue(ctx: Ctx, customer_id: int, operator_code: str | None = None) -> str:
    body: dict = {"customer_id": customer_id}
    if operator_code:
        body["operator_code"] = operator_code
    resp, data = ctx.exchange(
        "POST",
        "/api/v1/auth/token",
        headers={"Content-Type": "application/json"},
        json_body=body,
        meta={"kind": "auth"},
    )
    resp.raise_for_status()
    return data["accessToken"]


def record(rows: list[dict], **row):
    rows.append(row)


def get_order(ctx: Ctx, token: str, order_id: int, source_ip: str, expected: str):
    path = f"/api/v1/orders/{order_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": source_ip,
        "X-Real-IP": source_ip,
    }
    resp, body = ctx.exchange(
        "GET",
        path,
        headers=headers,
        expected=expected,
        meta={"kind": "order_get", "source_ip": source_ip, "order_id": order_id},
    )
    return path, resp.status_code, body


def run_normal_orders(
    ctx: Ctx,
    rows,
    user_count: int,
    rounds: int,
    operator_code_enabled: bool,
):
    """Benign: JWT customer_id N → GET /api/v1/orders/N, distinct XFF per user."""
    ctx.scenario = "normal_orders"
    if user_count < 1 or user_count > MAX_USERS:
        raise SystemExit(f"--users 는 1..{MAX_USERS} 범위여야 합니다")
    if rounds < 1 or rounds > MAX_ROUNDS:
        raise SystemExit(f"--rounds 는 1..{MAX_ROUNDS} 범위여야 합니다")
    token_op = "OP_LARGE" if operator_code_enabled else None
    tokens: dict[int, str] = {}
    for round_i in range(1, rounds + 1):
        for customer_id in range(1, user_count + 1):
            if customer_id not in tokens:
                # OP_LARGE assigns 1..500; only attach claim when in range
                code = token_op if (token_op and customer_id <= 500) else None
                tokens[customer_id] = issue(ctx, customer_id, code)
            token = tokens[customer_id]
            order_id = bola_model.order_id_for(customer_id, 0)
            owner = bola_model.customer_id_for_order(order_id)
            expected = bola_model.expected_label(customer_id, None, owner)
            if order_id != customer_id or expected != "benign":
                raise SystemExit(
                    f"normal_orders 불일치: customer={customer_id} order={order_id}"
                )
            source_ip = user_source_ip(customer_id)
            path, status, _ = get_order(ctx, token, order_id, source_ip, expected)
            record(
                rows,
                scenario="normal_orders",
                expected=expected,
                method="GET",
                path=path,
                status=status,
                source_ip=source_ip,
                operator_code=token_op if customer_id <= 500 else None,
                operator_code_enabled=operator_code_enabled,
                customer_id=customer_id,
                issued_at=None,
                owner_customer_id=owner,
                notes=f"match cid==order · round {round_i}/{rounds}",
            )


def run_attack_orders(
    ctx: Ctx,
    rows,
    user_count: int,
    rounds: int,
    operator_code_enabled: bool,
):
    """BOLA: JWT customer_id N → GET /api/v1/orders/M (M≠N), distinct XFF per user."""
    ctx.scenario = "attack_orders"
    if user_count < 2 or user_count > MAX_USERS:
        raise SystemExit(f"attack_orders --users 는 2..{MAX_USERS} 범위여야 합니다")
    if rounds < 1 or rounds > MAX_ROUNDS:
        raise SystemExit(f"--rounds 는 1..{MAX_ROUNDS} 범위여야 합니다")
    tokens: dict[int, str] = {}
    for round_i in range(1, rounds + 1):
        for customer_id in range(1, user_count + 1):
            if customer_id not in tokens:
                tokens[customer_id] = issue(ctx, customer_id, None)
            token = tokens[customer_id]
            order_id = mismatched_order_id(customer_id, user_count)
            owner = bola_model.customer_id_for_order(order_id)
            expected = bola_model.expected_label(customer_id, None, owner)
            if expected != "bola" or order_id == customer_id:
                raise SystemExit(
                    f"attack_orders 라벨 오류: customer={customer_id} order={order_id} expected={expected}"
                )
            source_ip = user_source_ip(customer_id)
            path, status, _ = get_order(ctx, token, order_id, source_ip, expected)
            record(
                rows,
                scenario="attack_orders",
                expected=expected,
                method="GET",
                path=path,
                status=status,
                source_ip=source_ip,
                operator_code=None,
                operator_code_enabled=operator_code_enabled,
                customer_id=customer_id,
                issued_at=None,
                owner_customer_id=owner,
                notes=f"mismatch cid→order {customer_id}→{order_id} · round {round_i}/{rounds}",
            )


def run_operator_orders(
    ctx: Ctx,
    rows,
    customer_pool: int,
    request_count: int,
    shared_ip_count: int,
    operator_code_enabled: bool,
):
    """Benign operator: reuse a fixed pool of customer IDs; each hits own order.

    XFF comes from a small shared pool (not 1:1 with customer). IP count is configurable.
    """
    ctx.scenario = "operator_orders"
    if customer_pool < 1 or customer_pool > MAX_USERS:
        raise SystemExit(f"--operator-customers 는 1..{MAX_USERS} 범위여야 합니다")
    if request_count < 1 or request_count > 5000:
        raise SystemExit("--operator-requests 는 1..5000 범위여야 합니다")
    assigned = list(range(1, customer_pool + 1))
    shared = operator_shared_ips(shared_ip_count)
    # Prefer OP_LARGE (1..500) when claim enabled and pool fits
    token_op = None
    if operator_code_enabled and customer_pool <= 500:
        token_op = "OP_LARGE"
    for i in range(request_count):
        customer_id = assigned[i % len(assigned)]
        source_ip = shared[i % len(shared)]
        code = token_op if (token_op and customer_id <= 500) else None
        token = issue(ctx, customer_id, code)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        expected = bola_model.expected_label(customer_id, code, owner)
        if expected != "benign":
            raise SystemExit(
                f"operator_orders 는 자기 주문만: customer={customer_id} order={order_id}"
            )
        path, status, _ = get_order(ctx, token, order_id, source_ip, expected)
        record(
            rows,
            scenario="operator_orders",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=code,
            operator_code_enabled=operator_code_enabled,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=(
                f"운영사 공유IP×{len(shared)} · pool={customer_pool} · "
                f"cid={customer_id} order={order_id}"
            ),
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


def run_selected(ctx: Ctx, rows, name: str, args, operator_code_enabled: bool):
    if name == "normal_orders":
        run_normal_orders(
            ctx, rows, args.users, args.rounds, operator_code_enabled
        )
    elif name == "attack_orders":
        run_attack_orders(
            ctx, rows, args.users, args.rounds, operator_code_enabled
        )
    elif name == "operator_orders":
        run_operator_orders(
            ctx,
            rows,
            args.operator_customers,
            args.operator_requests,
            args.operator_shared_ips,
            operator_code_enabled,
        )
    else:
        raise SystemExit(f"알 수 없는 시나리오: {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Pet Shop BOLA scenario runner (normal / attack / operator)",
        epilog="GUI: python3 serve_lab.py  |  docs: ../docs/SCENARIOS.md",
    )
    parser.add_argument("--base", default="http://ncurity-test.local", help="Pet Shop base URL")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=SCENARIOS,
        help="normal_orders | attack_orders | operator_orders (여러 번 지정 가능)",
    )
    parser.add_argument("--list", action="store_true", help="시나리오 이름만 출력")
    parser.add_argument(
        "--operator-code",
        dest="operator_code_enabled",
        action="store_true",
        default=False,
        help="JWT에 operator_code 포함 (라벨에는 영향 없음)",
    )
    parser.add_argument(
        "--no-operator-code",
        dest="operator_code_enabled",
        action="store_false",
        help="JWT에 operator_code 없음 (기본)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=DEFAULT_USERS,
        help=f"정상/공격: 계정 수 (=서로 다른 XFF 수, 기본 {DEFAULT_USERS}, 권장 ≥50)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=DEFAULT_ROUNDS,
        help=f"정상/공격: 1..N 사이클 반복 (기본 {DEFAULT_ROUNDS})",
    )
    parser.add_argument(
        "--operator-customers",
        type=int,
        default=DEFAULT_OPERATOR_CUSTOMERS,
        help=f"운영사: 사용할 customer_id 풀 크기 (기본 {DEFAULT_OPERATOR_CUSTOMERS})",
    )
    parser.add_argument(
        "--operator-requests",
        type=int,
        default=DEFAULT_OPERATOR_REQUESTS,
        help=f"운영사: 총 요청 수 (풀을 순환, 기본 {DEFAULT_OPERATOR_REQUESTS})",
    )
    parser.add_argument(
        "--operator-shared-ips",
        type=int,
        default=DEFAULT_OPERATOR_SHARED_IPS,
        help=f"운영사: 공유 XFF 개수 1..{MAX_OPERATOR_SHARED_IPS} (기본 {DEFAULT_OPERATOR_SHARED_IPS})",
    )
    parser.add_argument(
        "--batch",
        choices=("normal", "attack", "all"),
        default=None,
        help="normal=normal_orders, attack=attack_orders, all=세 시나리오",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="선택한 시나리오를 N회 반복 (기본 1)",
    )
    parser.add_argument(
        "--enforce-ownership",
        action="store_true",
        default=False,
        help="정상 API 모드: X-Enforce-Ownership=1",
    )
    parser.add_argument("--quiet-http", action="store_true", help="HTTP JSONL 생략")
    parser.add_argument("--http-log", action="store_true", help="HTTP JSONL 강제")
    parser.add_argument("--out", type=Path, default=None, help="요약 JSONL 경로")
    args = parser.parse_args()

    if args.list:
        print("\n".join(SCENARIOS))
        return

    repeats = max(1, int(args.repeat))
    if args.batch and args.scenario:
        raise SystemExit("--batch 와 --scenario 는 함께 쓰지 마세요")
    if args.batch == "normal":
        selected = ["normal_orders"]
    elif args.batch == "attack":
        selected = ["attack_orders"]
    elif args.batch == "all":
        selected = list(SCENARIOS)
    else:
        selected = args.scenario or list(SCENARIOS)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    out_path = args.out or (OUT_DIR / f"bola-run-{stamp}.jsonl")
    http_path = out_path.with_name(out_path.stem + ".http.jsonl")

    if args.quiet_http:
        quiet_http = True
    elif args.http_log:
        quiet_http = False
    else:
        quiet_http = repeats > 1

    session = requests.Session()
    logger = ExchangeLogger(quiet=quiet_http)
    ctx = Ctx(session, args.base, logger, enforce_ownership=args.enforce_ownership)

    health = session.get(f"{args.base.rstrip('/')}/health", timeout=5)
    health.raise_for_status()
    logger.add(
        scenario=None,
        expected=None,
        method="GET",
        url=f"{args.base.rstrip('/')}/health",
        request_headers={},
        request_body=None,
        status=health.status_code,
        response_headers=header_map(health.headers),
        response_body=health.json() if health.content else None,
        meta={"kind": "health"},
    )

    rows: list[dict] = []
    for round_i in range(1, repeats + 1):
        if repeats > 1:
            print(f"[run] round {round_i}/{repeats}", flush=True)
            rows = []
        for name in selected:
            run_selected(ctx, rows, name, args, args.operator_code_enabled)

    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    if quiet_http:
        http_path = None
    else:
        logger.write_jsonl(http_path)

    summary = summarize(rows)
    summary["operator_code_enabled"] = args.operator_code_enabled
    summary["users"] = args.users
    summary["rounds"] = args.rounds
    summary["operator_shared_ips"] = args.operator_shared_ips
    summary["repeat"] = repeats
    summary["http_exchanges"] = logger._seq
    summary["http_log"] = str(http_path) if http_path else None
    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out_path), "http_log": str(http_path), "summary": summary}, ensure_ascii=False, indent=2))

    attack = [r for r in rows if r["scenario"] == "attack_orders"]
    if attack:
        if any(r["expected"] != "bola" for r in attack):
            raise SystemExit("attack_orders 는 expected=bola 이어야 합니다")
        want = 403 if args.enforce_ownership else 200
        if any(r["status"] != want for r in attack):
            raise SystemExit(
                f"attack_orders 는 enforce={'on' if args.enforce_ownership else 'off'} 일 때 HTTP {want}"
            )
    normal = [r for r in rows if r["scenario"] == "normal_orders"]
    if normal and any(r["expected"] != "benign" or r["status"] != 200 for r in normal):
        raise SystemExit("normal_orders 는 expected=benign 이고 HTTP 200 이어야 합니다")
    op = [r for r in rows if r["scenario"] == "operator_orders"]
    if op and any(r["expected"] != "benign" or r["status"] != 200 for r in op):
        raise SystemExit("operator_orders 는 expected=benign 이고 HTTP 200 이어야 합니다")


if __name__ == "__main__":
    main()
