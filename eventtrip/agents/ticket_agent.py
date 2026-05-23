"""Ticket market analysis agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.mcp_server.tools import get_ticket_market


class TicketAgent(BaseAgent):
    name = "ticket_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        match = trip_request["match"]
        ticket = get_ticket_market(match["match_id"])
        low, high = ticket["category_3_range"]
        trend = float(ticket["price_trend_7d"])

        if ticket["lowest_price"] <= low:
            recommendation = "buy if official resale inventory is verified"
        elif ticket["lowest_price"] <= high and trend <= 0.03:
            recommendation = "monitor; avoid panic buying at the current secondary-market ask"
        else:
            recommendation = "wait unless the price falls or official resale appears"

        body = f"""# Ticket Agent

Phase 1 uses mock ticket data only. No websites are scraped and no paid APIs are called.

## Match Scope

- Match: {match["name"]}
- Date: {match["date"]}
- Venue: {match["venue"]}, {match["city"]}
- Explicitly excluded: Germany vs Curacao and any other Houston match.

## Ticket Market Snapshot

| Signal | Mock Value |
|---|---:|
| Lowest secondary-market ask | ${ticket["lowest_price"]:.0f} |
| Active listings | {ticket["listings"]} |
| Category 3 mock range | ${low:.0f}-${high:.0f} |
| Demand level | {ticket["demand_level"]} |
| 7-day price trend | {trend:+.1%} |
| Source type | {ticket["source_type"]} |

## Interpretation

The lowest ask is near the upper end of the mock Category 3 range. A 300-listing market with only a small 7-day increase does not justify panic buying in a budget-first plan. Portugal creates real demand, but Phase 1 should still treat current secondary-market scarcity as something to verify rather than obey.

## Recommendation

{recommendation.capitalize()}.

Category preference: start with the cheapest verified official resale or Category 3-style inventory. Avoid paying far above ${high:.0f} unless the travelers intentionally upgrade the experience.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "01_ticket_agent.md",
            {
                "summary": f"Lowest mock ask ${ticket['lowest_price']:.0f} with {ticket['listings']} listings.",
                "recommendation": recommendation,
                "next_agent": "flight_agent",
            },
            body,
        )
        return {"ticket": {**ticket, "recommendation": recommendation}}

