from eventtrip.source_evidence import get_match_sources
from eventtrip.source_traceability import (
    build_evidence_traceability,
    format_traceability_markdown,
)


def test_traceability_matrix_marks_source_backed_and_unsourced_claims():
    items = build_evidence_traceability(get_match_sources("portugal_dr_congo"))
    statuses = {item.status for item in items}

    assert "source_backed" in statuses
    assert "internal_estimate_not_source_backed" in statuses
    assert "no_source_backed_data_found" in statuses
    assert any("Traveler A estimated cost is $1120" in item.claim for item in items)
    assert any("No registered public source" in item.note for item in items)


def test_traceability_markdown_contains_statuses_and_sources():
    markdown = format_traceability_markdown(
        build_evidence_traceability(get_match_sources("portugal_dr_congo"))
    )

    assert "| Claim | Evidence status | Source group | Evidence / note |" in markdown
    assert "source_backed" in markdown
    assert "internal_estimate_not_source_backed" in markdown
    assert "no_source_backed_data_found" in markdown
    assert "FIFA" in markdown
