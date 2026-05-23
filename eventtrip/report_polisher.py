"""Optional LLM report polishing with deterministic invariant checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip import llm_client


PROTECTED_VALUES = [
    "Portugal vs DR Congo",
    "NRG Stadium",
    "Option A: One-night balanced plan",
    "$1120",
    "$1220",
    "Monitor with wait bias",
    "monitor_with_wait_bias",
    "41.9/100",
    "71.4/100",
    "$550",
    "$600",
]
OPTIONAL_THRESHOLD_FORMS = ["$680-$700", "$680\u2013$700"]
DATE_FORMS = ["2026-06-17", "June 17, 2026"]
VENUE_FORMS = ["NRG Stadium", "Houston Stadium"]
REQUIRED_LIMITATION_PHRASES = [
    "No live market, flight, hotel, or ticket APIs are used.",
    "No real paid travel APIs are used.",
    "No web scraping is used.",
    "This demo is decision support, not financial, legal, or travel advice.",
]
PROTECTED_METADATA_ORDER = [
    "match_name",
    "match_date",
    "venue",
    "recommended_plan",
    "ticket_timing_code",
    "ticket_timing_label",
    "traveler_a_cost",
    "traveler_b_cost",
    "single_day_scalper_stress_index",
    "snapshot_scalper_stress_index",
    "buy_trigger_official_resale",
    "strong_consider_trigger",
    "monitor_range",
]
LIMITATION_PHRASES = [
    *REQUIRED_LIMITATION_PHRASES,
    "No web scraping, no browser automation, and no real paid travel APIs are used.",
    "The demo is decision support, not financial, legal, or travel advice.",
]
FORBIDDEN_POLISHED_CLAIMS = [
    "real-time API",
    "live API data",
    "live ticket prices",
    "real ticket prices",
    "guaranteed",
    "prediction of real 2026 prices",
]


def extract_report_invariants(report_text: str) -> dict[str, Any]:
    """Extract source-of-truth strings that a polished report must preserve."""
    values = [value for value in PROTECTED_VALUES if value in report_text]

    date_value = next((value for value in DATE_FORMS if value in report_text), None)
    if date_value:
        values.append(date_value)

    venue_values = [value for value in VENUE_FORMS if value in report_text]
    for venue_value in venue_values:
        if venue_value not in values:
            values.append(venue_value)

    threshold_value = next((value for value in OPTIONAL_THRESHOLD_FORMS if value in report_text), None)
    if threshold_value:
        values.append(threshold_value)

    limitations = list(REQUIRED_LIMITATION_PHRASES)
    limitations.extend(phrase for phrase in LIMITATION_PHRASES if phrase in report_text)
    values.extend(phrase for phrase in limitations if phrase not in values)
    metadata = _extract_protected_metadata(values, date_value, venue_values, threshold_value)

    return {
        "protected_values": sorted(set(values), key=values.index),
        "date_value": date_value,
        "venue_values": venue_values,
        "threshold_value": threshold_value,
        "limitations": limitations,
        "metadata": metadata,
    }


def build_polishing_prompt(report_text: str, invariants: dict[str, Any]) -> tuple[str, str]:
    """Build system and user prompts for presentation-only report polishing."""
    protected = "\n".join(f"- {value}" for value in invariants["protected_values"])
    required_limitations = "\n".join(f"- {phrase}" for phrase in REQUIRED_LIMITATION_PHRASES)
    system_prompt = (
        "You polish Markdown reports for EventTrip-AgentOS. Your task is presentation only. "
        "Preserve all protected values exactly, keep the output as Markdown, do not invent live "
        "data, do not change recommendations, and do not remove limitations. You must preserve "
        "a Limitations section with the exact required limitation phrases. The report may include "
        "a Protected Decision Metadata block; do not remove or rewrite that block if present."
    )
    user_prompt = f"""Rewrite the report for clarity, readability, and professional tone.

Rules:
- Preserve all headings or use equivalent headings.
- Preserve every protected value exactly where possible.
- Do not change computed numbers, option names, dates, scores, trigger thresholds, match names, traveler names, or recommendations.
- Do not invent live data, real prices, external API results, real predictions, or purchase advice.
- Do not add unsupported claims.
- Do not remove limitations.
- Do not convert mock estimates into real predictions.
- Preserve a `## Limitations` section.
- Preserve any `## Protected Decision Metadata` block if present.
- Include these exact limitation phrases without paraphrasing, removing, or weakening them:
{required_limitations}

Protected values:
{protected}

Source report:
{report_text}
"""
    return system_prompt, user_prompt


def ensure_required_limitations(polished_text: str) -> str:
    """Append a deterministic Limitations section when required phrases are missing."""
    missing = [phrase for phrase in REQUIRED_LIMITATION_PHRASES if phrase not in polished_text]
    if not missing:
        return polished_text

    limitation_lines = "\n".join(f"- {phrase}" for phrase in REQUIRED_LIMITATION_PHRASES)
    return f"""{polished_text.rstrip()}

## Limitations

