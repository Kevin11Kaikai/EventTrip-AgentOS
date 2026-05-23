from eventtrip.market_snapshots import (
    append_market_snapshot,
    compute_snapshot_scalper_stress,
    load_market_snapshots,
    save_market_snapshots,
    analyze_market_trend,
    default_snapshot_path,
)
from eventtrip.schemas import MarketSnapshot


def test_load_seed_market_snapshots():
    snapshots = load_market_snapshots(default_snapshot_path("portugal_dr_congo"), "portugal_dr_congo")

    assert len(snapshots) >= 5
    assert snapshots[0].snapshot_date == "2026-01-15"
    assert snapshots[-1].lowest_price == 680


def test_analyze_market_trend_recommendation_and_stress_range():
    snapshots = load_market_snapshots(default_snapshot_path("portugal_dr_congo"), "portugal_dr_congo")
    result = analyze_market_trend(snapshots)
    stress = compute_snapshot_scalper_stress(snapshots[-1])

    assert result.recommendation in {
        "buy",
        "strongly_consider_buying",
        "monitor",
        "wait",
        "insufficient_data",
    }
    assert result.snapshot_count >= 5
    assert 0 <= stress["score"] <= 100


def test_save_and_append_market_snapshots(tmp_path):
    path = tmp_path / "snapshots.csv"
    snapshot = MarketSnapshot(
        snapshot_date="2026-01-01",
        match_id="portugal_dr_congo",
        lowest_price=700,
        listings=300,
        category_3_low=400,
        category_3_high=750,
        hotel_availability_score=0.55,
        flight_price_pressure=0.50,
        social_buzz_score=0.85,
        days_before_event=183,
        source_type="test_manual",
        notes="test",
    )

    save_market_snapshots(path, [snapshot])
    append_market_snapshot(path, snapshot)
    loaded = load_market_snapshots(path, "portugal_dr_congo")

    assert len(loaded) == 2
    assert loaded[0].match_id == "portugal_dr_congo"


def test_insufficient_snapshot_data():
    result = analyze_market_trend([])

    assert result.recommendation == "insufficient_data"
    assert result.explanation
