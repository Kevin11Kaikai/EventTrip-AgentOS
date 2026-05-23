"""Market timing and anti-scalper agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.mcp_server.tools import (
    compute_scalper_stress_index,
    get_market_signals,
    get_ticket_market,
)


class MarketAgent(BaseAgent):
    name = "market_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        match_id = trip_request["match"]["match_id"]
        ticket = context.get("ticket") or get_ticket_market(match_id)
        market = get_market_signals(match_id)
        stress = compute_scalper_stress_index(ticket, market)

        if stress["score"] <= 35:
            timing = "buy/monitor"
        elif stress["score"] <= 65:
            timing = "monitor"
        else:
            timing = "wait"

        explanation_lines = "\n".join(f"- {item}" for item in stress["explanation"])
        body = f"""# Market Agent

Phase 1 uses mock market signals. This analysis is scoped only to Portugal vs DR Congo.

## Scalper Stress Index

- Score: {stress["score"]}/100
- Interpretation: {stress["interpretation"]}
- Ticket timing recommendation: {timing}

## Inputs

| Signal | Mock Value |
|---|---:|
| Ticket listings | {ticket["listings"]} |
| Lowest ticket ask | ${ticket["lowest_price"]:.0f} |
| 7-day ticket trend | {ticket["price_trend_7d"]:+.1%} |
| Hotel availability score | {market["hotel_availability_score"]:.2f} |
| Flight price pressure | {market["flight_price_pressure"]:.2f} |
| Social buzz score | {market["social_buzz_score"]:.2f} |
| Days before event | {market["days_before_event"]} |

## Explanation

{explanation_lines}

The market has real demand because Portugal drives strong social buzz, but hotel availability and flight pressure are not extreme in the mock signals. The current setup looks like a mixed market: real fan interest plus enough resale inventory that travelers should avoid letting secondary sellers force premature buying.

## Purchase Window Strategy

Monitor official resale and verified secondary listings before buying. A budget-first trigger is a verified ticket near or below $550, a falling 7-day trend with rising listings, or official resale inventory that reduces counterfeit and transfer risk.

## Signals To Monitor

- Listings rising while prices flatten or fall.
- Hotel availability staying stable near NRG Stadium or METRORail.
- PIT and SEA flight pressure staying moderate.
- Official resale opening or expanding.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "04_market_agent.md",
            {
                "summary": f"Scalper Stress Index {stress['score']}/100.",
                "recommendation": timing,
                "next_agent": "budget_agent",
            },
            body,
        )
        return {"market": market, "scalper_stress": stress, "ticket_timing": timing}

