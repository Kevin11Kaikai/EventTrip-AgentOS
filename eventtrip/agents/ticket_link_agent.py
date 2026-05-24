"""Ticket link recommendation agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.ticket_links import recommend_ticket_links


class TicketLinkAgent(BaseAgent):
    name = "ticket_link_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        match_id = trip_request["match"]["match_id"]
        ticket_timing = context.get("combined_ticket_timing_recommendation") or context.get(
            "ticket_timing", "monitor"
        )
        recommendations = recommend_ticket_links(match_id, ticket_timing=ticket_timing)
        primary_rows = "\n".join(
            _link_line(link) for link in recommendations["primary_links"]
        )
        info_rows = "\n".join(_link_line(link) for link in recommendations["info_links"])
        optional_rows = "\n".join(_link_line(link) for link in recommendations["optional_links"])
        secondary_rows = "\n".join(
            _link_line(link) for link in recommendations.get("secondary_links", [])
        )
        warning_lines = "\n".join(f"- {item}" for item in recommendations["warnings"])
        checklist_lines = "\n".join(
            f"- {item}" for item in recommendations["manual_purchase_checklist"]
        )

        body = f"""# Ticket Link Recommendations

Phase 7.2 recommends safe manual navigation links only. EventTrip-AgentOS does not log in, bypass access controls, automate checkout, or purchase tickets.

## Official First

{primary_rows}

## Official Information / Caution References

{info_rows}

## Optional Premium Official Path

{optional_rows}

## Secondary Marketplace Candidate

{secondary_rows}

## Warnings

{warning_lines}

## Manual Purchase Checklist

{checklist_lines}
"""
        self.write_output(
            run_dir,
            "01b_ticket_link_agent.md",
            {
                "summary": "Official-first ticket link recommendations generated.",
                "recommendation": "Use FIFA official ticketing or FIFA official resale/exchange first.",
                "next_agent": "flight_agent",
            },
            body,
        )
        return {"ticket_links": recommendations}


def _link_line(link: dict[str, Any]) -> str:
    checks = "; ".join(link.get("manual_checks", []))
    return (
        f"- [{link['label']}]({link['url']}) "
        f"({link['source_type']}, risk: {link['risk_level']}): "
        f"{link['recommendation']} Manual checks: {checks}"
    )
