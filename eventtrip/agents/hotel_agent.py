"""Hotel value agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.mcp_server.tools import compute_aa_split, get_hotel_quotes
from eventtrip.scoring import hotel_value_score


class HotelAgent(BaseAgent):
    name = "hotel_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        city = trip_request["destination_city"]
        one_night = self._rank_hotels(get_hotel_quotes(city, "2026-06-16", "2026-06-17", beds=2))
        two_night = self._rank_hotels(get_hotel_quotes(city, "2026-06-16", "2026-06-18", beds=2))
        selected = one_night[0]

        one_rows = [self._row(quote) for quote in one_night]
        two_rows = [self._row(quote) for quote in two_night]
        selected_split = compute_aa_split(selected["total_price"], people=2)

        body = f"""# Hotel Agent

Phase 1 uses mock hotel data. The hotel search is constrained to shared two-bed options for the Portugal vs DR Congo match.

## One-Night Options: June 16-17

| Hotel | Total | Per Person | Access | Rating | Cancellation | Value Score |
|---|---:|---:|---|---:|---|---:|
{chr(10).join(one_rows)}

## Two-Night Options: June 16-18

| Hotel | Total | Per Person | Access | Rating | Cancellation | Value Score |
|---|---:|---:|---|---:|---|---:|
{chr(10).join(two_rows)}

## Recommendation

Baseline hotel: {selected["name"]}.

- One-night total: ${selected["total_price"]:.0f}
- AA split: ${selected_split["per_person"]:.0f} per traveler
- Beds: {selected["beds"]}
- Cancellation: {selected["cancellation_policy"]}

This option is close to NRG Stadium, has two beds, stays refundable, and avoids paying for an unnecessary second night in the budget-first baseline.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "03_hotel_agent.md",
            {
                "summary": f"Selected {selected['name']} at ${selected['total_price']:.0f} one-night total.",
                "recommendation": "Use refundable shared two-bed one-night hotel as baseline.",
                "next_agent": "snapshot_agent",
            },
            body,
        )
        return {"hotels": {"one_night": one_night, "two_night": two_night, "selected": selected}}

    @staticmethod
    def _rank_hotels(quotes: list[dict]) -> list[dict]:
        ranked = []
        for quote in quotes:
            scored = dict(quote)
            scored["value_score"] = hotel_value_score(
                price_per_person=quote["total_price"] / 2,
                walking_minutes_to_venue=quote.get("walking_minutes_to_venue"),
                transit_minutes_to_venue=quote.get("transit_minutes_to_venue"),
                beds=int(quote["beds"]),
                rating=float(quote["rating"]),
                cancellation_policy=quote["cancellation_policy"],
            )
            ranked.append(scored)
        return sorted(ranked, key=lambda item: item["value_score"], reverse=True)

    @staticmethod
    def _row(quote: dict) -> str:
        if quote.get("walking_minutes_to_venue") is not None:
            access = f"{quote['walking_minutes_to_venue']} min walk"
        else:
            access = f"{quote['transit_minutes_to_venue']} min transit"
        return (
            f"| {quote['name']} | ${quote['total_price']:.0f} | "
            f"${quote['total_price'] / 2:.0f} | {access} | {quote['rating']:.1f} | "
            f"{quote['cancellation_policy']} | {quote['value_score']:.1f} |"
        )
