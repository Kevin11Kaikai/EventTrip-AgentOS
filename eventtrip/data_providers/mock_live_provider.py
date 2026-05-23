"""Deterministic mock provider skeleton for future live integrations."""

from __future__ import annotations

from eventtrip.schemas import MarketSnapshot


class MockLiveProvider:
    """Return deterministic mock snapshots without APIs, scraping, or secrets."""

    def __init__(self) -> None:
        self._snapshots = [
            MarketSnapshot(
                snapshot_date="2026-05-15",
                match_id="portugal_dr_congo",
                lowest_price=680,
                listings=340,
                category_3_low=400,
                category_3_high=750,
                hotel_availability_score=0.52,
                flight_price_pressure=0.52,
                social_buzz_score=0.86,
                days_before_event=33,
                source_type="mock_live_placeholder",
                notes="Deterministic placeholder for future provider adapters.",
            )
        ]

    def get_snapshots(self, match_id: str) -> list[MarketSnapshot]:
        return [snapshot for snapshot in self._snapshots if snapshot.match_id == match_id]

    def append_snapshot(self, snapshot: MarketSnapshot) -> None:
        self._snapshots.append(snapshot)
