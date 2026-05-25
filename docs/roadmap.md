# Roadmap

## Completed

- Phase 1: deterministic multi-agent workflow.
- Phase 1.1: GitHub-ready cleanup.
- Phase 2: MCP server wrapper.
- Phase 2.1: MCP client validation script.
- Phase 2.2: verified MCP SDK validation artifact.
- Phase 2.3: MCP validation documentation.
- Phase 2.4: architecture documentation.
- Phase 3.1: manual market snapshot tracker.
- Phase 3.2: trend-based ticket timing.
- Phase 3.3: data provider interface.
- Phase 3.4: optional live data integration skeleton.
- Phase 3.5: manual snapshot CLI.
- Phase 3.6: demo walkthrough and portfolio packaging.
- Phase 4.0: optional OhMyGPT report-polishing layer.
- Phase 4.1: release v0.1.0 preparation.
- Phase 4.2: OhMyGPT real polishing success hardening with protected metadata repair.
- Phase 5.0: lightweight local Streamlit dashboard.
- Phase 5.1: dashboard guide and release-page draft.
- Phase 6.0: safe local snapshot import/provider adapter foundation.
- Phase 5.2: dashboard mockup asset and README media polish.
- Phase 6.1: disabled-by-default official API adapter design and stubs.
- Phase 7.0: safe web collection layer, local fixture extraction, and preview-only MCP evidence tools.
- Phase 7.1: reviewed evidence to snapshot conversion with dry-run and duplicate protection.
- Phase 7.2: official-first ticket link recommendation layer.
- Phase 7.3: source-backed public report with official, marketplace, and news evidence registry.
- Phase 7.4: grouped source-backed citations and latest source-backed report CLI.
- Phase 7.5: optional source-backed citation summary in the internal deterministic report.
- Phase 7.6: claim-level evidence traceability matrix in the internal report.
- Phase 7.7: source-backed public report usability polish.
- Phase 7.8: static HTML source-backed report and claim anchors.
- Phase 7.9: client-facing HTML visual polish.
- Phase 8.0: opt-in HTTP JSON provider and live data preview CLI.
- Phase 8.1: reviewed live data import with `--save --reviewed` write gate.
- Phase 8.2: reviewed live/API snapshot display in source-backed HTML reports.
- Phase 8.3: Chinese HTML forecast charts and conservative web collection policy hardening.
- Phase 8.4: field-level source attribution in the Chinese source-backed HTML report.
- Phase 8.5: customer-facing HTML spacing, screenshot, mobile, and print polish.
- Phase 8.6: reviewed source intake workflow with citation group, source tag, and field attribution validation.
- Phase 8.7: source registry review packaging with Markdown/JSON validation summaries and PR checklist.
- Phase 8.7a: customer-facing HTML quantitative analysis tables for source counts, reviewed rows, pressure indices, trigger thresholds, and still-unknown real prices.

## Phase 3 Status

Phase 3 adds deterministic market snapshot tracking without live APIs or scraping.

- Manual snapshots are stored in CSV under `data/market_snapshots/`.
- Trend analysis compares price and listing movement over time.
- SnapshotAgent writes one Markdown memory file into each run directory.
- MCP exposes snapshot listing and analysis tools.
- The manual snapshot CLI supports analysis, dry-run append, validation, duplicate protection, and explicit overwrite.
- Portfolio documentation now includes a demo walkthrough and short project summary.
- Phase 3.4 adds live data provider interfaces and mock provider skeletons only; real live integrations remain deferred.

## Recommended Future Work

### Phase 5.3: Dashboard Screenshot Capture

- Capture a real local dashboard screenshot.
- Add it under `docs/assets/dashboard_screenshot.png` after checking it contains no secrets or private data.
- Keep the static mockup as the fallback asset.

### Phase 6.2: One Opt-In Official API Candidate

- Choose one official API candidate.
- Implement it behind explicit opt-in config.
- Use fixtures or recorded responses for tests.
- Prefer official APIs or safe search APIs.
- Keep web scraping deferred.
- Preserve manual snapshot mode as the default fallback.

### Phase 8.8: Delivery Handoff Package

- Bundle final demo commands, expected outputs, latest report paths, and source registry review packet commands into a concise handoff checklist.
- Keep the handoff package offline and deterministic.
- Do not introduce new source claims or live data behavior.

## Phase 5 Status

Phase 5.0 adds a local Streamlit dashboard for deterministic portfolio demos.

- Reads manual snapshot CSV data.
- Displays trend analysis and deterministic budget recommendations.
- Finds latest generated report paths under `runs/`.
- Does not call live APIs, scrape websites, or require OhMyGPT.
- Presentation-only: source-of-truth calculations remain in the CLI, agents, and deterministic report.

Phase 5.1 adds `docs/dashboard_guide.md`, `docs/assets/.gitkeep`, and a GitHub release-page draft at `docs/release_v0_1_0.md`.

Phase 5.2 adds `docs/assets/dashboard_mockup.svg` and README dashboard preview wiring.

## Phase 6 Status

