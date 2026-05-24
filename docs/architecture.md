# Architecture

## System Goal

EventTrip-AgentOS is a cost-aware collaborative event travel planning system under market uncertainty. It helps travelers reason about ticket timing, flight windows, hotel value, shared costs, market trend signals, and practical booking risk before spending money.

The system is intentionally transparent: agents exchange Markdown files with YAML frontmatter, deterministic tools expose mock data, and the final report shows how each recommendation was produced.

## Environment Policy

- Phase 1 core demo remains compatible with Python 3.9+ where practical.
- `smiley_bot` with Python 3.9.23 remains the legacy/core compatibility environment.
- Phase 3+ development and official MCP workflows are recommended on Python 3.11 using the `eventtrip_mcp` environment.
- The official MCP SDK path requires Python 3.10+.

## Demo Scope

- Match: Portugal vs DR Congo only.
- Date: June 17, 2026.
- Venue: NRG Stadium / Houston Stadium.
- Travelers: one from PIT and one from SEA.
- Planning mode: budget-first, AA shared costs, and anti-scalper ticket timing.
- Germany vs Curacao is intentionally excluded from this demo.

## High-Level Workflow

```text
User Request
   |
   v
Orchestrator
   |
   v
Markdown Shared Memory / File Bus
   |
   v
Ticket Agent -> Ticket Link Agent -> Flight Agent -> Hotel Agent -> Snapshot Agent -> Market Agent -> Budget Agent -> Risk Agent -> Report Agent
   |
   v
Final Markdown Report
```

## Local Dashboard Layer

Phase 5 adds a local Streamlit dashboard as a presentation layer only.

```text
Local Dashboard
   |
   v
Snapshot CSV + trend analysis + deterministic report outputs
```

The dashboard reads local CSV snapshots, deterministic helper outputs, and latest generated report paths. It does not change source-of-truth calculations, does not call live APIs, does not scrape websites, and does not require OhMyGPT.

Phase 5.2 adds `docs/assets/dashboard_mockup.svg`, a static labeled mockup for GitHub presentation. It is not a fake screenshot.

## Agent Responsibilities

| Agent | Input | Output | Purpose |
|---|---|---|---|
| Ticket Agent | mock ticket data | ticket recommendation | Analyze ticket price/listings |
| Ticket Link Agent | local ticket link registry | official-first link guidance plus separated secondary-market candidates | Recommend manual ticket purchase paths |
| Flight Agent | mock flight data | flight window comparison | Compare same-day, one-night, two-night plans |
| Hotel Agent | mock hotel data | ranked shared hotel options | Evaluate two-bed shared lodging |
| Snapshot Agent | manual market snapshots | trend analysis | Track price/listing movement over time |
| Market Agent | ticket + market signals | Scalper Stress Index | Anti-scalper timing analysis |
| Budget Agent | ticket/flight/hotel estimates | ranked options | Cost-effectiveness ranking |
| Risk Agent | plan candidates | risk register | Mitigation planning |
| Report Agent | all prior outputs | final report | Human-readable decision support |

## Markdown Shared Memory

Each run creates a timestamped run directory. Every agent writes one Markdown file. YAML frontmatter provides machine-readable metadata, while the Markdown body provides human-readable reasoning.

Generated run outputs are ignored by Git except `runs/.gitkeep`.

Expected files:

```text
00_user_request.md
01_ticket_agent.md
01b_ticket_link_agent.md
02_flight_agent.md
03_hotel_agent.md
04_snapshot_agent.md
05_market_agent.md
06_budget_agent.md
07_risk_agent.md
08_final_report.md
```

## Market Snapshot Data Flow

Phase 3 adds a manual market snapshot tracker. Users can log point-in-time ticket and demand-proxy observations without scraping websites or calling live APIs.

```text
Manual Snapshot CLI
   |
   v
data/market_snapshots/*.csv
   |
   v
ManualSnapshotProvider
   |
   v
eventtrip.market_snapshots
   |
   v
Snapshot Agent and MCP snapshot tools
   |
   v
Final report trend section
```

