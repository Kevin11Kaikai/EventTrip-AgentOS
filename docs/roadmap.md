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
- Web scraping remains deferred and should be avoided when official or manual data paths are sufficient.

## Engineering Principles

- Preserve deterministic demo behavior.
- Keep tests fast and offline.
- Do not commit secrets.
- Avoid breaking Python 3.9 core compatibility where practical.
- Use Python 3.11 and `eventtrip_mcp` for Phase 3+ development and official MCP workflows.
- Keep MCP integration optional and well-documented.
- Keep future live integrations behind provider adapters and MCP tools.
