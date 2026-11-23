"""Canonical hashing utilities."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: Any) -> str:
    if not isinstance(data, (str, bytes)):
        data = canonical_json(data)
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def prefixed_hash(data: Any) -> str:
    return "0x" + sha256_hex(data)
