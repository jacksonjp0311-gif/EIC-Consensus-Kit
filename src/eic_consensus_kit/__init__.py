"""EIC Consensus Kit public API."""

from eic_consensus_kit.models import EICRecord, EvaluationResult
from eic_consensus_kit.profiles import PROFILES, PolicyProfile, get_profile
from eic_consensus_kit.scoring import evaluate_record, load_record
from eic_consensus_kit.workflows import seal_run, verify_run
from eic_consensus_kit.proofs import (
    hash_leaf,
    merkle_proof,
    merkle_proof_object,
    merkle_root,
    verify_merkle_proof,
    verify_merkle_proof_object,
)

__all__ = [
    "EICRecord",
    "EvaluationResult",
    "evaluate_record",
    "load_record",
    "hash_leaf",
    "merkle_proof",
    "merkle_proof_object",
    "merkle_root",
    "verify_merkle_proof_object",
    "verify_merkle_proof",
    "PROFILES",
    "PolicyProfile",
    "get_profile",
    "seal_run",
    "verify_run",
]
