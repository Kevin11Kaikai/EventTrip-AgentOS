"""Source-backed evidence registry for public web/news report artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_EVIDENCE_PATH = PROJECT_ROOT / "data" / "source_evidence.yaml"
ALLOWED_SOURCE_TYPES = {
    "official",
    "news",
    "government",
    "transportation",
    "marketplace",
    "travel_data",
}
SOURCE_CITATION_GROUPS: dict[str, dict[str, Any]] = {
    "match_facts": {
        "title": "Match facts",
        "tags": {"match", "date", "venue"},
    },
    "ticket_safety": {
        "title": "Ticket safety",
        "tags": {
            "tickets",
            "official_purchase",
            "official_resale",
            "ticket_safety",
            "resale_risk",
            "secondary_market",
        },
    },
    "houston_logistics": {
        "title": "Houston logistics",
        "tags": {"houston", "local_transport", "venue_readiness", "team_base_camp"},
    },
    "cost_trends": {
        "title": "Cost trend evidence",
        "tags": {"airfare_trend", "hotel_trend", "ticket_market_pressure"},
    },
}


def load_source_evidence(path: str | Path = SOURCE_EVIDENCE_PATH) -> dict[str, Any]:
    """Load public source evidence from the local curated registry."""
    source_path = Path(path)
    return yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}


def get_match_sources(match_id: str, path: str | Path = SOURCE_EVIDENCE_PATH) -> dict[str, Any]:
    """Return source evidence for one match."""
    registry = load_source_evidence(path)
    return dict(registry.get(match_id, {}))


def validate_source_evidence(path: str | Path = SOURCE_EVIDENCE_PATH) -> list[str]:
    """Return validation errors for the source evidence registry."""
    errors: list[str] = []
    registry = load_source_evidence(path)
    for match_id, match_data in registry.items():
        if not match_data.get("sources"):
            errors.append(f"{match_id} has no sources.")
        for source in match_data.get("sources", []):
            source_id = source.get("source_id", "")
            url = source.get("url", "")
            if not source_id:
                errors.append(f"{match_id} has source without source_id.")
            if not source.get("title"):
                errors.append(f"{match_id}/{source_id} missing title.")
            if not source.get("publisher"):
                errors.append(f"{match_id}/{source_id} missing publisher.")
            if not url.startswith("https://"):
                errors.append(f"{match_id}/{source_id} URL must use https.")
            if source.get("source_type") not in ALLOWED_SOURCE_TYPES:
                errors.append(f"{match_id}/{source_id} has unsupported source_type.")
            if not source.get("summary"):
                errors.append(f"{match_id}/{source_id} missing summary.")
    return errors


def sources_by_tag(match_sources: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    """Return sources with a given evidence tag."""
    return [
        dict(source)
        for source in match_sources.get("sources", [])
        if tag in source.get("evidence_tags", [])
    ]


def sources_by_any_tag(match_sources: dict[str, Any], tags: set[str]) -> list[dict[str, Any]]:
    """Return sources that include at least one tag from a tag group."""
    grouped: list[dict[str, Any]] = []
    for source in match_sources.get("sources", []):
        source_tags = set(source.get("evidence_tags", []))
        if source_tags.intersection(tags):
            grouped.append(dict(source))
    return grouped


def grouped_citations(match_sources: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return report-ready citation groups for source-backed public reports."""
    return {
        group_key: sources_by_any_tag(match_sources, set(group_config["tags"]))
        for group_key, group_config in SOURCE_CITATION_GROUPS.items()
    }


def citation_label(source: dict[str, Any]) -> str:
    """Return a concise Markdown citation label."""
    return f"[{source['publisher']}: {source['title']}]({source['url']})"
