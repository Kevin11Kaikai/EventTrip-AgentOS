"""CLI for source registry review packets and validation summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from eventtrip.source_evidence import SOURCE_EVIDENCE_PATH
from eventtrip.source_review_packet import (
    build_source_registry_review_summary,
    render_source_registry_review_markdown,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export source registry review summaries for PRs, customer review, "
            "or advisor review. This CLI does not fetch URLs or scrape websites."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="Print a compact validation summary.")
    _add_common_args(summary)

    export = subparsers.add_parser("export", help="Export a Markdown or JSON review packet.")
    _add_common_args(export)
    export.add_argument("--format", choices=["md", "json"], default="md")
    export.add_argument("--output", type=Path, help="Optional output path. Defaults to stdout.")

    return parser


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--registry", type=Path, default=SOURCE_EVIDENCE_PATH)
    parser.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")


def run_summary(args: argparse.Namespace) -> int:
    summary = build_source_registry_review_summary(args.registry, args.match_id)
    print(f"Source registry review status: {summary['status'].upper()}")
    print(f"Match ID: {summary['match_id']}")
    print(f"Registry: {summary['registry_path']}")
    print(f"Source count: {summary['source_count']}")
    print("Citation groups:")
    for group in summary["citation_groups"]:
        print(f"- {group['group_key']}: {group['source_count']} source(s)")
    if summary["validation_errors"]:
        print("Validation errors:")
        for error in summary["validation_errors"]:
            print(f"- {error}")
        return 1
    print("Validation errors: none")
    return 0


def run_export(args: argparse.Namespace) -> int:
    summary = build_source_registry_review_summary(args.registry, args.match_id)
    if args.format == "md":
        text = render_source_registry_review_markdown(summary)
    else:
        text = json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True)

    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Source registry review packet written to {args.output}")
    else:
        print(text)
    return 0 if summary["status"] == "pass" else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "summary":
        return run_summary(args)
    if args.command == "export":
        return run_export(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
