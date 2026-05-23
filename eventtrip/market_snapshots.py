"""Manual market snapshot loading and trend analysis."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

from eventtrip import scoring
from eventtrip.schemas import MarketSnapshot, TrendAnalysisResult, to_plain_dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MARKET_SNAPSHOT_DIR = PROJECT_ROOT / "data" / "market_snapshots"
SNAPSHOT_FIELDNAMES = [
    "snapshot_date",
    "match_id",
    "lowest_price",
    "listings",
    "category_3_low",
    "category_3_high",
    "hotel_availability_score",
    "flight_price_pressure",
    "social_buzz_score",
    "days_before_event",
    "source_type",
    "notes",
]


def default_snapshot_path(match_id: str) -> Path:
    """Return the default manual snapshot CSV path for a match ID."""
    return MARKET_SNAPSHOT_DIR / f"{match_id}_snapshots.csv"


def load_market_snapshots(path: str | Path, match_id: str | None = None) -> list[MarketSnapshot]:
    """Load market snapshots from CSV, optionally filtering by match ID."""
    csv_path = Path(path)
    if not csv_path.exists():
        return []

    snapshots: list[MarketSnapshot] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if match_id and row.get("match_id") != match_id:
                continue
            snapshots.append(_snapshot_from_row(row))
    return sorted(snapshots, key=lambda snapshot: snapshot.snapshot_date)


def save_market_snapshots(path: str | Path, snapshots: list[MarketSnapshot]) -> None:
    """Save snapshots to CSV in deterministic date order."""
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(snapshots, key=lambda snapshot: snapshot.snapshot_date)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SNAPSHOT_FIELDNAMES)
        writer.writeheader()
        for snapshot in ordered:
            writer.writerow(_snapshot_to_row(snapshot))


def append_market_snapshot(path: str | Path, snapshot: MarketSnapshot) -> None:
    """Append one new snapshot, failing when the same match/date already exists."""
    result = upsert_market_snapshot(path, snapshot, overwrite=False)
    if not result["saved"]:
        raise ValueError("; ".join(result["errors"]))


def validate_market_snapshot(snapshot: MarketSnapshot) -> list[str]:
    """Return validation errors for a manual market snapshot."""
    errors: list[str] = []

    if not snapshot.match_id.strip():
        errors.append("match_id must not be empty.")

    try:
        parsed_date = date.fromisoformat(snapshot.snapshot_date)
        if parsed_date.isoformat() != snapshot.snapshot_date:
            errors.append("snapshot_date must use YYYY-MM-DD format.")
    except ValueError:
        errors.append("snapshot_date must use YYYY-MM-DD format.")

    if snapshot.lowest_price <= 0:
        errors.append("lowest_price must be positive.")
    if snapshot.listings < 0:
        errors.append("listings must be non-negative.")
    if snapshot.category_3_low > snapshot.category_3_high:
        errors.append("category_3_low must be less than or equal to category_3_high.")

    score_fields = {
        "hotel_availability_score": snapshot.hotel_availability_score,
        "flight_price_pressure": snapshot.flight_price_pressure,
        "social_buzz_score": snapshot.social_buzz_score,
    }
    for field_name, value in score_fields.items():
        if value < 0 or value > 1:
            errors.append(f"{field_name} must be between 0 and 1.")

    if snapshot.days_before_event < 0:
        errors.append("days_before_event must be non-negative.")

    return errors


def find_snapshot_index(
    snapshots: list[MarketSnapshot],
    match_id: str,
    snapshot_date: str,
) -> int | None:
    """Return the index of an existing match/date snapshot, if present."""
    for index, snapshot in enumerate(snapshots):
        if snapshot.match_id == match_id and snapshot.snapshot_date == snapshot_date:
            return index
    return None


def upsert_market_snapshot(
    path: str | Path,
    snapshot: MarketSnapshot,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Append or replace a snapshot with validation and duplicate protection."""
    errors = validate_market_snapshot(snapshot)
    csv_path = Path(path)
    if errors:
        return {
            "status": "validation_error",
            "saved": False,
            "errors": errors,
            "path": str(csv_path),
        }

    snapshots = load_market_snapshots(csv_path)
    existing_index = find_snapshot_index(snapshots, snapshot.match_id, snapshot.snapshot_date)
    if existing_index is not None and not overwrite:
        return {
            "status": "duplicate",
            "saved": False,
            "errors": [
                (
                    "Snapshot already exists for "
                    f"{snapshot.match_id} on {snapshot.snapshot_date}; use --overwrite to replace it."
                )
            ],
            "path": str(csv_path),
        }

    if existing_index is not None:
        snapshots[existing_index] = snapshot
        status = "overwritten"
    else:
        snapshots.append(snapshot)
        status = "appended"

    save_market_snapshots(csv_path, snapshots)
    return {
        "status": status,
        "saved": True,
        "errors": [],
        "path": str(csv_path),
        "match_id": snapshot.match_id,
        "snapshot_date": snapshot.snapshot_date,
    }


