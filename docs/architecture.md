# Architecture

## System Goal

EventTrip-AgentOS is a cost-aware collaborative event travel planning system under market uncertainty. It is designed to help travelers reason about ticket timing, travel options, shared costs, and practical risk before spending money.

## Demo Scope

- Match: Portugal vs DR Congo only.
- Date: June 17, 2026.
- Venue: NRG Stadium / Houston Stadium.
- Travelers: one from PIT and one from SEA.
- Planning mode: budget-first, AA shared costs, and anti-scalper ticket timing.

## High-Level Workflow

```text
User Request
   ↓
Orchestrator
   ↓
Markdown Shared Memory / File Bus
   ↓
Ticket Agent → Flight Agent → Hotel Agent → Market Agent → Budget Agent → Risk Agent → Report Agent
   ↓
Final Markdown Report
```

## Agent Responsibilities

| Agent | Input | Output | Purpose |
|---|---|---|---|
| Ticket Agent | mock ticket data | ticket recommendation | Analyze ticket price/listings |
| Flight Agent | mock flight data | flight window comparison | Compare same-day, one-night, two-night plans |
| Hotel Agent | mock hotel data | ranked shared hotel options | Evaluate two-bed shared lodging |
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
04_market_agent.md
05_budget_agent.md
06_risk_agent.md
07_final_report.md
```

## MCP Layer

- `eventtrip/mcp_server/tools.py` contains deterministic mock tool functions.
- `eventtrip/mcp_server/server.py` exposes those tools through MCP.
- Python 3.10+/3.11 uses the official FastMCP path when available.
- Python 3.9 uses fallback and guard behavior to preserve compatibility.
- Existing agents still call local Python functions directly; MCP exposure is an additional interface.

## Skills Layer

- `ticket_timing_skill`: explains buy, wait, or monitor logic for event tickets.
- `market_intelligence_skill`: explains real-demand versus reseller-pressure reasoning.
- `hotel_value_skill`: explains two-bed lodging, access, cancellation, and price scoring.
- `aa_split_skill`: explains fair handling of individual and shared costs.
- `travel_risk_skill`: explains event-trip risks and mitigation rules.

## LLM Backend

Default mode is deterministic and does not call any LLM.

Optional OhMyGPT integration is OpenAI-compatible and used only for prose polishing. LLM usage must not change computed numbers, scores, option names, dates, or recommendations.

`.env` is ignored by Git, and secrets are not committed.

## Data Layer

- `data/worldcup_houston_demo.yaml`: demo request, travelers, match, and constraints.
- `data/mock_tickets.yaml`: mock secondary-market ticket data.
- `data/mock_flights.yaml`: mock flight quotes for PIT and SEA.
- `data/mock_hotels.yaml`: mock shared two-bed hotel options.
- `data/mock_market_signals.yaml`: mock travel-demand and market-pressure signals.

## Testing Strategy

- Markdown IO tests verify YAML frontmatter roundtrip behavior.
- Scoring tests verify deterministic scalper-stress behavior.
- MCP server tests verify wrapper registration and direct mock outputs.
- MCP client validation tests verify guard behavior and helper parsing.
- Orchestrator smoke tests verify end-to-end report generation.
- Python 3.9 core demo compatibility is preserved through `smiley_bot`.
- Python 3.11 official MCP SDK validation is captured in `examples/mcp_client_validation_output.txt`.

