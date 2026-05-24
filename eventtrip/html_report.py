"""Static HTML report rendering for source-backed public reports."""

from __future__ import annotations

import re
from html import escape
from typing import Any

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
) -> str:
    """Build a static, dependency-free HTML report for client-facing review."""
    primary_links = ticket_links.get("primary_links", [])
    info_links = ticket_links.get("info_links", [])
    secondary_links = ticket_links.get("secondary_links", [])
    all_ticket_links = [*primary_links, *info_links]
    sources = source_data.get("sources", [])
    forecast = _forecast_model(reviewed_live_snapshots or [])

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
      --panel-strong: #eef6f5;
      --accent: #0f766e;
      --warn: #9a3412;
      --ok: #166534;
      --unknown: #6b21a8;
      --danger-bg: #fff7ed;
      --ok-bg: #eef8f1;
      --unknown-bg: #f5f3ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background: #ffffff;
      line-height: 1.5;
    }}
    header {{
      padding: 32px clamp(20px, 5vw, 64px);
      border-bottom: 1px solid var(--line);
      background: #f8fbfd;
    }}
    main {{ padding: 28px clamp(20px, 5vw, 64px) 56px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(28px, 4vw, 44px); }}
    h2 {{ margin-top: 34px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }}
    h3 {{ margin-bottom: 8px; }}
    a {{ color: #0b5cad; }}
    .subtitle {{ color: var(--muted); max-width: 900px; }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 14px;
      color: var(--accent);
      font-weight: 700;
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: .04em;
    }}
    .report-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 22px;
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
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 22px;
    }}
    .metric, .card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: #fff;
    }}
    .metric span {{ display: block; color: var(--muted); font-size: 13px; }}
    .metric strong {{ display: block; font-size: 20px; margin-top: 4px; }}
    .status-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin: 18px 0 8px;
    }}
    .status-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: var(--panel);
    }}
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
    }}
    .unknown {{
      border-left: 4px solid var(--warn);
      background: var(--danger-bg);
    }}
    .section-lead {{ max-width: 900px; color: var(--muted); }}
    ul {{ padding-left: 20px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: var(--panel); }}
    .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 9px;
      font-size: 12px;
      font-weight: 600;
      background: #eef2ff;
    }}
    .source-backed, .internal-estimate, .not-found {{
      font-weight: 700;
      border-radius: 6px;
    }}
    .source-backed {{ color: var(--ok); background: var(--ok-bg); }}
    .internal-estimate {{ color: var(--warn); background: var(--danger-bg); }}
    .not-found {{ color: var(--unknown); background: var(--unknown-bg); }}
    .print-note {{
      display: none;
      color: var(--muted);
      font-size: 12px;
    }}
    footer {{ color: var(--muted); font-size: 13px; margin-top: 36px; }}
    @media print {{
      body {{ font-size: 11pt; }}
      header, main {{ padding: 18px; }}
      .report-nav {{ display: none; }}
      .card, .metric, .status-card {{ break-inside: avoid; }}
      a {{ color: var(--ink); text-decoration: none; }}
      .print-note {{ display: block; }}
    }}
  </style>
</head>
<body>
  <header>
    <span class="eyebrow">静态客户展示报告</span>
    <h1>EventTrip-AgentOS 中文来源报告</h1>
    <p class="subtitle">这个 HTML 页面由已登记的官方、市场和新闻来源生成。没有公开来源支持的机票、酒店、门票和总预算数值不会被伪装成真实报价。</p>
    <div class="metrics">
      <div class="metric"><span>比赛</span><strong>{escape(str(match["name"]))}</strong></div>
      <div class="metric"><span>日期</span><strong>{escape(str(match["date"]))}</strong></div>
      <div class="metric"><span>场馆</span><strong>{escape(str(match["venue"]))} / Houston Stadium</strong></div>
      <div class="metric"><span>购票立场</span><strong>官方优先</strong></div>
    </div>
    <nav class="report-nav" aria-label="报告章节">
      <a href="#next-actions">下一步</a>
      <a href="#official-paths">官方路径</a>
      <a href="#secondary-market">二级市场</a>
      <a href="#unknowns">未知项</a>
      <a href="#live-data">审核数据</a>
      <a href="#forecast">趋势预测</a>
      <a href="#citations">来源分组</a>
      <a href="#traceability">证据追踪</a>
      <a href="#registry">来源清单</a>
    </nav>
  </header>
  <main>
    <section id="decision-summary">
      <h2>决策摘要</h2>
      <p class="section-lead">本页用于客户查看：有来源支持的事实、仍未知的价格、以及模型预测会分开展示。</p>
      <div class="status-strip">
        <div class="status-card"><strong>购票路径</strong>先看 FIFA 官方票务或 FIFA 官方转售/换票；StubHub 只作为二级市场监控。</div>
        <div class="status-card"><strong>未知价格</strong>精确门票、机票、酒店、交通和总预算还没有完整公开来源支持。</div>
        <div class="status-card"><strong>自动化边界</strong>不自动结账、不绕过登录、不处理 CAPTCHA、不执行付款。</div>
      </div>
    </section>

    <section id="next-actions">
      <h2>下一步怎么做</h2>
      <p class="section-lead">以下步骤只基于已登记的官方、市场和新闻来源。</p>
      {_html_list(_next_actions())}
    </section>

    <section id="official-paths">
      <h2>推荐官方购票路径</h2>
      <p class="note">这里只提供人工打开的链接。EventTrip-AgentOS 不登录、不绕过访问控制、不自动结账、不购票。</p>
      {_link_cards(all_ticket_links)}
    </section>

    <section id="secondary-market">
      <h2>二级市场候选渠道</h2>
      <p class="note unknown">StubHub 可以作为二级市场监控渠道，但它不是 FIFA 官方票务来源。付款前必须人工核验具体比赛、总价含税费、交付时间、FIFA 转票方式、退款政策和买家保护。</p>
      {_link_cards(secondary_links)}
    </section>

    <section id="unknowns">
      <h2>仍然未知的内容</h2>
      <p class="note unknown">这些数值还没有公开来源支持。如果查不到，就保持未知，不用本地估算填充。</p>
      {_html_list(_still_unknowns())}
    </section>

    <section id="live-data">
      <h2>人工审核 Live/API 数据状态</h2>
      {_live_data_status(live_snapshot_preview, reviewed_live_snapshots)}
    </section>

    <section id="forecast">
      <h2>价格趋势图与购买窗口预测</h2>
      {_forecast_section(forecast)}
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


