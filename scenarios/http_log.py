"""Request/response exchange logger for PoC verification."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def header_map(headers) -> dict[str, str]:
    try:
        return {str(k): str(v) for k, v in headers.items()}
    except Exception:
        return {}


def decode_jwt_payload(token: str | None) -> dict[str, Any] | None:
    """Decode JWT payload without verifying the signature (lab display only)."""
    if not token or not isinstance(token, str):
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        raw = parts[1] + "=" * (-len(parts[1]) % 4)
        data = json.loads(base64.urlsafe_b64decode(raw.encode("ascii")))
        return data if isinstance(data, dict) else None
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _bearer_token(headers: dict | None) -> str | None:
    if not headers:
        return None
    raw = headers.get("Authorization") or headers.get("authorization")
    if not isinstance(raw, str):
        return None
    parts = raw.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


class ExchangeLogger:
    """Collects full HTTP exchanges for offline verification."""

    def __init__(self):
        self.entries: list[dict[str, Any]] = []
        self._seq = 0

    def clear(self):
        self.entries.clear()
        self._seq = 0

    def add(
        self,
        *,
        scenario: str | None,
        expected: str | None,
        method: str,
        url: str,
        request_headers: dict | None,
        request_body: Any,
        status: int,
        response_headers: dict | None,
        response_body: Any,
        meta: dict | None = None,
    ) -> int:
        self._seq += 1
        req_headers = dict(request_headers or {})
        entry = {
            "seq": self._seq,
            "ts": _now(),
            "scenario": scenario,
            "expected": expected,
            "request": {
                "method": method,
                "url": url,
                "headers": _jsonable(req_headers),
                "body": _jsonable(request_body),
            },
            "response": {
                "status": status,
                "headers": _jsonable(response_headers or {}),
                "body": _jsonable(response_body),
            },
        }
        req_jwt = decode_jwt_payload(_bearer_token(req_headers))
        if req_jwt is not None:
            entry["request"]["jwt"] = _jsonable(req_jwt)
        if isinstance(response_body, dict):
            issued = decode_jwt_payload(response_body.get("accessToken"))
            if issued is not None:
                entry["response"]["jwt"] = _jsonable(issued)
        if meta:
            entry["meta"] = _jsonable(meta)
        self.entries.append(entry)
        return self._seq

    def write_jsonl(self, path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            for entry in self.entries:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
