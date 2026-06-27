from eic_consensus_kit import evaluate_record, load_record, merkle_root
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

