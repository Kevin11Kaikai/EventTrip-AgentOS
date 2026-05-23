from eventtrip.scoring import compute_scalper_stress_index


def test_scalper_stress_range():
    result = compute_scalper_stress_index(
        listings=300,
        lowest_price=700,
        price_trend_7d=0.02,
        hotel_availability_score=0.55,
        flight_price_pressure=0.50,
        social_buzz_score=0.85,
        days_before_event=183,
    )

    assert 0 <= result["score"] <= 100
    assert result["interpretation"]


def test_more_listings_and_falling_prices_increase_score():
    low_pressure = compute_scalper_stress_index(
        listings=100,
        lowest_price=500,
        price_trend_7d=0.05,
        hotel_availability_score=0.35,
        flight_price_pressure=0.80,
        social_buzz_score=0.90,
        days_before_event=183,
    )
    high_pressure = compute_scalper_stress_index(
        listings=500,
        lowest_price=500,
        price_trend_7d=-0.08,
        hotel_availability_score=0.35,
        flight_price_pressure=0.80,
        social_buzz_score=0.90,
        days_before_event=183,
    )

    assert high_pressure["score"] > low_pressure["score"]

