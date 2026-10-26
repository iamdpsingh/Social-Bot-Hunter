"""Canonical JSON and hashing helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def dumps(obj: Any) -> str:
    """Deterministic JSON: sorted keys, compact separators, UTF-8 friendly."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def loads(value: Any) -> Any:
    """Read a JSON column. PostgreSQL returns parsed objects, SQLite returns text."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
