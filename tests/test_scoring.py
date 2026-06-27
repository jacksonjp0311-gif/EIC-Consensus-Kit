from eic_consensus_kit import (
    evaluate_record,
    load_record,
    merkle_proof,
    merkle_proof_object,
    merkle_root,
    verify_merkle_proof,
    verify_merkle_proof_object,
)
from eic_consensus_kit.scoring import weight_drift


def test_valid_distributed_record_promotes():
    result = evaluate_record(load_record("examples/valid_distributed_record.json"))

    assert result.outcome == "EIC-A"
    assert result.consensus_integrity >= 0.85
    assert result.dynamic_weight_integrity == 1.0
    assert result.proof_preservation == 1.0


def test_rejected_record_collapses_on_missing_proof():
    result = evaluate_record(load_record("examples/rejected_record.json"))

    assert result.outcome == "EIC-E"
    assert result.proof_preservation == 0.0
    assert result.consensus_calibrated_gci == 0.0


def test_weight_drift_sums_absolute_subgroup_changes():
    previous = {"a": 0.5, "b": 0.5}
    current = {"a": 0.7, "b": 0.2, "c": 0.1}

    assert round(weight_drift(previous, current), 6) == 0.6


def test_merkle_root_is_deterministic_for_canonical_records():
    records = [{"b": 2, "a": 1}, {"event": "x"}]

    assert merkle_root(records) == merkle_root([{"a": 1, "b": 2}, {"event": "x"}])


def test_merkle_proof_verifies_inclusion():
    records = [{"cycle": 1}, {"cycle": 2}, {"cycle": 3}]
    proof = merkle_proof(records, 1)

    assert verify_merkle_proof(records[1], proof, merkle_root(records)) is True
    assert verify_merkle_proof({"cycle": 99}, proof, merkle_root(records)) is False


def test_merkle_proof_object_verifies_inclusion():
    records = [{"cycle": 1}, {"cycle": 2}, {"cycle": 3}]
    proof_object = merkle_proof_object(records, 2)

    assert verify_merkle_proof_object(proof_object) is True
    proof_object["record"] = {"cycle": 99}
    assert verify_merkle_proof_object(proof_object) is False


def test_cli_scaffold_shape_is_importable():
    from eic_consensus_kit.cli import _scaffold

    scaffold = _scaffold("candidate", "claim")

    assert scaffold["candidate"] == "candidate"
    assert scaffold["distributed_trust_claim"] is True


def test_ed25519_signature_verification_when_crypto_available():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except Exception:
        return

    from eic_consensus_kit.proofs import verify_attestation_signature

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    root = "abc123"
    signature = private_key.sign(f"node-a:{root}".encode("utf-8")).hex()

    assert verify_attestation_signature(public_key, signature, root, "node-a") is True
    assert verify_attestation_signature(public_key, signature, root, "node-b") is False


def test_operator_keygen_and_sign_root_when_crypto_available():
    try:
        from eic_consensus_kit.crypto import keygen, sign_root
    except Exception:
        return

    from eic_consensus_kit.proofs import verify_attestation_signature

    keys = keygen()
    signature = sign_root(keys.private_key, "abc123", "node-a")

    assert verify_attestation_signature(keys.public_key, signature, "abc123", "node-a") is True


def test_strict_profile_downgrades_when_policy_is_too_loose():
    result = evaluate_record(load_record("examples/valid_distributed_record.json"), profile="strict")

    assert result.outcome == "EIC-B"
    assert any("quorum threshold" in action for action in result.required_actions)
