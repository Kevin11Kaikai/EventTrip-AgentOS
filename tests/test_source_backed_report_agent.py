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
    assert "## Reviewed Quantitative Quote Status" in text
    assert "No reviewed source-backed quote rows are attached" in text
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
    assert "定量分析：哪些数字是真的，哪些还不能声称是真的" in html
    assert "真实审核报价与总成本曲线" in html
    assert "目前没有经过人工审核且可引用的真实报价" in html
    assert "成本压力指数变化表" in html
    assert "仍然未知的内容" in html
    assert "二级市场候选渠道" in html
    assert "StubHub World Cup Tickets" in html
    assert "claim-match-facts" in html
    assert "claim-secondary-marketplace-stubhub" in html
    assert "价格趋势图与购买窗口预测" in html
    assert "字段级来源标注" in html
    assert "forecast_chart" in html
    assert "官方购票路径" in html
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
    assert "355 listings" in html
    assert "Human-reviewed API response." in html
    assert "Should not appear in source-backed live section." not in text


def test_source_backed_report_agent_includes_reviewed_quotes_from_context(tmp_path):
    trip_request = {
        "match": {
            "match_id": "portugal_dr_congo",
            "name": "Portugal vs DR Congo",
            "date": "2026-06-17",
            "venue": "NRG Stadium",
            "city": "Houston",
        }
    }
    base_quote = {
        "quote_date": "2026-05-20",
        "match_id": "portugal_dr_congo",
        "currency": "USD",
        "confidence": "medium",
        "notes": "Reviewed row.",
    }
    context = {
        "ticket_links": recommend_ticket_links("portugal_dr_congo", "monitor_with_wait_bias"),
        "reviewed_quotes": [
            {**base_quote, "component": "ticket", "amount": 640, "source_id": "ticket_quote", "source_url": "https://example.com/ticket", "source_label": "Ticket quote", "origin": ""},
            {**base_quote, "component": "pit_flight", "amount": 420, "source_id": "pit_quote", "source_url": "https://example.com/pit", "source_label": "PIT quote", "origin": "PIT"},
            {**base_quote, "component": "sea_flight", "amount": 520, "source_id": "sea_quote", "source_url": "https://example.com/sea", "source_label": "SEA quote", "origin": "SEA"},
            {**base_quote, "component": "hotel", "amount": 95, "source_id": "hotel_quote", "source_url": "https://example.com/hotel", "source_label": "Hotel quote", "origin": ""},
            {**base_quote, "component": "local_transport", "amount": 35, "source_id": "transport_quote", "source_url": "https://example.com/transport", "source_label": "Transport quote", "origin": ""},
        ],
    }

    result = SourceBackedReportAgent().run(trip_request, tmp_path, context)
    text = result["source_backed_report_path"].read_text(encoding="utf-8")
    html = result["source_backed_html_report_path"].read_text(encoding="utf-8")

    assert result["reviewed_quote_analysis"]["latest_totals"]["pit"] == 1190
    assert "$1190" in text
    assert "$1290" in text
    assert "ticket_quote" in text
    assert "PIT 来源支持总成本" in html
    assert "已审核美元报价折线图" in html
