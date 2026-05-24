"""Source-backed public web/news report agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.source_evidence import (
    SOURCE_CITATION_GROUPS,
    citation_label,
    get_match_sources,
    grouped_citations,
)


class SourceBackedReportAgent(BaseAgent):
    name = "source_backed_report_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        match = trip_request["match"]
        match_id = match["match_id"]
        source_data = get_match_sources(match_id)
        ticket_links = context.get("ticket_links", {})
        source_rows = "\n".join(_source_row(source) for source in source_data.get("sources", []))
        official_ticket_rows = "\n".join(
            _ticket_row(link) for link in ticket_links.get("primary_links", [])
        )
        info_ticket_rows = "\n".join(_ticket_row(link) for link in ticket_links.get("info_links", []))
        checklist_rows = "\n".join(
            f"- {item}" for item in ticket_links.get("manual_purchase_checklist", [])
        )
        citation_groups = grouped_citations(source_data)

        body = f"""# Source-Backed Final Report

This report uses only curated public web, official, and news sources listed below. It intentionally excludes local planning estimates for flight, hotel, ticket, and budget totals.

## Executive Summary

- Event: {match["name"]}
- Date: {match["date"]}
- Venue: {match["venue"]} / Houston Stadium, {match["city"]}
- Ticket purchase stance: use official FIFA ticketing or official FIFA resale/exchange; do not use social-media or unofficial resale offers as a primary path.
- Travel-cost stance: no source-backed flight, hotel, or local-transport price estimates are included yet, so this report does not claim a sourced total trip budget.

## Citation Groups

### Match facts

{_grouped_source_list(citation_groups["match_facts"])}

### Ticket safety

{_grouped_source_list(citation_groups["ticket_safety"])}

### Houston logistics

{_grouped_source_list(citation_groups["houston_logistics"])}

### Unknown or not source-backed yet

- Exact all-in ticket price for Portugal vs DR Congo: no source-backed citation registered yet.
- Traveler A airfare from PIT: no source-backed citation registered yet.
- Traveler B airfare from SEA: no source-backed citation registered yet.
- Shared hotel quote for a two-bed room: no source-backed citation registered yet.
- Local transportation cost estimate: no source-backed citation registered yet.
- Total trip budget per traveler: no source-backed citation registered yet.

## Official Ticket Links For Manual Purchase

{official_ticket_rows}

## Official Information / Risk References

{info_ticket_rows}

## Manual Checklist Before Buying

{checklist_rows}

## What This Report Does Not Claim

- No sourced airfare estimate is included.
- No sourced hotel quote is included.
- No sourced ticket price for this exact match is included.
- No sourced total trip budget is included.
- No automatic purchase, login, checkout, or payment action is performed.

## Source Registry

| Source | Publisher | Type | Date | Use |
|---|---|---|---|---|
{source_rows}
"""
        output_path = self.write_output(
            run_dir,
            "10_source_backed_final_report.md",
            {
                "summary": "Source-backed report generated from public web/news evidence.",
                "recommendation": "Use source-backed report for public sharing; keep deterministic report for internal regression.",
                "next_agent": None,
            },
            body,
        )
        return {"source_backed_report_path": output_path, "source_evidence": source_data}


def _source_row(source: dict[str, Any]) -> str:
    tags = ", ".join(source.get("evidence_tags", []))
    return (
        f"| [{source['title']}]({source['url']}) | {source['publisher']} | "
        f"{source['source_type']} | {source.get('published_date', 'n/a')} | {tags} |"
    )


def _ticket_row(link: dict[str, Any]) -> str:
    return (
        f"- [{link['label']}]({link['url']}) "
        f"({link['source_type']}, risk: {link['risk_level']}): {link['recommendation']}"
    )


def _bullet_summaries(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "- No source-backed evidence registered for this area."
    return "\n".join(
        f"- {source['summary']} Source: {citation_label(source)}." for source in sources
    )


def _grouped_source_list(sources: list[dict[str, Any]]) -> str:
    return _bullet_summaries(sources)


def citation_group_titles() -> list[str]:
    """Return human-readable citation group titles used in source-backed reports."""
    return [str(config["title"]) for config in SOURCE_CITATION_GROUPS.values()] + [
        "Unknown or not source-backed yet"
    ]
