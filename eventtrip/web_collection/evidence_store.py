"""Local JSON evidence store for web collection outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eventtrip.web_collection.schemas import WebEvidence, to_dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / "data" / "web_evidence"


def save_web_evidence(evidence: WebEvidence, output_dir: Path | str = DEFAULT_EVIDENCE_DIR) -> Path:
    """Save structured web evidence JSON to a local output directory."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{evidence.evidence_id}.json"
    path.write_text(json.dumps(to_dict(evidence), indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_web_evidence(path: Path | str) -> WebEvidence:
    """Load one structured evidence JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _evidence_from_dict(data)


def list_web_evidence(
    output_dir: Path | str = DEFAULT_EVIDENCE_DIR,
    match_id: str | None = None,
) -> list[WebEvidence]:
    """List structured evidence files from a local output directory."""
    directory = Path(output_dir)
    if not directory.exists():
        return []
    evidence_items = []
    for path in sorted(directory.glob("*.json")):
        evidence = load_web_evidence(path)
        if match_id and evidence.match_id != match_id:
            continue
        evidence_items.append(evidence)
    return evidence_items


def _evidence_from_dict(data: dict[str, Any]) -> WebEvidence:
    return WebEvidence(
        evidence_id=data["evidence_id"],
        target_id=data["target_id"],
        match_id=data["match_id"],
        source_url=data.get("source_url"),
        local_path=data.get("local_path"),
        collected_at=data["collected_at"],
        title=data.get("title"),
        text_excerpt=data["text_excerpt"],
        raw_cache_path=data.get("raw_cache_path"),
        extraction_confidence=data["extraction_confidence"],
        extracted_fields=dict(data.get("extracted_fields", {})),
        notes=data.get("notes", ""),
    )
