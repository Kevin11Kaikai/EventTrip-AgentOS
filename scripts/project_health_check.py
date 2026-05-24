"""Local repository health checks for EventTrip-AgentOS.

The script is intentionally offline and avoids printing secret values.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMPORTANT_FILES = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "docs/architecture.md",
    "docs/mcp_validation.md",
    "docs/demo_walkthrough.md",
    "docs/project_summary.md",
    "docs/dashboard_guide.md",
    "docs/api_adapter_design.md",
    "docs/web_collection.md",
    "docs/ticket_links.md",
    "docs/source_backed_report.md",
    "examples/mcp_client_validation_output.txt",
    "examples/external_snapshot_import.csv",
    "examples/sample_ticket_market_page.html",
    "examples/sample_web_evidence.json",
    "app/streamlit_app.py",
    "data/web_evidence/.gitkeep",
    "data/web_evidence/raw/.gitkeep",
    "eventtrip/web_collect_cli.py",
    "eventtrip/evidence_review.py",
    "eventtrip/evidence_review_cli.py",
    "eventtrip/ticket_links.py",
    "eventtrip/source_evidence.py",
    "eventtrip/source_report_cli.py",
    "eventtrip/agents/ticket_link_agent.py",
    "eventtrip/agents/source_backed_report_agent.py",
    "data/ticket_links.yaml",
    "data/source_evidence.yaml",
    "eventtrip/web_collection/collector.py",
    "eventtrip/web_collection/extractor.py",
]
README_REQUIRED_PHRASES = [
    "deterministic, offline",
    "does not scrape websites",
    "EventTrip-AgentOS Dashboard",
    "OhMyGPT",
    "MCP",
]


def has_suspicious_secret(text: str) -> bool:
    """Return True when text appears to contain a real secret-like value."""
    secret_prefix = "s" + "k-"
    if re.search(re.escape(secret_prefix) + r"[A-Za-z0-9]{20,}", text):
        return True
    key_name = "OHMYGPT" + "_API_KEY"
    for match in re.finditer(re.escape(key_name) + r"=([^\s]+)", text):
        value = match.group(1).strip()
        if value and value != "your_ohmygpt_api_key_here":
            return True
    return False


def run_git(args: list[str]) -> tuple[int, str]:
    """Run a git command and return exit code and combined output."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, "git not available"
    return result.returncode, f"{result.stdout}{result.stderr}"


def check_important_files() -> list[str]:
    missing = [path for path in IMPORTANT_FILES if not (PROJECT_ROOT / path).exists()]
    if not (PROJECT_ROOT / "runs" / ".gitkeep").exists():
        missing.append("runs/.gitkeep")
    return [f"Missing required file: {path}" for path in missing]


def check_env_not_tracked() -> list[str]:
    code, output = run_git(["ls-files", ".env"])
    if code == 127:
        return []
    if code != 0:
        return [f"Unable to check tracked .env status: {output.strip()}"]
    if output.strip():
        return [".env is tracked by Git."]
    return []


def check_generated_runs_not_staged() -> list[str]:
    code, output = run_git(["diff", "--cached", "--name-only"])
    if code == 127:
        return []
    if code != 0:
        return [f"Unable to inspect staged files: {output.strip()}"]
    staged = [line.strip() for line in output.splitlines() if line.strip()]
    bad = [path for path in staged if path.startswith("runs/portugal_dr_congo_houston_demo_")]
    return [f"Generated run output is staged: {path}" for path in bad]


def check_tracked_text_for_secrets() -> list[str]:
    code, output = run_git(["ls-files"])
    if code == 127:
        return []
    if code != 0:
        return [f"Unable to list tracked files: {output.strip()}"]

    issues = []
    for relative in output.splitlines():
        path = PROJECT_ROOT / relative
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if has_suspicious_secret(text):
            issues.append(f"Potential secret in tracked file: {relative}")
    return issues


def check_readme_content() -> list[str]:
    readme = PROJECT_ROOT / "README.md"
    if not readme.exists():
        return ["README.md missing."]
    text = readme.read_text(encoding="utf-8")
    return [
        f"README missing expected phrase: {phrase}"
        for phrase in README_REQUIRED_PHRASES
        if phrase not in text
    ]


def run_checks() -> list[tuple[str, list[str]]]:
    return [
        ("important files", check_important_files()),
        (".env tracking", check_env_not_tracked()),
        ("generated run staging", check_generated_runs_not_staged()),
        ("tracked file secrets", check_tracked_text_for_secrets()),
        ("README content", check_readme_content()),
    ]


def main() -> int:
    failures = []
    print("EventTrip-AgentOS project health check")
    for name, issues in run_checks():
        if issues:
            failures.extend(issues)
            print(f"[FAIL] {name}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[OK] {name}")

    if failures:
        print(f"Health check failed with {len(failures)} issue(s).")
        return 1
    print("Health check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
