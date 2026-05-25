"""Exportable source registry review packets.

This module is intentionally metadata-only. It summarizes the curated source
registry, citation group coverage, source tags, and field-level attribution
checks without fetching URLs or scraping websites.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eventtrip.source_evidence import (
    SOURCE_CITATION_GROUPS,
    SOURCE_EVIDENCE_PATH,
    build_field_source_attributions,
    grouped_citations,
    load_source_evidence,
)
from eventtrip.source_intake import (
    REQUIRED_SOURCE_FIELDS,
    matched_citation_groups,
    validate_source_registry,
)


PR_REVIEW_CHECKLIST = [
    "The source URL is a public HTTPS page and does not require login, payment, checkout, or CAPTCHA.",
    "The source summary is human-reviewed and does not overstate what the page supports.",
    "The source uses supported source_type and evidence_tags values.",
    "The source maps to at least one citation group used by the public report.",
    "No unsupported ticket, flight, hotel, local transport, or total-budget number is presented as source-backed.",
    "Field-level attribution still distinguishes source-backed facts, model inference, internal policy, and unknown values.",
    "No secrets, credentials, generated run outputs, or private local files are included.",
]


def build_source_registry_review_summary(
    registry_path: str | Path = SOURCE_EVIDENCE_PATH,
    match_id: str = "portugal_dr_congo",
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Return a JSON-serializable review summary for one match registry."""
    registry_path = Path(registry_path)
    registry = load_source_evidence(registry_path)
    match_sources = registry.get(match_id, {"match_id": match_id, "sources": []})
    sources = [dict(source) for source in match_sources.get("sources", [])]
    validation_errors = validate_source_registry(registry_path, match_id=match_id)
    citations = grouped_citations(match_sources)
    attributions = build_field_source_attributions(match_sources)
    source_ids = {str(source.get("source_id")) for source in sources if source.get("source_id")}

    return {
        "generated_at": generated_at or _utc_now(),
        "registry_path": str(registry_path),
        "match_id": match_id,
        "status": "pass" if not validation_errors else "fail",
        "source_count": len(sources),
        "source_counts_by_type": _counter_dict(source.get("source_type", "unknown") for source in sources),
        "evidence_tag_counts": _counter_dict(
            tag
            for source in sources
            for tag in source.get("evidence_tags", [])
        ),
        "citation_groups": _citation_group_rows(citations),
        "sources": _source_rows(sources),
        "field_attributions": _field_attribution_rows(attributions, source_ids),
        "validation_errors": validation_errors,
        "review_checklist": PR_REVIEW_CHECKLIST,
        "review_status_checks": _review_status_checks(
            sources=sources,
            citation_groups=citations,
            validation_errors=validation_errors,
            attributions=attributions,
            source_ids=source_ids,
        ),
    }


def render_source_registry_review_markdown(summary: dict[str, Any]) -> str:
    """Render a review summary as a GitHub-friendly Markdown packet."""
    status_label = "PASS" if summary["status"] == "pass" else "FAIL"
    validation_errors = summary.get("validation_errors", [])
    error_rows = (
        "\n".join(f"- {error}" for error in validation_errors)
        if validation_errors
        else "- None."
    )
    checklist_rows = "\n".join(
        f"- [{'x' if item['passed'] else ' '}] {item['label']}"
        for item in summary.get("review_status_checks", [])
    )
    pr_checklist_rows = "\n".join(
        f"- [ ] {item}" for item in summary.get("review_checklist", [])
    )

    return f"""# Source Registry Review Packet

## Summary

| Field | Value |
|---|---|
| Generated at | {_md(summary["generated_at"])} |
| Match ID | `{_md(summary["match_id"])}` |
| Registry | `{_md(summary["registry_path"])}` |
| Validation status | **{status_label}** |
| Source count | {summary["source_count"]} |

## Automated Review Checks

{checklist_rows}

## Citation Group Coverage

{_citation_group_table(summary.get("citation_groups", []))}

## Source Inventory

{_source_inventory_table(summary.get("sources", []))}

## Evidence Tag Counts

{_counter_table(summary.get("evidence_tag_counts", {}), "Evidence tag")}

## Field-Level Attribution Coverage

{_field_attribution_table(summary.get("field_attributions", []))}

## Validation Errors

{error_rows}

## Pull Request Review Checklist

{pr_checklist_rows}

## Reviewer Notes

- This packet is generated from local source metadata only.
- It does not fetch URLs, scrape websites, verify article contents automatically, or purchase tickets.
- If a public source does not support a value, keep that value unknown or internally labeled rather than source-backed.
"""


