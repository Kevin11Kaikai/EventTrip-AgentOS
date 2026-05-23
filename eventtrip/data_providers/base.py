"""Provider contract for market snapshot data."""

from __future__ import annotations

from typing import Protocol

from eventtrip.schemas import MarketSnapshot


class MarketDataProvider(Protocol):
    """Interface for manual or future live market snapshot providers."""

    def get_snapshots(self, match_id: str) -> list[MarketSnapshot]:
        """Return snapshots for a match ID."""

    def append_snapshot(self, snapshot: MarketSnapshot) -> None:
        """Persist one snapshot."""