Phase 6 adds a safe local import path for external snapshot files:

```text
External CSV/JSON snapshot file
   |
   v
SnapshotImportProvider
   |
   v
snapshots_cli import --dry-run / import
   |
   v
Manual snapshot CSV
   |
   v
SnapshotAgent / dashboard / MCP snapshot tools
```

This prepares provider adapters without enabling live APIs by default. External imports read only local CSV/JSON files, validate every row, and preserve the deterministic manual snapshot store.

Phase 8.0 adds a concrete opt-in JSON provider:

```text
Local JSON fixture or explicitly enabled HTTP JSON endpoint
   |
   v
OptInHttpJsonProvider
   |
   v
Validated MarketSnapshot objects
   |
   v
Preview CLI / reviewed import dry-run / explicit reviewed save / HTML live data status
```

Live HTTP requires `--live-http`, `EVENTTRIP_ENABLE_LIVE_PROVIDERS=true`, and an explicit host allowlist. The default orchestrator path remains offline.

Phase 8.1 adds the reviewed live-data import gate:

```text
Opt-in JSON preview
   |
   v
live_data_cli import --dry-run
   |
   v
Human review of source, match, date, price, listings, and notes
   |
   v
live_data_cli import --save --reviewed
   |
   v
Manual snapshot CSV
```

The import command refuses to write live/API-derived snapshots unless the user explicitly passes `--reviewed`. Duplicate match/date rows still require `--overwrite`.

The seed file is `data/market_snapshots/portugal_dr_congo_snapshots.csv`. It records deterministic mock snapshots for lowest ticket price, listings, Category 3 range, hotel availability proxy, flight price pressure, social buzz, and days before event.

`python -m eventtrip.snapshots_cli` provides safe manual commands to analyze snapshots, validate proposed rows, dry-run appends, and overwrite duplicate match/date rows only when explicitly requested. These manual snapshots feed the SnapshotAgent and final trend analysis.

## Web Evidence Collection Layer

Phase 7 adds an opt-in evidence collection layer. It is separate from the default demo and does not write directly to market snapshots.

```text
Public URL / Local HTML Fixture
   |
   v
WebCollector
   |
   v
Raw Evidence Cache
   |
   v
EvidenceExtractor
   |
   v
Structured Evidence JSON
   |
   v
Human Review / Snapshot Import
   |
   v
SnapshotAgent / Report / Dashboard
```

Local fixtures are the default path. Live HTTP requires explicit `--live-http`, uses one simple public GET, and does not execute JavaScript, manage sessions, bypass access controls, or automate purchases. MCP web evidence tools are preview-only and do not write evidence files or snapshot CSV rows.

Phase 7.1 adds reviewed evidence conversion:

```text
WebEvidence JSON
   |
   v
evidence_review_cli preview / convert --dry-run
   |
   v
Explicit human confirmation of missing snapshot fields
   |
   v
Optional --save to manual snapshot CSV
```

This keeps extracted web values as candidates until a human supplies the remaining demand-proxy fields and explicitly writes the reviewed snapshot.

## Source-Backed Public Report

Phase 7.3 adds a source-backed public report that avoids local planning estimates in the visible output.

```text
data/source_evidence.yaml
   |
   v
SourceBackedReportAgent
   |
   v
10_source_backed_final_report.md
11_source_backed_final_report.html
```

The deterministic `08_final_report.md` remains useful for regression and internal planning logic. The shareable source-backed report uses only registered public web, official, marketplace, and news sources. If airfare, hotel, ticket price, or total trip budget data is not source-backed, the report explicitly omits those claims.

Phase 7.4 groups source-backed citations into reader-facing categories:

- Match facts
- Ticket safety
- Houston logistics
- Unknown or not source-backed yet

The helper CLI can print or open the newest generated source-backed report:

```powershell
python -m eventtrip.source_report_cli latest
python -m eventtrip.source_report_cli latest --format html
python -m eventtrip.source_report_cli latest --format html --open
```

Phase 7.7 improves the public report's reading path:

- What To Do Next
- Recommended Official Purchase Paths
- What Is Still Unknown
- Citation Groups
- Source Registry

