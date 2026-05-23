"""Final report agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):
    name = "report_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        match = trip_request["match"]
        ticket = context["ticket"]
        stress = context["scalper_stress"]
        timing = context["ticket_timing"]
        selected_hotel = context["hotels"]["selected"]
        recommended = context["budget"]["recommended"]
        option_a = next(
            option for option in context["budget"]["options"] if option["option_name"].startswith("Option A:")
        )
        option_b = next(
            option for option in context["budget"]["options"] if option["option_name"].startswith("Option B:")
        )
        budget_rows = []
        for option in context["budget"]["options"]:
            totals = "<br>".join(
                f"{name}: ${total:.0f}" for name, total in option["total_cost_per_traveler"].items()
            )
            budget_rows.append(
                f"| {option['option_name']} | {totals} | "
                f"${option['shared_costs']['hotel_total']:.0f} | "
                f"${option['shared_costs']['local_transport_total']:.0f} | "
                f"{option['recommendation_score']:.1f} |"
            )

        traveler_cost_lines = "\n".join(
            f"- {name}: ${total:.0f}" for name, total in recommended["total_cost_per_traveler"].items()
        )
        option_a_totals = ", ".join(
            f"{name}: ${total:.0f}" for name, total in option_a["total_cost_per_traveler"].items()
        )
        option_b_totals = ", ".join(
            f"{name}: ${total:.0f}" for name, total in option_b["total_cost_per_traveler"].items()
        )
        sample_traveler = next(iter(option_a["traveler_costs"]))
        hotel_savings = (
            option_a["traveler_costs"][sample_traveler]["hotel_share"]
            - option_b["traveler_costs"][sample_traveler]["hotel_share"]
        )
        flight_increase = (
            option_b["traveler_costs"][sample_traveler]["flight"]
            - option_a["traveler_costs"][sample_traveler]["flight"]
        )
        local_transport_increase = (
            option_b["traveler_costs"][sample_traveler]["local_transport_share"]
            - option_a["traveler_costs"][sample_traveler]["local_transport_share"]
        )
        risk_lines = "\n".join(f"- {risk}" for risk in context["risks"])
        mitigation_lines = "\n".join(f"- {item}" for item in context["mitigations"])

        body = f"""# EventTrip-AgentOS Final Report

## Executive Summary

Recommended plan: {recommended["option_name"]}.

Estimated cost per traveler:

{traveler_cost_lines}

Ticket timing recommendation: {timing}. The current mock lowest ask is ${ticket["lowest_price"]:.0f}, with {ticket["listings"]} listings and a Scalper Stress Index of {stress["score"]}/100.

This is a disciplined monitoring signal. The mock market is not cheap enough to buy blindly, not weak enough for a hard wait, and not tight enough to justify panic buying.

## Demo Assumptions

- Phase 1 uses deterministic mock data only.
- No web scraping, no browser automation, and no real paid travel APIs are used.
- Default execution does not call any LLM API.
- The scenario includes only {match["name"]} on {match["date"]} at {match["venue"]} in {match["city"]}.
- Germany vs Curacao is intentionally excluded from this demo.
- Shared hotel and shared local transportation are split AA.

## Agent Workflow

1. Ticket Agent reviewed the mock ticket market.
2. Flight Agent compared same-day, one-night, and two-night flight windows.
3. Hotel Agent ranked shared two-bed hotel options.
4. Market Agent computed anti-scalper timing signals.
5. Budget Agent ranked trip options by cost-effectiveness.
6. Risk Agent flagged booking and coordination risks.
7. Report Agent generated this Markdown report from shared memory and structured outputs.

## Portugal vs DR Congo Ticket Analysis

| Signal | Value |
|---|---:|
| Lowest mock ask | ${ticket["lowest_price"]:.0f} |
| Listings | {ticket["listings"]} |
| Category 3 mock range | ${ticket["category_3_range"][0]:.0f}-${ticket["category_3_range"][1]:.0f} |
| 7-day trend | {ticket["price_trend_7d"]:+.1%} |

