"""Compatibility CLI alias for source-backed quote intake."""

from __future__ import annotations

from eventtrip.reviewed_quotes_cli import main


if __name__ == "__main__":
    raise SystemExit(main())
