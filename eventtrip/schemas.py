"""Shared schemas for EventTrip-AgentOS.

Pydantic is used when available. The dataclass fallback keeps the demo
importable in minimal Python environments before dependencies are installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:  # pragma: no cover - exercised when pydantic is installed
    from pydantic import BaseModel

    class Traveler(BaseModel):
        name: str
        origin: str
        flexible_dates: bool = True
        budget_preference: str = "budget_first"

    class EventMatch(BaseModel):
        match_id: str
        name: str
        date: str
        venue: str
        city: str

    class FlightQuote(BaseModel):
        origin: str
        destination: str
        depart_date: str
        return_date: str
        estimated_roundtrip_cost: float
        trip_type: str
        risk_level: str
        notes: str = ""

    class HotelQuote(BaseModel):
        hotel_id: str
        name: str
        city: str
        price_per_night: float
        total_price: float
        beds: int
        walking_minutes_to_venue: int | None = None
        transit_minutes_to_venue: int | None = None
        rating: float
        cancellation_policy: str
        notes: str = ""

    class TicketQuote(BaseModel):
        match_id: str
        lowest_price: float
        listings: int
        category_3_range: list[float]
        demand_level: str
        price_trend_7d: float
        source_type: str

    class MarketSignal(BaseModel):
        match_id: str
        hotel_availability_score: float
        flight_price_pressure: float
        social_buzz_score: float
        days_before_event: int
        notes: str = ""

    class TripRequest(BaseModel):
        travelers: list[Traveler]
        match: EventMatch
        destination_city: str
        constraints: list[str] = []

    class AgentOutput(BaseModel):
        agent: str
        status: str
        confidence: str
        summary: str
        recommendation: str
        next_agent: str | None = None

    class BudgetPlan(BaseModel):
        option_name: str
        description: str
        traveler_costs: dict[str, dict[str, float]]
        shared_costs: dict[str, float]
        total_cost_per_traveler: dict[str, float]
        pros: list[str]
        cons: list[str]
        recommendation_score: float

except Exception:  # pragma: no cover - fallback path

    @dataclass
    class Traveler:
        name: str
        origin: str
        flexible_dates: bool = True
        budget_preference: str = "budget_first"

    @dataclass
    class EventMatch:
        match_id: str
        name: str
        date: str
        venue: str
        city: str

    @dataclass
    class FlightQuote:
        origin: str
        destination: str
        depart_date: str
        return_date: str
        estimated_roundtrip_cost: float
        trip_type: str
        risk_level: str
        notes: str = ""

    @dataclass
    class HotelQuote:
        hotel_id: str
        name: str
        city: str
        price_per_night: float
        total_price: float
        beds: int
        walking_minutes_to_venue: int | None = None
        transit_minutes_to_venue: int | None = None
        rating: float = 0.0
        cancellation_policy: str = ""
        notes: str = ""

    @dataclass
    class TicketQuote:
        match_id: str
        lowest_price: float
        listings: int
        category_3_range: list[float]
        demand_level: str
        price_trend_7d: float
        source_type: str

    @dataclass
    class MarketSignal:
        match_id: str
        hotel_availability_score: float
        flight_price_pressure: float
        social_buzz_score: float
        days_before_event: int
        notes: str = ""

    @dataclass
    class TripRequest:
        travelers: list[Traveler]
        match: EventMatch
        destination_city: str
        constraints: list[str] = field(default_factory=list)

    @dataclass
    class AgentOutput:
        agent: str
        status: str
        confidence: str
        summary: str
        recommendation: str
        next_agent: str | None = None

    @dataclass
    class BudgetPlan:
        option_name: str
        description: str
        traveler_costs: dict[str, dict[str, float]]
        shared_costs: dict[str, float]
        total_cost_per_traveler: dict[str, float]
        pros: list[str]
        cons: list[str]
        recommendation_score: float


def to_plain_dict(value: Any) -> dict[str, Any]:
    """Return a plain dict for either pydantic models or dataclasses."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return dict(value.__dict__)

