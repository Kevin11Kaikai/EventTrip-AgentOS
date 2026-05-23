"""Budget synthesis agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.mcp_server.tools import rank_budget_options


class BudgetAgent(BaseAgent):
    name = "budget_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        travelers = trip_request["travelers"]
        ticket_cost = float(context["ticket"]["lowest_price"])
        selected_hotel = context["hotels"]["selected"]
        flights = context["flights_by_trip"]

        options = [
            self._build_option(
                option_name="Option A: One-night balanced plan",
                description=(
                    "Arrive June 16, share one two-bed hotel night, attend Portugal vs DR Congo "
                    "on June 17, and return June 17 night or June 18 morning."
                ),
                travelers=travelers,
                ticket_cost=ticket_cost,
                flight_quotes=flights["one_night_balanced"],
                hotel_total=selected_hotel["price_per_night"],
                local_transport_total=80,
                hotel_nights=1,
                pros=["Best balance of cost and schedule buffer", "Uses AA split for hotel and local transport"],
                cons=["Requires both travelers to commit to shared lodging"],
                travel_fatigue=0.35,
                schedule_simplicity=0.80,
                shared_cost_efficiency=0.90,
                risk_of_missing_match=0.25,
            ),
            self._build_option(
                option_name="Option B: Same-day aggressive plan",
                description="Arrive June 17 morning, attend the match, return June 17 night, and skip the hotel.",
                travelers=travelers,
                ticket_cost=ticket_cost,
                flight_quotes=flights["same_day_aggressive"],
                hotel_total=0,
                local_transport_total=120,
                hotel_nights=0,
                pros=["No planned hotel spend", "Shortest time away from home"],
                cons=["High same-day delay risk", "Likely higher ride-share surge exposure"],
                travel_fatigue=0.80,
                schedule_simplicity=0.45,
                shared_cost_efficiency=0.50,
                risk_of_missing_match=0.80,
            ),
            self._build_option(
                option_name="Option C: Two-night comfortable plan",
                description="Arrive June 16, stay June 16 and June 17 nights, and return June 18.",
                travelers=travelers,
                ticket_cost=ticket_cost,
                flight_quotes=flights["two_night_comfortable"],
                hotel_total=selected_hotel["price_per_night"] * 2,
                local_transport_total=100,
                hotel_nights=2,
                pros=["Lowest schedule stress", "More rest before and after the match"],
                cons=["Pays for an extra hotel night", "Weaker budget-first fit"],
                travel_fatigue=0.20,
                schedule_simplicity=0.75,
                shared_cost_efficiency=0.85,
                risk_of_missing_match=0.15,
            ),
            self._build_option(
                option_name="Option D: Independent booking plan",
                description=(
                    "Each traveler books their own flight and ticket, coordinates local transport, "
                    "and optionally shares the one-night hotel."
                ),
                travelers=travelers,
                ticket_cost=ticket_cost,
                flight_quotes=flights["one_night_balanced"],
                hotel_total=selected_hotel["price_per_night"],
                local_transport_total=80,
                hotel_nights=1,
                pros=["Keeps individual flight and ticket responsibility clear", "Reduces reimbursement ambiguity"],
                cons=["Needs explicit agreement before shared hotel booking", "Less unified than Option A"],
                travel_fatigue=0.45,
                schedule_simplicity=0.65,
                shared_cost_efficiency=0.75,
                risk_of_missing_match=0.30,
            ),
        ]
        ranked = rank_budget_options(options)
        recommended = ranked[0]

        rows = []
        for option in ranked:
            traveler_totals = ", ".join(
                f"{name}: ${total:.0f}" for name, total in option["total_cost_per_traveler"].items()
            )
            rows.append(
                f"| {option['option_name']} | {traveler_totals} | "
                f"${option['shared_costs']['hotel_total']:.0f} | "
                f"${option['shared_costs']['local_transport_total']:.0f} | "
                f"{option['recommendation_score']:.1f} |"
            )

        body = f"""# Budget Agent

All prices are mock Phase 1 estimates. Tickets and flights are individual costs. Shared hotel and shared local transportation are split AA.

## Budget Comparison

| Option | Estimated Total Per Traveler | Shared Hotel Total | Shared Local Transport | Score |
|---|---|---:|---:|---:|
{chr(10).join(rows)}

## Recommended Option

{recommended["option_name"]}.

This option is the best cost-effectiveness tradeoff because it avoids the same-day missed-match risk while not adding an unnecessary second hotel night.

## Cost Rules

- Each traveler buys their own flight.
- Each traveler buys their own ticket.
- Shared hotel is split equally only after cancellation terms are clear.
- Shared Uber or local transport is split equally.
- If one traveler cancels after a shared booking, the AA agreement should say who absorbs the unrecoverable cost.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "05_budget_agent.md",
            {
                "summary": f"Recommended {recommended['option_name']}.",
                "recommendation": recommended["option_name"],
                "next_agent": "risk_agent",
            },
            body,
        )
        return {"budget": {"options": ranked, "recommended": recommended}}

    @staticmethod
    def _build_option(
        option_name: str,
        description: str,
        travelers: list[dict],
        ticket_cost: float,
        flight_quotes: dict[str, dict],
        hotel_total: float,
        local_transport_total: float,
        hotel_nights: int,
        pros: list[str],
        cons: list[str],
        travel_fatigue: float,
        schedule_simplicity: float,
        shared_cost_efficiency: float,
        risk_of_missing_match: float,
    ) -> dict:
        people = len(travelers)
        hotel_share = hotel_total / people
        local_share = local_transport_total / people
        traveler_costs: dict[str, dict[str, float]] = {}
        totals: dict[str, float] = {}
        for traveler in travelers:
            name = traveler["name"]
            origin = traveler["origin"]
            flight_cost = float(flight_quotes[origin]["estimated_roundtrip_cost"])
            traveler_costs[name] = {
                "ticket": ticket_cost,
                "flight": flight_cost,
                "hotel_share": hotel_share,
                "local_transport_share": local_share,
            }
            totals[name] = round(ticket_cost + flight_cost + hotel_share + local_share, 2)

        return {
            "option_name": option_name,
            "description": description,
            "traveler_costs": traveler_costs,
            "shared_costs": {
                "hotel_total": round(hotel_total, 2),
                "local_transport_total": round(local_transport_total, 2),
            },
            "total_cost_per_traveler": totals,
            "hotel_nights": hotel_nights,
            "pros": pros,
            "cons": cons,
            "travel_fatigue": travel_fatigue,
            "schedule_simplicity": schedule_simplicity,
            "shared_cost_efficiency": shared_cost_efficiency,
            "risk_of_missing_match": risk_of_missing_match,
        }