The usability sections are still source-backed only. They do not introduce unsupported ticket, flight, hotel, or budget prices.

Phase 7.8 adds a static HTML renderer:

```text
SourceBackedReportAgent
   |
   v
eventtrip/html_report.py
   |
   v
11_source_backed_final_report.html
```

The HTML report is a presentation artifact for client demos. It is generated from local structured evidence, uses inline CSS, and performs no live network calls.

Phase 7.9 keeps the HTML layer presentation-only while improving client readability with section navigation, decision summary cards, color-coded traceability statuses, and print styles. It still reads only local generated evidence and does not call live APIs.

Phase 7.5 adds a citation-summary bridge back into the internal deterministic report:

```text
data/source_evidence.yaml
   |
   v
ReportAgent
   |
   v
08_final_report.md Source-Backed Citation Summary
```

This is context only. It does not change computed costs, scores, option rankings, or ticket timing.

Phase 7.6 adds claim-level traceability:

```text
Internal report claim
   |
   v
Evidence Traceability Matrix
   |
   +-- source_backed
   +-- internal_estimate_not_source_backed
   +-- no_source_backed_data_found
```

The report is explicit when real public evidence is missing. Unsupported values remain marked as internal estimates or not source-backed; they are not disguised as live market data.

## Ticket Link Recommendation Layer

Phase 7.2 adds official-first ticket link recommendations without purchase automation.

```text
data/ticket_links.yaml
   |
   v
Ticket Link Agent / MCP link tools / Dashboard
   |
   v
Recommended Ticket Links section in final report
```

The layer recommends manual navigation links only. It does not open checkout, log in, handle payment, bypass CAPTCHA, or purchase tickets. FIFA official ticketing and FIFA official resale/exchange are prioritized before any other path. StubHub is represented only as a separated secondary-market candidate for manual monitoring and verification.

## Ticket Timing Fusion

The final report keeps the single-day MarketAgent signal and the multi-snapshot SnapshotAgent signal separate, then fuses them into one user-facing stance.

In the seed demo:

- MarketAgent single-day signal: `monitor`
- SnapshotAgent trend signal: `wait`
- Final report stance: `monitor_with_wait_bias` / "Monitor with wait bias"

This means travelers should not panic buy in the current $680-$700 range, but should keep active trigger-based monitoring in place.

## MCP Layer

- `eventtrip/mcp_server/tools.py` contains deterministic mock tool functions.
- `eventtrip/mcp_server/server.py` exposes those tools through MCP.
- Python 3.10+/3.11 uses the official FastMCP path when available.
- Python 3.9 uses fallback and guard behavior to preserve compatibility.
- Existing agents still call local Python functions directly; MCP exposure is an additional interface.

Current MCP tools:

- `get_ticket_market`
- `get_ticket_links`
- `recommend_ticket_links`
- `get_flight_quotes`
- `get_hotel_quotes`
- `get_market_signals`
- `compute_aa_split`
- `compute_scalper_stress_index`
- `rank_budget_options`
- `get_market_snapshots`
- `analyze_market_snapshots`
- `append_market_snapshot`
- `preview_snapshot_import`
- `preview_web_evidence_from_text`
- `preview_web_evidence_from_local_file`

## Data Provider Layer

Phase 3 introduces a provider interface for market snapshots:

- `MarketDataProvider`: protocol for reading and appending snapshots.
- `ManualSnapshotProvider`: CSV-backed provider under `data/market_snapshots/`.
- `MockLiveProvider`: deterministic placeholder for future provider adapters.
- `SnapshotImportProvider`: local CSV/JSON import provider for validated external snapshots.
- `get_provider`: deterministic provider registry for `manual_csv`, `mock_live`, and `import_file`.

Phase 6 keeps official API adapters deferred. `official_api` and `web_scraper` provider types raise clear errors instead of making network calls or scraping websites.

Future official API adapters should follow this disabled-by-default flow:

```text
Future Official API Providers (disabled by default)
   |
   v
Provider Adapters
   |
   v
Normalized snapshots/quotes
   |
   v
Existing agents, MCP tools, dashboard
```

