"""MCP server wrapper for EventTrip-AgentOS mock tools.

Phase 2 exposes deterministic mock tool functions through the official MCP
Python SDK when it is available. Phase 3 extends that MCP surface with manual
market snapshot tools. The multi-agent demo still calls the local Python
functions directly; this module is a separate MCP-compatible interface for
local clients.
"""

from __future__ import annotations

import sys
import json
from typing import Any

from eventtrip.mcp_server import tools as mock_tools

SERVER_NAME = "EventTrip-AgentOS MCP Server"
EXPECTED_TOOL_NAMES = [
    "get_ticket_market",
    "get_flight_quotes",
    "get_hotel_quotes",
    "get_market_signals",
    "compute_aa_split",
    "compute_scalper_stress_index",
    "rank_budget_options",
    "get_market_snapshots",
    "analyze_market_snapshots",
    "append_market_snapshot",
    "preview_snapshot_import",
]

try:  # pragma: no cover - depends on optional SDK availability
    from mcp.server.fastmcp import FastMCP

    MCP_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # pragma: no cover - exercised when SDK unavailable
    FastMCP = None  # type: ignore[assignment]
    MCP_IMPORT_ERROR = exc


mcp = FastMCP(SERVER_NAME) if FastMCP is not None else None


def _register_tool(func):
    """Register a wrapper with FastMCP when the SDK is installed."""
    if mcp is not None:
        return mcp.tool()(func)
    return func


@_register_tool
def get_ticket_market(match_id: str) -> dict:
    """Return mock secondary-market ticket data for one match ID."""
    return mock_tools.get_ticket_market(match_id)


@_register_tool
def get_flight_quotes(origin: str, destination: str, depart_date: str, return_date: str) -> list[dict]:
    """Return deterministic mock flight quotes for a traveler origin and date window."""
    return mock_tools.get_flight_quotes(origin, destination, depart_date, return_date)


@_register_tool
def get_hotel_quotes(city: str, checkin: str, checkout: str, beds: int = 2) -> list[dict]:
    """Return deterministic mock hotel quotes for a city, stay window, and bed count."""
    return mock_tools.get_hotel_quotes(city, checkin, checkout, beds)


@_register_tool
def get_market_signals(match_id: str) -> dict:
    """Return mock travel-demand and market-pressure signals for one match ID."""
    return mock_tools.get_market_signals(match_id)


@_register_tool
def compute_aa_split(total_cost: float, people: int = 2) -> dict:
    """Split a shared cost equally across the specified number of people."""
    return mock_tools.compute_aa_split(total_cost, people)


@_register_tool
def compute_scalper_stress_index(ticket_data: dict, market_data: dict | None = None) -> dict:
    """Compute the deterministic ticket-market Scalper Stress Index."""
    return mock_tools.compute_scalper_stress_index(ticket_data, market_data)


@_register_tool
def rank_budget_options(options: list[dict]) -> list[dict]:
    """Rank budget options using the existing deterministic scoring function."""
    return mock_tools.rank_budget_options(options)


@_register_tool
def get_market_snapshots(match_id: str) -> list[dict]:
    """Return deterministic manual market snapshots for one match ID."""
    return mock_tools.get_market_snapshots(match_id)


@_register_tool
def analyze_market_snapshots(match_id: str) -> dict:
    """Analyze manual market snapshots and return a deterministic trend recommendation."""
    return mock_tools.analyze_market_snapshots(match_id)


@_register_tool
def append_market_snapshot(snapshot: dict) -> dict:
    """Append a validated manual market snapshot to the local CSV store."""
    return mock_tools.append_market_snapshot(snapshot)


@_register_tool
def preview_snapshot_import(input_path: str, match_id: str | None = None) -> dict:
    """Preview a local CSV/JSON snapshot import without writing data."""
    return mock_tools.preview_snapshot_import(input_path, match_id)


