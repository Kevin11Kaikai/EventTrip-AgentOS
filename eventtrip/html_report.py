"""Static HTML report rendering for source-backed public reports."""

from __future__ import annotations

import re
from html import escape
from typing import Any

from eventtrip.reviewed_quotes import COMPONENT_LABELS, ReviewedQuote, analyze_reviewed_quotes
from eventtrip.source_evidence import FieldSourceAttribution, build_field_source_attributions
from eventtrip.source_traceability import EvidenceTraceabilityItem


def build_source_backed_html_report(
    *,
    match: dict[str, Any],
    ticket_links: dict[str, Any],
    citation_groups: dict[str, list[dict[str, Any]]],
    source_data: dict[str, Any],
    traceability_items: list[EvidenceTraceabilityItem],
    live_snapshot_preview: dict[str, Any] | None = None,
    reviewed_live_snapshots: list[dict[str, Any]] | None = None,
    reviewed_quotes: list[dict[str, Any]] | None = None,
) -> str:
    """Build a static, dependency-free HTML report for client-facing review."""
    primary_links = ticket_links.get("primary_links", [])
    info_links = ticket_links.get("info_links", [])
    secondary_links = ticket_links.get("secondary_links", [])
    all_ticket_links = [*primary_links, *info_links]
    sources = source_data.get("sources", [])
    reviewed_snapshots = reviewed_live_snapshots or []
    quote_rows = reviewed_quotes or []
    quote_analysis = analyze_reviewed_quotes(_quote_dicts_to_objects(quote_rows))
    forecast = _forecast_model(quote_analysis)
    source_attributions = build_field_source_attributions(source_data)
    coverage = _source_coverage_metrics(citation_groups, sources, traceability_items)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EventTrip-AgentOS 中文来源报告</title>
  <style>
    :root {{
      --ink: #172033;
      --muted: #5d6878;
      --line: #d8dee8;
      --panel: #f7f9fc;
      --accent: #0f766e;
      --accent-strong: #0b5f59;
      --accent-soft: #e7f5f3;
      --warn: #9a3412;
      --ok: #166534;
      --unknown: #6b21a8;
      --danger-bg: #fff7ed;
      --ok-bg: #eef8f1;
      --unknown-bg: #f5f3ff;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 8% -10%, rgba(15, 118, 110, 0.14), transparent 28%),
        linear-gradient(180deg, #f8fbfd 0%, #ffffff 320px);
      line-height: 1.5;
    }}
    header {{
      padding: 36px clamp(20px, 5vw, 64px) 28px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(231,245,243,0.86));
    }}
    header > *, main {{
      max-width: 1180px;
      margin-left: auto;
      margin-right: auto;
    }}
    main {{ padding: 28px clamp(20px, 5vw, 64px) 64px; }}
    section {{
      margin-top: 24px;
      padding: 22px;
      border: 1px solid rgba(216, 222, 232, 0.9);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.92);
      box-shadow: 0 8px 22px rgba(23, 32, 51, 0.045);
      overflow-x: auto;
      scroll-margin-top: 18px;
    }}
    section:first-child {{ margin-top: 0; }}
    #decision-summary, #quantitative-analysis {{
      background: linear-gradient(135deg, #ffffff 0%, var(--accent-soft) 100%);
      border-color: rgba(15, 118, 110, 0.24);
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(28px, 4vw, 44px); }}
    h2 {{ margin: 0 0 14px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }}
    h3 {{ margin-bottom: 8px; }}
    a {{ color: #0b5cad; }}
    .subtitle {{ color: var(--muted); max-width: 920px; }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 14px;
      color: var(--accent);
      font-weight: 700;
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: .04em;
    }}
    .client-summary-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .client-summary-strip span {{
      border: 1px solid rgba(15, 118, 110, 0.24);
      border-radius: 999px;
      padding: 7px 11px;
      background: rgba(255, 255, 255, 0.84);
      color: var(--accent-strong);
      font-size: 13px;
      font-weight: 700;
    }}
    .report-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 22px;
      position: sticky;
      top: 0;
      z-index: 5;
      padding: 8px 0;
      backdrop-filter: blur(10px);
    }}
    .report-nav a {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      background: #fff;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
    }}
    .report-nav a:hover {{ border-color: var(--accent); color: var(--accent-strong); }}
    .metrics, .status-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 22px;
    }}
    .metric, .card, .status-card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 16px;
      background: #fff;
      box-shadow: 0 6px 18px rgba(23, 32, 51, 0.055);
    }}
    .metric {{ min-height: 118px; }}
    .metric span {{ display: block; color: var(--muted); font-size: 13px; }}
    .metric strong {{ display: block; font-size: 20px; margin-top: 4px; }}
    .status-card {{ background: var(--panel); min-height: 132px; }}
    .status-card strong {{ display: block; margin-bottom: 4px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }}
    .note {{
      border-left: 4px solid var(--accent);
      background: var(--panel);
      padding: 12px 14px;
      margin: 16px 0;
      border-radius: 0 10px 10px 0;
    }}
    .unknown {{
      border-left: 4px solid var(--warn);
      background: var(--danger-bg);
    }}
    .section-lead {{ max-width: 920px; color: var(--muted); }}
    ul {{ padding-left: 20px; }}
    table {{ width: 100%; min-width: 720px; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: var(--panel); position: sticky; top: 0; z-index: 1; }}
    tr:nth-child(even) td {{ background: #fbfcfe; }}
    .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 9px;
      font-size: 12px;
      font-weight: 600;
      background: #eef2ff;
    }}
    .field-source {{
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
    }}
    .field-source strong {{ color: var(--ink); }}
    .field-source code {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 1px 4px;
      font-size: 11px;
    }}
    .source-backed-badge {{ background: var(--ok-bg); color: var(--ok); }}
    .model-inference-badge {{ background: #eff6ff; color: #1d4ed8; }}
    .source-backed-data-badge {{ background: #ecfeff; color: #0e7490; }}
    .internal-policy-badge {{ background: var(--danger-bg); color: var(--warn); }}
    .unknown-badge {{ background: var(--unknown-bg); color: var(--unknown); }}
    .source-backed, .internal-estimate, .not-found {{
      font-weight: 700;
      border-radius: 6px;
    }}
    .source-backed {{ color: var(--ok); background: var(--ok-bg); }}
    .internal-estimate {{ color: var(--warn); background: var(--danger-bg); }}
    .not-found {{ color: var(--unknown); background: var(--unknown-bg); }}
    .delta-up {{ color: var(--warn); font-weight: 700; }}
    .delta-down {{ color: var(--ok); font-weight: 700; }}
    .print-note {{
      display: none;
      color: var(--muted);
      font-size: 12px;
    }}
    footer {{ color: var(--muted); font-size: 13px; margin-top: 36px; }}
    svg {{
      width: 100%;
      height: auto;
      display: block;
    }}
    @media (max-width: 720px) {{
      header {{ padding-top: 26px; }}
      main {{ padding-left: 14px; padding-right: 14px; }}
      section {{ padding: 16px; border-radius: 12px; }}
      .metrics, .status-strip, .grid {{ grid-template-columns: 1fr; }}
      .report-nav {{ position: static; }}
      .client-summary-strip span {{ width: 100%; }}
    }}
    @media print {{
      @page {{ margin: 14mm; }}
      body {{ font-size: 11pt; }}
      body, header, section, .metric, .card, .status-card {{
        background: #ffffff !important;
        box-shadow: none !important;
      }}
      header, main {{ padding: 18px; }}
      header > *, main {{ max-width: none; }}
      section {{
        margin-top: 14px;
        padding: 12px 0;
        border: 0;
        border-top: 1px solid var(--line);
        border-radius: 0;
        overflow: visible;
      }}
      table {{ min-width: 0; font-size: 9pt; }}
      th {{ position: static; }}
      .report-nav {{ display: none; }}
      .card, .metric, .status-card {{ break-inside: avoid; }}
      .metrics, .status-strip, .grid {{ break-inside: avoid; }}
      a {{ color: var(--ink); text-decoration: none; }}
      .print-note {{ display: block; }}
    }}
  </style>
</head>
<body>
  <header>
    <span class="eyebrow">静态客户展示报告</span>
    <h1>EventTrip-AgentOS 中文来源报告</h1>
    <p class="subtitle">这个 HTML 页面只展示已登记公开来源支撑的事实、美元报价和基于报价的预测区间。没有公开来源支持的门票、机票、酒店、本地交通和总预算数值会保持“未知”，不会用本地估算冒充真实报价。</p>
    <div class="client-summary-strip screenshot-friendly">
      <span>客户展示版</span>
      <span>静态 HTML / 可截图</span>
      <span>打印友好</span>
      <span>不自动购票</span>
    </div>
    <div class="metrics">
      <div class="metric"><span>比赛</span><strong>{escape(str(match["name"]))}</strong>{_field_source_badge("match_name", source_attributions)}</div>
      <div class="metric"><span>日期</span><strong>{escape(str(match["date"]))}</strong>{_field_source_badge("match_date", source_attributions)}</div>
      <div class="metric"><span>场馆</span><strong>{escape(str(match["venue"]))} / Houston Stadium</strong>{_field_source_badge("match_venue", source_attributions)}</div>
      <div class="metric"><span>购票立场</span><strong>官方优先</strong>{_field_source_badge("official_ticket_path", source_attributions)}</div>
    </div>
    <nav class="report-nav" aria-label="报告章节">
      <a href="#quantitative-analysis">定量分析</a>
      <a href="#real-quote-analysis">来源报价</a>
      <a href="#next-actions">下一步</a>
      <a href="#official-paths">官方路径</a>
      <a href="#secondary-market">二级市场</a>
      <a href="#unknowns">未知项</a>
      <a href="#live-data">审核数据</a>
      <a href="#forecast">美元预测</a>
      <a href="#field-attribution">字段来源</a>
      <a href="#citations">来源分组</a>
      <a href="#traceability">证据追踪</a>
      <a href="#registry">来源清单</a>
    </nav>
  </header>
  <main>
    <section id="decision-summary">
      <h2>决策摘要</h2>
      <p class="section-lead">本页用于客户查看：有来源支持的事实、来源支撑报价、仍未知的真实价格和基于报价的预测区间分开展示。关键原则是：查不到真实公开数据就明确承认未知。</p>
      <div class="status-strip">
        <div class="status-card"><strong>购票路径</strong>先看 FIFA 官方票务或 FIFA 官方转售/换票；StubHub 只作为二级市场监控渠道。{_field_source_badge("official_ticket_path", source_attributions)}</div>
        <div class="status-card"><strong>价格真实性</strong>精确门票、机票、酒店、交通和总预算目前没有完整公开来源支持，因此不写成已验证报价。{_field_source_badge("unknown_exact_prices", source_attributions)}</div>
        <div class="status-card"><strong>自动化边界</strong>不自动结账、不绕过登录、不处理 CAPTCHA、不执行付款。{_field_source_badge("trigger_policy", source_attributions)}</div>
      </div>
    </section>

    <section id="quantitative-analysis">
      <h2>定量分析：哪些数字是真的，哪些还不能声称是真的</h2>
      <p class="section-lead">这部分补足客户最关心的量化信息：哪些是公开来源支撑的美元报价，哪些是基于这些报价的预测区间，哪些仍然未知。</p>
      {_quantitative_analysis_section(coverage, forecast, quote_analysis, source_attributions)}
    </section>

    <section id="real-quote-analysis">
      <h2>来源支撑报价与总成本曲线</h2>
      {_reviewed_quote_analysis_section(quote_analysis, quote_rows)}
    </section>

    <section id="next-actions">
      <h2>下一步怎么做</h2>
      <p class="section-lead">以下步骤只基于已登记的官方、市场和新闻来源。</p>
      {_html_list(_next_actions())}
    </section>

    <section id="official-paths">
      <h2>推荐官方购票路径</h2>
      <p class="note">这里只提供人工打开的链接。EventTrip-AgentOS 不登录、不绕过访问控制、不自动结账、不购票。</p>
      {_link_cards(all_ticket_links, "official_ticket_path", source_attributions)}
    </section>

    <section id="secondary-market">
      <h2>二级市场候选渠道</h2>
      <p class="note unknown">StubHub 可以作为二级市场监控渠道，但它不是 FIFA 官方票务来源。付款前必须人工核验具体比赛、总价含税费、交付时间、FIFA 转票方式、退款政策和买家保护。</p>
      {_link_cards(secondary_links, "secondary_market_stubhub", source_attributions)}
    </section>

    <section id="unknowns">
      <h2>仍然未知的内容</h2>
      <p class="note unknown">这些数值还没有公开来源支持。如果查不到，就保持未知，不用本地估算填充。</p>
      {_field_source_badge("unknown_exact_prices", source_attributions)}
      {_unknown_values_table()}
    </section>

    <section id="live-data">
      <h2>来源支撑 Live/API 数据状态</h2>
      {_live_data_status(live_snapshot_preview, reviewed_snapshots, source_attributions)}
    </section>

    <section id="forecast">
      <h2>美元价格预测与购买窗口</h2>
      {_forecast_section(forecast, source_attributions)}
    </section>

    <section id="field-attribution">
      <h2>字段级来源标注</h2>
      <p class="note">本表说明每个关键展示字段来自公开来源、来源支撑数据、模型推断、内部策略，还是尚未找到来源支持。</p>
      {_field_attribution_table(source_attributions, sources)}
    </section>

    <section id="citations">
      <h2>来源分组</h2>
      <div class="grid">
        {_citation_card("比赛事实", citation_groups.get("match_facts", []))}
        {_citation_card("购票安全", citation_groups.get("ticket_safety", []))}
        {_citation_card("休斯顿交通与住宿", citation_groups.get("houston_logistics", []))}
        {_citation_card("价格趋势依据", citation_groups.get("cost_trends", []))}
      </div>
    </section>

    <section id="traceability">
      <h2>证据追踪</h2>
      <p class="note">下表区分有来源支持的事实、模型估计和没有公开来源支持的未知项。</p>
      {_traceability_table(traceability_items)}
    </section>

    <section id="registry">
      <h2>来源清单</h2>
      {_source_registry_table(sources)}
    </section>

    <footer>
      由 EventTrip-AgentOS 生成。不执行实时购票、自动结账、登录绕过、CAPTCHA 绕过或付款操作。
      <p class="print-note">这是本地静态 HTML 报告。链接仅作为来源引用或人工导航入口，不代表自动购买行为。</p>
    </footer>
  </main>
</body>
</html>
"""


def _next_actions() -> list[str]:
    return [
        "先查看 FIFA 官方票务页面，再考虑其他购票来源。",
        "如果需要转售票，优先查看 FIFA 官方转售/换票信息。",
        "StubHub 只作为二级市场候选渠道监控，且必须先确认 FIFA 官方票务和官方转售路径。",
        "付款前人工确认比赛、日期、场馆、座位类别、数量、转票规则、退款政策和总价含税费。",
        "社交媒体、聊天软件和非官方转售报价应视为高风险，除非能通过官方路径独立验证。",
        "机票、酒店和本地交通价格如果没有公开来源支持，就不要写成已验证价格。",
    ]


def _still_unknowns() -> list[tuple[str, str, str]]:
    return [
        ("官方或转售门票精确含税费价格", "未知", "没有登记到可核验的公开报价"),
        ("StubHub 对本场比赛的精确含税费价格", "未知", "只有二级市场入口，没有核验到本场 all-in price"),
        ("官方转售库存数量", "未知", "没有公开来源支持库存数字"),
        ("PIT 出发机票真实报价", "未知", "没有登记到具体航班报价来源"),
        ("SEA 出发机票真实报价", "未知", "没有登记到具体航班报价来源"),
        ("NRG Stadium 附近双床酒店真实报价", "未知", "没有登记到具体酒店报价来源"),
        ("比赛日本地交通真实估价", "未知", "没有登记到具体交通报价来源"),
        ("每位旅客完整来源支持总预算", "未知", "门票、机票、酒店和交通缺少完整来源链"),
    ]


def _html_list(items: list[str]) -> str:
    rows = "\n".join(f"        <li>{escape(item)}</li>" for item in items)
    return f"      <ul>\n{rows}\n      </ul>"


def _link_cards(
    links: list[dict[str, Any]],
    field_id: str | None = None,
    attributions: dict[str, FieldSourceAttribution] | None = None,
) -> str:
    if not links:
        return '<p class="note">暂未配置相关购票链接。</p>'
    cards = []
    for link in links:
        source_badge = _field_source_badge(field_id, attributions or {}) if field_id else ""
        cards.append(
            "        <article class=\"card\">"
            f"<h3><a href=\"{escape(str(link['url']), quote=True)}\">{escape(str(link['label']))}</a></h3>"
            f"<p>{escape(str(link['recommendation']))}</p>"
            f"<p><span class=\"badge\">{escape(_source_type_label(str(link['source_type'])))}</span> "
            f"<span class=\"badge\">风险：{escape(_risk_label(str(link['risk_level'])))}</span></p>"
            f"{source_badge}"
            "</article>"
        )
    return "      <div class=\"grid\">\n" + "\n".join(cards) + "\n      </div>"


def _citation_card(title: str, sources: list[dict[str, Any]]) -> str:
    if not sources:
        body = "<p>这个部分还没有登记来源支持。</p>"
    else:
        items = []
        for source in sources:
            items.append(
                f"<li>{escape(str(source['summary']))} "
                f"<a href=\"{escape(str(source['url']), quote=True)}\">"
                f"{escape(str(source['publisher']))}: {escape(str(source['title']))}</a></li>"
            )
        body = "<ul>" + "".join(items) + "</ul>"
    return f"        <article class=\"card\"><h3>{escape(title)}</h3>{body}</article>"


def _source_coverage_metrics(
    citation_groups: dict[str, list[dict[str, Any]]],
    sources: list[dict[str, Any]],
    traceability_items: list[EvidenceTraceabilityItem],
) -> dict[str, int]:
    source_backed_claims = sum(1 for item in traceability_items if item.status == "source_backed")
    internal_claims = sum(1 for item in traceability_items if item.status == "internal_estimate_not_source_backed")
    unknown_claims = sum(1 for item in traceability_items if item.status == "no_source_backed_data_found")
    covered_groups = sum(1 for group in citation_groups.values() if group)
    return {
        "source_count": len(sources),
        "covered_groups": covered_groups,
        "total_groups": len(citation_groups),
        "source_backed_claims": source_backed_claims,
        "internal_claims": internal_claims,
        "unknown_claims": unknown_claims,
    }


def _quantitative_analysis_section(
    coverage: dict[str, int],
    forecast: dict[str, Any],
    quote_analysis: dict[str, Any],
    attributions: dict[str, FieldSourceAttribution],
) -> str:
    latest_ticket = quote_analysis["latest_by_component"].get("ticket")
    latest_ticket_value = _format_currency(_float_or_none(latest_ticket.get("amount"))) if latest_ticket else "未知"
    pit_total = quote_analysis["latest_totals"]["pit"]
    sea_total = quote_analysis["latest_totals"]["sea"]
    return (
        '<div class="metrics">'
        f'<div class="metric"><span>已登记公开来源</span><strong>{coverage["source_count"]} 个</strong></div>'
        f'<div class="metric"><span>已覆盖来源分组</span><strong>{coverage["covered_groups"]}/{coverage["total_groups"]}</strong></div>'
        f'<div class="metric"><span>有来源支持的主张</span><strong>{coverage["source_backed_claims"]} 条</strong></div>'
        f'<div class="metric"><span>仍未知价格类主张</span><strong>{coverage["unknown_claims"]} 条</strong></div>'
        f'<div class="metric"><span>来源支撑门票报价</span><strong>{escape(latest_ticket_value)}</strong></div>'
        f'<div class="metric"><span>PIT 来源支撑总成本</span><strong>{escape(_format_currency(pit_total))}</strong></div>'
        f'<div class="metric"><span>SEA 来源支撑总成本</span><strong>{escape(_format_currency(sea_total))}</strong></div>'
        '</div>'
        '<h3>量化结论表</h3>'
        f'{_quantitative_facts_table(coverage, quote_analysis)}'
        '<h3>来源支撑美元预测区间</h3>'
        f'{_forecast_range_table(forecast)}'
        '<h3>触发规则与真实报价缺口</h3>'
        f'{_trigger_policy_table(attributions)}'
    )


def _quantitative_facts_table(
    coverage: dict[str, int],
    quote_analysis: dict[str, Any],
) -> str:
    latest_ticket = quote_analysis["latest_by_component"].get("ticket")
    latest_ticket_text = (
        f"{latest_ticket['quote_date']}：{_format_currency(_float_or_none(latest_ticket.get('amount')))}"
        if latest_ticket
        else "暂无来源支撑真实报价"
    )
    rows = [
        ("比赛日期", "2026-06-17", "公开来源支持", "FIFA / 公开新闻来源登记"),
        ("比赛场馆", "NRG Stadium / Houston Stadium", "公开来源支持", "FIFA 与休斯顿公开报道来源登记"),
        ("来源样本量", f'{coverage["source_count"]} 个来源', "来源注册表", "用于引用覆盖，不等于价格样本"),
        ("来源支撑报价行", f'{quote_analysis["quote_count"]} 条', "公开来源支撑", "来自已保存 WebEvidence 或本地 source-backed quote 文件"),
        ("最新来源支撑门票点", latest_ticket_text, "公开来源支撑" if latest_ticket else "未找到来源", "没有则保持未知"),
        ("PIT 真实全量预算", _format_currency(quote_analysis["latest_totals"]["pit"]), "公开来源支撑" if quote_analysis["latest_totals"]["pit"] else "未找到来源", "缺少组件则保持未知"),
        ("SEA 真实全量预算", _format_currency(quote_analysis["latest_totals"]["sea"]), "公开来源支撑" if quote_analysis["latest_totals"]["sea"] else "未找到来源", "缺少组件则保持未知"),
    ]
    return _simple_table(["指标", "数值", "状态", "说明"], rows)


def _reviewed_quote_analysis_section(
    analysis: dict[str, Any],
    quote_rows: list[dict[str, Any]],
) -> str:
    if analysis["quote_count"] == 0:
        return (
            '<p class="note unknown">'
            "目前没有可引用的来源支撑真实报价，因此不生成美元价格曲线。"
            "门票、PIT 机票、SEA 机票、酒店、本地交通和每位旅客总成本继续显示为未知；"
            "这比用未核验估算冒充真实报价更适合客户决策。"
            "</p>"
            + _simple_table(
                ["项目", "当前状态", "下一步"],
                [
                    ("门票真实含税费价格", "暂无来源支撑报价", "登记官方或可信市场页面的含税费报价"),
                    ("PIT 出发机票", "暂无来源支撑报价", "登记具体航班/日期/总价与来源链接"),
                    ("SEA 出发机票", "暂无来源支撑报价", "登记具体航班/日期/总价与来源链接"),
                    ("酒店人均分摊", "暂无来源支撑报价", "登记双床房总价、入住日期和分摊口径"),
                    ("本地交通人均分摊", "暂无来源支撑报价", "登记交通估价来源或实际报价"),
                    ("PIT / SEA 总成本曲线", "暂不生成", "集齐组件后自动显示美元总成本曲线"),
                ],
            )
        )

    pit_total = analysis["latest_totals"]["pit"]
    sea_total = analysis["latest_totals"]["sea"]
    return (
        '<p class="note">'
        "以下只展示带来源 URL 和 source_id 的 source-backed 报价行。"
        "每个金额都必须能追溯到公开来源；未登记的组件不会被自动补全。"
        "</p>"
        '<div class="metrics">'
        f'<div class="metric"><span>来源支撑真实报价行</span><strong>{analysis["quote_count"]} 条</strong></div>'
        f'<div class="metric"><span>PIT 来源支持总成本</span><strong>{escape(_format_currency(pit_total))}</strong></div>'
        f'<div class="metric"><span>SEA 来源支持总成本</span><strong>{escape(_format_currency(sea_total))}</strong></div>'
        f'<div class="metric"><span>已覆盖组件</span><strong>{len(analysis["components_present"])} / 5</strong></div>'
        "</div>"
        "<h3>最新组件报价</h3>"
        f"{_reviewed_quote_component_table(analysis)}"
        "<h3>报价来源明细</h3>"
        f"{_reviewed_quote_source_table(quote_rows)}"
        "<h3>美元成本曲线</h3>"
        f"{_reviewed_quote_dollar_chart(analysis)}"
    )


def _reviewed_quote_component_table(analysis: dict[str, Any]) -> str:
    rows: list[tuple[Any, ...]] = []
    for component in sorted(COMPONENT_LABELS):
        quote = analysis["latest_by_component"].get(component)
        if quote:
            source = (
                f'<a href="{escape(str(quote["source_url"]), quote=True)}">'
                f'<code>{escape(str(quote["source_id"]))}</code></a>'
            )
            rows.append(
                (
                    COMPONENT_LABELS[component],
                    _format_currency(float(quote["amount"])),
                    quote["quote_date"],
                    source,
                    quote.get("confidence", "n/a"),
                )
            )
        else:
            rows.append((COMPONENT_LABELS[component], "未知", "n/a", "无来源支撑报价", "n/a"))
    return _simple_table(["组件", "最新金额", "日期", "来源", "可信度"], rows, escape_cells=False)


def _reviewed_quote_source_table(quote_rows: list[dict[str, Any]]) -> str:
    rows = []
    for quote in sorted(quote_rows, key=lambda item: (item.get("quote_date", ""), item.get("component", ""))):
        component = str(quote.get("component", ""))
        source_url = str(quote.get("source_url", ""))
        rows.append(
            (
                quote.get("quote_date", ""),
                COMPONENT_LABELS.get(component, component),
                _format_currency(_float_or_none(quote.get("amount"))),
                f'<a href="{escape(source_url, quote=True)}">{escape(str(quote.get("source_label", source_url)))}</a>',
                f'<code>{escape(str(quote.get("source_id", "")))}</code>',
                quote.get("notes", ""),
            )
        )
    return _simple_table(["日期", "组件", "金额", "来源页面", "source_id", "来源说明"], rows, escape_cells=False)


def _reviewed_quote_dollar_chart(analysis: dict[str, Any]) -> str:
    timeline = analysis.get("timeline", [])
    series = {
        "门票": [(item["quote_date"], item.get("ticket")) for item in timeline if item.get("ticket") is not None],
        "PIT机票": [(item["quote_date"], item.get("pit_flight")) for item in timeline if item.get("pit_flight") is not None],
        "SEA机票": [(item["quote_date"], item.get("sea_flight")) for item in timeline if item.get("sea_flight") is not None],
        "酒店": [(item["quote_date"], item.get("hotel")) for item in timeline if item.get("hotel") is not None],
        "PIT总成本": [(item["quote_date"], item.get("pit_total")) for item in timeline if item.get("pit_total") is not None],
        "SEA总成本": [(item["quote_date"], item.get("sea_total")) for item in timeline if item.get("sea_total") is not None],
    }
    series = {name: points for name, points in series.items() if points}
    if not series:
        return '<p class="note unknown">来源支撑报价不足，暂时不能生成美元成本曲线。</p>'
    return (
        '<p class="section-lead">这张图只使用来源支撑报价行。缺失组件不会被补齐；总成本线只有在门票、对应机票、酒店和本地交通都存在时才显示。</p>'
        + _dollar_line_chart(series)
    )


def _dollar_line_chart(series: dict[str, list[tuple[str, float]]]) -> str:
    width = 860
    height = 360
    left = 68
    top = 30
    chart_width = 720
    chart_height = 245
    labels = sorted({date for points in series.values() for date, _ in points})
    values = [float(value) for points in series.values() for _, value in points]
    min_value = max(0, min(values) - 40)
    max_value = max(values) + 40
    if max_value == min_value:
        max_value += 1
    palette = ["#0f766e", "#2563eb", "#7c3aed", "#ca8a04", "#dc2626", "#0891b2"]
    x_step = chart_width / max(1, len(labels) - 1)

    def point(label: str, value: float) -> tuple[float, float]:
        x = left + labels.index(label) * x_step
        y = top + (max_value - value) / (max_value - min_value) * chart_height
        return x, y

    grid_lines = []
    for ratio in [0, 0.25, 0.5, 0.75, 1]:
        value = min_value + (max_value - min_value) * ratio
        y = top + (max_value - value) / (max_value - min_value) * chart_height
        grid_lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" stroke="#d8dee8"/>'
            f'<text x="12" y="{y + 4:.1f}" font-size="12" fill="#5d6878">${value:.0f}</text>'
        )

    paths = []
    legend = []
    for idx, (name, points) in enumerate(series.items()):
        color = palette[idx % len(palette)]
        if len(points) == 1:
            x, y = point(points[0][0], float(points[0][1]))
            paths.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
        else:
            d = " ".join(
                ("M" if point_index == 0 else "L")
                + f" {point(date, float(value))[0]:.1f} {point(date, float(value))[1]:.1f}"
                for point_index, (date, value) in enumerate(points)
            )
            paths.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3"/>')
            for date, value in points:
                x, y = point(date, float(value))
                paths.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
        legend_y = top + idx * 22
        legend.append(
            f'<rect x="650" y="{legend_y - 10}" width="12" height="12" fill="{color}"/>'
            f'<text x="668" y="{legend_y}" font-size="12" fill="#172033">{escape(name)}</text>'
        )

    x_labels = []
    for idx, label in enumerate(labels):
        x = left + idx * x_step
        x_labels.append(
            f'<text x="{x:.1f}" y="{top + chart_height + 26}" font-size="12" text-anchor="middle" fill="#5d6878">{escape(label)}</text>'
        )

    return (
        '<div class="card">'
        '<h3>来源支撑美元报价折线图</h3>'
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="来源支撑美元报价折线图">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>'
        + "".join(grid_lines)
        + f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#172033"/>'
        + f'<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#172033"/>'
        + "".join(paths)
        + "".join(x_labels)
        + "".join(legend)
        + "</svg></div>"
    )


def _forecast_range_table(forecast: dict[str, Any]) -> str:
    if not forecast.get("has_source_backed_quotes"):
        return (
            '<p class="note unknown">'
            "没有来源支撑的当前美元报价，因此不生成预测美元价格。"
            "本报告不会用示例数据或无来源估算替代真实报价。"
            "</p>"
        )
    rows: list[tuple[Any, ...]] = []
    for item in forecast["component_ranges"]:
        rows.append(
            (
                item["label"],
                _format_currency(item["current"]),
                f'{_format_currency(item["low"])} - {_format_currency(item["high"])}',
                item["basis"],
            )
        )
    for item in forecast["traveler_ranges"]:
        rows.append(
            (
                item["label"],
                _format_currency(item["current"]),
                f'{_format_currency(item["low"])} - {_format_currency(item["high"])}',
                item["basis"],
            )
        )
    return _simple_table(["项目", "当前来源支撑价格", "预测区间", "依据"], rows)


def _trigger_policy_table(attributions: dict[str, FieldSourceAttribution]) -> str:
    rows = [
        ("≤ $550", "如果是已验证官方转售", "立即购买", "内部触发策略，不是市场事实"),
        ("< $600", "如果 all-in 价格可信", "强烈考虑购买", "内部触发策略，不是市场事实"),
        ("$680-$700", "如果仍只有高价且挂票充足", "继续监控", "与当前报告未知项分开展示"),
        ("任意价格", "如果来源无法验证、转票方式不清、费用不透明", "不建议付款", "购票安全优先"),
    ]
    return _simple_table(["价格/条件", "适用前提", "动作", "来源状态"], rows) + _field_source_badge(
        "trigger_policy", attributions
    )


def _unknown_values_table() -> str:
    return _simple_table(["项目", "当前状态", "原因"], _still_unknowns())


def _simple_table(headers: list[str], rows: list[tuple[Any, ...]], escape_cells: bool = True) -> str:
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = []
        for cell in row:
            value = str(cell)
            cells.append(f"<td>{escape(value) if escape_cells else value}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def _traceability_table(items: list[EvidenceTraceabilityItem]) -> str:
    rows = []
    for item in items:
        class_name = {
            "source_backed": "source-backed",
            "internal_estimate_not_source_backed": "internal-estimate",
            "no_source_backed_data_found": "not-found",
        }.get(item.status, "")
        evidence = (
            "<br>".join(_markdown_link_to_html(evidence_item) for evidence_item in item.evidence)
            if item.evidence
            else escape(item.note)
        )
        rows.append(
            "<tr>"
            f"<td id=\"{escape(item.claim_id, quote=True)}\"><code>{escape(item.claim_id)}</code></td>"
            f"<td>{escape(item.claim)}</td>"
            f"<td class=\"{class_name}\">{escape(_status_label(item.status))}</td>"
            f"<td>{escape(item.evidence_group)}</td>"
            f"<td>{evidence}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>主张 ID</th><th>主张</th><th>状态</th>"
        "<th>来源组</th><th>证据 / 说明</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _source_registry_table(sources: list[dict[str, Any]]) -> str:
    rows = []
    for source in sources:
        tags = ", ".join(source.get("evidence_tags", []))
        rows.append(
            "<tr>"
            f"<td><a href=\"{escape(str(source['url']), quote=True)}\">{escape(str(source['title']))}</a></td>"
            f"<td>{escape(str(source['publisher']))}</td>"
            f"<td>{escape(str(source['source_type']))}</td>"
            f"<td>{escape(str(source.get('published_date', 'n/a')))}</td>"
            f"<td>{escape(tags)}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>来源</th><th>发布方</th><th>类型</th>"
        "<th>日期</th><th>用途</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _field_source_badge(
    field_id: str | None,
    attributions: dict[str, FieldSourceAttribution],
) -> str:
    if not field_id:
        return ""
    attribution = attributions.get(field_id)
    if not attribution:
        return ""
    class_name = _field_status_class(attribution.status)
    source_ids = ", ".join(attribution.source_ids) if attribution.source_ids else "无直接来源 ID"
    return (
        f'<span class="field-source" data-field-id="{escape(attribution.field_id, quote=True)}">'
        f'<span class="badge {class_name}">{escape(_field_status_label(attribution.status))}</span> '
        f'<strong>{escape(attribution.label)}</strong> · {escape(attribution.source_group)} · '
        f'<code>{escape(source_ids)}</code>'
        "</span>"
    )


def _field_attribution_table(
    attributions: dict[str, FieldSourceAttribution],
    sources: list[dict[str, Any]],
) -> str:
    source_by_id = {str(source["source_id"]): source for source in sources if source.get("source_id")}
    rows = []
    for field_id in sorted(attributions):
        attribution = attributions[field_id]
        rows.append(
            "<tr>"
            f"<td><code>{escape(attribution.field_id)}</code><br>{escape(attribution.label)}</td>"
            f"<td><span class=\"badge {_field_status_class(attribution.status)}\">{escape(_field_status_label(attribution.status))}</span></td>"
            f"<td>{escape(attribution.source_group)}</td>"
            f"<td>{_source_id_links(attribution.source_ids, source_by_id)}</td>"
            f"<td>{escape(attribution.note)}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>字段</th><th>状态</th><th>来源组</th>"
        "<th>来源 ID</th><th>说明</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _source_id_links(source_ids: list[str], source_by_id: dict[str, dict[str, Any]]) -> str:
    if not source_ids:
        return "无直接来源 ID"
    rendered = []
    for source_id in source_ids:
        source = source_by_id.get(source_id)
        if source:
            rendered.append(
                f'<a href="{escape(str(source["url"]), quote=True)}"><code>{escape(source_id)}</code></a>'
            )
        else:
            rendered.append(f"<code>{escape(source_id)}</code>")
    return "<br>".join(rendered)


def _field_status_class(status: str) -> str:
    return {
        "source_backed": "source-backed-badge",
        "model_inference": "model-inference-badge",
        "human_reviewed_data": "source-backed-data-badge",
        "internal_policy": "internal-policy-badge",
        "no_source_backed_data_found": "unknown-badge",
    }.get(status, "")


def _field_status_label(status: str) -> str:
    return {
        "source_backed": "公开来源支持",
        "model_inference": "模型推断",
        "human_reviewed_data": "来源支撑数据",
        "internal_policy": "内部策略",
        "no_source_backed_data_found": "未找到来源支持",
    }.get(status, status)


def _markdown_link_to_html(text: str) -> str:
    match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if not match:
        return escape(text)
    label, url = match.groups()
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def _live_data_status(
    preview: dict[str, Any] | None,
    reviewed_live_snapshots: list[dict[str, Any]] | None = None,
    attributions: dict[str, FieldSourceAttribution] | None = None,
) -> str:
    reviewed = reviewed_live_snapshots or []
    source_badge = _field_source_badge("reviewed_live_snapshots", attributions or {})
    if reviewed:
        return (
            '<p class="note">以下是来源支撑的 live/API snapshot。'
            "这些数据只有在显式审核后才会显示，并且与未解决的公开来源未知项分开展示。"
            f"{source_badge}</p>"
            + _reviewed_live_snapshot_table(reviewed)
        )
    if not preview:
        return (
            '<p class="note">本报告没有附加来源支撑 live/API 数据。'
            f"默认演示仍然是离线、可复现的流程。{source_badge}</p>"
        )
    rows = [
        f"<li>状态：{escape(str(preview.get('status', 'unknown')))}</li>",
        f"<li>Snapshot 数量：{escape(str(preview.get('snapshot_count', 0)))}</li>",
        f"<li>来源：{escape(str(preview.get('source', 'n/a')))}</li>",
    ]
    return source_badge + "<ul>" + "".join(rows) + "</ul>"


def _forecast_model(quote_analysis: dict[str, Any]) -> dict[str, Any]:
    """Return source-backed current prices and deterministic USD forecast ranges."""
    latest = quote_analysis.get("latest_by_component", {})
    component_ranges: list[dict[str, Any]] = []
    factors = {
        "ticket": (0.90, 1.05, "基于当前来源支撑票价；等待偏向只给区间，不保证降价。"),
        "pit_flight": (1.00, 1.18, "PIT 航班价格可能随出发临近上行；需继续看实际航空报价。"),
        "sea_flight": (1.02, 1.22, "SEA 航程更长，临近出发的票价上行风险更高。"),
        "hotel": (1.00, 1.15, "大型赛事酒店可订性不确定；预测只基于已登记酒店报价。"),
        "local_transport": (1.00, 1.30, "比赛日交通可能受拥堵和 surge pricing 影响。"),
    }
    for component in sorted(COMPONENT_LABELS):
        quote = latest.get(component)
        if not quote:
            continue
        current = _float_or_none(quote.get("amount"))
        if current is None:
            continue
        low_factor, high_factor, basis = factors[component]
        component_ranges.append(
            {
                "component": component,
                "label": COMPONENT_LABELS[component],
                "current": current,
                "low": round(current * low_factor, 2),
                "high": round(current * high_factor, 2),
                "basis": basis,
            }
        )

    traveler_ranges = _traveler_forecast_ranges(latest, factors)
    return {
        "has_source_backed_quotes": bool(component_ranges),
        "component_ranges": component_ranges,
        "traveler_ranges": traveler_ranges,
        "best_window": "只在真实来源报价齐全后给购买窗口；当前策略是继续收集来源报价，价格低于触发价再行动。",
        "pit_plan": "PIT 方案只使用 PIT 来源支撑航班报价、门票、酒店和本地交通报价计算；缺失项保持未知。",
        "sea_plan": "SEA 方案只使用 SEA 来源支撑航班报价、门票、酒店和本地交通报价计算；缺失项保持未知。",
    }


def _traveler_forecast_ranges(
    latest: dict[str, dict[str, Any]],
    factors: dict[str, tuple[float, float, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    traveler_components = {
        "PIT 旅客总成本": ["ticket", "pit_flight", "hotel", "local_transport"],
        "SEA 旅客总成本": ["ticket", "sea_flight", "hotel", "local_transport"],
    }
    for label, components in traveler_components.items():
        if any(component not in latest for component in components):
            continue
        current_values = [_float_or_none(latest[component].get("amount")) for component in components]
        if any(value is None for value in current_values):
            continue
        current = round(sum(value for value in current_values if value is not None), 2)
        low = round(
            sum(
                (_float_or_none(latest[component].get("amount")) or 0) * factors[component][0]
                for component in components
            ),
            2,
        )
        high = round(
            sum(
                (_float_or_none(latest[component].get("amount")) or 0) * factors[component][1]
                for component in components
            ),
            2,
        )
        rows.append(
            {
                "label": label,
                "current": current,
                "low": low,
                "high": high,
                "basis": "由已登记来源报价逐项相加；预测区间不补齐缺失组件。",
            }
        )
    return rows


def _forecast_section(
    forecast: dict[str, Any],
    attributions: dict[str, FieldSourceAttribution],
) -> str:
    unsupported_note = (
        "未找到可靠公开来源支持“美国黄牛手中约20%的票卖不出去”这个具体数字；"
        "因此该数字没有进入预测模型。"
    )
    return (
        '<p class="note">本节只展示美元价格和预测区间；如果没有来源支撑当前报价，就显示未知。</p>'
        f'<p class="note unknown">{unsupported_note}</p>'
        f"{_forecast_range_table(forecast)}"
        "<div class=\"grid\">"
        f"<article class=\"card\"><h3>推荐购买窗口</h3><p>{escape(str(forecast['best_window']))}</p>{_field_source_badge('trigger_policy', attributions)}</article>"
        f"<article class=\"card\"><h3>从 Pittsburgh / PIT 出发</h3><p>{escape(str(forecast['pit_plan']))}</p>{_field_source_badge('pit_recommendation', attributions)}</article>"
        f"<article class=\"card\"><h3>从 Seattle / SEA 出发</h3><p>{escape(str(forecast['sea_plan']))}</p>{_field_source_badge('sea_recommendation', attributions)}</article>"
        "</div>"
        "<p class=\"section-lead\">预测依据：已登记的来源支撑美元报价、Expedia 2026 Air Hacks 的国内机票窗口、KAYAK 2026 酒店预订趋势、AP 关于部分世界杯小组赛仍在售但价格偏高的报道，以及 Houston 当地住宿/交通报道。预测区间是决策辅助，不是保证价格。</p>"
    )


def _reviewed_live_snapshot_table(snapshots: list[dict[str, Any]]) -> str:
    rows = []
    for snapshot in snapshots:
        rows.append(
            "<tr>"
            f"<td>{escape(str(snapshot.get('snapshot_date', 'n/a')))}</td>"
            f"<td>{escape(str(snapshot.get('match_id', 'n/a')))}</td>"
            f"<td>${escape(_format_number(snapshot.get('lowest_price')))}</td>"
            f"<td>{escape(_format_number(snapshot.get('listings')))}</td>"
            f"<td>{escape(str(snapshot.get('source_type', 'n/a')))}</td>"
            f"<td>{escape(str(snapshot.get('notes', '')))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>日期</th><th>比赛</th><th>最低价</th>"
        "<th>挂票数</th><th>来源类型</th><th>审核说明</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _quote_dicts_to_objects(rows: list[dict[str, Any]]) -> list[ReviewedQuote]:
    quotes: list[ReviewedQuote] = []
    for row in rows:
        try:
            amount = float(row.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0.0
        quotes.append(
            ReviewedQuote(
                quote_date=str(row.get("quote_date", "")),
                match_id=str(row.get("match_id", "")),
                component=str(row.get("component", "")),
                amount=amount,
                currency=str(row.get("currency", "USD")),
                source_id=str(row.get("source_id", "")),
                source_url=str(row.get("source_url", "")),
                source_label=str(row.get("source_label", "")),
                origin=str(row.get("origin", "")),
                confidence=str(row.get("confidence", "medium")),
                notes=str(row.get("notes", "")),
            )
        )
    return quotes


def _format_currency(value: float | None) -> str:
    if value is None:
        return "未知"
    return f"${value:.0f}" if float(value).is_integer() else f"${value:.2f}"


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_number(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value if value is not None else "n/a")


def _source_type_label(source_type: str) -> str:
    return {
        "official_primary": "官方主票务",
        "official_resale": "官方转售",
        "official_info": "官方说明",
        "official_hospitality": "官方 hospitality",
        "secondary_market": "二级市场",
    }.get(source_type, source_type)


def _risk_label(risk: str) -> str:
    return {
        "low": "低",
        "medium": "中",
        "medium_high": "中高",
        "high": "高",
    }.get(risk, risk)


def _status_label(status: str) -> str:
    return {
        "source_backed": "有公开来源支持",
        "internal_estimate_not_source_backed": "内部模型估计，非公开来源事实",
        "no_source_backed_data_found": "未找到公开来源支持",
    }.get(status, status)