def analyze_market_trend(snapshots: list[MarketSnapshot]) -> TrendAnalysisResult:
    """Analyze price/listing trends and produce a deterministic recommendation."""
    ordered = sorted(snapshots, key=lambda snapshot: snapshot.snapshot_date)
    if not ordered:
        return TrendAnalysisResult(
            match_id="",
            snapshot_count=0,
            latest_price=0.0,
            latest_listings=0,
            price_change_abs=0.0,
            price_change_pct=0.0,
            listings_change_abs=0,
            listings_change_pct=0.0,
            latest_scalper_stress_index=0.0,
            recommendation="insufficient_data",
            trigger_status="insufficient_data",
            explanation=["No market snapshots are available."],
        )

    first = ordered[0]
    latest = ordered[-1]
    previous = ordered[-2] if len(ordered) >= 2 else latest
    price_change_abs = latest.lowest_price - first.lowest_price
    price_change_pct = _pct_change(first.lowest_price, latest.lowest_price)
    listings_change_abs = latest.listings - first.listings
    listings_change_pct = _pct_change(first.listings, latest.listings)
    latest_price_trend = _pct_change(previous.lowest_price, latest.lowest_price) / 100.0
    latest_stress = _compute_scalper_stress(latest, latest_price_trend)
    recommendation = recommend_from_trend(ordered)
    trigger_status = _trigger_status(latest, ordered)
    explanation = _build_explanation(
        ordered=ordered,
        price_change_abs=price_change_abs,
        price_change_pct=price_change_pct,
        listings_change_abs=listings_change_abs,
        listings_change_pct=listings_change_pct,
        stress=latest_stress,
        trigger_status=trigger_status,
    )

    if len(ordered) < 2:
        recommendation = "insufficient_data"
        trigger_status = "insufficient_data"
        explanation.insert(0, "At least two snapshots are needed for trend analysis.")

    return TrendAnalysisResult(
        match_id=latest.match_id,
        snapshot_count=len(ordered),
        latest_price=round(latest.lowest_price, 2),
        latest_listings=int(latest.listings),
        price_change_abs=round(price_change_abs, 2),
        price_change_pct=round(price_change_pct, 2),
        listings_change_abs=int(listings_change_abs),
        listings_change_pct=round(listings_change_pct, 2),
        latest_scalper_stress_index=float(latest_stress["score"]),
        recommendation=recommendation,
        trigger_status=trigger_status,
        explanation=explanation,
    )


def compute_snapshot_scalper_stress(snapshot: MarketSnapshot) -> dict:
    """Compute scalper stress for a single snapshot without trend context."""
    return _compute_scalper_stress(snapshot, price_trend_7d=0.0)


