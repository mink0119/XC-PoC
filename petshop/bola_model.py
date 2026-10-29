"""Operator assignment and JWT helpers for the vulnerable Pet Shop BOLA lab.

The API itself never enforces ownership. Ground-truth helpers here are for the
local scenario runner only — response bodies stay ordinary business objects.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any

JWT_SECRET = os.environ.get("PETSHOP_JWT_SECRET", "petshop-bola-poc-secret")
ACCESS_TOKEN_TTL_SEC = 86400  # 24h access token, similar to common OAuth daily TTL
TOKEN_REUSE_WINDOW_SEC = 21600  # within 6h, return the same access token

# (customer_id, operator_code) -> (issued_at, access_token)
_token_cache: dict[tuple[int, str | None], tuple[int, str]] = {}

# Stable operator codes used as the identity key (not source IP).
OPERATORS: dict[str, dict[str, Any]] = {
    "OP_CYCLE_A": {
        "name": "Cyclic A",
        "mode": "cyclic",
        "customer_ids": list(range(1, 265)),  # 264 IDs
        "shared_ips": ["203.0.113.10", "203.0.113.11"],
    },
    "OP_CYCLE_B": {
        "name": "Cyclic B",
        "mode": "cyclic",
        "customer_ids": list(range(265, 345)),
        "shared_ips": ["203.0.113.20"],
    },
    "OP_CYCLE_C": {
        "name": "Cyclic C",
        "mode": "cyclic",
        "customer_ids": list(range(345, 405)),
        "shared_ips": ["203.0.113.30", "203.0.113.31"],
    },
    "OP_FIXED_A": {
        "name": "Fixed A",
        "mode": "fixed",
        "customer_ids": [405],
        "shared_ips": [f"198.51.100.{i}" for i in range(1, 9)],
    },
    "OP_FIXED_B": {
        "name": "Fixed B",
        "mode": "fixed",
        "customer_ids": [406],
        "shared_ips": [f"198.51.100.{i}" for i in range(10, 18)],
    },
    "OP_FIXED_C": {
        "name": "Fixed C",
        "mode": "fixed",
        "customer_ids": [407],
        "shared_ips": [f"198.51.100.{i}" for i in range(20, 28)],
    },
    "OP_LARGE": {
        "name": "Large multi-account",
        "mode": "cyclic",
        "customer_ids": list(range(1, 501)),  # up to 500 IDs
        "shared_ips": ["203.0.113.50"],
    },
    "OP_MIX_A": {
        "name": "Mixed A",
        "mode": "cyclic",
        "customer_ids": list(range(501, 541)),
        "shared_ips": ["203.0.113.60"],
    },
    "OP_MIX_B": {
        "name": "Mixed B",
        "mode": "fixed",
        "customer_ids": [541],
        "shared_ips": [f"198.51.100.{i}" for i in range(40, 48)],
    },
}

CUSTOMER_COUNT = 600
ORDERS_PER_CUSTOMER = 2
PAYMENTS_PER_CUSTOMER = 1
MEDICAL_PER_PET = 2


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_json(obj: Any) -> str:
    return _b64url(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def issue_token(
    *,
    customer_id: int,
    operator_code: str | None = None,
    issued_at: int | None = None,
) -> dict[str, Any]:
    """Issue a 24h access token. Identity claims stay stable; iat/exp change the string.

    If the same customer/operator asks again within TOKEN_REUSE_WINDOW_SEC of the
    previous issue (and issued_at is omitted), the previous token is returned.
    Pass issued_at explicitly to simulate a later day's re-issue for lab traffic.
    """
    if customer_id < 1 or customer_id > CUSTOMER_COUNT:
        raise ValueError(f"customer_id 는 1..{CUSTOMER_COUNT} 범위여야 합니다")
    if operator_code is not None and operator_code not in OPERATORS:
        raise ValueError(f"알 수 없는 operator_code: {operator_code}")
    if operator_code is not None and customer_id not in OPERATORS[operator_code]["customer_ids"]:
        raise ValueError(f"operator {operator_code} 에 customer {customer_id} 가 배정되지 않았습니다")
    if issued_at is not None and (not isinstance(issued_at, int) or issued_at < 0):
        raise ValueError("issued_at 는 unix epoch 초(정수)여야 합니다")

    now = int(datetime.now(timezone.utc).timestamp()) if issued_at is None else issued_at
    cache_key = (customer_id, operator_code)
    if issued_at is None and cache_key in _token_cache:
        prev_iat, prev_token = _token_cache[cache_key]
        if now - prev_iat < TOKEN_REUSE_WINDOW_SEC and now < prev_iat + ACCESS_TOKEN_TTL_SEC:
            return {
                "accessToken": prev_token,
                "tokenType": "Bearer",
                "expiresIn": max(0, prev_iat + ACCESS_TOKEN_TTL_SEC - now),
            }

    header = {"alg": "HS256", "typ": "JWT"}
    # When operator_code is omitted, do not put it in the JWT — matches "no operator
    # identity in token" traffic that XC should evaluate for false positives.
    payload = {
        "sub": f"customer-{customer_id}",
        "customer_id": customer_id,
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL_SEC,
    }
    if operator_code is not None:
        payload["operator_code"] = operator_code
    signing_input = f"{_b64url_json(header)}.{_b64url_json(payload)}".encode("ascii")
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    token = f"{signing_input.decode('ascii')}.{_b64url(signature)}"
    _token_cache[cache_key] = (now, token)
    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresIn": ACCESS_TOKEN_TTL_SEC,
    }


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
        expected = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(expected), parts[2]):
            return None
        payload = json.loads(_b64url_decode(parts[1]))
        if not isinstance(payload, dict):
            return None
        return payload
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def claims_from_authorization(header_value: str | None) -> dict[str, Any] | None:
    if not header_value:
        return None
    parts = header_value.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return decode_token(parts[1].strip())


def customer_record(customer_id: int) -> dict[str, Any]:
    return {
        "id": customer_id,
        "email": f"customer{customer_id}@petshop.local",
        "firstName": ["Ada", "Jin", "Noah", "Mina", "Owen"][(customer_id - 1) % 5],
        "lastName": ["Kim", "Park", "Cho", "Lee", "Song"][(customer_id - 1) % 5],
        "phone": f"+1-415-555-{(customer_id % 10000):04d}",
        "loyaltyTier": ["bronze", "silver", "gold"][(customer_id - 1) % 3],
        "status": "active",
    }


def order_id_for(customer_id: int, slot: int = 0) -> int:
    return (customer_id - 1) * ORDERS_PER_CUSTOMER + slot + 1


def customer_id_for_order(order_id: int) -> int:
    return ((order_id - 1) // ORDERS_PER_CUSTOMER) + 1


def payment_id_for(customer_id: int, slot: int = 0) -> int:
    return (customer_id - 1) * PAYMENTS_PER_CUSTOMER + slot + 1


def customer_id_for_payment(payment_id: int) -> int:
    return ((payment_id - 1) // PAYMENTS_PER_CUSTOMER) + 1


def pet_id_for(customer_id: int) -> int:
    return customer_id


def customer_id_for_pet(pet_id: int) -> int:
    return pet_id


def medical_record_id_for(pet_id: int, slot: int = 0) -> int:
    return (pet_id - 1) * MEDICAL_PER_PET + slot + 1


def pet_id_for_medical(record_id: int) -> int:
    return ((record_id - 1) // MEDICAL_PER_PET) + 1


def order_record(order_id: int) -> dict[str, Any]:
    customer_id = customer_id_for_order(order_id)
    return {
        "id": order_id,
        "number": f"PS-2026-{1000 + order_id}",
        "customerId": customer_id,
        "status": ["placed", "paid", "shipped", "delivered"][(order_id - 1) % 4],
        "currency": "USD",
        "subtotal": round(20 + order_id * 1.5, 2),
        "shipping": 4.5,
        "total": round(24.5 + order_id * 1.5, 2),
        "storeId": ((order_id - 1) % 3) + 1,
        "createdAt": "2026-10-01T09:00:00Z",
        "updatedAt": "2026-10-15T03:12:00Z",
    }


def payment_record(payment_id: int) -> dict[str, Any]:
    customer_id = customer_id_for_payment(payment_id)
    order_id = order_id_for(customer_id, 0)
    return {
        "id": payment_id,
        "orderId": order_id,
        "customerId": customer_id,
        "method": ["card", "paypal", "gift_card"][(payment_id - 1) % 3],
        "status": "captured",
        "amount": round(24.5 + order_id * 1.5, 2),
        "currency": "USD",
        "last4": f"{1000 + payment_id}"[-4:],
        "createdAt": "2026-10-01T09:05:00Z",
        "updatedAt": "2026-10-01T09:05:00Z",
    }


def medical_record(record_id: int) -> dict[str, Any]:
    pet_id = pet_id_for_medical(record_id)
    customer_id = customer_id_for_pet(pet_id)
    return {
        "id": record_id,
        "petId": pet_id,
        "customerId": customer_id,
        "visitAt": f"2026-09-{(record_id % 27) + 1:02d}T16:00:00Z",
        "diagnosis": ["healthy", "otitis", "allergy"][(record_id - 1) % 3],
        "veterinarianId": ((record_id - 1) % 4) + 1,
        "notes": "Clinic visit summary",
        "createdAt": "2026-09-02T16:00:00Z",
        "updatedAt": "2026-09-02T16:00:00Z",
    }


def pet_record(pet_id: int) -> dict[str, Any]:
    customer_id = customer_id_for_pet(pet_id)
    names = ["Buddy", "Milo", "Nemo", "Coco", "Luna"]
    species = ["dog", "cat", "fish", "bird", "rabbit"]
    return {
        "id": pet_id,
        "name": names[(pet_id - 1) % len(names)],
        "species": species[(pet_id - 1) % len(species)],
        "breedId": ((pet_id - 1) % 6) + 1,
        "status": ["available", "pending", "sold"][(pet_id - 1) % 3],
        "customerId": customer_id,
        "weightKg": round(1.2 + (pet_id % 20) * 1.7, 1),
        "createdAt": "2026-04-12T09:00:00Z",
        "updatedAt": "2026-10-01T03:12:00Z",
    }


def payment_method_record(customer_id: int, method_id: int = 1) -> dict[str, Any]:
    return {
        "id": method_id,
        "customerId": customer_id,
        "brand": "visa",
        "last4": f"{4240 + customer_id}"[-4:],
        "expires": "2028-08",
        "createdAt": "2026-08-01T00:00:00Z",
        "updatedAt": "2026-08-01T00:00:00Z",
    }


def is_assigned(operator_code: str | None, customer_id: int) -> bool:
    if not operator_code:
        return False
    op = OPERATORS.get(operator_code)
    if not op:
        return False
    return customer_id in op["customer_ids"]


def authorized_for_owner(claims: dict[str, Any] | None, owner_customer_id: int) -> bool:
    """Local ground truth for the scenario runner — not used by the API."""
    if not claims:
        return False
    if claims.get("customer_id") == owner_customer_id:
        return True
    return is_assigned(claims.get("operator_code"), owner_customer_id)


def expected_label(customer_id: int | None, operator_code: str | None, owner_customer_id: int) -> str:
    claims = None
    if customer_id is not None:
        claims = {"customer_id": customer_id, "operator_code": operator_code}
    return "benign" if authorized_for_owner(claims, owner_customer_id) else "bola"


def operator_summary() -> dict[str, Any]:
    return {
        "customerCount": CUSTOMER_COUNT,
        "operators": [
            {
                "code": code,
                "name": meta["name"],
                "mode": meta["mode"],
                "assignedCustomers": len(meta["customer_ids"]),
                "sharedIps": meta["shared_ips"],
                "customerIdSample": meta["customer_ids"][:5],
            }
            for code, meta in OPERATORS.items()
        ],
    }
