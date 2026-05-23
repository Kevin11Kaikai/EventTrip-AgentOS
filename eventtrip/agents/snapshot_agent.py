"""Market snapshot trend analysis agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.agents.base_agent import BaseAgent
from eventtrip.data_providers import ManualSnapshotProvider
from eventtrip.market_snapshots import analyze_market_trend, snapshot_to_dict, trend_result_to_dict


class SnapshotAgent(BaseAgent):
    name = "snapshot_agent"

    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        match_id = trip_request["match"]["match_id"]
        snapshots = ManualSnapshotProvider().get_snapshots(match_id)
        trend = analyze_market_trend(snapshots)
        trend_data = trend_result_to_dict(trend)
        latest_snapshot = snapshots[-1] if snapshots else None

        explanation = "\n".join(f"- {item}" for item in trend.explanation)
        body = f"""# Snapshot Agent

Phase 3 uses manual mock market snapshots only. No live APIs, scraping, or paid services are used.

## Snapshot Summary

- Match ID: {match_id}
- Snapshot count: {trend.snapshot_count}
- Latest snapshot date: {latest_snapshot.snapshot_date if latest_snapshot else "n/a"}
- Latest lowest price: ${trend.latest_price:.0f}
- Latest listings: {trend.latest_listings}
- Price change from first to latest: ${trend.price_change_abs:.0f} ({trend.price_change_pct:+.1f}%)
- Listings change from first to latest: {trend.listings_change_abs:+d} ({trend.listings_change_pct:+.1f}%)
- Latest Scalper Stress Index: {trend.latest_scalper_stress_index:.1f}/100
- Trend recommendation: {trend.recommendation}
- Trigger status: {trend.trigger_status}

## Explanation

{explanation}

## Interpretation

The manual snapshot series shows whether ticket prices and listings are moving together. Falling prices with rising listings usually supports disciplined monitoring or waiting unless a trigger price is reached.
"""
        body = self.polish_if_enabled(body)
        self.write_output(
            run_dir,
            "04_snapshot_agent.md",
            {
                "summary": (
                    f"Analyzed {trend.snapshot_count} manual market snapshots for {match_id}."
                ),
                "recommendation": trend.recommendation,
                "next_agent": "market_agent",
            },
            body,
        )
        return {
            "market_snapshots": [snapshot_to_dict(snapshot) for snapshot in snapshots],
            "snapshot_trend": trend_data,
        }
