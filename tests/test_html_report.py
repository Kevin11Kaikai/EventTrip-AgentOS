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
    assert "EventTrip-AgentOS 中文来源报告" in html
    assert "静态客户展示报告" in html
    assert "决策摘要" in html
    assert "定量分析：哪些数字是真的，哪些还不能声称是真的" in html
    assert "真实审核报价与总成本曲线" in html
    assert "目前没有经过人工审核且可引用的真实报价" in html
    assert "暂不生成" in html
    assert "已登记公开来源" in html
    assert "成本压力指数变化表" in html
    assert "PIT机票压力指数" in html
    assert "SEA机票压力指数" in html
    assert "到比赛周变化" in html
    assert "真实全量预算" in html
    assert "未知" in html
    assert "下一步怎么做" in html
    assert "推荐官方购票路径" in html
    assert "二级市场候选渠道" in html
    assert "StubHub World Cup Tickets" in html
    assert "仍然未知的内容" in html
    assert "人工审核 Live/API 数据状态" in html
    assert "本报告没有附加已审核的 live/API 数据" in html
    assert "价格趋势图与购买窗口预测" in html
    assert "成本压力指数折线图" in html
    assert "字段级来源标注" in html
    assert "公开来源支持" in html
    assert "模型推断" in html
    assert "人工审核数据" in html
    assert "未找到来源支持" in html
    assert "forecast_chart" in html
    assert "pit_recommendation" in html
    assert "sea_recommendation" in html
    assert "official_ticket_path" in html
    assert "未找到可靠公开来源支持" in html
    assert "report-nav" in html
    assert "client-summary-strip" in html
    assert "screenshot-friendly" in html
    assert "scroll-behavior: smooth" in html
    assert "@page" in html
    assert "overflow-x: auto" in html
    assert "@media print" in html
    assert "claim-match-facts" in html
    assert "claim-secondary-marketplace-stubhub" in html
    assert "FIFA: Portugal v Congo DR" in html
    assert "[FIFA: Portugal v Congo DR" not in html
    assert "不执行实时购票" in html
    assert "mock" not in html.lower()


def test_html_report_displays_reviewed_live_snapshots():
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
        reviewed_live_snapshots=[
            {
                "snapshot_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "lowest_price": 640.0,
                "listings": 355,
                "source_type": "reviewed_live_data",
                "notes": "Human-reviewed fixture preview.",
            }
        ],
    )

    assert "以下是已人工审核的 live/API snapshot" in html
    assert "reviewed_live_snapshots" in html
    assert "$640" in html
    assert "355 listings" in html
    assert "reviewed_live_data" in html
    assert "Human-reviewed fixture preview." in html


def test_html_report_displays_reviewed_quote_totals_and_chart():
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
        reviewed_quotes=[
            {
                "quote_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "component": "ticket",
                "amount": 640,
                "currency": "USD",
                "source_id": "ticket_quote",
                "source_url": "https://example.com/ticket",
                "source_label": "Ticket quote",
                "origin": "",
                "confidence": "medium",
                "notes": "Reviewed row.",
            },
            {
                "quote_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "component": "pit_flight",
                "amount": 420,
                "currency": "USD",
                "source_id": "pit_quote",
                "source_url": "https://example.com/pit",
                "source_label": "PIT quote",
                "origin": "PIT",
                "confidence": "medium",
                "notes": "Reviewed row.",
            },
            {
                "quote_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "component": "sea_flight",
                "amount": 520,
                "currency": "USD",
                "source_id": "sea_quote",
                "source_url": "https://example.com/sea",
                "source_label": "SEA quote",
                "origin": "SEA",
                "confidence": "medium",
                "notes": "Reviewed row.",
            },
            {
                "quote_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "component": "hotel",
                "amount": 95,
                "currency": "USD",
                "source_id": "hotel_quote",
                "source_url": "https://example.com/hotel",
                "source_label": "Hotel quote",
                "origin": "",
                "confidence": "medium",
                "notes": "Reviewed row.",
            },
            {
                "quote_date": "2026-05-20",
                "match_id": "portugal_dr_congo",
                "component": "local_transport",
                "amount": 35,
                "currency": "USD",
                "source_id": "transport_quote",
                "source_url": "https://example.com/transport",
                "source_label": "Transport quote",
                "origin": "",
                "confidence": "medium",
                "notes": "Reviewed row.",
            },
        ],
    )

    assert "PIT 来源支持总成本" in html
    assert "SEA 来源支持总成本" in html
    assert "$1190" in html
    assert "$1290" in html
    assert "已审核美元报价折线图" in html
    assert "ticket_quote" in html
