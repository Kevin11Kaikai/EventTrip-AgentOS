from pathlib import Path

import pytest

from eventtrip.reviewed_quotes import (
    ReviewedQuote,
    analyze_reviewed_quotes,
    import_reviewed_quotes,
    load_reviewed_quotes,
    save_reviewed_quotes,
    upsert_reviewed_quote,
    validate_reviewed_quote,
)


def _quote(component, amount, date="2026-05-20", source_id=None, origin=""):
    return ReviewedQuote(
        quote_date=date,
        match_id="portugal_dr_congo",
        component=component,
        amount=amount,
        currency="USD",
        source_id=source_id or f"source_{component}",
        source_url=f"https://example.com/{component}",
        source_label=f"Example {component}",
        origin=origin,
        confidence="medium",
        notes="Reviewed fixture row.",
    )


def test_validate_reviewed_quote_requires_source_and_positive_amount():
    quote = ReviewedQuote(
        quote_date="2026-05-20",
        match_id="portugal_dr_congo",
        component="ticket",
        amount=0,
        source_url="http://example.com",
        source_label="",
        source_id="",
    )

    errors = validate_reviewed_quote(quote)

    assert "amount must be positive." in errors
    assert "source_id is required for field-level attribution." in errors
    assert "source_label is required." in errors
    assert "source_url must be an https URL." in errors


def test_save_load_and_analyze_reviewed_quotes(tmp_path):
    path = tmp_path / "quotes.csv"
    quotes = [
        _quote("ticket", 640),
        _quote("pit_flight", 420, origin="PIT"),
        _quote("sea_flight", 520, origin="SEA"),
        _quote("hotel", 95),
        _quote("local_transport", 35),
    ]

    save_reviewed_quotes(path, quotes)
    loaded = load_reviewed_quotes(path, match_id="portugal_dr_congo")
    analysis = analyze_reviewed_quotes(loaded)

    assert len(loaded) == 5
    assert analysis["quote_count"] == 5
    assert analysis["latest_totals"]["pit"] == 1190
    assert analysis["latest_totals"]["sea"] == 1290
    assert analysis["missing_components"]["pit"] == []
    assert analysis["timeline"][-1]["pit_total"] == 1190


def test_upsert_duplicate_requires_overwrite(tmp_path):
    path = tmp_path / "quotes.csv"
    quote = _quote("ticket", 640)

    first = upsert_reviewed_quote(path, quote)
    duplicate = upsert_reviewed_quote(path, quote)
    replaced = upsert_reviewed_quote(path, _quote("ticket", 610), overwrite=True)
    loaded = load_reviewed_quotes(path)

    assert first["saved"] is True
    assert duplicate["status"] == "duplicate"
    assert replaced["status"] == "overwritten"
    assert loaded[0].amount == 610


def test_import_reviewed_quotes_dry_run_and_write(tmp_path):
    source = Path("examples/reviewed_quote_import.csv")
    destination = tmp_path / "quotes.csv"

    dry_run = import_reviewed_quotes(source, destination, dry_run=True)

    assert dry_run["status"] == "dry_run"
    assert not destination.exists()
    written = import_reviewed_quotes(source, destination, dry_run=False)
    duplicate = import_reviewed_quotes(source, destination, dry_run=False)
    assert written["saved"] is True
    assert len(load_reviewed_quotes(destination)) == 5
    assert duplicate["status"] == "duplicate"


def test_invalid_reviewed_quote_file_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "quote_date,match_id,component,amount,currency,source_id,source_url,source_label,origin,confidence,notes\n"
        "2026-05-20,portugal_dr_congo,ticket,-1,USD,src,https://example.com,Example,,medium,bad\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="amount must be positive"):
        load_reviewed_quotes(path)
