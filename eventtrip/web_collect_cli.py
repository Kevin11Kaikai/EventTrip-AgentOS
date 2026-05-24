"""CLI for safe, opt-in web evidence collection and preview extraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from eventtrip.web_collection.collector import WebCollector
from eventtrip.web_collection.evidence_store import DEFAULT_EVIDENCE_DIR, save_web_evidence
from eventtrip.web_collection.extractor import (
    extract_market_evidence,
    extract_text_from_html,
    extraction_to_dict,
)
from eventtrip.web_collection.policies import collection_policy_summary
from eventtrip.web_collection.schemas import WebCollectionTarget, to_dict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely preview or save local web evidence for EventTrip-AgentOS."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Collect one local file or opt-in URL.")
    collect_parser.add_argument("--target-id", required=True)
    collect_parser.add_argument("--url")
    collect_parser.add_argument("--local-path", type=Path)
    collect_parser.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")
    collect_parser.add_argument("--notes", default="")
    collect_parser.add_argument("--live-http", action="store_true")
    collect_parser.add_argument("--dry-run", action="store_true")
    collect_parser.add_argument("--save", action="store_true")
    collect_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
        help="Evidence JSON output directory when --save is used.",
    )

    extract_parser = subparsers.add_parser("extract", help="Extract candidates from one local file.")
    extract_parser.add_argument("--local-path", required=True, type=Path)
    extract_parser.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")

    subparsers.add_parser("policy", help="Print the conservative web collection policy.")

    return parser


def run_collect(args: argparse.Namespace) -> int:
    _print_safety_note(live_http=args.live_http)
    if args.url and not args.live_http:
        print("Live HTTP collection is disabled unless --live-http is explicitly passed.")
        return 2

    target = WebCollectionTarget(
        target_id=args.target_id,
        url=args.url,
        local_path=str(args.local_path) if args.local_path else None,
        match_id=args.match_id,
        source_type="public_web" if args.url else "local_fixture",
        notes=args.notes,
    )

    try:
        evidence = WebCollector().collect_target(
            target,
            cache_dir=args.output_dir,
            live_http=args.live_http,
            save_raw=args.save,
        )
    except Exception as exc:
        print(f"Web evidence collection failed: {exc}")
        return 2

    print("Collected evidence preview:")
    print(json.dumps(to_dict(evidence), indent=2, sort_keys=True))

    if args.save:
        output_path = save_web_evidence(evidence, args.output_dir)
        print(f"Saved evidence JSON: {output_path}")
        return 0

    if args.dry_run:
        print("Dry run: no evidence JSON or raw cache was written.")
    else:
        print("Preview only: pass --save to write evidence JSON and raw cache.")
    return 0


def run_extract(args: argparse.Namespace) -> int:
    _print_safety_note(live_http=False)
    try:
        raw_text = args.local_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Local file not found: {args.local_path}")
        return 2

    text = extract_text_from_html(raw_text)
    extraction = extract_market_evidence(text, args.match_id)
    print("Extracted candidate market evidence:")
    print(json.dumps(extraction_to_dict(extraction), indent=2, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "collect":
        return run_collect(args)
    if args.command == "extract":
        return run_extract(args)
    if args.command == "policy":
        print(json.dumps(collection_policy_summary(), indent=2, sort_keys=True))
        return 0
    parser.error(f"Unsupported command: {args.command}")
    return 2


def _print_safety_note(live_http: bool) -> None:
    print(
        "Safety: no login bypass, no CAPTCHA bypass, no purchase automation, "
        "and no snapshot writes are performed by this command."
    )
    if live_http:
        print("Live HTTP mode: one explicitly requested public page only.")
    else:
        print("Live HTTP mode: disabled.")


if __name__ == "__main__":
    raise SystemExit(main())