def write_source_registry_review_packet(
    output_path: str | Path,
    registry_path: str | Path = SOURCE_EVIDENCE_PATH,
    match_id: str = "portugal_dr_congo",
    *,
    output_format: str = "md",
) -> Path:
    """Write a review packet in Markdown or JSON format and return its path."""
    import json

    summary = build_source_registry_review_summary(registry_path, match_id)
    path = Path(output_path)
    if output_format == "md":
        path.write_text(render_source_registry_review_markdown(summary), encoding="utf-8")
    elif output_format == "json":
        path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
    else:
        raise ValueError(f"Unsupported review packet format: {output_format}")
    return path


def _review_status_checks(
    *,
    sources: list[dict[str, Any]],
    citation_groups: dict[str, list[dict[str, Any]]],
    validation_errors: list[str],
    attributions: dict[str, Any],
    source_ids: set[str],
) -> list[dict[str, Any]]:
    return [
        {
            "label": "Registry passes strict source intake validation.",
            "passed": not validation_errors,
        },
        {
            "label": "Every source has required metadata fields.",
            "passed": all(_has_required_fields(source) for source in sources),
        },
        {
            "label": "Every citation group has at least one source.",
            "passed": all(citation_groups.get(group_key) for group_key in SOURCE_CITATION_GROUPS),
        },
        {
            "label": "Every source maps to at least one citation group.",
            "passed": all(
                matched_citation_groups([str(tag) for tag in source.get("evidence_tags", [])])
                for source in sources
            ),
        },
        {
            "label": "Field-level source IDs all point to registered sources.",
            "passed": all(
                source_id in source_ids
                for attribution in attributions.values()
                for source_id in attribution.source_ids
            ),
        },
        {
            "label": "Unknown or model-derived values remain separated from source-backed facts.",
            "passed": any(
                attribution.status == "no_source_backed_data_found"
                for attribution in attributions.values()
            )
            and any(
                attribution.status == "model_inference"
                for attribution in attributions.values()
            ),
        },
    ]


def _citation_group_rows(
    citations: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for group_key, group_config in SOURCE_CITATION_GROUPS.items():
        sources = citations.get(group_key, [])
        rows.append(
            {
                "group_key": group_key,
                "title": group_config["title"],
                "source_count": len(sources),
                "source_ids": [str(source.get("source_id")) for source in sources],
            }
        )
    return rows


def _source_rows(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for source in sources:
        tags = [str(tag) for tag in source.get("evidence_tags", [])]
        rows.append(
            {
                "source_id": source.get("source_id"),
                "title": source.get("title"),
                "publisher": source.get("publisher"),
                "published_date": str(source.get("published_date", "")),
                "source_type": source.get("source_type"),
                "url": source.get("url"),
                "evidence_tags": tags,
                "citation_groups": matched_citation_groups(tags),
            }
        )
    return rows


def _field_attribution_rows(
    attributions: dict[str, Any],
    source_ids: set[str],
) -> list[dict[str, Any]]:
    rows = []
    for field_id, attribution in sorted(attributions.items()):
        rows.append(
            {
                "field_id": field_id,
                "label": attribution.label,
                "status": attribution.status,
                "source_group": attribution.source_group,
                "source_ids": list(attribution.source_ids),
                "unknown_source_ids": [
                    source_id
                    for source_id in attribution.source_ids
                    if source_id not in source_ids
                ],
                "note": attribution.note,
            }
        )
    return rows


def _has_required_fields(source: dict[str, Any]) -> bool:
    return all(source.get(field) not in (None, "", []) for field in REQUIRED_SOURCE_FIELDS)


def _counter_dict(values: Any) -> dict[str, int]:
    counter = Counter(str(value) for value in values if str(value))
    return dict(sorted(counter.items()))


def _citation_group_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Group | Title | Sources | Source IDs |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{_md(row['group_key'])}` | {_md(row['title'])} | {row['source_count']} | "
            f"{_md(', '.join(row['source_ids']) or 'None')} |"
        )
    return "\n".join(lines)


def _source_inventory_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Source ID | Publisher | Type | Tags | Citation groups |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{_md(row['source_id'])}` | {_md(row['publisher'])} | {_md(row['source_type'])} | "
            f"{_md(', '.join(row['evidence_tags']))} | {_md(', '.join(row['citation_groups']))} |"
        )
    return "\n".join(lines)


def _field_attribution_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Field ID | Status | Source IDs | Unknown source refs |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{_md(row['field_id'])}` | {_md(row['status'])} | "
            f"{_md(', '.join(row['source_ids']) or 'None')} | "
            f"{_md(', '.join(row['unknown_source_ids']) or 'None')} |"
        )
    return "\n".join(lines)


def _counter_table(counter: dict[str, int], first_header: str) -> str:
    lines = [
        f"| {first_header} | Count |",
        "|---|---:|",
    ]
    for key, count in sorted(counter.items()):
        lines.append(f"| `{_md(key)}` | {count} |")
    return "\n".join(lines)


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
