# EventTrip-AgentOS

MCP-style, skill-based, file-memory multi-agent planning for collaborative event travel under market uncertainty.

EventTrip-AgentOS is a Phase 1 prototype for budget-first event-trip decision support. It coordinates specialized agents through Markdown shared memory, uses mock MCP-style tools, and produces a final Markdown report that explains ticket timing, flight tradeoffs, hotel value, market pressure, AA cost splitting, and travel risk.

The default demo is deterministic, offline, and does not call paid APIs. It does not require API keys and does not scrape websites.

## Quickstart

Run from Windows PowerShell in the repository root:

```powershell
conda activate smiley_bot
cd D:\others\Eventrip_agentos
pip install -r requirements.txt
python -m eventtrip.orchestrator --demo portugal_dr_congo_houston
pytest
```

## Requirements

- Python 3.9+
- Conda recommended
- Tested with the `smiley_bot` conda environment using Python 3.9.23

## Why This Project Exists

Most travel-agent demos generate generic itineraries. Real event travel often depends on harder decisions: when to buy tickets, whether visible scarcity is real, how to split shared costs, and whether a cheap plan creates too much risk.

This project focuses on collaborative event travel planning under market uncertainty.

## Demo Scenario

The first demo plans one match only:

- Match: Portugal vs DR Congo
- Date: June 17, 2026
- Venue: NRG Stadium / Houston Stadium
- City: Houston, Texas
- Traveler A origin: Pittsburgh, PA (PIT)
- Traveler B origin: Seattle, WA (SEA)

Germany vs Curacao is intentionally excluded from Phase 1.

## Architecture

```text
User Request
   |
   v
Markdown Shared Memory / File Bus
   |
   v
Ticket Agent -> Flight Agent -> Hotel Agent -> Market Agent -> Budget Agent -> Risk Agent -> Report Agent
   |
   v
Final Markdown Report
```

## Demo Output

Each run creates a timestamped directory:

```text
runs\portugal_dr_congo_houston_demo_YYYYMMDD_HHMMSS\
```

The final report is written to:

```text
runs\portugal_dr_congo_houston_demo_YYYYMMDD_HHMMSS\07_final_report.md
```

Example CLI summary:

```text
Final report: runs\portugal_dr_congo_houston_demo_YYYYMMDD_HHMMSS\07_final_report.md
Recommended option: Option A: One-night balanced plan
Estimated cost per traveler:
  Traveler A: $1120
  Traveler B: $1220
Ticket timing recommendation: monitor
```

## MCP-Style Tools

Phase 1 implements pure Python functions in `eventtrip/mcp_server/tools.py`. They look like MCP tools but use local mock data:

- `get_ticket_market`
- `get_flight_quotes`
- `get_hotel_quotes`
- `get_market_signals`
- `compute_aa_split`
- `compute_scalper_stress_index`
- `rank_budget_options`

Phase 2 can expose these same functions through a real MCP server without changing the agent contract.

## Phase 2: MCP Server

Phase 2 exposes the existing mock tools through a real MCP server wrapper. The default multi-agent demo still runs offline without MCP, and the existing agents continue to call local Python functions directly.

The MCP server is local and stdio-based by default. It does not start a public network service, does not call live travel APIs, does not scrape websites, and does not require secrets. All tools are deterministic and backed by mock data.

The official MCP Python SDK currently requires Python 3.10+. The core EventTrip-AgentOS demo remains Python 3.9+ and is tested in `smiley_bot` with Python 3.9.23. In Python 3.10+ with the `mcp` package installed, the server uses FastMCP. In Python 3.9, the same command starts a minimal stdio JSON-RPC fallback so local tool metadata and calls remain testable.

Run the server from Windows PowerShell:

```powershell
conda activate smiley_bot
cd D:\others\Eventrip_agentos
pip install -r requirements.txt
python -m eventtrip.mcp_server.server
```

Use a Python 3.10+ environment for full official SDK-based MCP client integration.

Exposed MCP tools:

- `get_ticket_market`
- `get_flight_quotes`
- `get_hotel_quotes`
- `get_market_signals`
- `compute_aa_split`
- `compute_scalper_stress_index`
- `rank_budget_options`

Example local MCP client config:

```text
examples/mcp_client_config.example.json
```

## Skills

Reusable skills live under `eventtrip/skills/*/SKILL.md`:

- Ticket timing
- Hotel value
- AA split rules
- Travel risk
- Market intelligence

They document the reasoning policies that agents apply in deterministic form.

## Markdown Shared Memory

Each run directory acts as a simple file bus. Every agent writes one Markdown file with YAML frontmatter so humans and downstream agents can both read it:

```yaml
---
agent: ticket_agent
status: completed
confidence: medium
created_at: 2026-01-01T12:00:00
next_agent: flight_agent
---
```

Deterministic filenames:

- `00_user_request.md`
- `01_ticket_agent.md`
- `02_flight_agent.md`
- `03_hotel_agent.md`
- `04_market_agent.md`
- `05_budget_agent.md`
- `06_risk_agent.md`
- `07_final_report.md`

## Final Report Contents

- Executive Summary
- Demo Assumptions
- Agent Workflow
- Portugal vs DR Congo Ticket Analysis
- Flight Analysis
- Hotel Analysis
- Market Timing / Anti-Scalper Analysis
- Budget Comparison Table
- Recommended Plan
- Practical Booking Rules
- Next Actions
- Limitations
- Optional LLM Backend Note

## Optional OhMyGPT Integration

The default demo uses deterministic mock outputs. If `--use-llm` is not passed, no LLM API is called.

OhMyGPT can be used as an optional OpenAI-compatible LLM backend for prose polishing only. The project calls the API endpoint, not the OhMyGPT dashboard UI. The dashboard is only for human account management, balance checking, API key creation, and billing.

Copy `.env.example` to `.env` and fill it with `.env` content:

```env
OHMYGPT_API_KEY=your_ohmygpt_api_key_here
OHMYGPT_BASE_URL=https://api.ohmygpt.com/v1
OHMYGPT_MODEL=gpt-4o-mini
```

Do not commit `.env`. It is ignored by `.gitignore`.

Then run:

```powershell
python -m eventtrip.orchestrator --demo portugal_dr_congo_houston --use-llm
```

If `--use-llm` is passed without `OHMYGPT_API_KEY`, the program exits with a clear error message. LLM polishing must never change computed numbers, scores, option names, dates, or recommendations.

## How This Differs From Generic Travel Agents

Generic travel agents generate itineraries. EventTrip-AgentOS reasons over ticket markets, hotel and flight demand proxies, shared costs, cancellation risk, and timing uncertainty. It is designed to answer whether the travelers should spend money now, wait, or hold flexible options.

## Repository Structure

```text
.
|-- README.md
|-- AGENTS.md
|-- requirements.txt
|-- .gitignore
|-- .env.example
|-- pyproject.toml
|-- eventtrip/
|   |-- orchestrator.py
|   |-- schemas.py
|   |-- markdown_io.py
|   |-- scoring.py
|   |-- llm_client.py
|   |-- agents/
|   |-- mcp_server/
|   `-- skills/
|-- data/
|-- runs/
|-- examples/
`-- tests/
```

## Future Roadmap

- Phase 2: real MCP server
- Phase 3: live APIs, browser search, and web scraping
- Phase 4: Streamlit or FastAPI dashboard
- Phase 5: time-series ticket price forecasting
- Phase 6: generalized event travel planner for concerts, NBA, Olympics, F1, and other events
