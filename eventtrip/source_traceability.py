"""Claim-level traceability helpers for public-source evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from eventtrip.source_evidence import citation_label, grouped_citations


@dataclass(frozen=True)
class EvidenceTraceabilityItem:
    """One report claim mapped to its evidence status."""

    claim: str
    status: str
    evidence_group: str
    evidence: list[str]
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "status": self.status,
            "evidence_group": self.evidence_group,
            "evidence": list(self.evidence),
            "note": self.note,
        }


def build_evidence_traceability(match_sources: dict[str, Any]) -> list[EvidenceTraceabilityItem]:
    """Build deterministic claim-to-evidence mappings for the internal report.

    The matrix is intentionally conservative: values without a public source are
    marked as internal estimates or as not source-backed instead of being
    presented as real market facts.
    """
    groups = grouped_citations(match_sources)
    match_labels = _labels(groups.get("match_facts", []))
    ticket_labels = _labels(groups.get("ticket_safety", []))
    logistics_labels = _labels(groups.get("houston_logistics", []))

    return [
        EvidenceTraceabilityItem(
            claim="Portugal vs DR Congo is scheduled for June 17, 2026 in Houston.",
            status="source_backed",
            evidence_group="Match facts",
            evidence=match_labels,
            note="Backed by registered official/news sources.",
        ),
        EvidenceTraceabilityItem(
            claim="Manual ticket purchase should start with FIFA official ticketing or official resale/exchange paths.",
            status="source_backed",
            evidence_group="Ticket safety",
            evidence=ticket_labels,
            note="Backed by FIFA ticketing/support references and public ticket-safety reporting.",
        ),
        EvidenceTraceabilityItem(
            claim="Houston logistics and venue context should be monitored before travel.",
            status="source_backed",
            evidence_group="Houston logistics",
            evidence=logistics_labels,
            note="Backed by registered Houston public reporting.",
        ),
        EvidenceTraceabilityItem(
            claim="Option A: One-night balanced plan is the recommended travel plan.",
            status="internal_estimate_not_source_backed",
            evidence_group="Internal deterministic planning",
            evidence=[],
            note="This is a model recommendation from local deterministic planning logic, not a public-source fact.",
        ),
        EvidenceTraceabilityItem(
            claim="Traveler A estimated cost is $1120 and Traveler B estimated cost is $1220.",
            status="internal_estimate_not_source_backed",
            evidence_group="Internal deterministic planning",
            evidence=[],
            note="These are local planning estimates. No source-backed public airfare, hotel, ticket, or total-budget quote is registered.",
        ),
        EvidenceTraceabilityItem(
            claim="The current ticket timing stance is Monitor with wait bias.",
            status="internal_estimate_not_source_backed",
            evidence_group="Internal deterministic planning",
            evidence=[],
            note="This combines local market-signal logic and manual snapshots; it is not a sourced live-market recommendation.",
        ),
        EvidenceTraceabilityItem(
            claim="Exact all-in Portugal vs DR Congo ticket price, sourced flight prices, sourced hotel quote, and sourced total trip budget.",
            status="no_source_backed_data_found",
            evidence_group="Unknown or not source-backed yet",
            evidence=[],
            note="No registered public source currently supports these exact values. The report says this clearly instead of filling unsupported numbers.",
        ),
    ]


def format_traceability_markdown(items: list[EvidenceTraceabilityItem]) -> str:
    """Format traceability items as a compact Markdown table."""
    rows = [
        "| Claim | Evidence status | Source group | Evidence / note |",
        "|---|---|---|---|",
    ]
    for item in items:
        evidence_text = _evidence_text(item)
        rows.append(
            f"| {item.claim} | {item.status} | {item.evidence_group} | {evidence_text} |"
        )
    return "\n".join(rows)


def _labels(sources: list[dict[str, Any]]) -> list[str]:
    return [citation_label(source) for source in sources]


def _evidence_text(item: EvidenceTraceabilityItem) -> str:
    if item.evidence:
        return "<br>".join(item.evidence)
    return item.note
