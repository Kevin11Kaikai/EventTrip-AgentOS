# Roadmap

## Completed

- Phase 1: deterministic multi-agent workflow.
- Phase 1.1: GitHub-ready cleanup.
- Phase 2: MCP server wrapper.
- Phase 2.1: MCP client validation script.
- Phase 2.2: verified MCP SDK validation artifact.
- Phase 2.3: MCP validation documentation.
- Phase 2.4: architecture documentation.

## Near-Term Next Step: Phase 3

### Phase 3.1: Manual Market Snapshot Tracker

- Allow users to manually log ticket market snapshots.
- Store snapshots in YAML or CSV.
- Avoid live scraping in the first Phase 3 step.

### Phase 3.2: Trend-Based Ticket Timing

- Analyze price and listing trends over time.
- Generate buy, wait, or monitor recommendations from historical snapshots.

### Phase 3.3: Data Provider Interface

- Define clean interfaces for future live APIs.
- Keep live integrations behind provider adapters and MCP tools.

### Phase 3.4: Optional Live Data Integrations

- Add only after the manual snapshot workflow is stable.
- Consider official APIs or search APIs.
- Avoid risky scraping when possible.

## Deferred Ideas

- Streamlit/FastAPI dashboard.
- Multi-event support.
- Concert/NBA/Olympics/F1 templates.
- Real ticket price forecasting.
- Multi-model LLM comparison through OhMyGPT.

## Engineering Principles

- Preserve deterministic demo.
- Keep tests fast and offline.
- Do not commit secrets.
- Avoid breaking Python 3.9 core compatibility.
- Keep MCP integration optional and well-documented.