{limitation_lines}
"""


def ensure_protected_metadata(polished_text: str, invariants: dict[str, Any]) -> str:
    """Append a deterministic metadata block that preserves machine-readable decisions."""
    metadata = invariants.get("metadata", {})
    metadata = {key: value for key, value in metadata.items() if value}
    if not metadata:
        return polished_text

    cleaned_text = _remove_existing_metadata_block(polished_text)
    metadata_lines = [
        f"- {key}: {metadata[key]}"
        for key in PROTECTED_METADATA_ORDER
        if key in metadata and metadata[key]
    ]
    block = "## Protected Decision Metadata\n\n" + "\n".join(metadata_lines)
    return f"{cleaned_text.rstrip()}\n\n{block}\n"


def validate_polished_report(
    original_text: str,
    polished_text: str,
    invariants: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Conservatively verify that polished Markdown preserves protected facts."""
    issues: list[str] = []

    if not polished_text.strip():
        issues.append("Polished report is empty.")

    for value in invariants["protected_values"]:
        if value not in polished_text:
            issues.append(f"Missing protected value: {value}")

    if "Recommended plan: Option B" in polished_text and "Recommended plan: Option B" not in original_text:
        issues.append("Polished report appears to recommend Option B.")

    if "Option B: Same-day aggressive plan" in polished_text and "Recommended plan: Option B" in polished_text:
        issues.append("Polished report appears to recommend Option B.")

    if "$999" in polished_text and "$999" not in original_text:
        issues.append("Polished report includes changed or unsupported cost value: $999")

    lowered = polished_text.lower()
    for forbidden in FORBIDDEN_POLISHED_CLAIMS:
        if forbidden.lower() in lowered:
            issues.append(f"Polished report contains unsupported claim: {forbidden}")

    for phrase in REQUIRED_LIMITATION_PHRASES:
        if phrase not in polished_text:
            issues.append(f"Missing required limitation phrase: {phrase}")

    for phrase in invariants.get("limitations", []):
        if phrase not in polished_text:
            issues.append(f"Missing limitation phrase: {phrase}")

    return not issues, issues


def polish_report(original_report_path: Path, output_path: Path) -> dict[str, Any]:
    """Generate and validate a separate polished report artifact."""
    original_text = original_report_path.read_text(encoding="utf-8")
    invariants = extract_report_invariants(original_text)
    system_prompt, user_prompt = build_polishing_prompt(original_text, invariants)
    polished_text = llm_client.generate_text(system_prompt, user_prompt)
    model = llm_client.configured_model()

    if polished_text.startswith("ERROR:"):
        return {
            "status": "llm_error",
            "output_path": None,
            "issues": [polished_text],
            "model": model,
        }

    polished_text = ensure_required_limitations(polished_text)
    polished_text = ensure_protected_metadata(polished_text, invariants)
    ok, issues = validate_polished_report(original_text, polished_text, invariants)
    if not ok:
        failure_path = output_path.with_name(f"{output_path.stem}_FAILED{output_path.suffix}")
        failure_path.write_text(
            _format_failure_report(issues),
            encoding="utf-8",
        )
        return {
            "status": "validation_failed",
            "output_path": failure_path,
            "issues": issues,
            "model": model,
        }

    output_path.write_text(polished_text, encoding="utf-8")
    return {
        "status": "completed",
        "output_path": output_path,
        "issues": [],
        "model": model,
    }


def _format_failure_report(issues: list[str]) -> str:
    issue_lines = "\n".join(f"- {issue}" for issue in issues)
    return f"""# LLM Report Polishing Failed

The deterministic report remains the source of truth. The polished report was not saved because validation found protected-value issues.

## Validation Issues

{issue_lines}
"""


def _extract_protected_metadata(
    protected_values: list[str],
    date_value: str | None,
    venue_values: list[str],
    threshold_value: str | None,
) -> dict[str, str]:
    return {
        "match_name": _find_value(protected_values, "Portugal vs DR Congo"),
        "match_date": date_value or "",
        "venue": _find_first(protected_values, venue_values),
        "recommended_plan": _find_value(protected_values, "Option A: One-night balanced plan"),
        "ticket_timing_code": _find_value(protected_values, "monitor_with_wait_bias"),
        "ticket_timing_label": _find_value(protected_values, "Monitor with wait bias"),
        "traveler_a_cost": _find_value(protected_values, "$1120"),
        "traveler_b_cost": _find_value(protected_values, "$1220"),
        "single_day_scalper_stress_index": _find_value(protected_values, "41.9/100"),
        "snapshot_scalper_stress_index": _find_value(protected_values, "71.4/100"),
        "buy_trigger_official_resale": _find_value(protected_values, "$550"),
        "strong_consider_trigger": _find_value(protected_values, "$600"),
        "monitor_range": threshold_value or "",
    }


def _find_value(values: list[str], target: str) -> str:
    return target if target in values else ""


def _find_first(values: list[str], candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate in values:
            return candidate
    return ""


def _remove_existing_metadata_block(text: str) -> str:
    marker = "## Protected Decision Metadata"
    start = text.find(marker)
    if start == -1:
        return text

    next_section = text.find("\n## ", start + len(marker))
    if next_section == -1:
        return text[:start]
    return text[:start] + text[next_section + 1 :]
