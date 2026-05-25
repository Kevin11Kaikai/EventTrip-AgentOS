from eventtrip.source_evidence import (
    build_field_source_attributions,
    get_match_sources,
    grouped_citations,
    sources_by_tag,
    validate_source_evidence,
)


def test_source_evidence_registry_validates():
    assert validate_source_evidence() == []


def test_source_evidence_has_match_and_ticket_safety_sources():
    sources = get_match_sources("portugal_dr_congo")

    assert sources["match_id"] == "portugal_dr_congo"
    assert sources_by_tag(sources, "match")
    assert sources_by_tag(sources, "ticket_safety")


def test_source_evidence_uses_public_https_sources():
    sources = get_match_sources("portugal_dr_congo")

    assert all(source["url"].startswith("https://") for source in sources["sources"])
    assert any(source["source_type"] == "news" for source in sources["sources"])
    assert any(source["source_type"] == "official" for source in sources["sources"])
    assert any(source["source_type"] == "marketplace" for source in sources["sources"])


def test_source_evidence_grouped_citations_cover_expected_sections():
    sources = get_match_sources("portugal_dr_congo")
    groups = grouped_citations(sources)

    assert groups["match_facts"]
    assert groups["ticket_safety"]
    assert groups["houston_logistics"]
    assert groups["cost_trends"]


def test_field_source_attributions_cover_html_report_fields():
    sources = get_match_sources("portugal_dr_congo")
    attributions = build_field_source_attributions(sources)

    assert attributions["match_name"].status == "source_backed"
    assert attributions["official_ticket_path"].source_ids
    assert attributions["secondary_market_stubhub"].source_ids
    assert attributions["forecast_chart"].status == "model_inference"
    assert attributions["pit_recommendation"].status == "model_inference"
    assert attributions["sea_recommendation"].status == "model_inference"
    assert attributions["trigger_policy"].status == "internal_policy"
    assert attributions["unknown_exact_prices"].status == "no_source_backed_data_found"
