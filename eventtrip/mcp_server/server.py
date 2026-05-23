"""Minimal Phase 1 MCP server placeholder.

The demo uses local mock MCP-style tools directly instead of starting a full
MCP server. Phase 2 can wrap the registered functions below with a real MCP
transport without changing agent logic.
"""

from __future__ import annotations

from eventtrip.mcp_server import tools


TOOL_REGISTRY = {
    "get_ticket_market": tools.get_ticket_market,
    "get_flight_quotes": tools.get_flight_quotes,
    "get_hotel_quotes": tools.get_hotel_quotes,
    "get_market_signals": tools.get_market_signals,
    "compute_aa_split": tools.compute_aa_split,
    "compute_scalper_stress_index": tools.compute_scalper_stress_index,
    "rank_budget_options": tools.rank_budget_options,
}