TOOL_REGISTRY = {
    "get_ticket_market": get_ticket_market,
    "get_flight_quotes": get_flight_quotes,
    "get_hotel_quotes": get_hotel_quotes,
    "get_market_signals": get_market_signals,
    "compute_aa_split": compute_aa_split,
    "compute_scalper_stress_index": compute_scalper_stress_index,
    "rank_budget_options": rank_budget_options,
    "get_market_snapshots": get_market_snapshots,
    "analyze_market_snapshots": analyze_market_snapshots,
    "append_market_snapshot": append_market_snapshot,
    "preview_snapshot_import": preview_snapshot_import,
}


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "get_ticket_market": {
        "type": "object",
        "properties": {"match_id": {"type": "string"}},
        "required": ["match_id"],
    },
    "get_flight_quotes": {
        "type": "object",
        "properties": {
            "origin": {"type": "string"},
            "destination": {"type": "string"},
            "depart_date": {"type": "string"},
            "return_date": {"type": "string"},
        },
        "required": ["origin", "destination", "depart_date", "return_date"],
    },
    "get_hotel_quotes": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "checkin": {"type": "string"},
            "checkout": {"type": "string"},
            "beds": {"type": "integer", "default": 2},
        },
        "required": ["city", "checkin", "checkout"],
    },
    "get_market_signals": {
        "type": "object",
        "properties": {"match_id": {"type": "string"}},
        "required": ["match_id"],
    },
    "compute_aa_split": {
        "type": "object",
        "properties": {
            "total_cost": {"type": "number"},
            "people": {"type": "integer", "default": 2},
        },
        "required": ["total_cost"],
    },
    "compute_scalper_stress_index": {
        "type": "object",
        "properties": {
            "ticket_data": {"type": "object"},
            "market_data": {"type": ["object", "null"], "default": None},
        },
        "required": ["ticket_data"],
    },
    "rank_budget_options": {
        "type": "object",
        "properties": {"options": {"type": "array", "items": {"type": "object"}}},
        "required": ["options"],
    },
    "get_market_snapshots": {
        "type": "object",
        "properties": {"match_id": {"type": "string"}},
        "required": ["match_id"],
    },
    "analyze_market_snapshots": {
        "type": "object",
        "properties": {"match_id": {"type": "string"}},
        "required": ["match_id"],
    },
    "append_market_snapshot": {
        "type": "object",
        "properties": {"snapshot": {"type": "object"}},
        "required": ["snapshot"],
    },
    "preview_snapshot_import": {
        "type": "object",
        "properties": {
            "input_path": {"type": "string"},
            "match_id": {"type": ["string", "null"], "default": None},
        },
        "required": ["input_path"],
    },
}


def list_tools_payload() -> dict[str, Any]:
    """Return MCP-style tool metadata for the registered wrappers."""
    return {
        "tools": [
            {
                "name": name,
                "description": (TOOL_REGISTRY[name].__doc__ or "").strip(),
                "inputSchema": TOOL_SCHEMAS[name],
            }
            for name in EXPECTED_TOOL_NAMES
        ]
    }


def _jsonrpc_result(message_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _jsonrpc_error(message_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def _handle_jsonrpc_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    message_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        return _jsonrpc_result(
            message_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": "0.3.0"},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return _jsonrpc_result(message_id, list_tools_payload())
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if tool_name not in TOOL_REGISTRY:
            return _jsonrpc_error(message_id, -32602, f"Unknown tool: {tool_name}")
        try:
            tool_result = TOOL_REGISTRY[tool_name](**arguments)
        except Exception as exc:
            return _jsonrpc_error(message_id, -32000, f"Tool call failed: {exc}")
        return _jsonrpc_result(
            message_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_result, sort_keys=True),
                    }
                ],
                "isError": False,
            },
        )
    if message_id is None:
        return None
    return _jsonrpc_error(message_id, -32601, f"Unsupported method: {method}")


def run_stdio_fallback() -> None:
    """Run a minimal stdio JSON-RPC MCP-compatible server when SDK is unavailable."""
    for line in sys.stdin:
        raw = line.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            response = _handle_jsonrpc_message(message)
        except Exception as exc:
            response = _jsonrpc_error(None, -32700, f"Invalid JSON-RPC message: {exc}")
        if response is not None:
            print(json.dumps(response), flush=True)


def main() -> int:
    """Run the local MCP server over stdio."""
    if mcp is None:
        print(
            "WARNING: The official MCP Python SDK is unavailable; starting the "
            "minimal stdio fallback. Use Python 3.10+ with `pip install mcp` "
            "for the FastMCP SDK server.",
            file=sys.stderr,
        )
        if MCP_IMPORT_ERROR is not None:
            print(f"Import detail: {MCP_IMPORT_ERROR}", file=sys.stderr)
        run_stdio_fallback()
        return 0

    # FastMCP defaults to stdio transport for local MCP clients.
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