def _still_unknowns() -> list[str]:
    return [
        "Portugal vs DR Congo 的精确含税费门票价格。",
        "Portugal vs DR Congo 在 StubHub 上的精确含税费价格。",
        "本场比赛官方转售库存数量。",
        "Traveler A 从 PIT 出发的真实机票报价。",
        "Traveler B 从 SEA 出发的真实机票报价。",
        "NRG Stadium / Houston Stadium 附近双床共享酒店真实报价。",
        "比赛日本地交通真实估价。",
        "每位旅客的完整来源支持总预算。",
    ]


def _html_list(items: list[str]) -> str:
    rows = "\n".join(f"        <li>{escape(item)}</li>" for item in items)
    return f"      <ul>\n{rows}\n      </ul>"


def _link_cards(links: list[dict[str, Any]]) -> str:
    if not links:
        return '<p class="note">暂未配置相关购票链接。</p>'
    cards = []
    for link in links:
        cards.append(
            "        <article class=\"card\">"
            f"<h3><a href=\"{escape(str(link['url']), quote=True)}\">{escape(str(link['label']))}</a></h3>"
            f"<p>{escape(str(link['recommendation']))}</p>"
            f"<p><span class=\"badge\">{escape(_source_type_label(str(link['source_type'])))}</span> "
            f"<span class=\"badge\">风险：{escape(_risk_label(str(link['risk_level'])))}</span></p>"
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


def _markdown_link_to_html(text: str) -> str:
    match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if not match:
        return escape(text)
    label, url = match.groups()
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def _live_data_status(
    preview: dict[str, Any] | None,
    reviewed_live_snapshots: list[dict[str, Any]] | None = None,
) -> str:
    reviewed = reviewed_live_snapshots or []
    if reviewed:
        return (
            '<p class="note">以下是已人工审核的 live/API snapshot。'
            "这些数据只有在显式审核后才会显示，并且与未解决的公开来源未知项分开。</p>"
            + _reviewed_live_snapshot_table(reviewed)
        )
    if not preview:
        return (
            '<p class="note">本报告没有附加已审核的 live/API 数据。'
            "默认演示仍然是离线、可复现的流程。</p>"
        )
    rows = [
        f"<li>状态：{escape(str(preview.get('status', 'unknown')))}</li>",
        f"<li>Snapshot 数量：{escape(str(preview.get('snapshot_count', 0)))}</li>",
        f"<li>来源：{escape(str(preview.get('source', 'n/a')))}</li>",
    ]
    return "<ul>" + "".join(rows) + "</ul>"


def _forecast_model(reviewed_live_snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    """Return source-backed trend guidance and model index data for the Chinese HTML report."""
    ticket_point = _latest_reviewed_ticket_point(reviewed_live_snapshots)
    labels = ["现在", "出发前45天", "出发前30天", "出发前15天", "比赛周"]
    series = {
        "球票压力指数": [100, 96, 92, 88, 84],
        "PIT机票压力指数": [100, 102, 106, 111, 122],
        "SEA机票压力指数": [100, 103, 108, 115, 128],
        "酒店压力指数": [100, 101, 103, 106, 113],
        "PIT总成本压力指数": [100, 99, 99, 100, 106],
        "SEA总成本压力指数": [100, 100, 101, 103, 111],
    }
    return {
        "labels": labels,
        "series": series,
        "latest_reviewed_ticket": ticket_point,
        "claim_20_percent_unsold_supported": False,
        "best_window": "先锁定可取消酒店；机票重点观察出发前15-30天；门票继续监控官方转售和二级市场，触发价到达再买。",
        "pit_plan": "PIT 出发建议采用 Option A：提前锁定可取消双床酒店，机票设置价格提醒，若出发前15-30天出现合理航班再购买；门票等官方转售或二级市场含税价触发。",
        "sea_plan": "SEA 出发航程更长、延误成本更高，仍建议 Option A；如果30-45天前出现时间可靠且价格合理的航班，可以比 PIT 更早锁定机票。",
    }


def _latest_reviewed_ticket_point(snapshots: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not snapshots:
        return None
    ordered = sorted(snapshots, key=lambda item: str(item.get("snapshot_date", "")))
    latest = ordered[-1]
    return {
        "date": latest.get("snapshot_date"),
        "lowest_price": latest.get("lowest_price"),
        "listings": latest.get("listings"),
        "notes": latest.get("notes", ""),
    }


def _forecast_section(forecast: dict[str, Any]) -> str:
    ticket = forecast.get("latest_reviewed_ticket")
    ticket_note = (
        f"最近一条已审核 live/API 门票数据：{escape(str(ticket['date']))}，"
        f"最低价 ${escape(_format_number(ticket['lowest_price']))}，"
        f"挂票数 {escape(_format_number(ticket['listings']))}。"
        if ticket
        else "目前没有已审核 live/API 门票价格，因此图表使用来源趋势做压力指数预测，不伪装成真实美元报价。"
    )
    unsupported_note = (
        "未找到可靠公开来源支持“美国黄牛手中约20%的票卖不出去”这个具体数字；"
        "因此该数字没有进入预测模型。"
    )
    return (
        f'<p class="note">{ticket_note}</p>'
        f'<p class="note unknown">{unsupported_note}</p>'
        f"{_line_chart(forecast['labels'], forecast['series'])}"
        "<div class=\"grid\">"
        f"<article class=\"card\"><h3>推荐购买窗口</h3><p>{escape(str(forecast['best_window']))}</p></article>"
        f"<article class=\"card\"><h3>从 Pittsburgh / PIT 出发</h3><p>{escape(str(forecast['pit_plan']))}</p></article>"
        f"<article class=\"card\"><h3>从 Seattle / SEA 出发</h3><p>{escape(str(forecast['sea_plan']))}</p></article>"
        "</div>"
        "<p class=\"section-lead\">预测依据：Expedia 2026 Air Hacks 的国内机票窗口、KAYAK 2026 酒店预订趋势、AP 关于部分世界杯小组赛仍在售但价格偏高的报道，以及 Houston 当地住宿/交通报道。这里展示的是模型压力指数，不是未核验的真实报价。</p>"
    )


def _line_chart(labels: list[str], series: dict[str, list[int]]) -> str:
    width = 860
    height = 360
    left = 58
    top = 30
    chart_width = 740
    chart_height = 250
    values = [value for points in series.values() for value in points]
    min_value = min(values)
    max_value = max(values)
    palette = ["#0f766e", "#2563eb", "#7c3aed", "#ca8a04", "#dc2626", "#0891b2"]
    x_step = chart_width / (len(labels) - 1)

    def point(index: int, value: int) -> tuple[float, float]:
        x = left + index * x_step
        y = top + (max_value - value) / (max_value - min_value) * chart_height
        return x, y

    grid_lines = []
    for value in [80, 90, 100, 110, 120, 130]:
        if value < min_value or value > max_value:
            continue
        y = top + (max_value - value) / (max_value - min_value) * chart_height
        grid_lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" stroke="#d8dee8"/>'
            f'<text x="12" y="{y + 4:.1f}" font-size="12" fill="#5d6878">{value}</text>'
        )

    paths = []
    legend = []
    for idx, (name, points) in enumerate(series.items()):
        color = palette[idx % len(palette)]
        d = " ".join(
            ("M" if point_index == 0 else "L") + f" {point(point_index, value)[0]:.1f} {point(point_index, value)[1]:.1f}"
            for point_index, value in enumerate(points)
        )
        paths.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3"/>')
        for point_index, value in enumerate(points):
            x, y = point(point_index, value)
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
        '<h3>成本压力指数折线图</h3>'
        '<p class="section-lead">指数 100 代表当前基准。高于 100 表示成本压力上升，低于 100 表示模型认为价格压力下降。没有审核报价时，不显示伪造美元价格。</p>'
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="成本压力指数折线图">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>'
        + "".join(grid_lines)
        + f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#172033"/>'
        + f'<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#172033"/>'
        + "".join(paths)
        + "".join(x_labels)
        + "".join(legend)
        + '</svg></div>'
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
