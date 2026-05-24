from eventtrip.agents.source_backed_report_agent import SourceBackedReportAgent
from eventtrip.ticket_links import recommend_ticket_links


def test_source_backed_report_agent_writes_no_mock_report(tmp_path):
    trip_request = {
        "match": {
            "match_id": "portugal_dr_congo",
            "name": "Portugal vs DR Congo",
            "date": "2026-06-17",
            "venue": "NRG Stadium",
            "city": "Houston",
        }
    }
    context = {
        "ticket_links": recommend_ticket_links("portugal_dr_congo", "monitor_with_wait_bias"),
    }

    result = SourceBackedReportAgent().run(trip_request, tmp_path, context)
    output = result["source_backed_report_path"]
    html_output = result["source_backed_html_report_path"]
    text = output.read_text(encoding="utf-8")
    html = html_output.read_text(encoding="utf-8")

    assert output.name == "10_source_backed_final_report.md"
    assert html_output.name == "11_source_backed_final_report.html"
    assert "Source-Backed Final Report" in text
    assert "## What To Do Next" in text
    assert "## Recommended Official Purchase Paths" in text
    assert "## What Is Still Unknown" in text
    assert "Exact all-in ticket price for Portugal vs DR Congo." in text
    assert "EventTrip-AgentOS does not log in" in text
    assert "## Citation Groups" in text
    assert "### Match facts" in text
    assert "### Ticket safety" in text
    assert "### Houston logistics" in text
    assert "### Unknown or not source-backed yet" in text
    assert "Axios" in text
    assert "FIFA" in text
    assert "mock" not in text.lower()
    assert "EventTrip-AgentOS Source-Backed Report" in html
    assert "What Is Still Unknown" in html
    assert "claim-match-facts" in html
    assert "mock" not in html.lower()
