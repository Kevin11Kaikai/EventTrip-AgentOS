# Demo Walkthrough

## What This Project Solves

EventTrip-AgentOS helps two travelers plan a cost-aware event trip under ticket-market uncertainty. It is not a generic itinerary generator: it reasons about tickets, flights, hotels, shared AA costs, resale-market pressure, and the timing decision of whether to buy, wait, or monitor.

The project is built as a deterministic, offline, multi-agent workflow so the reasoning is inspectable and repeatable.

## Demo Scenario

- Event: Portugal vs DR Congo
- Date: June 17, 2026
- Venue: NRG Stadium / Houston Stadium, Houston
- Traveler A: Pittsburgh / PIT
- Traveler B: Seattle / SEA
- Constraint: budget-first, shared two-bed hotel if needed, AA shared costs, avoid panic buying from secondary sellers

## Why This Is Different From a Generic Travel Agent

Generic travel agents generate itineraries. EventTrip-AgentOS performs decision support under market uncertainty.

It combines travel planning with anti-scalper market reasoning, tracks price/listing trends over time using manual snapshots, and exposes deterministic tools through MCP. The output is a decision report, not just a schedule.

## Architecture In One Minute

```text
User Request
   ↓
Orchestrator
   ↓
Markdown Shared Memory / File Bus
   ↓
Ticket → Flight → Hotel → Snapshot → Market → Budget → Risk → Report
   ↓
Final Report
```

Each agent writes one Markdown file into the run directory. YAML frontmatter stores machine-readable metadata such as agent name, status, confidence, and next agent. The Markdown body stores human-readable reasoning so the run directory works as both shared memory and an audit trail.

## Agent Pipeline

- `TicketAgent`: reads mock ticket data and reviews price, listings, Category 3 range, and initial buy/monitor posture.
- `FlightAgent`: compares same-day, one-night, and two-night flight windows for PIT and SEA travelers.
- `HotelAgent`: evaluates shared two-bed hotel options by cost, access, cancellation policy, and rating.
- `SnapshotAgent`: analyzes manual ticket market snapshots and trend direction.
- `MarketAgent`: computes the single-day Scalper Stress Index from ticket and demand-proxy signals.
- `BudgetAgent`: ranks trip options by total cost, schedule risk, comfort, and shared-cost efficiency.
- `RiskAgent`: flags resale, lodging, delay, rideshare, shared-room, and cancellation risks.
- `ReportAgent`: fuses structured agent outputs into a final Markdown decision report.

## Market Snapshot Tracker

Manual snapshots are stored in `data/market_snapshots/portugal_dr_congo_snapshots.csv`.

Snapshot fields include ticket price, listings, Category 3 range, hotel availability proxy, flight pressure, social buzz, days before event, source type, and notes. SnapshotAgent analyzes whether prices and listings are moving in a way that suggests reseller pressure.

The current seed trend supports `monitor_with_wait_bias` / "Monitor with wait bias": the single-day signal says monitor, while the multi-snapshot trend shows falling prices and rising listings, which supports disciplined waiting/monitoring rather than panic buying.

Example commands:

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
python -m eventtrip.snapshots_cli analyze --match portugal_dr_congo
python -m eventtrip.snapshots_cli append --match portugal_dr_congo --snapshot-date 2026-05-22 --lowest-price 650 --listings 360 --category-3-low 400 --category-3-high 750 --hotel-availability-score 0.50 --flight-price-pressure 0.55 --social-buzz-score 0.86 --days-before-event 26 --source-type manual --notes "Manual check" --dry-run
```

Use `--dry-run` before writing. Use `--overwrite` only when intentionally replacing the same match/date.

## MCP Validation

The project exposes deterministic tools through an MCP server. Official MCP SDK validation was run in `eventtrip_mcp` / Python 3.11.15. The validation listed tools and called selected tools through stdio.

References:

- `docs/mcp_validation.md`
- `examples/mcp_client_validation_output.txt`

## Running The Main Demo

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
python -m eventtrip.orchestrator --demo portugal_dr_congo_houston
```

The final report appears in a timestamped `runs/` directory. Generated run directories are ignored by Git except for `runs/.gitkeep`.

## Expected Decision Output

- Travel plan: Option A: One-night balanced plan
- Traveler A estimated cost: $1120
- Traveler B estimated cost: $1220
- Ticket timing: Monitor with wait bias
- Snapshot trend: falling prices and rising listings support disciplined waiting/monitoring rather than panic buying

## Example Final Report Sections

- Executive Summary
- Ticket Trigger Policy
- Market Snapshot Trend Analysis
- Budget Comparison Table
- Risk Register
- Mitigations

## Engineering Highlights

- Multi-agent orchestration
- Markdown shared memory / file bus
- YAML frontmatter metadata
- MCP server wrapper
- Official MCP client validation
- Manual snapshot tracker
- Trend-based ticket timing
- Safe CLI with dry-run and overwrite protection
- Deterministic offline tests
- Optional OhMyGPT LLM backend reserved for future report polishing

## Limitations

- No real ticket, hotel, or flight APIs yet.
- No scraping.
- No dashboard UI.
- Manual snapshots are mock/manual inputs.
- Not financial, legal, or travel advice.

## Next Step

Next planned phase: optional OhMyGPT report-polishing layer that generates a separate polished report while preserving deterministic source-of-truth numbers.
