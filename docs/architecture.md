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
Ticket Agent -> Flight Agent -> Hotel Agent -> Snapshot Agent -> Market Agent -> Budget Agent -> Risk Agent -> Report Agent
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

## Agent Responsibilities

| Agent | Input | Output | Purpose |
|---|---|---|---|
| Ticket Agent | mock ticket data | ticket recommendation | Analyze ticket price/listings |
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

The seed file is `data/market_snapshots/portugal_dr_congo_snapshots.csv`. It records deterministic mock snapshots for lowest ticket price, listings, Category 3 range, hotel availability proxy, flight price pressure, social buzz, and days before event.

`python -m eventtrip.snapshots_cli` provides safe manual commands to analyze snapshots, validate proposed rows, dry-run appends, and overwrite duplicate match/date rows only when explicitly requested. These manual snapshots feed the SnapshotAgent and final trend analysis.

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
- `get_flight_quotes`
- `get_hotel_quotes`
- `get_market_signals`
- `compute_aa_split`
- `compute_scalper_stress_index`
- `rank_budget_options`
- `get_market_snapshots`
- `analyze_market_snapshots`
- `append_market_snapshot`

## Data Provider Layer

Phase 3 introduces a provider interface for market snapshots:

- `MarketDataProvider`: protocol for reading and appending snapshots.
- `ManualSnapshotProvider`: CSV-backed provider under `data/market_snapshots/`.
- `MockLiveProvider`: deterministic placeholder for future provider adapters.

Phase 3.4 is intentionally skeleton-only. It defines the interface for future live integrations but does not call real APIs, scrape websites, or require API keys.

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

## Testing Strategy

- Markdown IO tests verify YAML frontmatter roundtrip behavior.
- Scoring tests verify deterministic scalper-stress behavior.
- Market snapshot tests verify CSV loading, append/save behavior, trend analysis, and snapshot scoring.
- Snapshot Agent tests verify Markdown output and YAML frontmatter.
- Snapshot CLI tests verify dry-run, append, duplicate handling, overwrite, and validation failures.
- Dashboard tests verify import-safe helpers, deterministic snapshot summaries, budget rows, and latest-run path detection.
- MCP server tests verify wrapper registration and direct mock outputs.
- MCP client validation tests verify guard behavior and helper parsing.
- Orchestrator smoke tests verify end-to-end report generation.
- Python 3.9 core demo compatibility is preserved where practical through `smiley_bot`.
- Python 3.11 official MCP SDK validation is captured in `examples/mcp_client_validation_output.txt`.
