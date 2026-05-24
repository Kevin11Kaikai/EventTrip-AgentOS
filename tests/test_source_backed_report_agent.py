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
    assert "## Secondary Marketplace Candidate" in text
    assert "StubHub World Cup Tickets" in text
    assert "not treated as an official FIFA source" in text
    assert "## What Is Still Unknown" in text
    assert "## Reviewed Live/API Snapshot Status" in text
    assert "No reviewed live/API snapshots are attached" in text
    assert "Exact all-in ticket price for Portugal vs DR Congo." in text
    assert "EventTrip-AgentOS does not log in" in text
    assert "## Citation Groups" in text
    assert "### Match facts" in text
    assert "### Ticket safety" in text
    assert "### Houston logistics" in text
    assert "### Cost trend evidence" in text
    assert "### Unknown or not source-backed yet" in text
    assert "Axios" in text
    assert "FIFA" in text
    assert "StubHub" in text
    assert "mock" not in text.lower()
    assert "EventTrip-AgentOS 中文来源报告" in html
    assert "仍然未知的内容" in html
    assert "二级市场候选渠道" in html
    assert "StubHub World Cup Tickets" in html
    assert "claim-match-facts" in html
    assert "claim-secondary-marketplace-stubhub" in html
    assert "价格趋势图与购买窗口预测" in html
    assert "mock" not in html.lower()


def test_source_backed_report_agent_includes_reviewed_live_snapshots(tmp_path):
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
        "market_snapshots": [
            {
                "snapshot_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "lowest_price": 640.0,
                "listings": 355,
                "source_type": "reviewed_live_data",
                "notes": "Human-reviewed API response.",
            },
            {
                "snapshot_date": "2026-05-15",
                "match_id": "portugal_dr_congo",
                "lowest_price": 680.0,
                "listings": 340,
                "source_type": "mock_manual",
                "notes": "Should not appear in source-backed live section.",
            },
        ],
    }

    result = SourceBackedReportAgent().run(trip_request, tmp_path, context)
    text = result["source_backed_report_path"].read_text(encoding="utf-8")
    html = result["source_backed_html_report_path"].read_text(encoding="utf-8")

    assert result["reviewed_live_snapshots"][0]["lowest_price"] == 640.0
    assert "$640.0" in text
    assert "Human-reviewed API response." in text
    assert "$640" in html
    assert "Human-reviewed API response." in html
    assert "Should not appear in source-backed live section." not in text