def recommend_from_trend(snapshots: list[MarketSnapshot]) -> str:
    """Return buy/strongly_consider_buying/monitor/wait/insufficient_data."""
    ordered = sorted(snapshots, key=lambda snapshot: snapshot.snapshot_date)
    if len(ordered) < 2:
        return "insufficient_data"

    first = ordered[0]
    latest = ordered[-1]
    previous = ordered[-2]
    price_change_abs = latest.lowest_price - first.lowest_price
    listings_change_abs = latest.listings - first.listings
    latest_price_trend = _pct_change(previous.lowest_price, latest.lowest_price) / 100.0
    stress = _compute_scalper_stress(latest, latest_price_trend)

    if latest.lowest_price <= 550:
        return "buy"
    if latest.lowest_price <= 600:
        return "strongly_consider_buying"

    recent_listings_drop = latest.listings <= previous.listings * 0.85
    pressure_rising = (
        latest.flight_price_pressure > previous.flight_price_pressure
        and latest.hotel_availability_score < previous.hotel_availability_score
    )
    if recent_listings_drop and pressure_rising:
        return "strongly_consider_buying"

    if price_change_abs < 0 and listings_change_abs > 0 and stress["score"] >= 55:
        return "wait"
    return "monitor"


def trend_result_to_dict(result: TrendAnalysisResult) -> dict[str, Any]:
    """Convert a trend result model to a plain JSON-serializable dict."""
    return to_plain_dict(result)


def snapshot_to_dict(snapshot: MarketSnapshot) -> dict[str, Any]:
    """Convert a snapshot model to a plain JSON-serializable dict."""
    return to_plain_dict(snapshot)


def _snapshot_from_row(row: dict[str, str]) -> MarketSnapshot:
    return MarketSnapshot(
        snapshot_date=row["snapshot_date"],
        match_id=row["match_id"],
        lowest_price=float(row["lowest_price"]),
        listings=int(row["listings"]),
        category_3_low=float(row["category_3_low"]),
        category_3_high=float(row["category_3_high"]),
        hotel_availability_score=float(row["hotel_availability_score"]),
        flight_price_pressure=float(row["flight_price_pressure"]),
        social_buzz_score=float(row["social_buzz_score"]),
        days_before_event=int(row["days_before_event"]),
        source_type=row["source_type"],
        notes=row.get("notes", ""),
    )


def _snapshot_to_row(snapshot: MarketSnapshot) -> dict[str, Any]:
    data = snapshot_to_dict(snapshot)
    return {field: data.get(field, "") for field in SNAPSHOT_FIELDNAMES}


def _pct_change(start: float, end: float) -> float:
    if start == 0:
        return 0.0
    return ((end - start) / start) * 100.0


def _compute_scalper_stress(snapshot: MarketSnapshot, price_trend_7d: float) -> dict:
    return scoring.compute_scalper_stress_index(
        listings=snapshot.listings,
        lowest_price=snapshot.lowest_price,
        price_trend_7d=price_trend_7d,
        hotel_availability_score=snapshot.hotel_availability_score,
        flight_price_pressure=snapshot.flight_price_pressure,
        social_buzz_score=snapshot.social_buzz_score,
        days_before_event=snapshot.days_before_event,
    )


def _trigger_status(latest: MarketSnapshot, ordered: list[MarketSnapshot]) -> str:
    if latest.lowest_price <= 550:
        return "buy_trigger_met"
    if latest.lowest_price <= 600:
        return "strong_consideration_trigger_met"
    if latest.lowest_price >= 675 and latest.listings >= 300:
        return "monitor_high_listings_near_700"
    if len(ordered) >= 2:
        previous = ordered[-2]
        listings_falling = latest.listings <= previous.listings * 0.85
        pressure_rising = (
            latest.flight_price_pressure > previous.flight_price_pressure
            and latest.hotel_availability_score < previous.hotel_availability_score
        )
        if listings_falling and pressure_rising:
            return "tightening_market_recheck"
    return "monitor"


def _build_explanation(
    ordered: list[MarketSnapshot],
    price_change_abs: float,
    price_change_pct: float,
    listings_change_abs: int,
    listings_change_pct: float,
    stress: dict,
    trigger_status: str,
) -> list[str]:
    first = ordered[0]
    latest = ordered[-1]
    return [
        f"Snapshots run from {first.snapshot_date} to {latest.snapshot_date}.",
        f"Lowest price changed ${price_change_abs:.0f} ({price_change_pct:+.1f}%).",
        f"Listings changed {listings_change_abs:+d} ({listings_change_pct:+.1f}%).",
        f"Latest Scalper Stress Index is {stress['score']}/100 ({stress['interpretation']}).",
        f"Trigger status: {trigger_status}.",
    ]
