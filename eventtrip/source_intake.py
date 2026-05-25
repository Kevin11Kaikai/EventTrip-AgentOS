"""Reviewed source intake helpers for the public source registry.

The intake workflow is intentionally metadata-only. It validates local
YAML/JSON candidate files and can update ``data/source_evidence.yaml`` only
when a caller explicitly asks to save. It does not fetch URLs, scrape pages,
or verify source claims automatically.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from eventtrip.source_evidence import (
    ALLOWED_SOURCE_TYPES,
    SOURCE_CITATION_GROUPS,
    SOURCE_EVIDENCE_PATH,
    build_field_source_attributions,
    grouped_citations,
    load_source_evidence,
    validate_source_evidence,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SOURCE_FIELDS = [
    "source_id",
    "title",
    "publisher",
    "published_date",
    "url",
    "source_type",
    "evidence_tags",
    "summary",
]
ALLOWED_EVIDENCE_TAGS = sorted(
    {
        tag
        for group_config in SOURCE_CITATION_GROUPS.values()
        for tag in group_config["tags"]
    }
)
REQUIRED_FIELD_ATTRIBUTIONS = {
    "match_name",
    "match_date",
    "match_venue",
    "official_ticket_path",
    "secondary_market_stubhub",
    "unknown_exact_prices",
    "reviewed_live_snapshots",
    "forecast_chart",
    "pit_recommendation",
    "sea_recommendation",
    "trigger_policy",
    "houston_logistics",
}
SOURCE_BACKED_REQUIRED_FIELDS = {
    "match_name",
    "match_date",
    "match_venue",
    "official_ticket_path",
    "secondary_market_stubhub",
    "houston_logistics",
}


def load_source_candidate(path: str | Path, default_match_id: str = "portugal_dr_congo") -> tuple[str, dict[str, Any]]:
    """Load one source candidate from a local YAML or JSON file."""
    candidate_path = Path(path)
    if not candidate_path.exists():
        raise FileNotFoundError(f"Source candidate file not found: {candidate_path}")
    suffix = candidate_path.suffix.lower()
    text = candidate_path.read_text(encoding="utf-8")
    if suffix in {".yaml", ".yml"}:
        payload = yaml.safe_load(text) or {}
    elif suffix == ".json":
        payload = json.loads(text)
    else:
        raise ValueError("Source candidate must be a .yaml, .yml, or .json file.")
    return normalize_candidate_payload(payload, default_match_id=default_match_id)


def normalize_candidate_payload(
    payload: dict[str, Any],
    default_match_id: str = "portugal_dr_congo",
) -> tuple[str, dict[str, Any]]:
    """Return ``(match_id, source)`` from a supported candidate payload shape."""
    if not isinstance(payload, dict):
        raise ValueError("Source candidate payload must be a mapping.")
    match_id = str(payload.get("match_id") or default_match_id).strip()
    source = payload.get("source", payload)
    if not isinstance(source, dict):
        raise ValueError("Source candidate must contain a source mapping.")
    normalized_source = dict(source)
    if normalized_source.get("published_date") is not None:
        normalized_source["published_date"] = str(normalized_source["published_date"])
    return match_id, normalized_source


def validate_source_record(
    source: dict[str, Any],
    *,
    existing_source_ids: set[str] | None = None,
    allow_duplicate: bool = False,
) -> list[str]:
    """Validate one source record before it is added to the registry."""
    errors: list[str] = []
    existing_ids = existing_source_ids or set()
    for field in REQUIRED_SOURCE_FIELDS:
        value = source.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"source missing required field: {field}")

    source_id = str(source.get("source_id", "")).strip()
    if source_id and source_id in existing_ids and not allow_duplicate:
        errors.append(f"duplicate source_id: {source_id}")

    url = str(source.get("url", "")).strip()
    if url and not url.startswith("https://"):
        errors.append("source url must use https://")

    source_type = source.get("source_type")
    if source_type and source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"unsupported source_type: {source_type}")

    tags = source.get("evidence_tags", [])
    if tags and not isinstance(tags, list):
        errors.append("evidence_tags must be a list.")
        tags = []
    normalized_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
    if not normalized_tags:
        errors.append("source must include at least one evidence tag.")
    unknown_tags = sorted(set(normalized_tags) - set(ALLOWED_EVIDENCE_TAGS))
    for tag in unknown_tags:
        errors.append(f"unknown evidence tag: {tag}")
    if normalized_tags and not matched_citation_groups(normalized_tags):
        errors.append("source evidence_tags do not map to any citation group.")
    return errors


def matched_citation_groups(tags: list[str]) -> list[str]:
    """Return citation group keys matched by evidence tags."""
    tag_set = set(tags)
    groups = []
    for group_key, group_config in SOURCE_CITATION_GROUPS.items():
        if tag_set.intersection(set(group_config["tags"])):
            groups.append(group_key)
    return groups


def validate_citation_group_coverage(match_sources: dict[str, Any]) -> list[str]:
    """Ensure each configured citation group has at least one registered source."""
    groups = grouped_citations(match_sources)
    errors = []
    for group_key in SOURCE_CITATION_GROUPS:
        if not groups.get(group_key):
            errors.append(f"citation group has no sources: {group_key}")
    return errors


def validate_source_tag_coverage(match_sources: dict[str, Any]) -> list[str]:
    """Validate source tags for all sources in one match registry."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    for source in match_sources.get("sources", []):
        source_id = str(source.get("source_id", "")).strip()
        errors.extend(
            f"{source_id or '<missing source_id>'}: {error}"
            for error in validate_source_record(
                source,
                existing_source_ids=seen_ids,
                allow_duplicate=False,
            )
        )
        if source_id:
            seen_ids.add(source_id)
    return errors