Phase 6.1 adds disabled stubs for `official_ticket_api`, `official_hotel_api`, and `official_flight_api`. They do not import external API SDKs, do not read secrets unless methods are explicitly called, and do not make network requests. See `docs/api_adapter_design.md`.

## Skills Layer

- `ticket_timing_skill`: explains buy, wait, or monitor logic for event tickets.
- `market_intelligence_skill`: explains real-demand versus reseller-pressure reasoning.
- `hotel_value_skill`: explains two-bed lodging, access, cancellation, and price scoring.
- `aa_split_skill`: explains fair handling of individual and shared costs.
- `travel_risk_skill`: explains event-trip risks and mitigation rules.

## LLM Backend

Default mode is deterministic and does not call any LLM.

Optional OhMyGPT integration is OpenAI-compatible and used only for a separate report-polishing artifact.

```text
08_final_report.md
   |
   v
Invariant extraction and polishing prompt
   |
   v
OhMyGPT OpenAI-compatible API, only when --use-llm is passed
   |
   v
Required limitations and protected decision metadata repair
   |
   v
Invariant validation
   |
   v
09_final_report_polished.md, only if validation passes
```

`08_final_report.md` is always the deterministic source of truth. `09_final_report_polished.md` is optional presentation output. LLM usage must not change computed numbers, scores, option names, dates, trigger thresholds, limitations, or recommendations. Phase 4.2 adds a deterministic `Protected Decision Metadata` block so polished reports can remain readable while preserving machine-readable invariants such as `monitor_with_wait_bias`. If validation fails, the deterministic report remains intact and the polished report is rejected or clearly marked as failed.

`.env` is ignored by Git, and secrets are not committed.

## Data Layer

- `data/worldcup_houston_demo.yaml`: demo request, travelers, match, and constraints.
- `data/mock_tickets.yaml`: mock secondary-market ticket data.
- `data/mock_flights.yaml`: mock flight quotes for PIT and SEA.
- `data/mock_hotels.yaml`: mock shared two-bed hotel options.
- `data/mock_market_signals.yaml`: mock travel-demand and market-pressure signals.
- `data/market_snapshots/portugal_dr_congo_snapshots.csv`: manual ticket market snapshot history.
- `data/ticket_links.yaml`: official-first manual ticket link registry with separated secondary-market candidates.
- `data/source_evidence.yaml`: curated public web/news evidence registry for source-backed reports.
- `data/web_evidence/`: ignored local web evidence cache, with tracked `.gitkeep` placeholders.
- `examples/sample_ticket_market_page.html`: deterministic local HTML fixture for web evidence extraction.

## Testing Strategy

- Markdown IO tests verify YAML frontmatter roundtrip behavior.
- Scoring tests verify deterministic scalper-stress behavior.
- Market snapshot tests verify CSV loading, append/save behavior, trend analysis, and snapshot scoring.
- Snapshot Agent tests verify Markdown output and YAML frontmatter.
- Snapshot CLI tests verify dry-run, append, duplicate handling, overwrite, and validation failures.
- Dashboard tests verify import-safe helpers, deterministic snapshot summaries, budget rows, and latest-run path detection.
- Web collection tests verify local fixture collection, extraction heuristics, safety policy behavior, evidence store roundtrip, and CLI dry-run behavior.
- Evidence review tests verify candidate snapshot construction, dry-run behavior, duplicate protection, overwrite, and safe writes to temporary CSV files.
- Ticket link tests verify registry validation, official-first ordering, Ticket Link Agent output, MCP link tools, and dashboard rows.
- Source-backed report tests verify public-source registry validation and ensure the shareable report excludes local placeholder estimates.
- MCP server tests verify wrapper registration and direct mock outputs.
- MCP client validation tests verify guard behavior and helper parsing.
- Orchestrator smoke tests verify end-to-end report generation.
- Python 3.9 core demo compatibility is preserved where practical through `smiley_bot`.
- Python 3.11 official MCP SDK validation is captured in `examples/mcp_client_validation_output.txt`.
