"""Markdown shared memory helpers.

Each run directory is treated as a small file bus. Agents write one Markdown
file with YAML frontmatter so humans and downstream agents can both read it.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_ROOT = PROJECT_ROOT / "runs"


def write_markdown(path: str | Path, frontmatter: dict[str, Any], body: str) -> None:
    """Write Markdown with YAML frontmatter."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    output_path.write_text(f"---\n{yaml_text}\n---\n\n{body.rstrip()}\n", encoding="utf-8")


def read_markdown(path: str | Path) -> tuple[dict[str, Any], str]:
    """Read Markdown frontmatter and body."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, raw_frontmatter, body = text.split("---", 2)
    metadata = yaml.safe_load(raw_frontmatter) or {}
    return metadata, body.lstrip("\n")


def list_agent_outputs(run_dir: Path) -> list[Path]:
    """Return deterministic Markdown files from a run directory."""
    return sorted(Path(run_dir).glob("*.md"))


def create_run_dir(base_name: str, runs_root: Path | None = None) -> Path:
    """Create a timestamped run directory under runs/."""
    root = runs_root or DEFAULT_RUNS_ROOT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"{base_name}_{timestamp}"
    suffix = 1
    while run_dir.exists():
        run_dir = root / f"{base_name}_{timestamp}_{suffix}"
        suffix += 1
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir

