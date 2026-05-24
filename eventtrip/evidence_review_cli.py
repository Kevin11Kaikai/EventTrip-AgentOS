"""CLI for reviewing web evidence and converting it to manual snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from eventtrip.evidence_review import (
    convert_reviewed_evidence_to_snapshot,
    load_evidence_for_review,
    summarize_evidence_for_review,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review web evidence and safely convert it into market snapshots."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview_parser = subparsers.add_parser("preview", help="Preview one evidence JSON file.")
    preview_parser.add_argument("--evidence", required=True, type=Path)

    convert_parser = subparsers.add_parser(
        "convert",
        help="Build and optionally save one reviewed evidence snapshot.",
    )
    convert_parser.add_argument("--evidence", required=True, type=Path)
    convert_parser.add_argument("--snapshot-date", required=True)
    convert_parser.add_argument("--category-3-low", required=True, type=float)
    convert_parser.add_argument("--category-3-high", required=True, type=float)
    convert_parser.add_argument("--hotel-availability-score", required=True, type=float)
    convert_parser.add_argument("--flight-price-pressure", required=True, type=float)
    convert_parser.add_argument("--social-buzz-score", required=True, type=float)
    convert_parser.add_argument("--days-before-event", required=True, type=int)
    convert_parser.add_argument("--source-type", default="reviewed_web_evidence")
    convert_parser.add_argument("--notes", default="")
    convert_parser.add_argument(
        "--destination",
        type=Path,
        help="Optional destination CSV path. Defaults to the match snapshot CSV.",
    )
    mode_group = convert_parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", help="Validate without writing.")
    mode_group.add_argument("--save", action="store_true", help="Write the reviewed snapshot.")
    convert_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing snapshot with the same match/date.",
    )

    return parser


def run_preview(args: argparse.Namespace) -> int:
    try:
        evidence = load_evidence_for_review(args.evidence)
    except Exception as exc:
        print(f"Evidence preview failed: {exc}")
        return 2

    print("Evidence review summary:")
    for key, value in summarize_evidence_for_review(evidence).items():
        print(f"- {key}: {value}")
    print("Review note: extracted values are candidates and require human confirmation.")
    return 0


def run_convert(args: argparse.Namespace) -> int:
    save = bool(args.save)
    if not args.save and not args.dry_run:
        print("Defaulting to dry-run preview. Pass --save to write a snapshot.")

    result = convert_reviewed_evidence_to_snapshot(
        evidence_path=args.evidence,
        snapshot_date=args.snapshot_date,
        category_3_low=args.category_3_low,
        category_3_high=args.category_3_high,
        hotel_availability_score=args.hotel_availability_score,
        flight_price_pressure=args.flight_price_pressure,
        social_buzz_score=args.social_buzz_score,
        days_before_event=args.days_before_event,
        source_type=args.source_type,
        notes=args.notes,
        destination_path=args.destination,
        save=save,
        overwrite=args.overwrite,
    )

    status = result["status"]
    if result.get("errors"):
        print(f"Evidence conversion failed: {status}")
        for error in result["errors"]:
            print(f"- {error}")
        return 1 if status == "duplicate" else 2

    if result["saved"]:
        print(f"Reviewed evidence snapshot {status} successfully.")
    else:
        print(f"Dry run: reviewed evidence snapshot is valid and would {result.get('would', 'write')}.")
    print(f"Snapshot file: {result['path']}")
    print("Snapshot candidate:")
    for key, value in result["snapshot"].items():
        print(f"- {key}: {value}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "preview":
        return run_preview(args)
    if args.command == "convert":
        return run_convert(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
