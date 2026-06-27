"""Executable EIC v1.6 scoring logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eic_consensus_kit.models import EICRecord, EvaluationResult


def clamp01(value: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def load_record(path: str | Path) -> EICRecord:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("record file must contain a JSON object")
    record = EICRecord.from_dict(raw)
    if not record.candidate:
        raise ValueError("record requires a candidate")
    if not record.claim:
        raise ValueError("record requires a claim")
    return record


def evaluate_record(record: EICRecord) -> EvaluationResult:
    consensus, consensus_factors = consensus_integrity(record)
    weights, weight_factors = dynamic_weight_integrity(record)
    proof, proof_factors = proof_preservation(record)

    calibrated = clamp01(record.base_collective_gci) * consensus * weights * proof
    calibrated = round(calibrated, 6)

    reasons: list[str] = []
    actions: list[str] = []

    if record.distributed_trust_claim and consensus == 0:
        reasons.append("Distributed trust claim collapses because consensus integrity is zero.")
    if record.compression_claimed and proof == 0:
        reasons.append("Continuity claim collapses because compression or pruning lacks retained proof.")
    if consensus_factors["disagreement_disclosed"] == 0 and record.distributed_trust_claim:
        actions.append("Disclose node disagreement whenever distributed consensus is claimed.")
    if consensus_factors["signed_quorum"] == 0 and record.distributed_trust_claim:
        actions.append("Provide verified signatures or equivalent attestations for quorum.")
    if weight_factors["policy_declared"] == 0 and record.current_weights:
        actions.append("Declare a dynamic subgroup weighting policy before adapting weights.")
    if weight_factors["drift_disclosed"] == 0 and record.current_weights:
        actions.append("Disclose subgroup weight drift.")
    if proof_factors["retained_proof"] == 0 and record.compression_claimed:
        actions.append("Retain Merkle proofs or equivalent proof objects before pruning or compression.")
    if not record.non_claim_locks:
        actions.append("Add non-claim locks: consensus is not truth, quorum is not correctness, GCI is not sentience.")

    outcome = classify(calibrated, consensus, weights, proof, actions)
    if outcome == "EIC-A":
        reasons.append("Distributed continuity claim is consensus-calibrated, weight-policy-bound, and proof-preserved.")
    elif outcome == "EIC-B":
        reasons.append("Continuity claim is usable but not strong enough for full promotion.")
    elif outcome == "EIC-C":
        reasons.append("Single-node or non-distributed continuity is valid only within its declared boundary.")
    elif outcome == "EIC-D":
        reasons.append("Record is inconclusive for distributed continuity.")
    else:
        reasons.append("Record is rejected for unsupported distributed continuity claims.")

    factors = {}
    factors.update({f"consensus.{key}": value for key, value in consensus_factors.items()})
    factors.update({f"weight.{key}": value for key, value in weight_factors.items()})
    factors.update({f"proof.{key}": value for key, value in proof_factors.items()})

    return EvaluationResult(
        candidate=record.candidate,
        claim=record.claim,
        base_collective_gci=round(clamp01(record.base_collective_gci), 6),
        consensus_integrity=round(consensus, 6),
        dynamic_weight_integrity=round(weights, 6),
        proof_preservation=round(proof, 6),
        consensus_calibrated_gci=calibrated,
        outcome=outcome,
        reasons=tuple(dict.fromkeys(reasons)),
        required_actions=tuple(dict.fromkeys(actions)),
        factors=factors,
    )


def consensus_integrity(record: EICRecord) -> tuple[float, dict[str, float]]:
    if not record.distributed_trust_claim:
        return 1.0, {
            "policy_declared": 1.0,
            "signed_quorum": 1.0,
            "node_agreement": 1.0,
            "root_comparison": 1.0,
            "disagreement_disclosed": 1.0,
        }

    available = [node for node in record.attestations if node.available]
    eligible = record.attestations
    accepted = record.accepted_root
    valid_signed = [node for node in eligible if node.root == accepted and node.signature_verified]
    agreeing_available = [node for node in available if node.root == accepted]

    quorum_ratio = len(valid_signed) / len(eligible) if eligible else 0.0
    signed_quorum = 1.0 if quorum_ratio >= record.consensus_policy.quorum_threshold else quorum_ratio
    node_agreement = len(agreeing_available) / len(available) if available else 0.0
    root_comparison = 1.0 if accepted and node_agreement > 0 else 0.0
    disclosed = 1.0 if record.disagreement_disclosed else 0.0
    policy = record.consensus_policy.completeness

    factors = {
        "policy_declared": clamp01(policy),
        "signed_quorum": clamp01(signed_quorum),
        "node_agreement": clamp01(node_agreement),
        "root_comparison": root_comparison,
        "disagreement_disclosed": disclosed,
    }
    score = 0.2 * factors["policy_declared"] + 0.3 * factors["signed_quorum"] + 0.2 * factors["node_agreement"] + 0.2 * root_comparison + 0.1 * disclosed
    return clamp01(score), factors


def dynamic_weight_integrity(record: EICRecord) -> tuple[float, dict[str, float]]:
    if not record.current_weights:
        return 1.0, {
            "policy_declared": 1.0,
            "normalized": 1.0,
            "bounds": 1.0,
            "drift_disclosed": 1.0,
            "evidence_supported": 1.0,
        }

    normalized = 1.0 if abs(sum(record.current_weights.values()) - 1.0) <= 1e-6 else 0.0
    bounds = 1.0 if all(0.0 <= weight <= 1.0 for weight in record.current_weights.values()) else 0.0
    drift = weight_drift(record.previous_weights, record.current_weights)
    drift_disclosed = 1.0 if drift <= record.weight_policy.max_drift else 0.0
    evidence = 1.0 if record.weight_evidence_supported else 0.0

    factors = {
        "policy_declared": clamp01(record.weight_policy.completeness),
        "normalized": normalized,
        "bounds": bounds,
        "drift_disclosed": drift_disclosed,
        "evidence_supported": evidence,
    }
    score = sum(factors.values()) / len(factors)
    return clamp01(score), factors


def proof_preservation(record: EICRecord) -> tuple[float, dict[str, float]]:
    if not record.compression_claimed:
        return 1.0, {
            "retention_policy": 1.0,
            "compression_declared": 1.0,
            "root_commitment": 1.0,
            "retained_proof": 1.0,
            "exception_coverage": 1.0,
        }

    retained = 1.0 if record.retained_proofs and record.inclusion_proofs_available else 0.0
    root = 1.0 if record.merkle_root else 0.0
    compression_declared = 1.0 if record.retention_policy.compression_method else 0.0
    exception_coverage = 1.0 if record.retention_policy.exception_records else 0.0
    factors = {
        "retention_policy": clamp01(record.retention_policy.completeness),
        "compression_declared": compression_declared,
        "root_commitment": root,
        "retained_proof": retained,
        "exception_coverage": exception_coverage,
    }
    if retained == 0:
        return 0.0, factors
    score = sum(factors.values()) / len(factors)
    return clamp01(score), factors


def weight_drift(previous: dict[str, float], current: dict[str, float]) -> float:
    keys = set(previous) | set(current)
    return sum(abs(current.get(key, 0.0) - previous.get(key, 0.0)) for key in keys)


def classify(score: float, consensus: float, weights: float, proof: float, actions: list[str]) -> str:
    if consensus == 0 or proof == 0:
        return "EIC-E"
    if score >= 0.85 and not actions:
        return "EIC-A"
    if score >= 0.65:
        return "EIC-B"
    if consensus == 1.0 and weights == 1.0 and proof == 1.0:
        return "EIC-C"
    if score >= 0.35:
        return "EIC-D"
    return "EIC-E"


def result_to_markdown(result: EvaluationResult) -> str:
    lines = [
        f"# EIC Consensus Report: {result.candidate}",
        "",
        f"**Claim:** {result.claim}",
        f"**Outcome:** {result.outcome}",
        f"**Base collective GCI:** {result.base_collective_gci:.6f}",
        f"**Consensus integrity:** {result.consensus_integrity:.6f}",
        f"**Dynamic weight integrity:** {result.dynamic_weight_integrity:.6f}",
        f"**Proof preservation:** {result.proof_preservation:.6f}",
        f"**Consensus-calibrated GCI:** {result.consensus_calibrated_gci:.6f}",
        "",
        "## Reasons",
    ]
    lines.extend(f"- {reason}" for reason in result.reasons)
    if result.required_actions:
        lines.extend(["", "## Required Actions"])
        lines.extend(f"- {action}" for action in result.required_actions)
    lines.extend(["", "## Factors", "", "| Factor | Value |", "| --- | --- |"])
    for key, value in sorted(result.factors.items()):
        lines.append(f"| {key} | {value:.6f} |")
    return "\n".join(lines) + "\n"


def dump_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"

