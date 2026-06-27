"""Command-line interface for EIC Consensus Kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eic_consensus_kit.crypto import keygen, sign_root
from eic_consensus_kit.profiles import PROFILES
from eic_consensus_kit.proofs import (
    merkle_proof,
    merkle_proof_object,
    merkle_root,
    verify_attestation_signature,
    verify_merkle_proof,
    verify_merkle_proof_object,
)
from eic_consensus_kit.scoring import dump_json, evaluate_record, load_record, result_to_markdown
from eic_consensus_kit.workflows import seal_run, verify_run


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
    evaluate.add_argument("--profile", choices=sorted(PROFILES), default="standard")

    root = sub.add_parser("merkle-root", help="Compute a Merkle root for a JSON list of records.")
    root.add_argument("records_file")

    proof = sub.add_parser("merkle-proof", help="Build a Merkle inclusion proof for a JSON list item.")
    proof.add_argument("records_file")
    proof.add_argument("index", type=int)
    proof.add_argument("--object", action="store_true", help="Emit a self-contained proof object.")

    verify = sub.add_parser("verify-proof", help="Verify a Merkle inclusion proof.")
    verify.add_argument("record_file")
    verify.add_argument("proof_file")
    verify.add_argument("expected_root")

    verify_object = sub.add_parser("verify-proof-object", help="Verify a self-contained Merkle proof object.")
    verify_object.add_argument("proof_file")

    keygen_parser = sub.add_parser("keygen", help="Generate an Ed25519 keypair.")
    keygen_parser.add_argument("--output", type=Path, default=None, help="Optional path for the keypair JSON.")

    sign = sub.add_parser("sign-root", help="Sign node_id:root with an Ed25519 private key.")
    sign.add_argument("--private-key", required=True)
    sign.add_argument("--node-id", required=True)
    sign.add_argument("--root", required=True)

    verify_attestations = sub.add_parser("verify-attestations", help="Verify cryptographic attestations in a record.")
    verify_attestations.add_argument("record_file")

    seal = sub.add_parser("seal-run", help="Seal ledger records into a root, attestation, and proof bundle.")
    seal.add_argument("records_file")
    seal.add_argument("--node-id", required=True)
    seal.add_argument("--private-key", default=None)
    seal.add_argument("--public-key", default=None)
    seal.add_argument("--proof-limit", type=int, default=None)
    seal.add_argument("--output", type=Path, default=None)

    verify_run_parser = sub.add_parser("verify-run", help="Verify schema, attestations, proofs, and scoring together.")
    verify_run_parser.add_argument("record_file")
    verify_run_parser.add_argument("--profile", choices=sorted(PROFILES), default="standard")
    verify_run_parser.add_argument("--fail", action="store_true", help="Exit non-zero when the combined run fails.")

    profiles = sub.add_parser("profiles", help="List built-in evaluation profiles.")
    profiles.add_argument("--format", choices=("markdown", "json"), default="markdown")

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
            payload = merkle_proof_object(records, args.index) if args.object else merkle_proof(records, args.index)
            print(json.dumps(payload, indent=2))
            return 0
        if args.command == "verify-proof":
            record = json.loads(Path(args.record_file).read_text(encoding="utf-8"))
            proof = json.loads(Path(args.proof_file).read_text(encoding="utf-8"))
            if not isinstance(proof, list):
                raise ValueError("proof file must contain a JSON list")
            print(str(verify_merkle_proof(record, proof, args.expected_root)).lower())
            return 0
        if args.command == "verify-proof-object":
            proof_object = json.loads(Path(args.proof_file).read_text(encoding="utf-8"))
            if not isinstance(proof_object, dict):
                raise ValueError("proof object file must contain a JSON object")
            print(str(verify_merkle_proof_object(proof_object)).lower())
            return 0
        if args.command == "keygen":
            keys = keygen()
            payload = {"public_key": keys.public_key, "private_key": keys.private_key}
            rendered = json.dumps(payload, indent=2)
            if args.output:
                args.output.write_text(rendered + "\n", encoding="utf-8")
            else:
                print(rendered)
            return 0
        if args.command == "sign-root":
            print(sign_root(args.private_key, args.root, args.node_id))
            return 0
        if args.command == "verify-attestations":
            record = load_record(args.record_file)
            results = [
                {
                    "node_id": node.node_id,
                    "root": node.root,
                    "signature_verified": node.signature_verified
                    or verify_attestation_signature(node.public_key, node.signature, node.root, node.node_id),
                }
                for node in record.attestations
            ]
            print(json.dumps(results, indent=2))
            return 0
        if args.command == "seal-run":
            records = json.loads(Path(args.records_file).read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("records file must contain a JSON list")
            payload = seal_run(
                records,
                node_id=args.node_id,
                private_key=args.private_key,
                public_key=args.public_key,
                proof_limit=args.proof_limit,
            )
            rendered = json.dumps(payload, indent=2)
            if args.output:
                args.output.write_text(rendered + "\n", encoding="utf-8")
            else:
                print(rendered)
            return 0
        if args.command == "verify-run":
            payload = verify_run(args.record_file, profile=args.profile)
            print(json.dumps(payload, indent=2, sort_keys=True))
            if args.fail and not payload["passed"]:
                return 2
            return 0
        if args.command == "profiles":
            payload = {
                name: {
                    "promotion_threshold": profile.promotion_threshold,
                    "quorum_threshold": profile.quorum_threshold,
                    "max_weight_drift": profile.max_weight_drift,
                    "require_distributed": profile.require_distributed,
                    "require_proof_for_compression": profile.require_proof_for_compression,
                }
                for name, profile in PROFILES.items()
            }
            if args.format == "json":
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("| Profile | Promotion | Quorum | Max Drift | Distributed | Compression Proof |")
                print("| --- | --- | --- | --- | --- | --- |")
                for name, profile in sorted(PROFILES.items()):
                    print(
                        f"| {name} | {profile.promotion_threshold:.2f} | {profile.quorum_threshold:.2f} | "
                        f"{profile.max_weight_drift:.2f} | {str(profile.require_distributed).lower()} | "
                        f"{str(profile.require_proof_for_compression).lower()} |"
                    )
            return 0
        if args.command == "scaffold":
            print(json.dumps(_scaffold(args.candidate, args.claim), indent=2))
            return 0
        if args.command == "validate-schema":
            _validate_schema(args.record_file)
            print("valid")
            return 0

        result = evaluate_record(load_record(args.record_file), profile=args.profile)
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
