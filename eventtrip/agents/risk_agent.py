"""Risk review agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    name = "risk_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        risks = [
            "Ticket resale risk, including invalid transfer or speculative inventory.",
            "Non-refundable or semi-refundable hotel terms.",
            "Late-night arrival or post-match return fatigue.",
            "Same-day arrival delay causing a missed match.",
            "Ride-share surge around NRG Stadium.",
            "Shared-room boundary and two-bed confirmation risk.",
            "Mismatch in travel commitment between travelers.",
            "One person cancels after a shared booking.",
            "Overpaying during artificial secondary-market scarcity.",
        ]
        mitigations = [
            "Prefer official resale when possible.",
            "Book refundable hotel inventory while ticket timing remains uncertain.",
            "Each person buys their own flight and ticket.",
            "Split shared costs only after cancellation terms are clear.",
            "Use a confirmed two-bed room.",
            "Document AA expectations in writing before booking.",
            "Monitor hotel availability and listings before buying overpriced tickets.",
            "Avoid same-day arrival unless flight risk is low and arrival is early.",
            "Set a ticket trigger price before watching secondary-market listings.",
        ]
        risk_lines = "\n".join(f"- {risk}" for risk in risks)
        mitigation_lines = "\n".join(f"- {mitigation}" for mitigation in mitigations)

        body = f"""# Risk Agent

## Key Risks

{risk_lines}

## Mitigation Steps

{mitigation_lines}

## Risk Position

The one-night balanced plan is the best risk-adjusted baseline. It avoids the same-day missed-match risk while keeping the hotel commitment limited to one refundable shared night.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "06_risk_agent.md",
            {
                "summary": "Flagged ticket, lodging, delay, AA split, and secondary-market risks.",
                "recommendation": "Use one-night plan with refundable hotel and explicit AA rules.",
                "next_agent": "report_agent",
            },
            body,
        )
        return {"risks": risks, "mitigations": mitigations}

