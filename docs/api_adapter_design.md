# API Adapter Design

## Purpose

EventTrip-AgentOS currently uses deterministic mock data, manual snapshots, and local CSV/JSON imports. Future official APIs should be integrated behind provider adapters so the existing agents, MCP tools, dashboard, and tests can keep a stable contract.

## Non-Goals

- No scraping.
- No default live API calls.
- No required API keys for the demo.
- No production booking or purchase automation.

## Provider Principles

- Live providers must be disabled by default.
- API keys must come from environment variables.
- Provider outputs must normalize into `MarketSnapshot` or existing quote schemas.
- Tests should use mocks and fixtures, not live calls.
- Providers should fail closed when required keys are missing.
- Deterministic demo behavior must be preserved.

## Proposed Provider Types

- `official_ticket_api`: future official resale or ticket APIs.
- `official_hotel_api`: future hotel availability or quote APIs.
- `official_flight_api`: future flight quote APIs.
- `search_api_snapshot`: future search/API-assisted manual snapshot enrichment.

## Configuration

Potential future environment variables:

```env
EVENTTRIP_ENABLE_LIVE_PROVIDERS=false
EVENTTRIP_TICKET_API_KEY=
EVENTTRIP_HOTEL_API_KEY=
EVENTTRIP_FLIGHT_API_KEY=
```

These variables are proposed for future work. They are not required for the current deterministic demo.

## Safety Model

- Live providers should require explicit opt-in.
- No provider should run during tests unless mocked.
- Secrets must never be committed to Git.
- The default CLI, orchestrator, dashboard, and MCP validation must not make live calls.
- Provider failures should be explicit and actionable, not silent fallbacks to live behavior.

## Future Work

- Add one official API provider at a time.
- Keep manual snapshot import as the fallback.
- Add recorded fixtures for tests.
- Keep web scraping deferred unless a future phase explicitly accepts that risk.
