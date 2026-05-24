from eventtrip.html_report import build_source_backed_html_report
from eventtrip.source_evidence import get_match_sources, grouped_citations
from eventtrip.source_traceability import build_evidence_traceability
from eventtrip.ticket_links import recommend_ticket_links


def test_source_backed_html_report_is_static_and_client_readable():
    source_data = get_match_sources("portugal_dr_congo")
    html = build_source_backed_html_report(
        match={
            "match_id": "portugal_dr_congo",
            "name": "Portugal vs DR Congo",
            "date": "2026-06-17",
            "venue": "NRG Stadium",
            "city": "Houston",
        },
        ticket_links=recommend_ticket_links("portugal_dr_congo", "monitor_with_wait_bias"),
        citation_groups=grouped_citations(source_data),
        source_data=source_data,
        traceability_items=build_evidence_traceability(source_data),
    )

    assert "<!doctype html>" in html
    assert "EventTrip-AgentOS Source-Backed Report" in html
    assert "What To Do Next" in html
    assert "Recommended Official Purchase Paths" in html
    assert "What Is Still Unknown" in html
    assert "claim-match-facts" in html
    assert "No live purchase" in html
    assert "mock" not in html.lower()
