# MCP Validation

## Purpose

EventTrip-AgentOS exposes deterministic mock travel-planning tools through an MCP server. Phase 2.2 verified that a Python MCP client can start the local server over stdio, list available tools, and call selected tools with deterministic mock inputs. Phase 3 extends the same MCP surface with market snapshot tools.

## Compatibility Model

- The core Phase 1 demo supports Python 3.9+ where practical.
- `smiley_bot` uses Python 3.9.23 and remains the legacy/core compatibility environment.
- Phase 3+ development and official MCP workflows are recommended on Python 3.11 using the `eventtrip_mcp` environment.
- The official MCP Python SDK requires Python 3.10+.
- Full official MCP SDK validation is done in a separate Python 3.11 environment named `eventtrip_mcp`.
- The Python 3.9 fallback exists only to keep local tests and metadata validation stable. It is not a replacement for official MCP SDK validation.

## Validation Environments

| Environment | Python | Purpose | Status |
|---|---:|---|---|
| smiley_bot | 3.9.23 | Core demo, tests, fallback guard | Verified |
| eventtrip_mcp | 3.11.15 | Official MCP SDK validation and Phase 3 development | Verified |

## Exposed MCP Tools

- `get_ticket_market`: returns deterministic mock ticket market data for one match.
- `get_flight_quotes`: returns mock flight quotes for one origin and date window.
- `get_hotel_quotes`: returns mock hotel quotes for a city, stay window, and bed count.
- `get_market_signals`: returns mock demand and market-pressure signals.
- `compute_aa_split`: splits a shared cost equally across travelers.
- `compute_scalper_stress_index`: computes the deterministic anti-scalper market timing score.
- `rank_budget_options`: ranks budget options with the existing scoring logic.
- `get_market_snapshots`: returns manual market snapshots for one match.
- `analyze_market_snapshots`: analyzes historical snapshots and returns a trend recommendation.
- `append_market_snapshot`: appends one validated manual snapshot to the local CSV store.

## Validation Workflow

Official MCP SDK validation:

```powershell
conda create -n eventtrip_mcp python=3.11 -y
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
pip install -r requirements.txt
python scripts\validate_mcp_client.py
```

Python 3.9 guard workflow:

```powershell
conda activate smiley_bot
cd D:\others\Eventrip_agentos
python scripts\validate_mcp_client.py
```

In Python 3.9, the validation script should exit cleanly with a message that full official MCP SDK validation requires Python 3.10+.

## Verified Results

- The MCP client launched the local server through stdio.
- The client listed 10 tools.
- The client called:
  - `get_ticket_market`
  - `compute_scalper_stress_index`
  - `get_hotel_quotes`
  - `get_market_snapshots`
  - `analyze_market_snapshots`
- Outputs matched deterministic mock data.
- Sample output is stored at `examples/mcp_client_validation_output.txt`.

## What This Does Not Do

- No live APIs.
- No scraping.
- No paid travel APIs.
- No OhMyGPT call.
- No dashboard automation.
- No real ticket, hotel, or flight purchase.

## Troubleshooting

- If `mcp` fails to install, confirm the active Python version is 3.10+.
- If PowerShell cannot find `conda`, initialize conda for PowerShell or use Anaconda Prompt.
- If validation uses the guard path, confirm the active environment is Python 3.11.
- If stdio validation fails, run `pytest` and inspect MCP server import errors.
- If snapshot validation returns no data, confirm `data/market_snapshots/portugal_dr_congo_snapshots.csv` exists.
