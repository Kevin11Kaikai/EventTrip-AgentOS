"""Opt-in live data preview CLI.

Default usage is fixture/local-file based. Real HTTP is disabled unless the
caller explicitly passes --live-http and EVENTTRIP_ENABLE_LIVE_PROVIDERS=true.
"""

from __future__ import annotations

import argparse
import json

from eventtrip.data_providers.opt_in_http_provider import OptInHttpJsonProvider
from eventtrip.live_data_review import import_reviewed_live_snapshots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview opt-in live/API snapshot payloads.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview = subparsers.add_parser("preview", help="Preview normalized snapshots.")
    source = preview.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Local JSON fixture or exported API response.")
    source.add_argument("--endpoint-url", help="Explicit live HTTP JSON endpoint.")
    preview.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")
    preview.add_argument("--api-key-env", help="Optional environment variable for bearer token.")
    preview.add_argument(
        "--allow-host",
        action="append",
        default=[],
        help="Allowed endpoint hostname. Can be repeated.",
    )
    preview.add_argument("--live-http", action="store_true", help="Enable one explicit HTTP call.")

    import_parser = subparsers.add_parser(
        "import",
        help="Review and optionally save opt-in live/API snapshots.",
    )
    import_source = import_parser.add_mutually_exclusive_group(required=True)
    import_source.add_argument("--input", help="Local JSON fixture or exported API response.")
    import_source.add_argument("--endpoint-url", help="Explicit live HTTP JSON endpoint.")
    import_parser.add_argument("--match", "--match-id", dest="match_id", default="portugal_dr_congo")
    import_parser.add_argument("--api-key-env", help="Optional environment variable for bearer token.")
    import_parser.add_argument(
        "--allow-host",
        action="append",
        default=[],
        help="Allowed endpoint hostname. Can be repeated.",
    )
    import_parser.add_argument("--live-http", action="store_true", help="Enable one explicit HTTP call.")
    import_parser.add_argument("--destination", help="Destination snapshot CSV path.")
    mode_group = import_parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", help="Validate without writing.")
    mode_group.add_argument("--save", action="store_true", help="Write reviewed snapshots.")
    import_parser.add_argument(
        "--reviewed",
        action="store_true",
        help="Confirm a human reviewed the live/API-derived values before saving.",
    )
    import_parser.add_argument("--overwrite", action="store_true", help="Replace duplicate match/date rows.")
    import_parser.add_argument("--notes", default="", help="Human review note to append to saved snapshots.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "preview":
            provider = OptInHttpJsonProvider(
                input_path=args.input,
                endpoint_url=args.endpoint_url,
                api_key_env=args.api_key_env,
                allowed_hosts=args.allow_host,
            )
            preview = provider.preview(match_id=args.match_id, live_http=args.live_http)
        elif args.command == "import":
            preview = import_reviewed_live_snapshots(
                input_path=args.input,
                endpoint_url=args.endpoint_url,
                match_id=args.match_id,
                api_key_env=args.api_key_env,
                allowed_hosts=args.allow_host,
                live_http=args.live_http,
                destination_path=args.destination,
                save=bool(args.save),
                reviewed=bool(args.reviewed),
                overwrite=bool(args.overwrite),
                review_notes=args.notes,
            )
        else:
            parser.error(f"Unsupported command: {args.command}")
            return 2
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    print(json.dumps(preview, indent=2, sort_keys=True))
    if args.command == "import" and preview.get("errors"):
        return 1 if preview.get("status") in {"duplicate", "review_required"} else 2
    if args.endpoint_url and args.live_http:
        print("Live HTTP was explicitly enabled for this preview.")
    else:
        print("No live HTTP call was made.")
    if args.command == "import":
        if preview.get("saved"):
            print("Reviewed live data snapshots were saved.")
        else:
            print("Dry run or validation-only mode: no snapshot file was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
