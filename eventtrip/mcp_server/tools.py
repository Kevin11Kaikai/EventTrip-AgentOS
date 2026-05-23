"""Pure Python mock MCP-style tools.

Phase 1 keeps these functions local and deterministic. Phase 2 exposes the
same function signatures through a real MCP server while preserving the
agent-facing contract. Phase 3 adds deterministic market snapshot tools backed
by local CSV data.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from eventtrip.data_providers.import_provider import SnapshotImportProvider
from eventtrip import scoring
from eventtrip.market_snapshots import (
    analyze_market_trend,
    default_snapshot_path,
    load_market_snapshots,
    snapshot_to_dict,
    trend_result_to_dict,
    upsert_market_snapshot,
)
from eventtrip.schemas import MarketSnapshot, to_plain_dict


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if isinstance(data, list):
        merged: dict[str, Any] = {}
        for item in data:
            if isinstance(item, dict):
                merged.update(item)
        return merged
    return data


def get_ticket_market(match_id: str) -> dict:
    data = _load_yaml("mock_tickets.yaml")
    ticket = dict(data[match_id])
    ticket["match_id"] = match_id
    return ticket


def get_flight_quotes(origin: str, destination: str, depart_date: str, return_date: str) -> list[dict]:
    data = _load_yaml("mock_flights.yaml")
    quotes = []
    for quote_id, raw in data.items():
        quote = dict(raw)
        quote["quote_id"] = quote_id
        if quote["origin"] != origin:
            continue
        if destination and quote["destination"] != destination:
            continue
        if depart_date and quote["depart_date"] != depart_date:
            continue
        if return_date and quote["return_date"] != return_date:
            continue
        quotes.append(quote)
    return quotes


def get_hotel_quotes(city: str, checkin: str, checkout: str, beds: int = 2) -> list[dict]:
    data = _load_yaml("mock_hotels.yaml")
    nights = max((date.fromisoformat(checkout) - date.fromisoformat(checkin)).days, 1)
    quotes = []
    for hotel_id, raw in data.items():
        if raw.get("city", city) != city:
            continue
        if int(raw.get("beds", 0)) < beds:
            continue
        quote = dict(raw)
        quote["hotel_id"] = hotel_id
        quote["checkin"] = checkin
        quote["checkout"] = checkout
        quote["nights"] = nights
        quote["total_price"] = float(quote["price_per_night"]) * nights
        quotes.append(quote)
    return quotes


def get_market_signals(match_id: str) -> dict:
    data = _load_yaml("mock_market_signals.yaml")
    signal = dict(data[match_id])
    signal["match_id"] = match_id
    return signal


def compute_aa_split(total_cost: float, people: int = 2) -> dict:
    per_person = round(total_cost / people, 2)
    return {
        "total_cost": round(total_cost, 2),
        "people": people,
        "per_person": per_person,
    }


def compute_scalper_stress_index(ticket_data: dict, market_data: dict | None = None) -> dict:
    market_data = market_data or {}
    return scoring.compute_scalper_stress_index(
        listings=int(ticket_data["listings"]),
        lowest_price=float(ticket_data["lowest_price"]),
        price_trend_7d=float(ticket_data["price_trend_7d"]),
        hotel_availability_score=float(market_data.get("hotel_availability_score", 0.5)),
        flight_price_pressure=float(market_data.get("flight_price_pressure", 0.5)),
        social_buzz_score=float(market_data.get("social_buzz_score", 0.5)),
        days_before_event=int(market_data.get("days_before_event", 180)),
    )


def rank_budget_options(options: list[dict]) -> list[dict]:
    ranked = []
    for option in options:
        average_total = sum(option["total_cost_per_traveler"].values()) / len(
            option["total_cost_per_traveler"]
        )
        scored = dict(option)
        scored["recommendation_score"] = scoring.budget_option_score(
            total_cost=average_total,
            hotel_nights=int(option.get("hotel_nights", 0)),
            travel_fatigue=float(option.get("travel_fatigue", 0.5)),
            schedule_simplicity=float(option.get("schedule_simplicity", 0.5)),
            shared_cost_efficiency=float(option.get("shared_cost_efficiency", 0.5)),
            risk_of_missing_match=float(option.get("risk_of_missing_match", 0.5)),
        )
        ranked.append(scored)
    return sorted(ranked, key=lambda item: item["recommendation_score"], reverse=True)


def get_market_snapshots(match_id: str) -> list[dict]:
    snapshots = load_market_snapshots(default_snapshot_path(match_id), match_id=match_id)
    return [snapshot_to_dict(snapshot) for snapshot in snapshots]


def analyze_market_snapshots(match_id: str) -> dict:
    snapshots = load_market_snapshots(default_snapshot_path(match_id), match_id=match_id)
    return trend_result_to_dict(analyze_market_trend(snapshots))


def append_market_snapshot(snapshot: dict) -> dict:
    overwrite = bool(snapshot.pop("overwrite", False))
    validated = MarketSnapshot(**snapshot)
    result = upsert_market_snapshot(
        default_snapshot_path(validated.match_id),
        validated,
        overwrite=overwrite,
    )
    result["match_id"] = validated.match_id
    result["saved_snapshot"] = to_plain_dict(validated) if result["saved"] else None
    return result


def preview_snapshot_import(input_path: str, match_id: str | None = None) -> dict:
    """Preview local CSV/JSON snapshot imports without writing to the snapshot store."""
    try:
        safe_path = _resolve_safe_local_import_path(input_path)
        snapshots = SnapshotImportProvider(safe_path).load_snapshots(match_id=match_id)
    except Exception as exc:
        return {
            "validation_status": "error",
            "error": str(exc),
            "count": 0,
            "snapshots": [],
        }
    return {
        "validation_status": "valid",
        "error": None,
        "input_path": str(safe_path),
        "count": len(snapshots),
        "snapshots": [snapshot_to_dict(snapshot) for snapshot in snapshots],
    }


def _resolve_safe_local_import_path(input_path: str) -> Path:
    if "://" in input_path or input_path.startswith("\\\\"):
        raise ValueError("Only local project files are supported for snapshot import preview.")
    raw_path = Path(input_path)
    candidate = raw_path if raw_path.is_absolute() else PROJECT_ROOT / raw_path
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("Snapshot import preview paths must stay inside the project root.") from exc
    return resolved
