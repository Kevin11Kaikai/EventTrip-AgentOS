"""CLI for source-backed quote intake.

The CLI never collects prices by itself. It only validates local CSV/JSON rows
that are tied to a public source URL.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from eventtrip.reviewed_quotes import (
    COMPONENT_LABELS,
    analyze_reviewed_quotes,
    default_reviewed_quotes_path,
    import_reviewed_quotes,
    load_reviewed_quotes,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage source-backed quote rows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="Summarize source-backed quotes for one match.")
    _add_match_argument(summary)
    summary.add_argument("--path", type=Path, help="Optional source-backed quote CSV/JSON path.")

    import_parser = subparsers.add_parser(
        "import",
        help="Import source-backed quote rows from a local CSV or JSON file.",
    )
    _add_match_argument(import_parser)
    import_parser.add_argument("--input", required=True, type=Path, help="Local CSV or JSON file.")
    import_parser.add_argument(
        "--destination",
        type=Path,
        help="Optional destination CSV path. Defaults to data/reviewed_quotes/<match>_quotes.csv.",
    )
    import_parser.add_argument("--dry-run", action="store_true", help="Validate without writing.")
    import_parser.add_argument("--overwrite", action="store_true", help="Replace duplicate rows.")

    return parser


def run_summary(args: argparse.Namespace) -> int:
    path = _resolve_quote_path(args.match_id, args.path)
    try:
        quotes = load_reviewed_quotes(path, match_id=args.match_id)
    except Exception as exc:
        print(f"Source-backed quote summary failed: {exc}")
        return 2
    analysis = analyze_reviewed_quotes(quotes)

    print(f"Source-backed quote file: {path}")
    print(f"Match ID: {args.match_id}")
    print(f"Source-backed quote count: {analysis['quote_count']}")
    if not quotes:
        print("No source-backed quotes are available yet.")
        print("Customer-facing reports should keep ticket, flight, hotel, transport, and total costs unknown.")
        return 0

    print("Latest components:")
    for component in analysis["components_present"]:
        quote = analysis["latest_by_component"][component]
        label = COMPONENT_LABELS.get(component, component)
        print(
            f"- {label}: ${quote['amount']:.0f} "
            f"({quote['quote_date']}, source_id={quote['source_id']})"
        )

    pit_total = analysis["latest_totals"]["pit"]
    sea_total = analysis["latest_totals"]["sea"]
    print(f"PIT source-backed total: {_format_total(pit_total)}")
    print(f"SEA source-backed total: {_format_total(sea_total)}")
    print(f"Missing PIT components: {', '.join(analysis['missing_components']['pit']) or 'none'}")
    print(f"Missing SEA components: {', '.join(analysis['missing_components']['sea']) or 'none'}")
    return 0


def run_import(args: argparse.Namespace) -> int:
    destination = _resolve_quote_path(args.match_id, args.destination)
    dry_run = bool(args.dry_run)
    try:
        result = import_reviewed_quotes(
            args.input,
            destination,
            match_id=args.match_id,
            overwrite=args.overwrite,
            dry_run=dry_run,
        )
    except Exception as exc:
        print(f"Source-backed quote import failed: {exc}")
        return 2

    if result["errors"]:
        print(f"Source-backed quote import status: {result['status']}")
        for error in result["errors"]:
            print(f"- {error}")
        return 1

    if dry_run:
        print(
            f"Dry run: validated {result['quote_count']} source-backed quote rows; "
            f"would import into {destination}."
        )
    else:
        print(f"Imported {result['quote_count']} source-backed quote rows into {destination}.")

    for quote in result["quotes"]:
        label = COMPONENT_LABELS.get(quote["component"], quote["component"])
        print(
            f"- {quote['quote_date']} {label}: ${quote['amount']:.0f} "
            f"source_id={quote['source_id']}"
        )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "summary":
        return run_summary(args)
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


def _resolve_quote_path(match_id: str, custom_path: Path | None) -> Path:
    return custom_path if custom_path is not None else default_reviewed_quotes_path(match_id)


def _format_total(value: float | None) -> str:
    return f"${value:.0f}" if value is not None else "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
