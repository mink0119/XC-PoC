"""Request/response exchange logger for PoC verification."""

from __future__ import annotations

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
        entry = {
            "seq": self._seq,
            "ts": _now(),
            "scenario": scenario,
            "expected": expected,
            "request": {
                "method": method,
                "url": url,
                "headers": _jsonable(request_headers or {}),
                "body": _jsonable(request_body),
            },
            "response": {
                "status": status,
                "headers": _jsonable(response_headers or {}),
                "body": _jsonable(response_body),
            },
        }
        if meta:
            entry["meta"] = _jsonable(meta)
        self.entries.append(entry)
        return self._seq

    def write_jsonl(self, path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            for entry in self.entries:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
