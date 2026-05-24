from eventtrip.source_evidence import (
    get_match_sources,
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
