"""Command-line interface for EIC Consensus Kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eic_consensus_kit.proofs import merkle_proof, merkle_root, verify_merkle_proof
from eic_consensus_kit.scoring import dump_json, evaluate_record, load_record, result_to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eicg",
        description="Validate distributed consensus, dynamic weighting, and proof-preserved continuity records.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate = sub.add_parser("evaluate", help="Evaluate an EIC consensus record JSON file.")
    evaluate.add_argument("record_file")
    evaluate.add_argument("--format", choices=("markdown", "json"), default="markdown")
    evaluate.add_argument("--fail-under", type=float, default=None)
    evaluate.add_argument("--output", type=Path, default=None)

    root = sub.add_parser("merkle-root", help="Compute a Merkle root for a JSON list of records.")
    root.add_argument("records_file")

    proof = sub.add_parser("merkle-proof", help="Build a Merkle inclusion proof for a JSON list item.")
    proof.add_argument("records_file")
    proof.add_argument("index", type=int)

    verify = sub.add_parser("verify-proof", help="Verify a Merkle inclusion proof.")
    verify.add_argument("record_file")
    verify.add_argument("proof_file")
    verify.add_argument("expected_root")

    scaffold = sub.add_parser("scaffold", help="Print a starter EIC consensus record JSON document.")
    scaffold.add_argument("--candidate", default="Distributed AGNT continuity ledger")
    scaffold.add_argument("--claim", default="Bounded distributed continuity claim.")

    schema = sub.add_parser("validate-schema", help="Validate an EIC record against the bundled JSON Schema.")
    schema.add_argument("record_file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "merkle-root":
            records = json.loads(Path(args.records_file).read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("records file must contain a JSON list")
            print(merkle_root(records))
            return 0
        if args.command == "merkle-proof":
            records = json.loads(Path(args.records_file).read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("records file must contain a JSON list")
            print(json.dumps(merkle_proof(records, args.index), indent=2))
            return 0
        if args.command == "verify-proof":
            record = json.loads(Path(args.record_file).read_text(encoding="utf-8"))
            proof = json.loads(Path(args.proof_file).read_text(encoding="utf-8"))
            if not isinstance(proof, list):
                raise ValueError("proof file must contain a JSON list")
            print(str(verify_merkle_proof(record, proof, args.expected_root)).lower())
            return 0
        if args.command == "scaffold":
            print(json.dumps(_scaffold(args.candidate, args.claim), indent=2))
            return 0
        if args.command == "validate-schema":
            _validate_schema(args.record_file)
            print("valid")
            return 0

        result = evaluate_record(load_record(args.record_file))
        rendered = dump_json(result.to_dict()) if args.format == "json" else result_to_markdown(result)
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        if args.fail_under is not None and result.consensus_calibrated_gci < args.fail_under:
            return 2
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should return clean operator errors.
        print(f"eicg: {exc}", file=sys.stderr)
        return 1


def _scaffold(candidate: str, claim: str) -> dict[str, object]:
    return {
        "candidate": candidate,
        "claim": claim,
        "base_collective_gci": 0.0,
        "distributed_trust_claim": True,
        "accepted_root": "",
        "consensus_policy": {
            "method": "",
            "quorum_threshold": 0.67,
            "signature_requirement": "",
            "root_comparison": "",
            "fork_handling": "",
            "timeout": "",
            "reason": "",
        },
        "attestations": [],
        "disagreement_disclosed": False,
        "previous_weights": {},
        "current_weights": {},
        "weight_policy": {
            "method": "",
            "max_drift": 0.25,
            "evidence_basis": "",
            "risk_adjustment": "",
            "normalization": "",
            "reason": "",
        },
        "weight_evidence_supported": False,
        "compression_claimed": False,
        "proof_records": [],
        "retained_proofs": [],
        "merkle_root": "",
        "inclusion_proofs_available": False,
        "retention_policy": {
            "full_retention_window": "",
            "compression_method": "",
            "proof_method": "",
            "pruning_rule": "",
            "exception_records": [],
            "reason": "",
        },
        "non_claim_locks": [
            "consensus is not truth",
            "quorum is not correctness",
            "coherence is not truth",
            "GCI is not sentience",
        ],
    }


def _validate_schema(record_file: str) -> None:
    try:
        import jsonschema
    except Exception as exc:
        raise RuntimeError("schema validation requires the optional 'jsonschema' package; install .[dev]") from exc

    record = json.loads(Path(record_file).read_text(encoding="utf-8"))
    schema_path = Path(__file__).resolve().parents[2] / "schema" / "eic_record.schema.json"
    if not schema_path.exists():
        schema_path = Path.cwd() / "schema" / "eic_record.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(record, schema)


if __name__ == "__main__":
    raise SystemExit(main())
