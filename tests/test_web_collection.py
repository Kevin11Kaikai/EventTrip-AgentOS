from pathlib import Path

import pytest

from eventtrip.mcp_server import server
from eventtrip.web_collection.collector import WebCollector
from eventtrip.web_collection.evidence_store import load_web_evidence, save_web_evidence
from eventtrip.web_collection.extractor import extract_market_evidence, extract_text_from_html
from eventtrip.web_collection.policies import is_probably_disallowed_url
from eventtrip.web_collection.schemas import WebCollectionTarget


FIXTURE = Path("examples/sample_ticket_market_page.html")


def test_local_html_fixture_collection_succeeds():
    evidence = WebCollector().collect_target(
        WebCollectionTarget(
            target_id="sample_fixture",
            local_path=str(FIXTURE),
            match_id="portugal_dr_congo",
        ),
        cache_dir="data/web_evidence",
    )

    assert evidence.match_id == "portugal_dr_congo"
    assert evidence.extracted_fields["candidate_lowest_price"] == 680.0
    assert evidence.extracted_fields["candidate_listings"] == 340
    assert evidence.raw_cache_path is None


def test_live_http_disabled_by_default():
    with pytest.raises(ValueError, match="Live HTTP collection is disabled"):
        WebCollector().collect_target(
            WebCollectionTarget(
                target_id="example_public",
                url="https://example.com",
                match_id="portugal_dr_congo",
            ),
            cache_dir="data/web_evidence",
            live_http=False,
        )


def test_policy_rejects_suspicious_urls():
    for url in [
        "https://example.com/login",
        "https://example.com/checkout",
        "https://example.com/cart",
        "https://example.com/payment",
    ]:
        disallowed, reason = is_probably_disallowed_url(url)
        assert disallowed
        assert reason


def test_extractor_finds_price_and_listings_from_fixture():
    text = extract_text_from_html(FIXTURE.read_text(encoding="utf-8"))
    extraction = extract_market_evidence(text, "portugal_dr_congo")

    assert extraction.candidate_lowest_price == 680.0
    assert extraction.candidate_listings == 340
    assert extraction.candidate_hotel_price == 160.0
    assert extraction.confidence == "medium"


def test_evidence_save_load_roundtrip(tmp_path):
    evidence = WebCollector().collect_target(
        WebCollectionTarget(
            target_id="sample_fixture",
            local_path=str(FIXTURE),
            match_id="portugal_dr_congo",
        ),
        cache_dir=tmp_path,
    )

    saved = save_web_evidence(evidence, tmp_path)
    loaded = load_web_evidence(saved)

    assert loaded.evidence_id == evidence.evidence_id
    assert loaded.extracted_fields["candidate_lowest_price"] == 680.0


def test_mcp_web_evidence_preview_tools_are_deterministic():
    text_preview = server.preview_web_evidence_from_text(
        "Lowest observed ticket price: $680. Approximate resale listings: 340 listings.",
        "portugal_dr_congo",
    )
    file_preview = server.preview_web_evidence_from_local_file(
        "examples/sample_ticket_market_page.html",
        "portugal_dr_congo",
    )

    assert text_preview["validation_status"] == "valid"
    assert text_preview["extraction"]["candidate_lowest_price"] == 680.0
    assert file_preview["validation_status"] == "valid"
    assert file_preview["extraction"]["candidate_listings"] == 340


def test_mcp_web_evidence_preview_rejects_env_files():
    preview = server.preview_web_evidence_from_local_file(".env", "portugal_dr_congo")

    assert preview["validation_status"] == "error"
    assert "environment files" in preview["error"]
