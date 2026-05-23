"""Deterministic scoring functions for the Phase 1 demo."""

from __future__ import annotations


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def compute_scalper_stress_index(
    listings: int,
    lowest_price: float,
    price_trend_7d: float,
    hotel_availability_score: float,
    flight_price_pressure: float,
    social_buzz_score: float,
    days_before_event: int,
) -> dict:
    """Compute a 0-100 proxy for artificial secondary-market pressure.

    Higher values mean the current ticket market looks more like reseller
    inventory pressure than unavoidable real travel demand.
    """
    listings_score = min(listings / 500.0, 1.0) * 25.0
    if price_trend_7d < 0:
        trend_score = min(abs(price_trend_7d) * 1000.0, 18.0)
    else:
        trend_score = max(0.0, 8.0 - min(price_trend_7d * 400.0, 8.0))
    hotel_score = _clamp(hotel_availability_score, 0.0, 1.0) * 15.0
    flight_score = (1.0 - _clamp(flight_price_pressure, 0.0, 1.0)) * 15.0
    buzz_score = (1.0 - _clamp(social_buzz_score, 0.0, 1.0)) * 10.0
    time_score = max(0.0, (120.0 - days_before_event) / 120.0) * 15.0
    price_premium_score = min(max(lowest_price - 300.0, 0.0) / 500.0, 1.0) * 12.0

    score = _clamp(
        listings_score
        + trend_score
        + hotel_score
        + flight_score
        + buzz_score
        + time_score
        + price_premium_score
    )

    if score <= 35:
        interpretation = "low scalper stress, buy/monitor"
    elif score <= 65:
        interpretation = "moderate scalper stress, monitor"
    else:
        interpretation = "high scalper stress, likely wait"

    explanation = [
        f"Listings contribution: {listings_score:.1f}/25 from {listings} active listings.",
        f"Seven-day price trend contribution: {trend_score:.1f}/18 from {price_trend_7d:+.1%}.",
        f"Hotel availability contribution: {hotel_score:.1f}/15 from availability score {hotel_availability_score:.2f}.",
        f"Flight pressure contribution: {flight_score:.1f}/15 from pressure score {flight_price_pressure:.2f}.",
        f"Social buzz contribution: {buzz_score:.1f}/10 from buzz score {social_buzz_score:.2f}.",
        f"Time pressure contribution: {time_score:.1f}/15 with {days_before_event} days before event.",
        f"Price premium contribution: {price_premium_score:.1f}/12 from lowest ask ${lowest_price:.0f}.",
    ]

    return {
        "score": round(score, 1),
        "interpretation": interpretation,
        "explanation": explanation,
    }


def hotel_value_score(
    price_per_person: float,
    walking_minutes_to_venue: int | None,
    transit_minutes_to_venue: int | None,
    beds: int,
    rating: float,
    cancellation_policy: str,
) -> float:
    """Score hotel value from a budget-first event-travel perspective."""
    price_score = max(0.0, 35.0 - max(price_per_person - 60.0, 0.0) * 0.25)

    if walking_minutes_to_venue is not None:
        access_score = max(10.0, 25.0 - max(walking_minutes_to_venue - 5, 0) * 0.8)
    elif transit_minutes_to_venue is not None:
        access_score = max(8.0, 22.0 - max(transit_minutes_to_venue - 15, 0) * 0.5)
    else:
        access_score = 5.0

    bed_score = 15.0 if beds >= 2 else 4.0
    rating_score = _clamp((rating - 2.5) / 2.5, 0.0, 1.0) * 15.0
    cancellation = cancellation_policy.lower()
    if cancellation == "refundable":
        cancellation_score = 10.0
    elif "semi" in cancellation:
        cancellation_score = 5.0
    else:
        cancellation_score = 0.0

    return round(_clamp(price_score + access_score + bed_score + rating_score + cancellation_score), 1)


def budget_option_score(
    total_cost: float,
    hotel_nights: int,
    travel_fatigue: float,
    schedule_simplicity: float,
    shared_cost_efficiency: float,
    risk_of_missing_match: float,
) -> float:
    """Score one budget option; higher is better."""
    cost_score = max(0.0, 100.0 - max(total_cost - 850.0, 0.0) / 7.5)
    night_penalty = max(hotel_nights - 1, 0) * 6.0
    fatigue_penalty = _clamp(travel_fatigue, 0.0, 1.0) * 10.0
    simplicity_bonus = _clamp(schedule_simplicity, 0.0, 1.0) * 8.0
    sharing_bonus = _clamp(shared_cost_efficiency, 0.0, 1.0) * 7.0
    miss_penalty = _clamp(risk_of_missing_match, 0.0, 1.0) * 18.0

    score = cost_score - night_penalty - fatigue_penalty + simplicity_bonus + sharing_bonus - miss_penalty
    return round(_clamp(score), 1)

