"""CLI for manual market snapshot management."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from eventtrip.data_providers.import_provider import SnapshotImportProvider
from eventtrip.market_snapshots import (
    analyze_market_trend,
    default_snapshot_path,
    find_snapshot_index,
    load_market_snapshots,
    snapshot_to_dict,
    upsert_market_snapshot,
    validate_market_snapshot,
)
from eventtrip.schemas import MarketSnapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage manual EventTrip market snapshots.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze snapshots for one match.")
    _add_match_argument(analyze_parser)
    analyze_parser.add_argument("--path", type=Path, help="Optional custom CSV path.")

    append_parser = subparsers.add_parser("append", help="Append one validated manual snapshot.")
    _add_match_argument(append_parser)
    append_parser.add_argument("--snapshot-date", required=True, help="Snapshot date in YYYY-MM-DD.")
    append_parser.add_argument("--lowest-price", required=True, type=float)
    append_parser.add_argument("--listings", required=True, type=int)
    append_parser.add_argument("--category-3-low", required=True, type=float)
    append_parser.add_argument("--category-3-high", required=True, type=float)
    append_parser.add_argument("--hotel-availability-score", required=True, type=float)
    append_parser.add_argument("--flight-price-pressure", required=True, type=float)
    append_parser.add_argument("--social-buzz-score", required=True, type=float)
    append_parser.add_argument("--days-before-event", required=True, type=int)
    append_parser.add_argument("--source-type", default="manual")
    append_parser.add_argument("--notes", default="")
    append_parser.add_argument("--path", type=Path, help="Optional custom CSV path.")
    append_parser.add_argument("--dry-run", action="store_true", help="Validate without writing.")
    append_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing snapshot with the same match/date.",
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Import validated snapshots from a local CSV or JSON file.",
    )
    _add_match_argument(import_parser)
    import_parser.add_argument("--input", required=True, type=Path, help="Local CSV or JSON file.")
    import_parser.add_argument(
        "--destination",
        type=Path,
        help="Optional destination CSV path. Defaults to the match snapshot CSV.",
    )
    import_parser.add_argument("--dry-run", action="store_true", help="Validate without writing.")
    import_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing snapshots with the same match/date.",
    )

    return parser


def run_analyze(args: argparse.Namespace) -> int:
    match_id = args.match_id
    path = _resolve_snapshot_path(match_id, args.path)
    snapshots = load_market_snapshots(path, match_id=match_id)
    result = analyze_market_trend(snapshots)

    print(f"Snapshot file: {path}")
    print(f"Match ID: {match_id}")
    print(f"Snapshot count: {result.snapshot_count}")
    if snapshots:
        latest = snapshots[-1]
        print(f"Latest date: {latest.snapshot_date}")
        print(f"Latest price: ${result.latest_price:.0f}")
        print(f"Latest listings: {result.latest_listings}")
        print(f"Price change: ${result.price_change_abs:.0f} ({result.price_change_pct:+.1f}%)")
        print(
            "Listings change: "
            f"{result.listings_change_abs:+d} ({result.listings_change_pct:+.1f}%)"
        )
        print(f"Latest SSI: {result.latest_scalper_stress_index:.1f}/100")
    print(f"Recommendation: {result.recommendation}")
    print(f"Trigger status: {result.trigger_status}")
    print("Explanation:")
    for item in result.explanation:
        print(f"- {item}")
    return 0


def run_append(args: argparse.Namespace) -> int:
    match_id = args.match_id
    path = _resolve_snapshot_path(match_id, args.path)
    snapshot = MarketSnapshot(
        snapshot_date=args.snapshot_date,
        match_id=match_id,
        lowest_price=args.lowest_price,
        listings=args.listings,
        category_3_low=args.category_3_low,
        category_3_high=args.category_3_high,
        hotel_availability_score=args.hotel_availability_score,
        flight_price_pressure=args.flight_price_pressure,
        social_buzz_score=args.social_buzz_score,
        days_before_event=args.days_before_event,
        source_type=args.source_type,
        notes=args.notes,
    )

    errors = validate_market_snapshot(snapshot)
    if errors:
        print("Snapshot validation failed:")
        for error in errors:
            print(f"- {error}")
        return 2

    existing = load_market_snapshots(path)
    duplicate_index = find_snapshot_index(existing, snapshot.match_id, snapshot.snapshot_date)
    if duplicate_index is not None and not args.overwrite:
        print(
            "Snapshot already exists for "
            f"{snapshot.match_id} on {snapshot.snapshot_date}; use --overwrite to replace it."
        )
        return 1

    if args.dry_run:
        action = "overwrite" if duplicate_index is not None else "append"
        print(f"Dry run: validated snapshot; would {action} this row.")
        print(f"Snapshot file: {path}")
        _print_snapshot(snapshot)
        return 0

    result = upsert_market_snapshot(path, snapshot, overwrite=args.overwrite)
    if not result["saved"]:
        print("Snapshot was not written:")
        for error in result["errors"]:
            print(f"- {error}")
        return 1

    print(f"Snapshot {result['status']} successfully.")
    print(f"Snapshot file: {path}")
    _print_snapshot(snapshot)
    return 0


def run_import(args: argparse.Namespace) -> int:
    match_id = args.match_id
    destination = _resolve_snapshot_path(match_id, args.destination)
    try:
        snapshots = SnapshotImportProvider(args.input).load_snapshots(match_id=match_id)
    except Exception as exc:
        print(f"Snapshot import failed: {exc}")
        return 2

    if not snapshots:
        print(f"No snapshots found for match_id={match_id}.")
        return 1

    existing = load_market_snapshots(destination)
    duplicates = [
        snapshot
        for snapshot in snapshots
        if find_snapshot_index(existing, snapshot.match_id, snapshot.snapshot_date) is not None
    ]
    if duplicates and not args.overwrite:
        print("Snapshot import found duplicate match/date rows; use --overwrite to replace them.")
        for snapshot in duplicates:
            print(f"- {snapshot.match_id} {snapshot.snapshot_date}")
        return 1

    action = "overwrite/import" if duplicates else "import"
    if args.dry_run:
        print(f"Dry run: validated {len(snapshots)} snapshots; would {action} into {destination}.")
        for snapshot in snapshots:
            print(f"- {snapshot.match_id} {snapshot.snapshot_date}: ${snapshot.lowest_price:.0f}, listings {snapshot.listings}")
        return 0

    for snapshot in snapshots:
        result = upsert_market_snapshot(destination, snapshot, overwrite=args.overwrite)
        if not result["saved"]:
            print("Snapshot import stopped before completing:")
            for error in result["errors"]:
                print(f"- {error}")
            return 1

    print(f"Imported {len(snapshots)} snapshots into {destination}.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        return run_analyze(args)
    if args.command == "append":
        return run_append(args)
    if args.command == "import":
        return run_import(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


def _add_match_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--match",
        "--match-id",
        dest="match_id",
        default="portugal_dr_congo",
        help="Match ID, default portugal_dr_congo.",
    )


def _resolve_snapshot_path(match_id: str, custom_path: Path | None) -> Path:
    return custom_path if custom_path is not None else default_snapshot_path(match_id)


def _print_snapshot(snapshot: MarketSnapshot) -> None:
    data = snapshot_to_dict(snapshot)
    for key, value in data.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    raise SystemExit(main())
