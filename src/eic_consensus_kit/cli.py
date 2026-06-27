"""Command-line interface for EIC Consensus Kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eic_consensus_kit.proofs import merkle_root
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


if __name__ == "__main__":
    raise SystemExit(main())

