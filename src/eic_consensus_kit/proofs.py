"""Small Merkle utilities for proof-preserved ledger commitments."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_leaf(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(b"leaf:" + payload).hexdigest()


def hash_pair(left: str, right: str) -> str:
    return hashlib.sha256(b"node:" + bytes.fromhex(left) + bytes.fromhex(right)).hexdigest()


def merkle_root(records: Iterable[Any]) -> str:
    leaves = [hash_leaf(record) for record in records]
    if not leaves:
        return hashlib.sha256(b"empty").hexdigest()
    level = leaves
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [hash_pair(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]

