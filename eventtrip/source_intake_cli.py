"""Guided CLI for reviewed public source intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import yaml

from eventtrip.source_evidence import SOURCE_EVIDENCE_PATH
from eventtrip.source_intake import (
    add_source_candidate,
    preview_source_candidate,
    source_template,
    validate_source_registry,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and add reviewed public source metadata for source-backed reports. "
            "This CLI does not fetch URLs, scrape websites, or verify claims automatically."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    template = subparsers.add_parser("template", help="Print or write a source candidate template.")
    template.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")
    template.add_argument("--output", type=Path, help="Optional YAML path to write.")

    validate = subparsers.add_parser("validate", help="Validate the source registry.")
    validate.add_argument("--registry", type=Path, default=SOURCE_EVIDENCE_PATH)
    validate.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")

    preview = subparsers.add_parser("preview", help="Preview one local source candidate.")
    preview.add_argument("--candidate", required=True, type=Path)
    preview.add_argument("--registry", type=Path, default=SOURCE_EVIDENCE_PATH)
    preview.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")
    preview.add_argument("--overwrite", action="store_true", help="Preview replacing duplicate source_id.")

    add = subparsers.add_parser("add", help="Dry-run or save one reviewed source candidate.")
    add.add_argument("--candidate", required=True, type=Path)
    add.add_argument("--registry", type=Path, default=SOURCE_EVIDENCE_PATH)
    add.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")
    mode = add.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate without writing.")
    mode.add_argument("--save", action="store_true", help="Write to the registry.")
    add.add_argument("--overwrite", action="store_true", help="Replace duplicate source_id.")

    return parser


def run_template(args: argparse.Namespace) -> int:
    data = source_template(args.match_id)
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Source candidate template written to {args.output}")
    else:
        print(text)
    return 0


def run_validate(args: argparse.Namespace) -> int:
    errors = validate_source_registry(args.registry, match_id=args.match_id)
    if errors:
        print("Source registry validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Source registry validation passed.")
    print(f"Registry: {args.registry}")
    print(f"Match ID: {args.match_id}")
    print("Checked: required fields, source tags, citation groups, field-level attribution.")
    return 0


def run_preview(args: argparse.Namespace) -> int:
    try:
        result = preview_source_candidate(
            args.candidate,
            registry_path=args.registry,
            default_match_id=args.match_id,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print(f"Source candidate preview failed: {exc}")
        return 2
    _print_json(result)
    return 0 if result["status"] == "valid" else 1


def run_add(args: argparse.Namespace) -> int:
    save = bool(args.save)
    if not args.save and not args.dry_run:
        print("Defaulting to dry-run. Pass --save to write to the registry.")
    try:
        result = add_source_candidate(
            args.candidate,
            registry_path=args.registry,
            default_match_id=args.match_id,
            save=save,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print(f"Source candidate add failed: {exc}")
        return 2
    _print_json(result)
    if result["errors"]:
        return 1
    if result["saved"]:
        print("Reviewed source candidate saved.")
    else:
        print("Dry run: source candidate is valid and no registry file was modified.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "template":
        return run_template(args)
    if args.command == "validate":
        return run_validate(args)
    if args.command == "preview":
        return run_preview(args)
    if args.command == "add":
        return run_add(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
