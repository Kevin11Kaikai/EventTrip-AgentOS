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

## Phase 3 Status

Phase 3 adds deterministic market snapshot tracking without live APIs or scraping.

- Manual snapshots are stored in CSV under `data/market_snapshots/`.
- Trend analysis compares price and listing movement over time.
- SnapshotAgent writes one Markdown memory file into each run directory.
- MCP exposes snapshot listing and analysis tools.
- The manual snapshot CLI supports analysis, dry-run append, validation, duplicate protection, and explicit overwrite.
- Portfolio documentation now includes a demo walkthrough and short project summary.
- Phase 3.4 adds live data provider interfaces and mock provider skeletons only; real live integrations remain deferred.

## Recommended Next Step: Phase 4.1

Phase 4.1 should prepare the repository for a v0.1.0 release:

- Add a version tag such as `v0.1.0`.
- Review README rendering and documentation links on GitHub.
- Add a concise release note summarizing Phases 1-3.6.
- Include Phase 4.0 report polishing in the release note.
- Keep generated run directories and secrets out of Git.

## Later Phase 3 Work

- Add charts or Markdown tables for snapshot trend history.
- Add rolling-window trend analysis.
- Add stronger trigger policy tests for buy, wait, and monitor paths.
- Add provider adapter tests that verify live providers are not called by default.
- Add richer report-polishing fixtures that cover validation failure examples.

## Deferred Ideas

- Streamlit/FastAPI dashboard.
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
