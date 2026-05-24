"""Opt-in live data preview CLI.

Default usage is fixture/local-file based. Real HTTP is disabled unless the
caller explicitly passes --live-http and EVENTTRIP_ENABLE_LIVE_PROVIDERS=true.
"""

from __future__ import annotations

import argparse
import json

from eventtrip.data_providers.opt_in_http_provider import OptInHttpJsonProvider


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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        provider = OptInHttpJsonProvider(
            input_path=args.input,
            endpoint_url=args.endpoint_url,
            api_key_env=args.api_key_env,
            allowed_hosts=args.allow_host,
        )
        preview = provider.preview(match_id=args.match_id, live_http=args.live_http)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    print(json.dumps(preview, indent=2, sort_keys=True))
    if args.endpoint_url and args.live_http:
        print("Live HTTP was explicitly enabled for this preview.")
    else:
        print("No live HTTP call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
