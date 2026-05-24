"""CLI helpers for locating source-backed public reports."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_ROOT = PROJECT_ROOT / "runs"
SOURCE_BACKED_REPORT_NAME = "10_source_backed_final_report.md"
RUN_DIR_PREFIX = "portugal_dr_congo_houston_demo_"


def find_latest_source_backed_report(
    runs_root: str | Path = DEFAULT_RUNS_ROOT,
    report_name: str = SOURCE_BACKED_REPORT_NAME,
) -> Path | None:
    """Return the newest source-backed report under timestamped run directories."""
    root = Path(runs_root)
    if not root.exists():
        return None
    candidates = [
        report
        for report in root.glob(f"{RUN_DIR_PREFIX}*/{report_name}")
        if report.is_file()
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: (path.parent.name, path.stat().st_mtime))[-1]


def open_report_path(path: str | Path) -> None:
    """Open a report with the local OS default application."""
    report_path = Path(path)
    if os.name == "nt":
        os.startfile(str(report_path))  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(report_path)])
        return
    subprocess.Popen(["xdg-open", str(report_path)])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print or open the latest source-backed EventTrip report."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    latest = subparsers.add_parser("latest", help="Print the latest source-backed report path.")
    latest.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT), help="Runs directory to scan.")
    latest.add_argument("--open", action="store_true", help="Also open the latest report.")

    open_cmd = subparsers.add_parser("open", help="Open the latest source-backed report.")
    open_cmd.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT), help="Runs directory to scan.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = find_latest_source_backed_report(args.runs_root)
    if report is None:
        print(f"No {SOURCE_BACKED_REPORT_NAME} found under {Path(args.runs_root)}.")
        print("Run: python -m eventtrip.orchestrator --demo portugal_dr_congo_houston")
        return 1

    print(report)
    should_open = args.command == "open" or getattr(args, "open", False)
    if should_open:
        try:
            open_report_path(report)
        except Exception as exc:
            print(f"Unable to open report automatically: {exc}")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