def validate_field_attribution_coverage(match_sources: dict[str, Any]) -> list[str]:
    """Check field-level attribution integrity for the source-backed HTML report."""
    errors: list[str] = []
    source_ids = {
        str(source.get("source_id"))
        for source in match_sources.get("sources", [])
        if source.get("source_id")
    }
    attributions = build_field_source_attributions(match_sources)
    missing_fields = sorted(REQUIRED_FIELD_ATTRIBUTIONS - set(attributions))
    for field_id in missing_fields:
        errors.append(f"missing field attribution: {field_id}")

    for field_id, attribution in attributions.items():
        for source_id in attribution.source_ids:
            if source_id not in source_ids:
                errors.append(f"{field_id} references unknown source_id: {source_id}")
        if field_id in SOURCE_BACKED_REQUIRED_FIELDS and not attribution.source_ids:
            errors.append(f"{field_id} is source_backed but has no source_ids.")
    return errors


def validate_source_registry(
    path: str | Path = SOURCE_EVIDENCE_PATH,
    match_id: str | None = None,
) -> list[str]:
    """Run strict registry validation for intake and publishing."""
    errors = list(validate_source_evidence(path))
    registry = load_source_evidence(path)
    match_items = (
        [(match_id, registry.get(match_id, {}))]
        if match_id
        else list(registry.items())
    )
    for current_match_id, match_sources in match_items:
        if not match_sources:
            errors.append(f"{current_match_id} has no source registry entry.")
            continue
        errors.extend(
            f"{current_match_id}: {error}"
            for error in validate_source_tag_coverage(match_sources)
        )
        errors.extend(
            f"{current_match_id}: {error}"
            for error in validate_citation_group_coverage(match_sources)
        )
        errors.extend(
            f"{current_match_id}: {error}"
            for error in validate_field_attribution_coverage(match_sources)
        )
    return errors


