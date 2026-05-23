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
        snapshot_trend = context.get("snapshot_trend")
        snapshots = context.get("market_snapshots", [])
        latest_snapshot_date = snapshots[-1]["snapshot_date"] if snapshots else "n/a"
        combined_timing = combine_ticket_timing(timing, snapshot_trend)
        combined_timing_explanation = "\n".join(
            f"- {item}" for item in combined_timing["explanation"]
        )
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
        snapshot_explanation = ""
        if snapshot_trend:
            snapshot_explanation = "\n".join(f"- {item}" for item in snapshot_trend["explanation"])

        body = f"""# EventTrip-AgentOS Final Report

## Executive Summary

Recommended plan: {recommended["option_name"]}.

Estimated cost per traveler:

{traveler_cost_lines}

Overall ticket timing recommendation: {combined_timing["label"]}.

The single-day market signal says {timing}; the multi-snapshot trend signal says {snapshot_trend["recommendation"] if snapshot_trend else "insufficient_data"}. The current mock lowest ask is ${ticket["lowest_price"]:.0f}, while the latest manual snapshot is ${snapshot_trend["latest_price"] if snapshot_trend else ticket["lowest_price"]:.0f}. This supports disciplined monitoring with a wait bias, not a panic buy.

## Demo Assumptions

- Phase 1 and Phase 3 use deterministic mock and manual snapshot data only.
- No web scraping, no browser automation, and no real paid travel APIs are used.
- Default execution does not call any LLM API.
- The scenario includes only {match["name"]} on {match["date"]} at {match["venue"]} in {match["city"]}.
- Germany vs Curacao is intentionally excluded from this demo.
- Shared hotel and shared local transportation are split AA.

## Agent Workflow

1. Ticket Agent reviewed the mock ticket market.
2. Flight Agent compared same-day, one-night, and two-night flight windows.
3. Hotel Agent ranked shared two-bed hotel options.
4. Snapshot Agent analyzed manual market snapshots.
5. Market Agent computed anti-scalper timing signals.
6. Budget Agent ranked trip options by cost-effectiveness.
7. Risk Agent flagged booking and coordination risks.
8. Report Agent generated this Markdown report from shared memory and structured outputs.

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

### Combined Ticket Timing

- Single-day market signal: {timing}
- Multi-snapshot trend signal: {snapshot_trend["recommendation"] if snapshot_trend else "insufficient_data"}
- Overall stance: {combined_timing["label"]}

{combined_timing_explanation}

## Market Snapshot Trend Analysis

- Snapshot count: {snapshot_trend["snapshot_count"] if snapshot_trend else 0}
- Latest snapshot date: {latest_snapshot_date}
- Latest price: ${snapshot_trend["latest_price"] if snapshot_trend else 0:.0f}
- Latest listings: {snapshot_trend["latest_listings"] if snapshot_trend else 0}
- Price trend from first to latest: ${snapshot_trend["price_change_abs"] if snapshot_trend else 0:.0f} ({snapshot_trend["price_change_pct"] if snapshot_trend else 0:+.1f}%)
- Listings trend from first to latest: {snapshot_trend["listings_change_abs"] if snapshot_trend else 0:+d} ({snapshot_trend["listings_change_pct"] if snapshot_trend else 0:+.1f}%)
- Latest snapshot Scalper Stress Index: {snapshot_trend["latest_scalper_stress_index"] if snapshot_trend else 0:.1f}/100
- Trend-based recommendation: {snapshot_trend["recommendation"] if snapshot_trend else "insufficient_data"}
- Trigger status: {snapshot_trend["trigger_status"] if snapshot_trend else "insufficient_data"}

{snapshot_explanation}

The trend is more wait-biased because prices are falling while listings are rising. That does not mean ignoring the market; it means active monitoring with concrete trigger prices before committing cash.

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

- Do not panic buy in the $680-$700 range.
- Monitor verified official resale inventory.
- Continue tracking whether listings rise while prices flatten or fall.
- Buy immediately if verified official resale appears at or below $550.
- Strongly consider buying if the all-in ticket price falls below $600.
- Re-evaluate earlier if listings fall sharply while flight and hotel pressure rises.
- Re-check PIT and SEA flight prices before committing.
- Hold or shortlist a refundable two-bed hotel near NRG Stadium or METRORail.
- Avoid same-day arrival unless inbound schedules produce a strong match buffer.

## Limitations

- All values are mock estimates.
- No live market, flight, hotel, or ticket APIs are used.
- No real paid travel APIs are used.
- No web scraping is used.
- The model does not predict real 2026 prices.
- This demo is decision support, not financial, legal, or travel advice.

## Optional LLM Backend Note

The default demo uses deterministic mock agent outputs. When `--use-llm` is passed and `OHMYGPT_API_KEY` is configured, the system can use OhMyGPT as an OpenAI-compatible LLM backend for prose polishing only. LLM polishing must not change computed numbers, scores, option names, dates, or recommendations.

## Risk Register

{risk_lines}

## Mitigations

{mitigation_lines}
"""
        output_path = self.write_output(
            run_dir,
            "08_final_report.md",
            {
                "summary": f"Final report recommends {recommended['option_name']}.",
                "recommendation": recommended["option_name"],
                "combined_ticket_timing_recommendation": combined_timing["code"],
                "next_agent": None,
            },
            body,
        )
        return {
            "final_report_path": output_path,
            "combined_ticket_timing_recommendation": combined_timing["code"],
            "combined_ticket_timing_label": combined_timing["label"],
        }


def combine_ticket_timing(single_day_signal: str, snapshot_trend: dict[str, Any] | None) -> dict[str, Any]:
    """Fuse single-day and multi-snapshot timing into one report stance."""
    trend_signal = (snapshot_trend or {}).get("recommendation", "insufficient_data")

    if single_day_signal == "monitor" and trend_signal == "wait":
        code = "monitor_with_wait_bias"
        label = "Monitor with wait bias"
    elif trend_signal == "buy":
        code = "buy"
        label = "Buy"
    elif trend_signal == "strongly_consider_buying":
        code = "strongly_consider_buying"
        label = "Strongly consider buying"
    elif single_day_signal == "wait" or trend_signal == "wait":
        code = "wait_with_active_monitoring"
        label = "Wait with active monitoring"
    elif single_day_signal == "buy/monitor":
        code = "buy_or_monitor"
        label = "Buy or monitor"
    else:
        code = "monitor"
        label = "Monitor"

    explanation = [
        f"The single-day market signal says {single_day_signal}.",
        f"The multi-snapshot trend signal says {trend_signal}.",
    ]
    if code == "monitor_with_wait_bias":
        explanation.extend(
            [
                "Because the trend shows falling prices and rising listings, the overall stance is monitor with wait bias.",
                "This is not a hard wait; it is disciplined monitoring with trigger prices.",
            ]
        )
    else:
        explanation.append("Use the ticket trigger policy to decide when monitoring becomes buying.")

    return {"code": code, "label": label, "explanation": explanation}
