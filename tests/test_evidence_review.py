import json
from pathlib import Path

from eventtrip.evidence_review import (
    build_snapshot_candidate,
    convert_reviewed_evidence_to_snapshot,
    load_evidence_for_review,
    summarize_evidence_for_review,
)
from eventtrip.market_snapshots import load_market_snapshots


SAMPLE_EVIDENCE = Path("examples/sample_web_evidence.json")


def test_load_evidence_for_review_and_summary():
    evidence = load_evidence_for_review(SAMPLE_EVIDENCE)
    summary = summarize_evidence_for_review(evidence)

    assert summary["match_id"] == "portugal_dr_congo"
    assert summary["candidate_lowest_price"] == 680.0
    assert summary["candidate_listings"] == 340


def test_build_snapshot_candidate_from_reviewed_evidence():
    evidence = load_evidence_for_review(SAMPLE_EVIDENCE)
    snapshot = build_snapshot_candidate(
        evidence=evidence,
        snapshot_date="2026-05-22",
        category_3_low=400,
        category_3_high=750,
        hotel_availability_score=0.50,
        flight_price_pressure=0.55,
        social_buzz_score=0.86,
        days_before_event=26,
        notes="Manual review accepted candidate values.",
    )

    assert snapshot.match_id == "portugal_dr_congo"
    assert snapshot.lowest_price == 680.0
    assert snapshot.listings == 340
    assert snapshot.source_type == "reviewed_web_evidence"


def test_convert_reviewed_evidence_dry_run_does_not_write(tmp_path):
    destination = tmp_path / "snapshots.csv"

    result = _convert(destination, save=False)

    assert result["status"] == "dry_run"
    assert not result["saved"]
    assert not destination.exists()


def test_convert_reviewed_evidence_save_writes_snapshot(tmp_path):
    destination = tmp_path / "snapshots.csv"

    result = _convert(destination, save=True)
    snapshots = load_market_snapshots(destination)

    assert result["saved"]
    assert result["status"] == "appended"
    assert len(snapshots) == 1
    assert snapshots[0].lowest_price == 680.0


def test_duplicate_without_overwrite_fails_safely(tmp_path):
    destination = tmp_path / "snapshots.csv"
    _convert(destination, save=True)

    result = _convert(destination, save=True)

    assert result["status"] == "duplicate"
    assert not result["saved"]
    assert "use --overwrite" in result["errors"][0]


def test_duplicate_with_overwrite_replaces_row(tmp_path):
    destination = tmp_path / "snapshots.csv"
    _convert(destination, save=True, notes="first")

    result = _convert(destination, save=True, overwrite=True, notes="replacement")
    snapshots = load_market_snapshots(destination)

    assert result["status"] == "overwritten"
    assert result["saved"]
    assert len(snapshots) == 1
    assert "replacement" in snapshots[0].notes


def test_missing_candidate_price_fails(tmp_path):
    data = json.loads(SAMPLE_EVIDENCE.read_text(encoding="utf-8"))
    data["extracted_fields"]["candidate_lowest_price"] = None
    bad_path = tmp_path / "bad_evidence.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")

    result = convert_reviewed_evidence_to_snapshot(
        evidence_path=bad_path,
        snapshot_date="2026-05-22",
        category_3_low=400,
        category_3_high=750,
        hotel_availability_score=0.50,
        flight_price_pressure=0.55,
        social_buzz_score=0.86,
        days_before_event=26,
        destination_path=tmp_path / "snapshots.csv",
        save=True,
    )

    assert result["status"] == "evidence_error"
    assert "candidate_lowest_price" in result["errors"][0]


def _convert(destination: Path, save: bool, overwrite: bool = False, notes: str = ""):
    return convert_reviewed_evidence_to_snapshot(
        evidence_path=SAMPLE_EVIDENCE,
        snapshot_date="2026-05-22",
        category_3_low=400,
        category_3_high=750,
        hotel_availability_score=0.50,
        flight_price_pressure=0.55,
        social_buzz_score=0.86,
        days_before_event=26,
        notes=notes,
        destination_path=destination,
        save=save,
        overwrite=overwrite,
    )
