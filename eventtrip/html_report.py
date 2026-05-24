"""Static HTML report rendering for source-backed public reports."""

from __future__ import annotations

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
) -> str:
    """Build a static, dependency-free HTML report for client-facing review."""
    primary_links = ticket_links.get("primary_links", [])
    info_links = ticket_links.get("info_links", [])
    all_ticket_links = [*primary_links, *info_links]
    sources = source_data.get("sources", [])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EventTrip-AgentOS Source-Backed Report</title>
  <style>
    :root {{
      --ink: #172033;
      --muted: #5d6878;
      --line: #d8dee8;
      --panel: #f7f9fc;
      --accent: #0f766e;
      --warn: #9a3412;
      --ok: #166534;
      --unknown: #6b21a8;
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
      background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
    }}
    main {{ padding: 28px clamp(20px, 5vw, 64px) 56px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(28px, 4vw, 44px); }}
    h2 {{ margin-top: 34px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }}
    h3 {{ margin-bottom: 8px; }}
    a {{ color: #0b5cad; }}
    .subtitle {{ color: var(--muted); max-width: 900px; }}
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
      background: #fff7ed;
    }}
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
    .source-backed {{ color: var(--ok); }}
    .internal-estimate {{ color: var(--warn); }}
    .not-found {{ color: var(--unknown); }}
    footer {{ color: var(--muted); font-size: 13px; margin-top: 36px; }}
  </style>
</head>
<body>
  <header>
    <h1>EventTrip-AgentOS Source-Backed Report</h1>
    <p class="subtitle">Client-facing HTML view built from curated public official/news evidence. It excludes local planning estimates for flight, hotel, ticket, and total budget values unless a public source is registered.</p>
    <div class="metrics">
      <div class="metric"><span>Event</span><strong>{escape(str(match["name"]))}</strong></div>
      <div class="metric"><span>Date</span><strong>{escape(str(match["date"]))}</strong></div>
      <div class="metric"><span>Venue</span><strong>{escape(str(match["venue"]))} / Houston Stadium</strong></div>
      <div class="metric"><span>Purchase stance</span><strong>Official-first</strong></div>
    </div>
  </header>
  <main>
    <section id="next-actions">
      <h2>What To Do Next</h2>
      {_html_list(_next_actions())}
    </section>

    <section id="official-paths">
      <h2>Recommended Official Purchase Paths</h2>
      <p class="note">Manual navigation only. EventTrip-AgentOS does not log in, bypass access controls, automate checkout, or purchase tickets.</p>
      {_link_cards(all_ticket_links)}
    </section>

    <section id="unknowns">
      <h2>What Is Still Unknown</h2>
      <p class="note unknown">These values are not source-backed yet. If they cannot be verified from public sources, they remain unknown rather than being filled with local estimates.</p>
      {_html_list(_still_unknowns())}
    </section>

    <section id="citations">
      <h2>Citation Groups</h2>
      <div class="grid">
        {_citation_card("Match facts", citation_groups.get("match_facts", []))}
        {_citation_card("Ticket safety", citation_groups.get("ticket_safety", []))}
        {_citation_card("Houston logistics", citation_groups.get("houston_logistics", []))}
      </div>
    </section>

    <section id="traceability">
      <h2>Evidence Traceability</h2>
      <p class="note">The matrix separates source-backed facts from internal estimates and values with no registered public source.</p>
      {_traceability_table(traceability_items)}
    </section>

    <section id="registry">
      <h2>Source Registry</h2>
      {_source_registry_table(sources)}
    </section>

    <footer>
      Generated by EventTrip-AgentOS. No live purchase, checkout automation, login bypass, CAPTCHA bypass, or payment action is performed.
    </footer>
  </main>
</body>
</html>
"""


def _next_actions() -> list[str]:
    return [
        "Start with FIFA official ticketing pages before considering any other ticket source.",
        "If resale is needed, use FIFA official resale/exchange information first.",
        "Verify match name, date, venue, seat category, quantity, transfer policy, refund policy, and all-in fees before paying.",
        "Treat social-media, messaging-app, and unofficial resale offers as high risk unless independently verified through official channels.",
        "Keep flight, hotel, and local-transport price claims out of this public report until a registered public source supports them.",
    ]


def _still_unknowns() -> list[str]:
    return [
        "Exact all-in ticket price for Portugal vs DR Congo.",
        "Verified official resale inventory level for this exact match.",
        "Traveler A airfare from PIT.",
        "Traveler B airfare from SEA.",
        "Shared two-bed hotel quote near NRG Stadium / Houston Stadium.",
        "Local transportation price estimate for match day.",
        "Total source-backed trip budget per traveler.",
    ]


def _html_list(items: list[str]) -> str:
    rows = "\n".join(f"        <li>{escape(item)}</li>" for item in items)
    return f"      <ul>\n{rows}\n      </ul>"


def _link_cards(links: list[dict[str, Any]]) -> str:
    if not links:
        return '<p class="note">No official purchase links are configured.</p>'
    cards = []
    for link in links:
        cards.append(
            "        <article class=\"card\">"
            f"<h3><a href=\"{escape(str(link['url']), quote=True)}\">{escape(str(link['label']))}</a></h3>"
            f"<p>{escape(str(link['recommendation']))}</p>"
            f"<p><span class=\"badge\">{escape(str(link['source_type']))}</span> "
            f"<span class=\"badge\">risk: {escape(str(link['risk_level']))}</span></p>"
            "</article>"
        )
    return "      <div class=\"grid\">\n" + "\n".join(cards) + "\n      </div>"


def _citation_card(title: str, sources: list[dict[str, Any]]) -> str:
    if not sources:
        body = "<p>No source-backed evidence registered for this area.</p>"
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
            "<br>".join(escape(evidence_item) for evidence_item in item.evidence)
            if item.evidence
            else escape(item.note)
        )
        rows.append(
            "<tr>"
            f"<td id=\"{escape(item.claim_id, quote=True)}\"><code>{escape(item.claim_id)}</code></td>"
            f"<td>{escape(item.claim)}</td>"
            f"<td class=\"{class_name}\">{escape(item.status)}</td>"
            f"<td>{escape(item.evidence_group)}</td>"
            f"<td>{evidence}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Claim ID</th><th>Claim</th><th>Status</th>"
        "<th>Group</th><th>Evidence / note</th></tr></thead><tbody>"
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
        "<table><thead><tr><th>Source</th><th>Publisher</th><th>Type</th>"
        "<th>Date</th><th>Use</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )
