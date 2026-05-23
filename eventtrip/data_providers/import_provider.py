"""Local CSV/JSON snapshot import provider.

This provider intentionally reads local files only. It does not call live APIs,
scrape websites, or require secrets.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from eventtrip.market_snapshots import SNAPSHOT_FIELDNAMES, validate_market_snapshot
from eventtrip.schemas import MarketSnapshot


class SnapshotImportProvider:
    """Load validated market snapshots from a local CSV or JSON file."""

    def __init__(self, input_path: str | Path) -> None:
        self.input_path = Path(input_path)

    def load_snapshots(self, match_id: str | None = None) -> list[MarketSnapshot]:
        """Load and validate snapshots, optionally filtering by match ID."""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Snapshot import file not found: {self.input_path}")
        if self.input_path.suffix.lower() == ".csv":
            rows = self._load_csv_rows()
        elif self.input_path.suffix.lower() == ".json":
            rows = self._load_json_rows()
        else:
            raise ValueError(
                "Unsupported snapshot import format. Use a local .csv or .json file."
            )

        snapshots = []
        for index, row in enumerate(rows, start=1):
            snapshot = _snapshot_from_mapping(row, row_number=index)
            if match_id and snapshot.match_id != match_id:
                continue
            errors = validate_market_snapshot(snapshot)
            if errors:
                joined = "; ".join(errors)
                raise ValueError(f"Invalid snapshot row {index}: {joined}")
            snapshots.append(snapshot)
        return sorted(snapshots, key=lambda snapshot: snapshot.snapshot_date)

    def _load_csv_rows(self) -> list[dict[str, Any]]:
        with self.input_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [field for field in SNAPSHOT_FIELDNAMES if field not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"CSV import file is missing required columns: {missing}")
            return [dict(row) for row in reader]

    def _load_json_rows(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self.input_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON import file is malformed: {exc}") from exc
        if not isinstance(data, list):
            raise ValueError("JSON import file must contain a list of snapshot objects.")
        rows = []
        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"JSON snapshot row {index} must be an object.")
            rows.append(item)
        return rows


def _snapshot_from_mapping(row: dict[str, Any], row_number: int) -> MarketSnapshot:
    missing = [field for field in SNAPSHOT_FIELDNAMES if field not in row]
    if missing:
        raise ValueError(f"Snapshot row {row_number} is missing required fields: {missing}")
    try:
        return MarketSnapshot(
            snapshot_date=str(row["snapshot_date"]),
            match_id=str(row["match_id"]),
            lowest_price=float(row["lowest_price"]),
            listings=int(row["listings"]),
            category_3_low=float(row["category_3_low"]),
            category_3_high=float(row["category_3_high"]),
            hotel_availability_score=float(row["hotel_availability_score"]),
            flight_price_pressure=float(row["flight_price_pressure"]),
            social_buzz_score=float(row["social_buzz_score"]),
            days_before_event=int(row["days_before_event"]),
            source_type=str(row["source_type"]),
            notes=str(row.get("notes", "")),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Snapshot row {row_number} has malformed values: {exc}") from exc
