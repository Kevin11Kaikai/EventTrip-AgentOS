# Project Summary

## One-Line Description

EventTrip-AgentOS is an MCP-enabled multi-agent system for budget-first collaborative event travel planning under ticket-market uncertainty.

## Technical Summary

EventTrip-AgentOS coordinates specialized Python agents through Markdown shared memory with YAML frontmatter. The system uses deterministic mock data, MCP-compatible tool wrappers, manual market snapshot tracking, and trend-based ticket timing to produce transparent travel decision reports for a Portugal vs DR Congo 2026 World Cup demo in Houston.

## Key Engineering Features

- Multi-agent orchestration
- Markdown shared memory
- MCP-compatible tool server
- MCP client validation
- Market snapshot tracker
- Trend-based ticket timing
- Snapshot CLI
- Local Streamlit dashboard
- CSV/JSON snapshot import provider
- Deterministic offline tests
- Optional LLM report polishing with invariant validation

## Resume Bullet Options

- Built an MCP-enabled multi-agent travel decision system that coordinates ticket, flight, hotel, market, budget, and risk agents through Markdown shared memory.
- Implemented deterministic anti-scalper ticket timing with manual market snapshots, trend analysis, and a safe CLI supporting dry-run and overwrite protection.
- Validated an offline MCP server and client workflow with Python tests, mock data providers, YAML frontmatter memory, reproducible final Markdown reports, and guarded optional LLM polishing.

## Suggested GitHub Description

MCP-enabled multi-agent event travel planner with Markdown memory, market snapshot tracking, and anti-scalper ticket timing.

## Suggested GitHub Topics

- ai-agents
- mcp
- multi-agent-system
- travel-planning
- decision-support
- python
- markdown-memory
- event-planning
- ticket-pricing

## v0.1.0 Release Summary

v0.1.0 includes the deterministic multi-agent workflow, Markdown shared memory, MCP server and client validation, manual market snapshot tracker, snapshot CLI, trend-based ticket timing, optional guarded OhMyGPT report polishing, local dashboard documentation, CSV/JSON snapshot import examples, and full portfolio documentation.

It intentionally excludes live travel APIs, web scraping, dashboard UI, committed secrets, and any required paid API dependency for the default demo.

This is portfolio-ready because the architecture, validation artifacts, tests, docs, and deterministic demo can be reviewed and run without external credentials.
