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


def merkle_proof(records: list[Any], index: int) -> list[dict[str, str]]:
    """Build a Merkle inclusion proof for one record index."""

    if index < 0 or index >= len(records):
        raise IndexError("proof index out of range")
    level = [hash_leaf(record) for record in records]
    proof: list[dict[str, str]] = []
    cursor = index
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        sibling = cursor ^ 1
        side = "left" if sibling < cursor else "right"
        proof.append({"side": side, "hash": level[sibling]})
        cursor //= 2
        level = [hash_pair(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return proof


def verify_merkle_proof(record: Any, proof: list[dict[str, str]], expected_root: str) -> bool:
    """Verify a Merkle inclusion proof produced by :func:`merkle_proof`."""

    current = hash_leaf(record)
    try:
        for step in proof:
            sibling = str(step["hash"])
            if step["side"] == "left":
                current = hash_pair(sibling, current)
            elif step["side"] == "right":
                current = hash_pair(current, sibling)
            else:
                return False
    except Exception:
        return False
    return current == expected_root


def verify_attestation_signature(public_key_hex: str, signature_hex: str, root: str, node_id: str = "") -> bool:
    """Verify an Ed25519 signature over the attested root.

    The signed message is ``node_id + ":" + root`` when ``node_id`` is supplied,
    otherwise just ``root``. If the optional ``cryptography`` dependency is not
    installed, this returns ``False`` instead of pretending verification passed.
    """

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:
        return False

    try:
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        message = f"{node_id}:{root}".encode("utf-8") if node_id else root.encode("utf-8")
        public_key.verify(bytes.fromhex(signature_hex), message)
        return True
    except Exception:
        return False
