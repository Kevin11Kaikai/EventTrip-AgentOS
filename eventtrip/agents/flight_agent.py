"""Flight comparison agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.mcp_server.tools import get_flight_quotes


TRIP_WINDOWS = {
    "same_day_aggressive": ("2026-06-17", "2026-06-17", "Same-day aggressive"),
    "one_night_balanced": ("2026-06-16", "2026-06-18", "One-night balanced"),
    "two_night_comfortable": ("2026-06-16", "2026-06-19", "Two-night comfortable"),
}


class FlightAgent(BaseAgent):
    name = "flight_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        destination = trip_request["destination_city"]
        travelers = trip_request["travelers"]
        flights_by_trip: dict[str, dict[str, dict]] = {}
        rows = []

        for trip_type, (depart, ret, label) in TRIP_WINDOWS.items():
            flights_by_trip[trip_type] = {}
            for traveler in travelers:
                quote = get_flight_quotes(traveler["origin"], destination, depart, ret)[0]
                flights_by_trip[trip_type][traveler["origin"]] = quote
                rows.append(
                    f"| {label} | {traveler['name']} ({traveler['origin']}) | "
                    f"{depart} | {ret} | ${quote['estimated_roundtrip_cost']:.0f} | "
                    f"{quote['risk_level']} |"
                )

        body = f"""# Flight Agent

Phase 1 uses mock flight quotes. Flights are individual costs, not AA shared costs.

## Flight Comparison

| Option | Traveler | Depart | Return | Roundtrip Cost | Risk |
|---|---|---|---|---:|---|
{chr(10).join(rows)}

## Interpretation

- Same-day travel is cash-light but has the highest risk of a missed match if either inbound flight is delayed.
- The one-night balanced plan gives both travelers a practical arrival buffer without paying for a second hotel night.
- The two-night comfortable plan lowers fatigue and schedule pressure, but the extra shared hotel night weakens budget efficiency.

## Recommendation

Use the one-night balanced flight window as the baseline. Keep same-day travel as a fallback only if prices fall materially and the inbound arrival times are early enough to preserve a match buffer.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "02_flight_agent.md",
            {
                "summary": "Compared same-day, one-night, and two-night mock flight options.",
                "recommendation": "Use one-night balanced flights as the baseline.",
                "next_agent": "hotel_agent",
            },
            body,
        )
        return {"flights_by_trip": flights_by_trip}

