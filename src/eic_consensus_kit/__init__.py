"""EIC Consensus Kit public API."""

from eic_consensus_kit.models import EICRecord, EvaluationResult
from eic_consensus_kit.scoring import evaluate_record, load_record
from eic_consensus_kit.proofs import hash_leaf, merkle_proof, merkle_root, verify_merkle_proof

__all__ = [
    "EICRecord",
    "EvaluationResult",
    "evaluate_record",
    "load_record",
    "hash_leaf",
    "merkle_proof",
    "merkle_root",
    "verify_merkle_proof",
]
