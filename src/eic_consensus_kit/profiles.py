"""Named policy profiles for EIC evaluation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyProfile:
    name: str
    promotion_threshold: float
    quorum_threshold: float
    max_weight_drift: float
    require_distributed: bool
    require_proof_for_compression: bool


PROFILES: dict[str, PolicyProfile] = {
    "strict": PolicyProfile(
        name="strict",
        promotion_threshold=0.9,
        quorum_threshold=0.75,
        max_weight_drift=0.1,
        require_distributed=True,
        require_proof_for_compression=True,
    ),
    "standard": PolicyProfile(
        name="standard",
        promotion_threshold=0.85,
        quorum_threshold=0.66,
        max_weight_drift=0.25,
        require_distributed=False,
        require_proof_for_compression=True,
    ),
    "single-node": PolicyProfile(
        name="single-node",
        promotion_threshold=0.75,
        quorum_threshold=1.0,
        max_weight_drift=0.25,
        require_distributed=False,
        require_proof_for_compression=True,
    ),
    "experimental": PolicyProfile(
        name="experimental",
        promotion_threshold=0.65,
        quorum_threshold=0.5,
        max_weight_drift=0.4,
        require_distributed=False,
        require_proof_for_compression=False,
    ),
    "audit-only": PolicyProfile(
        name="audit-only",
        promotion_threshold=0.0,
        quorum_threshold=0.0,
        max_weight_drift=1.0,
        require_distributed=False,
        require_proof_for_compression=False,
    ),
}


def get_profile(name: str) -> PolicyProfile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"unknown profile '{name}'; choose one of: {', '.join(sorted(PROFILES))}") from exc
