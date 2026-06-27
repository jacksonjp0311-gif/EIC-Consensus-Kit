"""Data models for EIC consensus validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ConsensusPolicy:
    method: str = ""
    quorum_threshold: float = 2 / 3
    signature_requirement: str = ""
    root_comparison: str = ""
    fork_handling: str = ""
    timeout: str = ""
    reason: str = ""

    @classmethod
    def from_raw(cls, raw: Any) -> "ConsensusPolicy":
        if raw is None:
            return cls()
        if not isinstance(raw, dict):
            raise TypeError("consensus_policy must be an object")
        return cls(
            method=_text(raw.get("method")),
            quorum_threshold=float(raw.get("quorum_threshold", 2 / 3)),
            signature_requirement=_text(raw.get("signature_requirement")),
            root_comparison=_text(raw.get("root_comparison")),
            fork_handling=_text(raw.get("fork_handling")),
            timeout=_text(raw.get("timeout")),
            reason=_text(raw.get("reason")),
        )

    @property
    def completeness(self) -> float:
        fields = (
            self.method,
            self.signature_requirement,
            self.root_comparison,
            self.fork_handling,
            self.timeout,
            self.reason,
        )
        return sum(bool(field) for field in fields) / len(fields)


@dataclass(frozen=True)
class NodeAttestation:
    node_id: str
    root: str
    available: bool = True
    signature_verified: bool = False

    @classmethod
    def from_raw(cls, raw: Any) -> "NodeAttestation":
        if not isinstance(raw, dict):
            raise TypeError("attestation entries must be objects")
        return cls(
            node_id=_text(raw.get("node_id")),
            root=_text(raw.get("root")),
            available=bool(raw.get("available", True)),
            signature_verified=bool(raw.get("signature_verified", False)),
        )


@dataclass(frozen=True)
class WeightPolicy:
    method: str = ""
    max_drift: float = 0.25
    evidence_basis: str = ""
    risk_adjustment: str = ""
    normalization: str = ""
    reason: str = ""

    @classmethod
    def from_raw(cls, raw: Any) -> "WeightPolicy":
        if raw is None:
            return cls()
        if not isinstance(raw, dict):
            raise TypeError("weight_policy must be an object")
        return cls(
            method=_text(raw.get("method")),
            max_drift=float(raw.get("max_drift", 0.25)),
            evidence_basis=_text(raw.get("evidence_basis")),
            risk_adjustment=_text(raw.get("risk_adjustment")),
            normalization=_text(raw.get("normalization")),
            reason=_text(raw.get("reason")),
        )

    @property
    def completeness(self) -> float:
        fields = (self.method, self.evidence_basis, self.risk_adjustment, self.normalization, self.reason)
        return sum(bool(field) for field in fields) / len(fields)


@dataclass(frozen=True)
class RetentionPolicy:
    full_retention_window: str = ""
    compression_method: str = ""
    proof_method: str = ""
    pruning_rule: str = ""
    exception_records: tuple[str, ...] = ()
    reason: str = ""

    @classmethod
    def from_raw(cls, raw: Any) -> "RetentionPolicy":
        if raw is None:
            return cls()
        if not isinstance(raw, dict):
            raise TypeError("retention_policy must be an object")
        return cls(
            full_retention_window=_text(raw.get("full_retention_window")),
            compression_method=_text(raw.get("compression_method")),
            proof_method=_text(raw.get("proof_method")),
            pruning_rule=_text(raw.get("pruning_rule")),
            exception_records=tuple(map(str, raw.get("exception_records", ()))),
            reason=_text(raw.get("reason")),
        )

    @property
    def completeness(self) -> float:
        fields = (
            self.full_retention_window,
            self.compression_method,
            self.proof_method,
            self.pruning_rule,
            ",".join(self.exception_records),
            self.reason,
        )
        return sum(bool(field) for field in fields) / len(fields)


@dataclass(frozen=True)
class EICRecord:
    candidate: str
    claim: str
    base_collective_gci: float
    distributed_trust_claim: bool = False
    accepted_root: str = ""
    consensus_policy: ConsensusPolicy = field(default_factory=ConsensusPolicy)
    attestations: tuple[NodeAttestation, ...] = ()
    disagreement_disclosed: bool = False
    previous_weights: dict[str, float] = field(default_factory=dict)
    current_weights: dict[str, float] = field(default_factory=dict)
    weight_policy: WeightPolicy = field(default_factory=WeightPolicy)
    weight_evidence_supported: bool = False
    compression_claimed: bool = False
    retained_proofs: tuple[str, ...] = ()
    merkle_root: str = ""
    inclusion_proofs_available: bool = False
    retention_policy: RetentionPolicy = field(default_factory=RetentionPolicy)
    non_claim_locks: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EICRecord":
        return cls(
            candidate=_text(raw.get("candidate")),
            claim=_text(raw.get("claim")),
            base_collective_gci=float(raw.get("base_collective_gci", 0.0)),
            distributed_trust_claim=bool(raw.get("distributed_trust_claim", False)),
            accepted_root=_text(raw.get("accepted_root")),
            consensus_policy=ConsensusPolicy.from_raw(raw.get("consensus_policy")),
            attestations=tuple(NodeAttestation.from_raw(item) for item in raw.get("attestations", ())),
            disagreement_disclosed=bool(raw.get("disagreement_disclosed", False)),
            previous_weights={str(k): float(v) for k, v in raw.get("previous_weights", {}).items()},
            current_weights={str(k): float(v) for k, v in raw.get("current_weights", {}).items()},
            weight_policy=WeightPolicy.from_raw(raw.get("weight_policy")),
            weight_evidence_supported=bool(raw.get("weight_evidence_supported", False)),
            compression_claimed=bool(raw.get("compression_claimed", False)),
            retained_proofs=tuple(map(str, raw.get("retained_proofs", ()))),
            merkle_root=_text(raw.get("merkle_root")),
            inclusion_proofs_available=bool(raw.get("inclusion_proofs_available", False)),
            retention_policy=RetentionPolicy.from_raw(raw.get("retention_policy")),
            non_claim_locks=tuple(map(str, raw.get("non_claim_locks", ()))),
            metadata=dict(raw.get("metadata", {})),
        )


@dataclass(frozen=True)
class EvaluationResult:
    candidate: str
    claim: str
    base_collective_gci: float
    consensus_integrity: float
    dynamic_weight_integrity: float
    proof_preservation: float
    consensus_calibrated_gci: float
    outcome: str
    reasons: tuple[str, ...]
    required_actions: tuple[str, ...]
    factors: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate,
            "claim": self.claim,
            "base_collective_gci": self.base_collective_gci,
            "consensus_integrity": self.consensus_integrity,
            "dynamic_weight_integrity": self.dynamic_weight_integrity,
            "proof_preservation": self.proof_preservation,
            "consensus_calibrated_gci": self.consensus_calibrated_gci,
            "outcome": self.outcome,
            "reasons": list(self.reasons),
            "required_actions": list(self.required_actions),
            "factors": self.factors,
        }


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()

