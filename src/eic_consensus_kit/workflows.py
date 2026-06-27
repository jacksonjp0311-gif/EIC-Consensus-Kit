"""Higher-level operator workflows for EIC continuity runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eic_consensus_kit.crypto import sign_root
from eic_consensus_kit.proofs import (
    merkle_proof_object,
    merkle_root,
    verify_attestation_signature,
    verify_merkle_proof_object,
)
from eic_consensus_kit.scoring import evaluate_record, load_record


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def seal_run(
    records: list[Any],
    node_id: str,
    private_key: str | None = None,
    public_key: str | None = None,
    proof_limit: int | None = None,
) -> dict[str, Any]:
    """Create a sealed run bundle from ledger records."""

    root = merkle_root(records)
    count = len(records) if proof_limit is None else min(len(records), proof_limit)
    proof_objects = [merkle_proof_object(records, index) for index in range(count)]
    attestation: dict[str, Any] = {
        "node_id": node_id,
        "root": root,
        "available": True,
        "signature_verified": False,
    }
    if private_key:
        attestation["signature"] = sign_root(private_key, root, node_id)
    if public_key:
        attestation["public_key"] = public_key
    return {
        "root": root,
        "record_count": len(records),
        "proof_count": len(proof_objects),
        "attestation": attestation,
        "proof_objects": proof_objects,
    }


def verify_run(record_file: str | Path, profile: str = "standard") -> dict[str, Any]:
    """Run schema-adjacent, attestation, proof-object, and scoring checks."""

    record = load_record(record_file)
    attestation_results = [
        {
            "node_id": node.node_id,
            "root": node.root,
            "signature_verified": node.signature_verified
            or verify_attestation_signature(node.public_key, node.signature, node.root, node.node_id),
        }
        for node in record.attestations
    ]

    proof_results = []
    for item in record.retained_proofs:
        text = str(item).strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                proof_results.append({"verified": isinstance(parsed, dict) and verify_merkle_proof_object(parsed)})
            except json.JSONDecodeError:
                proof_results.append({"verified": False})
        else:
            proof_results.append({"verified": bool(text), "legacy_label": text})

    result = evaluate_record(record, profile=profile)
    signed_quorum = result.factors.get("consensus.signed_quorum", 0.0) == 1.0
    pass_status = (
        result.outcome in {"EIC-A", "EIC-B"}
        and signed_quorum
        and all(item["verified"] for item in proof_results if proof_results)
    )
    return {
        "passed": pass_status,
        "profile": profile,
        "attestations": attestation_results,
        "proofs": proof_results,
        "evaluation": result.to_dict(),
    }