Phase 6.0 adds a safe provider-adapter foundation without live API calls.

- `SnapshotImportProvider` imports local CSV/JSON snapshot files.
- `snapshots_cli import` supports dry-run, validation, duplicate protection, and overwrite.
- `get_provider` registers `manual_csv`, `mock_live`, and `import_file`.
- `official_api` and `web_scraper` remain intentionally unimplemented.
- MCP exposes `preview_snapshot_import` as read-only preview behavior.

Phase 6.1 adds `docs/api_adapter_design.md` and disabled provider stubs for `official_ticket_api`, `official_hotel_api`, and `official_flight_api`. These stubs fail closed and do not make network calls.

## Phase 7 Status

Phase 7.0 adds a safe web evidence layer without changing default demo behavior.

- `WebCollector` supports local HTML/text fixtures and explicit single-page public HTTP collection.
- `EvidenceExtractor` extracts heuristic candidate prices/listings for human review.
- `web_collect_cli` provides extract, dry-run collect, and explicit save commands.
- Generated web evidence cache files are ignored by Git.
- MCP exposes preview-only web evidence tools.
- Dashboard previews the local fixture only and performs no live HTTP.
- Phase 7.1 adds `evidence_review_cli` so reviewed evidence can become a manual snapshot only after explicit human-provided fields and `--save`.
- Phase 7.2 adds `data/ticket_links.yaml`, `TicketLinkAgent`, dashboard ticket link rows, MCP link tools, and final-report ticket link guidance. StubHub is included only as a separated secondary-market candidate, not as an official FIFA path.
- Phase 7.3 adds `data/source_evidence.yaml` and `SourceBackedReportAgent`, producing `10_source_backed_final_report.md` without local planning estimates.
- Phase 7.4 groups source-backed citations into Match facts, Ticket safety, Houston logistics, and Unknown/not source-backed sections, and adds `source_report_cli` for locating the latest public report.
- Phase 7.5 adds a `Source-Backed Citation Summary` to `08_final_report.md` while preserving deterministic costs and recommendations.
- Phase 7.6 adds an `Evidence Traceability Matrix` so unsupported values are explicitly marked as internal estimates or not source-backed.
- Phase 7.7 adds public-report usability sections: What To Do Next, Recommended Official Purchase Paths, and What Is Still Unknown.
- Phase 7.8 adds claim IDs/anchors and `11_source_backed_final_report.html` for client-facing presentation.
- Phase 7.9 polishes the static HTML report with navigation, summary cards, color-coded evidence statuses, and print-friendly CSS.
- Phase 8.0 adds `OptInHttpJsonProvider` and `live_data_cli preview` for fixture-based or explicitly enabled HTTP JSON snapshot previews.
- Phase 8.1 adds `live_data_cli import`, which validates opt-in live/API previews and writes them to snapshot CSV only with `--save --reviewed`.
- Phase 8.2 displays only `reviewed_live_data` snapshots in the source-backed HTML live-data table.
- Phase 8.3 switches the client HTML to Chinese, adds inline SVG cost-pressure forecast charts, adds PIT/SEA timing guidance, and hardens the web collection policy output.
- Phase 8.4 adds field-level source badges and a `字段级来源标注` audit table to the Chinese HTML report.
- Phase 8.5 improves customer-facing HTML spacing, screenshot readiness, responsive tables, and print layout without changing source-of-truth values.
- Phase 8.6 adds a reviewed source intake CLI and validator for new public-source metadata. It checks source tags, citation group mapping, duplicate source IDs, and field-level attribution coverage before saving to `data/source_evidence.yaml`.
- Phase 8.7 adds `source_review_cli` for exporting a Markdown or JSON source registry review packet with citation group coverage, source tag counts, field-level attribution coverage, validation errors, and a PR review checklist.
- Phase 8.7a adds a quantitative analysis panel to `11_source_backed_final_report.html`. It shows numbers the project can defend, and keeps unverifiable ticket, flight, hotel, transportation, and total-cost prices explicitly unknown.

## Later Phase 3 Work

- Add charts or Markdown tables for snapshot trend history.
- Add rolling-window trend analysis.
- Add stronger trigger policy tests for buy, wait, and monitor paths.
- Add provider adapter tests that verify live providers are not called by default.
- Add richer report-polishing fixtures that cover validation failure examples.

## Deferred Ideas

- Multi-event support.
- Concert/NBA/Olympics/F1 templates.
- Real ticket price forecasting.
- Optional live data integrations through official APIs or search APIs.
- Multi-model LLM comparison through OhMyGPT.
- Broad scraping remains deferred and should be avoided when official, manual, import, or reviewed evidence paths are sufficient.

## Engineering Principles

- Preserve deterministic demo behavior.
- Keep tests fast and offline.
- Do not commit secrets.
- Avoid breaking Python 3.9 core compatibility where practical.
- Use Python 3.11 and `eventtrip_mcp` for Phase 3+ development and official MCP workflows.
- Keep MCP integration optional and well-documented.
- Keep future live integrations behind provider adapters and MCP tools.
