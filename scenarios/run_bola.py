#!/usr/bin/env python3
"""Local BOLA traffic runner against Pet Shop only.

Sends ordinary API traffic that matches the agreed scenarios. Labels
(expected=benign|bola) are computed locally from bola_model — the server
response is never annotated for detection.

operator_code in JWT is optional (--operator-code / --no-operator-code):
  off = current world (no operator identity in token; FP risk for XC)
  on  = future token with operator_code claim

Every HTTP exchange is written to *.http.jsonl for PoC request/response review.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from http_log import ExchangeLogger, header_map

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

sys.path.insert(0, str(ROOT.parent / "petshop"))
import bola_model  # noqa: E402

DEFAULT_CYCLIC_IDS = 264
MAX_CYCLIC_IDS = 500

# 일반 트래픽: 사용자(customer_id)마다 다른 XFF (소켓 IP는 못 바꾸므로 헤더만).
# 운영사 공유 IP 시나리오(operator_cyclic / operator_fixed)는 별도 경로 — 여기 풀을 쓰지 않음.
DEFAULT_XFF_IP_COUNT = 40  # XC User Identification=IP 학습 권장 ≥30
MAX_XFF_IP_COUNT = 508
DEFAULT_OPERATOR_SHARED_IPS = 1
MAX_OPERATOR_SHARED_IPS = 16


def _xff_pool_ip(slot: int) -> str:
    """Map 0-based slot → TEST-NET address (198.51.100/24 then 203.0.113/24)."""
    a = int(slot) % 508
    if a < 254:
        return f"198.51.100.{a + 1}"
    return f"203.0.113.{(a - 254) + 1}"


def user_source_ip(customer_id: int, *, ip_count: int = DEFAULT_XFF_IP_COUNT) -> str:
    """Stable per-user XFF: same customer_id → same IP across rounds.

    ``ip_count`` is the pool size (몇 개 IP를 돌아가며 쓸지).
    customers ≤ ip_count → 사용자마다 유일 IP.
    customers > ip_count → (customer_id-1) % ip_count 로 재사용하되 사용자 단위 고정.
    """
    if ip_count < 1 or ip_count > MAX_XFF_IP_COUNT:
        raise SystemExit(f"--xff-ip-count 는 1..{MAX_XFF_IP_COUNT} 범위여야 합니다")
    cid = max(1, int(customer_id))
    return _xff_pool_ip((cid - 1) % int(ip_count))


def operator_shared_ips(count: int = DEFAULT_OPERATOR_SHARED_IPS) -> list[str]:
    """운영사가 쓰는 소수 공유 IP (다계정 → 1~N개 IP). 일반 사용자 풀과 분리."""
    if count < 1 or count > MAX_OPERATOR_SHARED_IPS:
        raise SystemExit(f"--operator-shared-ips 는 1..{MAX_OPERATOR_SHARED_IPS} 범위여야 합니다")
    # 198.51.100 과 겹치지 않게 203.0.113.200+ 대역 사용
    return [f"203.0.113.{200 + i}" for i in range(int(count))]


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
        self.expected: str | None = None

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
            expected=expected if expected is not None else self.expected,
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


def issue(ctx: Ctx, customer_id: int, operator_code: str | None, issued_at: int | None = None) -> str:
    body: dict = {"customer_id": customer_id}
    if operator_code:
        body["operator_code"] = operator_code
    if issued_at is not None:
        body["issued_at"] = issued_at
    resp, data = ctx.exchange(
        "POST",
        "/api/v1/auth/token",
        headers={"Content-Type": "application/json"},
        json_body=body,
        meta={"kind": "auth"},
    )
    resp.raise_for_status()
    return data["accessToken"]


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


def get_private(ctx: Ctx, token: str, path: str, source_ip: str, expected: str | None = None):
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
        meta={"kind": "private_get", "source_ip": source_ip},
    )
    return resp.status_code, body


def post_private(
    ctx: Ctx,
    token: str,
    path: str,
    source_ip: str,
    json_body: dict,
    expected: str | None = None,
    meta: dict | None = None,
):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Forwarded-For": source_ip,
        "X-Real-IP": source_ip,
    }
    resp, body = ctx.exchange(
        "POST",
        path,
        headers=headers,
        json_body=json_body,
        expected=expected,
        meta={**(meta or {}), "kind": "private_post", "source_ip": source_ip},
    )
    return resp.status_code, body


def op_code(enabled: bool, code: str) -> str | None:
    return code if enabled else None


def run_catalog(ctx: Ctx, rows, count: int, operator_code_enabled: bool):
    ctx.scenario = "public_catalog"
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
        resp, _body = ctx.exchange("GET", path, expected="benign", meta={"kind": "catalog"})
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


def run_self_orders(
    ctx: Ctx,
    rows,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    ctx.scenario = "self_order"
    customer_id = 410
    source_ip = user_source_ip(customer_id, ip_count=xff_ip_count)
    token = issue(ctx, customer_id, None)
    order_id = bola_model.order_id_for(customer_id, 0)
    owner = bola_model.customer_id_for_order(order_id)
    path = f"/api/v1/orders/{order_id}"
    expected = bola_model.expected_label(customer_id, None, owner)
    status, _body = get_private(ctx, token, path, source_ip, expected=expected)
    record(
        rows,
        scenario="self_order",
        expected=expected,
        method="GET",
        path=path,
        status=status,
        source_ip=source_ip,
        operator_code=None,
        customer_id=customer_id,
        issued_at=None,
        owner_customer_id=owner,
        notes="본인 주문 조회 (per-user XFF)",
        operator_code_enabled=operator_code_enabled,
    )


def run_matched_order_learn(
    ctx: Ctx,
    rows,
    customer_count: int,
    rounds: int,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    """XC learning: JWT customer_id N → GET /api/v1/orders/N, repeated.

    One round = customers 1..N each hit their matching order once.
    ``rounds`` repeats that full cycle (e.g. N=300, rounds=100 → 30_000 GETs).

    XFF is bound per user (customer_id) from a pool of ``xff_ip_count`` IPs.
    Not the operator shared-IP pattern.
    """
    ctx.scenario = "matched_order_learn"
    if customer_count < 1 or customer_count > bola_model.CUSTOMER_COUNT:
        raise SystemExit(f"--matched-customers 는 1..{bola_model.CUSTOMER_COUNT} 범위여야 합니다")
    if rounds < 1 or rounds > MAX_MATCHED_ROUNDS:
        raise SystemExit(f"--matched-rounds 는 1..{MAX_MATCHED_ROUNDS} 범위여야 합니다")
    tokens: dict[int, str] = {}
    for round_i in range(1, rounds + 1):
        for customer_id in range(1, customer_count + 1):
            if customer_id not in tokens:
                tokens[customer_id] = issue(ctx, customer_id, None)
            token = tokens[customer_id]
            source_ip = user_source_ip(customer_id, ip_count=xff_ip_count)
            order_id = bola_model.order_id_for(customer_id, 0)
            owner = bola_model.customer_id_for_order(order_id)
            path = f"/api/v1/orders/{order_id}"
            expected = bola_model.expected_label(customer_id, None, owner)
            # Require numeric identity↔path match for XC private-resource learning shape.
            if order_id != customer_id or owner != customer_id or expected != "benign":
                raise SystemExit(
                    f"matched_order_learn 불일치: customer={customer_id} order={order_id} owner={owner}"
                )
            status, _body = get_private(ctx, token, path, source_ip, expected=expected)
            record(
                rows,
                scenario="matched_order_learn",
                expected=expected,
                method="GET",
                path=path,
                status=status,
                source_ip=source_ip,
                operator_code=None,
                customer_id=customer_id,
                issued_at=None,
                owner_customer_id=owner,
                notes=(
                    f"JWT customer_id == /orders/{{id}} · round {round_i}/{rounds} · "
                    f"xff_ip_count={xff_ip_count} (per-user)"
                ),
                operator_code_enabled=operator_code_enabled,
            )


def run_matched_account_learn(
    ctx: Ctx,
    rows,
    customer_count: int,
    rounds: int,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    """XC learning: JWT customer_id N → POST /accounts/inquire with own accountNo.

    accountNo = 10000000+N so Body private resource matches the token subject.
    XFF bound per user from ``xff_ip_count`` pool.
    """
    ctx.scenario = "matched_account_learn"
    if customer_count < 1 or customer_count > bola_model.CUSTOMER_COUNT:
        raise SystemExit(f"--matched-customers 는 1..{bola_model.CUSTOMER_COUNT} 범위여야 합니다")
    if rounds < 1 or rounds > MAX_MATCHED_ROUNDS:
        raise SystemExit(f"--matched-rounds 는 1..{MAX_MATCHED_ROUNDS} 범위여야 합니다")
    path = "/api/v1/accounts/inquire"
    tokens: dict[int, str] = {}
    for round_i in range(1, rounds + 1):
        for customer_id in range(1, customer_count + 1):
            if customer_id not in tokens:
                tokens[customer_id] = issue(ctx, customer_id, None)
            token = tokens[customer_id]
            source_ip = user_source_ip(customer_id, ip_count=xff_ip_count)
            account_no = bola_model.account_no_for(customer_id)
            owner = bola_model.customer_id_for_account_no(account_no)
            expected = bola_model.expected_label(customer_id, None, owner or -1)
            if owner != customer_id or expected != "benign":
                raise SystemExit(
                    f"matched_account_learn 불일치: customer={customer_id} accountNo={account_no} owner={owner}"
                )
            status, _body = post_private(
                ctx,
                token,
                path,
                source_ip,
                {"accountNo": account_no},
                expected=expected,
                meta={
                    "accountNo": account_no,
                    "round": round_i,
                    "xff_ip_count": xff_ip_count,
                },
            )
            record(
                rows,
                scenario="matched_account_learn",
                expected=expected,
                method="POST",
                path=path,
                status=status,
                source_ip=source_ip,
                operator_code=None,
                customer_id=customer_id,
                issued_at=None,
                owner_customer_id=owner,
                notes=(
                    f"JWT customer_id == accountNo owner · round {round_i}/{rounds} · "
                    f"xff_ip_count={xff_ip_count} (per-user)"
                ),
                operator_code_enabled=operator_code_enabled,
            )


def run_cyclic_operator(
    ctx: Ctx,
    rows,
    sample: int,
    id_count: int,
    operator_code_enabled: bool,
    operator_shared_ip_count: int = DEFAULT_OPERATOR_SHARED_IPS,
):
    """P2 오탐: 운영사가 소수 IP로 다계정 순환. 일반 per-user XFF 풀과 무관."""
    ctx.scenario = "operator_cyclic"
    if id_count < 1 or id_count > MAX_CYCLIC_IDS:
        raise SystemExit(f"--cyclic-ids 는 1..{MAX_CYCLIC_IDS} 범위여야 합니다")
    code = "OP_CYCLE_A" if id_count <= 264 else "OP_LARGE"
    assigned = list(range(1, id_count + 1))
    shared = operator_shared_ips(operator_shared_ip_count)
    token_op = op_code(operator_code_enabled, code)
    for i in range(sample):
        customer_id = assigned[i % len(assigned)]
        source_ip = shared[i % len(shared)]
        token = issue(ctx, customer_id, token_op)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        expected = bola_model.expected_label(customer_id, token_op, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="operator_cyclic",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=token_op,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=(
                f"운영사 공유 IP×{len(shared)} · 다계정 id_count={id_count}, "
                f"operator_code={'on' if operator_code_enabled else 'off'}"
            ),
            operator_code_enabled=operator_code_enabled,
        )


def run_fixed_operator(ctx: Ctx, rows, sample: int, operator_code_enabled: bool):
    ctx.scenario = "operator_fixed"
    code = "OP_FIXED_A"
    meta = bola_model.OPERATORS[code]
    customer_id = meta["customer_ids"][0]
    ips = meta["shared_ips"]
    token_op = op_code(operator_code_enabled, code)
    for i in range(sample):
        source_ip = ips[i % len(ips)]
        token = issue(ctx, customer_id, token_op)
        order_id = bola_model.order_id_for(customer_id, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        expected = bola_model.expected_label(customer_id, token_op, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="operator_fixed",
            expected=expected,
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


def run_access_token_reissue(
    ctx: Ctx,
    rows,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    ctx.scenario = "access_token_reissue"
    code = "OP_FIXED_B"
    customer_id = bola_model.OPERATORS[code]["customer_ids"][0]
    source_ip = user_source_ip(customer_id, ip_count=xff_ip_count)
    order_id = bola_model.order_id_for(customer_id, 0)
    owner = bola_model.customer_id_for_order(order_id)
    path = f"/api/v1/orders/{order_id}"
    token_op = op_code(operator_code_enabled, code)
    day0 = int(datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc).timestamp())
    tokens = []
    for day_offset in (0, 1, 2):
        issued_at = day0 + day_offset * bola_model.ACCESS_TOKEN_TTL_SEC
        token = issue(ctx, customer_id, token_op, issued_at=issued_at)
        tokens.append(token)
        expected = bola_model.expected_label(customer_id, token_op, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="access_token_reissue",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=token_op,
            customer_id=customer_id,
            issued_at=issued_at,
            owner_customer_id=owner,
            notes="24h access_token 재발급 (iat/exp만 변경, per-user XFF)",
            operator_code_enabled=operator_code_enabled,
        )
    if len(set(tokens)) != 3:
        raise SystemExit("access_token_reissue 는 일자마다 다른 accessToken 이어야 합니다")


def run_cross_customer_bola(
    ctx: Ctx,
    rows,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    ctx.scenario = "cross_customer_bola"
    attacker_id = 410
    source_ip = user_source_ip(attacker_id, ip_count=xff_ip_count)
    victim_order = bola_model.order_id_for(1, 0)
    victim_payment = bola_model.payment_id_for(1, 0)
    victim_pet = bola_model.pet_id_for(1)
    token = issue(ctx, attacker_id, None)
    targets = [
        (f"/api/v1/orders/{victim_order}", 1, "타 계정 주문"),
        (f"/api/v1/payments/{victim_payment}", 1, "타 계정 결제"),
        ("/api/v1/customers/1", 1, "타 계정 프로필"),
        (f"/api/v1/pets/{victim_pet}/medical-records", 1, "타 계정 진료기록"),
    ]
    for path, owner, note in targets:
        expected = bola_model.expected_label(attacker_id, None, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="cross_customer_bola",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=None,
            customer_id=attacker_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=note,
            operator_code_enabled=operator_code_enabled,
        )


def run_id_enumeration(
    ctx: Ctx,
    rows,
    count: int,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    ctx.scenario = "id_enumeration"
    attacker_id = 410
    source_ip = user_source_ip(attacker_id, ip_count=xff_ip_count)
    token = issue(ctx, attacker_id, None)
    start = bola_model.order_id_for(1, 0)
    for offset in range(count):
        order_id = start + offset
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        expected = bola_model.expected_label(attacker_id, None, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="id_enumeration",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=None,
            customer_id=attacker_id,
            issued_at=None,
            owner_customer_id=owner,
            notes="연속 order ID 열거",
            operator_code_enabled=operator_code_enabled,
        )


def run_account_body_bola(
    ctx: Ctx,
    rows,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    """P1b: private resource is accountNo in JSON body (not path)."""
    ctx.scenario = "account_body_bola"
    attacker_id = 410
    source_ip = user_source_ip(attacker_id, ip_count=xff_ip_count)
    path = "/api/v1/accounts/inquire"
    token = issue(ctx, attacker_id, None)
    # own account then foreign accounts via Body field
    targets = [
        (bola_model.account_no_for(attacker_id), attacker_id, "본인 계좌 Body 조회"),
        (bola_model.account_no_for(1), 1, "타 계좌 Body 조회"),
        (bola_model.account_no_for(2), 2, "타 계좌 Body 조회"),
    ]
    for account_no, owner, note in targets:
        expected = bola_model.expected_label(attacker_id, None, owner)
        status, _body = post_private(
            ctx,
            token,
            path,
            source_ip,
            {"accountNo": account_no},
            expected=expected,
            meta={"accountNo": account_no},
        )
        record(
            rows,
            scenario="account_body_bola",
            expected=expected,
            method="POST",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=None,
            customer_id=attacker_id,
            issued_at=None,
            owner_customer_id=owner,
            notes=note,
            operator_code_enabled=operator_code_enabled,
        )


def run_abnormal_probe(
    ctx: Ctx,
    rows,
    operator_code_enabled: bool,
    xff_ip_count: int = DEFAULT_XFF_IP_COUNT,
):
    """P3: a few benign self lookups, then sudden foreign object probing."""
    ctx.scenario = "abnormal_probe"
    customer_id = 410
    source_ip = user_source_ip(customer_id, ip_count=xff_ip_count)
    token = issue(ctx, customer_id, None)
    # benign self — path id == customer_id
    for path, owner in (
        (f"/api/v1/orders/{customer_id}", customer_id),
        (f"/api/v1/payments/{customer_id}", customer_id),
    ):
        expected = bola_model.expected_label(customer_id, None, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="abnormal_probe",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=None,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes="정상: 자기 객체 (id==customer_id)",
            operator_code_enabled=operator_code_enabled,
        )
    # abrupt foreign probe
    for cid in (1, 2, 3, 4, 5):
        order_id = bola_model.order_id_for(cid, 0)
        owner = bola_model.customer_id_for_order(order_id)
        path = f"/api/v1/orders/{order_id}"
        expected = bola_model.expected_label(customer_id, None, owner)
        status, _body = get_private(ctx, token, path, source_ip, expected=expected)
        record(
            rows,
            scenario="abnormal_probe",
            expected=expected,
            method="GET",
            path=path,
            status=status,
            source_ip=source_ip,
            operator_code=None,
            customer_id=customer_id,
            issued_at=None,
            owner_customer_id=owner,
            notes="이상: 타인 주문 급탐색",
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
    "matched_order_learn",
    "matched_account_learn",
    "operator_cyclic",
    "operator_fixed",
    "access_token_reissue",
    "cross_customer_bola",
    "account_body_bola",
    "id_enumeration",
    "abnormal_probe",
)

DEFAULT_MATCHED_CUSTOMERS = 40
DEFAULT_MATCHED_ROUNDS = 1
MAX_MATCHED_ROUNDS = 500

# Batch sets (lab UI: 정상 / 비정상 / 전체)
BATCH_BENIGN_SCENARIOS = (
    "public_catalog",
    "self_order",
    "matched_order_learn",
    "matched_account_learn",
    "operator_cyclic",
    "operator_fixed",
    "access_token_reissue",
)
BATCH_ATTACK_SCENARIOS = (
    "cross_customer_bola",
    "account_body_bola",
    "id_enumeration",
    "abnormal_probe",
)
LEARN_BENIGN_SCENARIOS = BATCH_BENIGN_SCENARIOS  # alias


def run_selected(ctx: Ctx, rows, name: str, args, operator_code_enabled: bool):
    xff_ip_count = getattr(args, "xff_ip_count", DEFAULT_XFF_IP_COUNT)
    operator_shared = getattr(args, "operator_shared_ips", DEFAULT_OPERATOR_SHARED_IPS)
    if name == "public_catalog":
        run_catalog(ctx, rows, args.catalog, operator_code_enabled)
    elif name == "self_order":
        run_self_orders(ctx, rows, operator_code_enabled, xff_ip_count=xff_ip_count)
    elif name == "matched_order_learn":
        run_matched_order_learn(
            ctx,
            rows,
            args.matched_customers,
            args.matched_rounds,
            operator_code_enabled,
            xff_ip_count=xff_ip_count,
        )
    elif name == "matched_account_learn":
        run_matched_account_learn(
            ctx,
            rows,
            args.matched_customers,
            args.matched_rounds,
            operator_code_enabled,
            xff_ip_count=xff_ip_count,
        )
    elif name == "operator_cyclic":
        run_cyclic_operator(
            ctx,
            rows,
            args.cyclic,
            args.cyclic_ids,
            operator_code_enabled,
            operator_shared_ip_count=operator_shared,
        )
    elif name == "operator_fixed":
        run_fixed_operator(ctx, rows, args.fixed, operator_code_enabled)
    elif name == "access_token_reissue":
        run_access_token_reissue(
            ctx, rows, operator_code_enabled, xff_ip_count=xff_ip_count
        )
    elif name == "cross_customer_bola":
        run_cross_customer_bola(
            ctx, rows, operator_code_enabled, xff_ip_count=xff_ip_count
        )
    elif name == "account_body_bola":
        run_account_body_bola(
            ctx, rows, operator_code_enabled, xff_ip_count=xff_ip_count
        )
    elif name == "id_enumeration":
        run_id_enumeration(
            ctx, rows, args.enum, operator_code_enabled, xff_ip_count=xff_ip_count
        )
    elif name == "abnormal_probe":
        run_abnormal_probe(
            ctx, rows, operator_code_enabled, xff_ip_count=xff_ip_count
        )
    else:
        raise SystemExit(f"알 수 없는 시나리오: {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Pet Shop BOLA scenario runner",
        epilog="GUI: http://<petshop-host>/lab  |  docs: ../docs/SCENARIOS.md",
    )
    parser.add_argument("--base", default="http://ncurity-test.local", help="Pet Shop base URL")
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
    parser.add_argument(
        "--matched-customers",
        type=int,
        default=DEFAULT_MATCHED_CUSTOMERS,
        help=(
            f"matched_order_learn: customer_id 1..N → GET /orders/N 계정 수 "
            f"1..{bola_model.CUSTOMER_COUNT} (기본 {DEFAULT_MATCHED_CUSTOMERS})"
        ),
    )
    parser.add_argument(
        "--matched-rounds",
        type=int,
        default=DEFAULT_MATCHED_ROUNDS,
        help=(
            f"matched_order_learn: 1..N 전체 사이클 반복 횟수 "
            f"1..{MAX_MATCHED_ROUNDS} (기본 {DEFAULT_MATCHED_ROUNDS}; "
            f"예: --matched-customers 300 --matched-rounds 100)"
        ),
    )
    parser.add_argument(
        "--xff-ip-count",
        type=int,
        default=DEFAULT_XFF_IP_COUNT,
        help=(
            f"일반 시나리오: 사용자(customer_id)별 X-Forwarded-For 풀 크기 "
            f"1..{MAX_XFF_IP_COUNT} (기본 {DEFAULT_XFF_IP_COUNT}, XC IP 식별 학습 권장 ≥30). "
            f"같은 사용자는 라운드가 바뀌어도 같은 XFF. "
            f"운영사 공유 IP 시나리오(operator_cyclic/fixed)에는 적용하지 않음"
        ),
    )
    parser.add_argument(
        "--operator-shared-ips",
        type=int,
        default=DEFAULT_OPERATOR_SHARED_IPS,
        help=(
            f"operator_cyclic 전용: 운영사가 쓰는 공유 IP 개수 "
            f"1..{MAX_OPERATOR_SHARED_IPS} (기본 {DEFAULT_OPERATOR_SHARED_IPS}). "
            f"다계정 → 소수 IP 오탐 재현"
        ),
    )
    parser.add_argument("--enum", type=int, default=20, help="ID 열거 샘플 수")
    parser.add_argument(
        "--enforce-ownership",
        action="store_true",
        default=False,
        help="정상 API 모드: X-Enforce-Ownership=1 (남의 객체면 403)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="선택한 시나리오(또는 --learn-benign)를 N회 반복 (기본 1)",
    )
    parser.add_argument(
        "--batch",
        choices=("benign", "attack", "all"),
        default=None,
        help=(
            "일괄 세트: benign=정상 학습, attack=비정상(BOLA/이상), all=전체. "
            "--scenario 와 함께 쓰지 않음. 예: --batch benign --repeat 300"
        ),
    )
    parser.add_argument(
        "--learn-benign",
        action="store_true",
        help="(--batch benign 과 동일) XC 학습용 정상 세트",
    )
    parser.add_argument(
        "--quiet-http",
        action="store_true",
        help="HTTP 상세 JSONL을 쓰지 않음 (카운트만). --http-log 보다 우선",
    )
    parser.add_argument(
        "--http-log",
        action="store_true",
        help="반복(--repeat)/배치에서도 HTTP 상세 JSONL을 남김 (차단·응답 확인용)",
    )
    parser.add_argument("--out", type=Path, default=None, help="요약 JSONL 경로")
    args = parser.parse_args()

    if args.list:
        print("\n".join(SCENARIOS))
        return

    repeats = max(1, int(args.repeat))
    batch = args.batch or ("benign" if args.learn_benign else None)
    if batch and args.scenario:
        raise SystemExit("--batch/--learn-benign 과 --scenario 는 함께 쓰지 마세요")
    if batch == "benign":
        selected = list(BATCH_BENIGN_SCENARIOS)
    elif batch == "attack":
        selected = list(BATCH_ATTACK_SCENARIOS)
    elif batch == "all":
        selected = list(SCENARIOS)
    else:
        selected = args.scenario or list(SCENARIOS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    out_path = args.out or (OUT_DIR / f"bola-run-{stamp}.jsonl")
    http_path = out_path.with_name(out_path.stem + ".http.jsonl")

    # Default: quiet when repeating; --http-log forces detail; --quiet-http always quiet
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
            print(f"[learn] round {round_i}/{repeats}", flush=True)
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
    summary["cyclic_ids"] = args.cyclic_ids
    summary["xff_ip_count"] = args.xff_ip_count
    summary["operator_shared_ips"] = args.operator_shared_ips
    summary["repeat"] = repeats
    summary["http_exchanges"] = logger._seq
    summary["http_log"] = str(http_path) if http_path else None
    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(out_path),
        "http_log": str(http_path),
        "summary": summary,
    }, ensure_ascii=False, indent=2))

    cross = [r for r in rows if r["scenario"] == "cross_customer_bola"]
    if cross:
        if any(r["expected"] != "bola" for r in cross):
            raise SystemExit("cross_customer_bola 는 expected=bola 이어야 합니다")
        want = 403 if args.enforce_ownership else 200
        if any(r["status"] != want for r in cross):
            raise SystemExit(
                f"cross_customer_bola 는 enforce={'on' if args.enforce_ownership else 'off'} 일 때 HTTP {want}"
            )
    cyclic = [r for r in rows if r["scenario"] == "operator_cyclic"]
    if cyclic and any(r["expected"] != "benign" or r["status"] != 200 for r in cyclic):
        raise SystemExit("operator_cyclic 는 expected=benign 이고 HTTP 200 이어야 합니다")
    if len(selected) == len(SCENARIOS) and (summary["bola"] < 1 or summary["benign"] < 1):
        raise SystemExit("전체 실행 시 benign/bola 라벨이 모두 필요합니다")


if __name__ == "__main__":
    main()
