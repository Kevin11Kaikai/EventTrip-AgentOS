from eventtrip.source_backed_quotes import quotes_from_web_evidence
from eventtrip.web_collection.schemas import WebEvidence


def test_web_evidence_with_public_url_becomes_source_backed_quotes():
    evidence = WebEvidence(
        evidence_id="ticket_hotel_source",
        target_id="ticket_hotel_source",
        match_id="portugal_dr_congo",
        source_url="https://example.com/public-ticket-page",
        local_path=None,
        collected_at="2026-05-25T12:00:00+00:00",
        title="Public ticket and hotel page",
        text_excerpt="Lowest ticket price $680. Hotel around $160 per night.",
        raw_cache_path=None,
        extraction_confidence="medium",
        extracted_fields={
            "candidate_lowest_price": 680,
            "candidate_hotel_price": 160,
            "candidate_currency": "USD",
        },
        notes="Public source-backed evidence.",
    )

    quotes = quotes_from_web_evidence([evidence])

    assert [(quote.component, quote.amount) for quote in quotes] == [
        ("hotel", 160.0),
        ("ticket", 680.0),
    ]
    assert all(quote.source_url == "https://example.com/public-ticket-page" for quote in quotes)
    assert all(quote.source_id == "web_evidence:ticket_hotel_source" for quote in quotes)


def test_web_evidence_without_public_url_is_not_reportable():
    evidence = WebEvidence(
        evidence_id="local_fixture",
        target_id="local_fixture",
        match_id="portugal_dr_congo",
        source_url=None,
        local_path="examples/sample_ticket_market_page.html",
        collected_at="2026-05-25T12:00:00+00:00",
        title="Local fixture",
        text_excerpt="Lowest ticket price $680.",
        raw_cache_path=None,
        extraction_confidence="medium",
        extracted_fields={"candidate_lowest_price": 680},
        notes="Local fixture should not become a customer quote.",
    )

    assert quotes_from_web_evidence([evidence]) == []


def test_flight_component_requires_origin_context():
    pit_evidence = WebEvidence(
        evidence_id="pit_flight_source",
        target_id="pit-flight-source",
        match_id="portugal_dr_congo",
        source_url="https://example.com/pit-flight",
        local_path=None,
        collected_at="2026-05-25T12:00:00+00:00",
        title="Pittsburgh to Houston flight quote",
        text_excerpt="Flight price $420.",
        raw_cache_path=None,
        extraction_confidence="medium",
        extracted_fields={"candidate_flight_price": 420},
        notes="PIT source.",
    )
    unknown_origin = WebEvidence(
        evidence_id="generic_flight_source",
        target_id="generic-flight-source",
        match_id="portugal_dr_congo",
        source_url="https://example.com/generic-flight",
        local_path=None,
        collected_at="2026-05-25T12:00:00+00:00",
        title="Houston flight quote",
        text_excerpt="Flight price $500.",
        raw_cache_path=None,
        extraction_confidence="medium",
        extracted_fields={"candidate_flight_price": 500},
        notes="No origin context.",
    )

    quotes = quotes_from_web_evidence([pit_evidence, unknown_origin])

    assert len(quotes) == 1
    assert quotes[0].component == "pit_flight"
    assert quotes[0].amount == 420