def preview_source_candidate(
    candidate_path: str | Path,
    *,
    registry_path: str | Path = SOURCE_EVIDENCE_PATH,
    default_match_id: str = "portugal_dr_congo",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Validate a candidate source and return a report-safe preview."""
    registry = load_source_evidence(registry_path)
    match_id, source = load_source_candidate(candidate_path, default_match_id=default_match_id)
    match_sources = deepcopy(registry.get(match_id, {"match_id": match_id, "sources": []}))
    existing_ids = {
        str(item.get("source_id"))
        for item in match_sources.get("sources", [])
        if item.get("source_id")
    }
    errors = validate_source_record(
        source,
        existing_source_ids=existing_ids,
        allow_duplicate=overwrite,
    )
    matched_groups = matched_citation_groups([str(tag) for tag in source.get("evidence_tags", [])])
    simulated_registry = deepcopy(registry)
    if not errors:
        apply_source_to_registry_data(simulated_registry, match_id, source, overwrite=overwrite)
        errors.extend(validate_source_registry_data(simulated_registry, match_id=match_id))

    return {
        "status": "valid" if not errors else "invalid",
        "match_id": match_id,
        "source_id": source.get("source_id"),
        "source_type": source.get("source_type"),
        "evidence_tags": list(source.get("evidence_tags", [])),
        "citation_groups": matched_groups,
        "field_attribution_status": "checked" if not errors else "blocked",
        "would_write": False,
        "errors": errors,
        "source": source,
    }


def validate_source_registry_data(
    registry: dict[str, Any],
    match_id: str | None = None,
) -> list[str]:
    """Validate an in-memory source registry."""
    errors: list[str] = []
    match_items = (
        [(match_id, registry.get(match_id, {}))]
        if match_id
        else list(registry.items())
    )
    for current_match_id, match_sources in match_items:
        if not match_sources:
            errors.append(f"{current_match_id} has no source registry entry.")
            continue
        errors.extend(validate_source_tag_coverage(match_sources))
        errors.extend(validate_citation_group_coverage(match_sources))
        errors.extend(validate_field_attribution_coverage(match_sources))
    return errors


def add_source_candidate(
    candidate_path: str | Path,
    *,
    registry_path: str | Path = SOURCE_EVIDENCE_PATH,
    default_match_id: str = "portugal_dr_congo",
    save: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Add one reviewed source candidate, or return a dry-run result."""
    registry_path = Path(registry_path)
    registry = load_source_evidence(registry_path)
    match_id, source = load_source_candidate(candidate_path, default_match_id=default_match_id)
    match_sources = registry.get(match_id, {"match_id": match_id, "sources": []})
    existing_ids = {
        str(item.get("source_id"))
        for item in match_sources.get("sources", [])
        if item.get("source_id")
    }
    errors = validate_source_record(
        source,
        existing_source_ids=existing_ids,
        allow_duplicate=overwrite,
    )
    if errors:
        return _intake_result("invalid", match_id, source, registry_path, False, errors)

    updated = deepcopy(registry)
    action = apply_source_to_registry_data(updated, match_id, source, overwrite=overwrite)
    errors = validate_source_registry_data(updated, match_id=match_id)
    if errors:
        return _intake_result("invalid", match_id, source, registry_path, False, errors)

    if not save:
        result = _intake_result("dry_run", match_id, source, registry_path, False, [])
        result["would"] = action
        return result

    write_source_registry(registry_path, updated)
    result = _intake_result("saved", match_id, source, registry_path, True, [])
    result["action"] = action
    return result


def apply_source_to_registry_data(
    registry: dict[str, Any],
    match_id: str,
    source: dict[str, Any],
    *,
    overwrite: bool = False,
) -> str:
    """Apply one source to an in-memory registry and return the planned action."""
    match_sources = registry.setdefault(match_id, {"match_id": match_id, "sources": []})
    sources = match_sources.setdefault("sources", [])
    source_id = str(source.get("source_id"))
    for index, existing in enumerate(sources):
        if str(existing.get("source_id")) == source_id:
            if not overwrite:
                raise ValueError(f"duplicate source_id: {source_id}")
            sources[index] = dict(source)
            return "replace"
    sources.append(dict(source))
    return "append"


def write_source_registry(path: str | Path, registry: dict[str, Any]) -> None:
    """Write a source registry with stable key order and UTF-8 encoding."""
    Path(path).write_text(
        yaml.safe_dump(registry, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def source_template(match_id: str = "portugal_dr_congo") -> dict[str, Any]:
    """Return a local template for adding one reviewed public source."""
    return {
        "match_id": match_id,
        "source": {
            "source_id": "example_public_source",
            "title": "Example public source title",
            "publisher": "Example Publisher",
            "published_date": "2026-05-24",
            "url": "https://example.com/public-source",
            "source_type": "news",
            "evidence_tags": ["tickets", "ticket_safety"],
            "summary": "Short human-reviewed summary of what this source supports.",
        },
    }


def _intake_result(
    status: str,
    match_id: str,
    source: dict[str, Any],
    path: Path,
    saved: bool,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "status": status,
        "match_id": match_id,
        "source_id": source.get("source_id"),
        "citation_groups": matched_citation_groups(
            [str(tag) for tag in source.get("evidence_tags", [])]
        ),
        "path": str(path),
        "saved": saved,
        "errors": list(errors),
    }