The ticket price is high enough to require discipline. The system recommends monitoring rather than panic buying unless verified official resale inventory appears or prices move closer to the planned trigger range.

## Ticket Trigger Policy

- Buy immediately if verified official resale appears at or below $550.
- Strongly consider buying if the total all-in ticket price falls below $600.
- Continue monitoring if the price remains around $700 and listings remain high.
- Re-evaluate if listings fall sharply while flight and hotel pressure rise.

## Flight Analysis

The one-night balanced flight window is the baseline because it gives both PIT and SEA travelers arrival buffer before match day. Same-day travel is not eliminated, but it should be used only when flight timing and delay risk are acceptable.

## Hotel Analysis

Recommended shared hotel baseline: {selected_hotel["name"]}.

- One-night total: ${selected_hotel["price_per_night"]:.0f}
- One-night AA split: ${selected_hotel["price_per_night"] / 2:.0f} per traveler
- Beds: {selected_hotel["beds"]}
- Cancellation policy: {selected_hotel["cancellation_policy"]}

## Market Timing / Anti-Scalper Analysis

Scalper Stress Index: {stress["score"]}/100 ({stress["interpretation"]}).

Portugal creates genuine demand, so the correct answer is not a hard wait. At the same time, hotel and flight pressure are only moderate in the mock data, the market is not clearly collapsing, and it is also not tight enough to justify panic buying. The best response is disciplined monitoring with a pre-defined trigger price.

Do not let secondary ticket sellers force premature buying if hotel and flight pressure remain moderate.

## Budget Comparison Table

| Option | Estimated Total Per Traveler | Shared Hotel Total | Shared Local Transport | Score |
|---|---|---:|---:|---:|
{chr(10).join(budget_rows)}

## Why Option B Is Not Recommended

Option B has the same estimated traveler totals as Option A in the current mock data: {option_b_totals}. Option A is also {option_a_totals}.

Skipping the hotel saves about ${hotel_savings:.0f} per traveler, but the same-day flights are about ${flight_increase:.0f} more expensive per traveler and shared local transportation is about ${local_transport_increase:.0f} higher per traveler. Those offsets remove the hotel savings.

Option B therefore does not materially save money, while it creates a much higher risk of missing the match due to flight delay. Its risk-adjusted value is worse than Option A.

## Recommended Plan

Use {recommended["option_name"]}. It keeps the trip budget-first while preserving a practical arrival buffer before the June 17 match. It also limits shared financial exposure to one hotel night and local transportation.

## Practical Booking Rules

- Buy individual flights separately.
- Buy individual tickets separately.
- Share only the hotel and local transportation.
- Use refundable hotel inventory while ticket prices remain uncertain.
- Confirm two beds before booking.
- Set a ticket trigger price before monitoring secondary-market listings.
- Put AA expectations in writing before either traveler books a shared cost.

## Next Actions

- Monitor verified official resale inventory.
- Track whether listings rise while prices flatten or fall.
- Re-check PIT and SEA flight prices before committing.
- Hold or shortlist a refundable two-bed hotel near NRG Stadium or METRORail.
- Avoid same-day arrival unless inbound schedules produce a strong match buffer.

## Limitations

- All values are mock estimates.
- No live market, flight, hotel, or ticket APIs are used.
- The model does not predict real 2026 prices.
- The demo is decision support, not financial, legal, or travel advice.

## Optional LLM Backend Note

The default demo uses deterministic mock agent outputs. When `--use-llm` is passed and `OHMYGPT_API_KEY` is configured, the system can use OhMyGPT as an OpenAI-compatible LLM backend for prose polishing only. LLM polishing must not change computed numbers, scores, option names, dates, or recommendations.

## Risk Register

{risk_lines}

## Mitigations

{mitigation_lines}
"""
        body = self.polish_if_enabled(body)
        output_path = self.write_output(
            run_dir,
            "07_final_report.md",
            {
                "summary": f"Final report recommends {recommended['option_name']}.",
                "recommendation": recommended["option_name"],
                "next_agent": None,
            },
            body,
        )
        return {"final_report_path": output_path}
