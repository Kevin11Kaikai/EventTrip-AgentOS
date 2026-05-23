"""Manual CSV-backed market snapshot provider."""

from __future__ import annotations

from pathlib import Path

from eventtrip.market_snapshots import (
    MARKET_SNAPSHOT_DIR,
    append_market_snapshot,
    default_snapshot_path,
    load_market_snapshots,
)
from eventtrip.schemas import MarketSnapshot


class ManualSnapshotProvider:
    """Read and write deterministic manual snapshots under data/market_snapshots."""

    def __init__(self, snapshot_dir: Path | None = None) -> None:
        self.snapshot_dir = snapshot_dir or MARKET_SNAPSHOT_DIR

    def get_snapshots(self, match_id: str) -> list[MarketSnapshot]:
        path = self._path_for_match(match_id)
        return load_market_snapshots(path, match_id=match_id)

    def append_snapshot(self, snapshot: MarketSnapshot) -> None:
        path = self._path_for_match(snapshot.match_id)
        append_market_snapshot(path, snapshot)

    def _path_for_match(self, match_id: str) -> Path:
        if self.snapshot_dir == MARKET_SNAPSHOT_DIR:
            return default_snapshot_path(match_id)
        return self.snapshot_dir / f"{match_id}_snapshots.csv"
