"""Validate the EventTrip-AgentOS MCP server with an MCP client.

This script is intentionally optional for the Python 3.9 default demo path.
The official MCP Python SDK requires Python 3.10+, so Python 3.9 exits cleanly
with instructions instead of failing cryptically.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_MODULE = "eventtrip.mcp_server.server"
EXPECTED_TOOL_NAMES = {
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
    "preview_web_evidence_from_text",
    "preview_web_evidence_from_local_file",
}
PYTHON_39_MESSAGE = (
    "Full MCP client validation requires Python 3.10+ because the official MCP SDK "
    "requires Python 3.10+. The Phase 1 demo and fallback server remain supported "
    "in Python 3.9."
)


def supports_official_mcp_sdk(version_info: Optional[Sequence[int]] = None) -> bool:
    """Return whether the Python version can install the official MCP SDK."""
    version = tuple(version_info or sys.version_info)
    return version >= (3, 10)


def sdk_is_available() -> bool:
    """Return whether the official MCP SDK import path is installed."""
    return importlib.util.find_spec("mcp") is not None


def environment_error_message(
    version_info: Optional[Sequence[int]] = None,
    sdk_available: Optional[bool] = None,
) -> Optional[str]:
    """Return a human-readable skip reason, or None when validation can run."""
    if not supports_official_mcp_sdk(version_info):
        return PYTHON_39_MESSAGE
    available = sdk_is_available() if sdk_available is None else sdk_available
    if not available:
        return (
            "The official MCP SDK is not installed. Use Python 3.10+ and run "
            "`pip install -r requirements.txt`, then retry `python scripts\\validate_mcp_client.py`."
        )
    return None


def extract_tool_payload(result: Any) -> Any:
    """Extract a JSON payload from an MCP call_tool result."""
    if isinstance(result, dict):
        if "structuredContent" in result:
            structured_content = result["structuredContent"]
            if isinstance(structured_content, dict) and set(structured_content) == {"result"}:
                return structured_content["result"]
            return structured_content
        if "structured_content" in result:
            structured_content = result["structured_content"]
            if isinstance(structured_content, dict) and set(structured_content) == {"result"}:
                return structured_content["result"]
            return structured_content
        content = result.get("content")
    else:
        structured = getattr(result, "structured_content", None) or getattr(
            result, "structuredContent", None
        )
        if structured is not None:
            if isinstance(structured, dict) and set(structured) == {"result"}:
                return structured["result"]
            return structured
        content = getattr(result, "content", None)

    if not content:
        raise ValueError("MCP tool result did not include content.")

    first = content[0]
    if isinstance(first, dict):
        text = first.get("text")
    else:
        text = getattr(first, "text", None)
    if text is None:
        raise ValueError("MCP tool result content did not include text.")

    return json.loads(text)


def tool_names_from_list_result(result: Any) -> set[str]:
    """Extract tool names from an MCP list_tools result."""
    tools = result.get("tools") if isinstance(result, dict) else getattr(result, "tools", [])
    names = set()
    for tool in tools:
        names.add(tool.get("name") if isinstance(tool, dict) else getattr(tool, "name"))
    return names


def _assert_json_serializable(value: Any) -> None:
    json.dumps(value, sort_keys=True)


def environment_label() -> str:
    """Return a concise environment label for validation output."""
    executable_parts = {part.lower() for part in Path(sys.executable).parts}
    if "eventtrip_mcp" in executable_parts:
        return "eventtrip_mcp"
    conda_env = os.getenv("CONDA_DEFAULT_ENV")
    if conda_env:
        return conda_env
    return Path(sys.executable).parent.name


async def run_validation() -> int:
    """Run MCP client validation against a local stdio server."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", SERVER_MODULE],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            list_result = await session.list_tools()
            tool_names = tool_names_from_list_result(list_result)
            missing = EXPECTED_TOOL_NAMES - tool_names
            if missing:
                raise AssertionError(f"Missing MCP tools: {sorted(missing)}")

            ticket = extract_tool_payload(
                await session.call_tool("get_ticket_market", {"match_id": "portugal_dr_congo"})
            )
            _assert_json_serializable(ticket)
            assert ticket["lowest_price"] == 700
            assert ticket["listings"] == 300
            assert ticket["demand_level"] == "high"

            stress = extract_tool_payload(
                await session.call_tool(
                    "compute_scalper_stress_index",
                    {
                        "ticket_data": {
                            "lowest_price": 700,
                            "listings": 300,
                            "price_trend_7d": 0.02,
                        },
                        "market_data": {
                            "hotel_availability_score": 0.55,
                            "flight_price_pressure": 0.50,
                            "social_buzz_score": 0.85,
                            "days_before_event": 183,
                        },
                    },
                )
            )
            _assert_json_serializable(stress)
            assert 0 <= stress["score"] <= 100
            assert stress["interpretation"]
            assert stress["explanation"]

            hotels = extract_tool_payload(
                await session.call_tool(
                    "get_hotel_quotes",
                    {
                        "city": "Houston",
                        "checkin": "2026-06-16",
                        "checkout": "2026-06-17",
                        "beds": 2,
                    },
                )
            )
            _assert_json_serializable(hotels)
            assert isinstance(hotels, list)
            assert hotels
            assert any(int(hotel["beds"]) >= 2 for hotel in hotels)

            snapshots = extract_tool_payload(
                await session.call_tool(
                    "get_market_snapshots",
                    {"match_id": "portugal_dr_congo"},
                )
            )
            _assert_json_serializable(snapshots)
            assert isinstance(snapshots, list)
            assert len(snapshots) >= 5

            trend = extract_tool_payload(
                await session.call_tool(
                    "analyze_market_snapshots",
                    {"match_id": "portugal_dr_congo"},
                )
            )
            _assert_json_serializable(trend)
            assert trend["snapshot_count"] >= 5
            assert trend["recommendation"] in {
                "buy",
                "strongly_consider_buying",
                "monitor",
                "wait",
                "insufficient_data",
            }

            import_preview = extract_tool_payload(
                await session.call_tool(
                    "preview_snapshot_import",
                    {
                        "input_path": "examples/external_snapshot_import.csv",
                        "match_id": "portugal_dr_congo",
                    },
                )
            )
            _assert_json_serializable(import_preview)
            assert import_preview["validation_status"] == "valid"
            assert import_preview["count"] >= 1

            web_preview = extract_tool_payload(
                await session.call_tool(
                    "preview_web_evidence_from_local_file",
                    {
                        "local_path": "examples/sample_ticket_market_page.html",
                        "match_id": "portugal_dr_congo",
                    },
                )
            )
            _assert_json_serializable(web_preview)
            assert web_preview["validation_status"] == "valid"
            assert web_preview["extraction"]["candidate_lowest_price"] == 680.0
            assert web_preview["extraction"]["candidate_listings"] == 340

    print(f"Python environment: {environment_label()} ({sys.version.split()[0]})")
    print("Official MCP SDK validation path used: yes")
    print("Listed MCP tools:")
    for tool_name in sorted(EXPECTED_TOOL_NAMES):
        print(f"- {tool_name}")
    print("Sample get_ticket_market(portugal_dr_congo):")
    print(f"- lowest_price = {ticket['lowest_price']}")
    print(f"- listings = {ticket['listings']}")
    print(f"- demand_level = {ticket['demand_level']}")
    print("Sample compute_scalper_stress_index:")
    print(f"- score = {stress['score']}")
    print(f"- interpretation = {stress['interpretation']}")
    print("Sample get_hotel_quotes:")
    print(f"- hotel_options_returned = {len(hotels)}")
    print(f"- first_hotel = {hotels[0]['name']}")
    print("Sample get_market_snapshots:")
    print(f"- snapshots_returned = {len(snapshots)}")
    print("Sample analyze_market_snapshots:")
    print(f"- recommendation = {trend['recommendation']}")
    print(f"- trigger_status = {trend['trigger_status']}")
    print("Sample preview_snapshot_import:")
    print(f"- validation_status = {import_preview['validation_status']}")
    print(f"- snapshots_returned = {import_preview['count']}")
    print("Sample preview_web_evidence_from_local_file:")
    print(f"- validation_status = {web_preview['validation_status']}")
    print(f"- candidate_lowest_price = {web_preview['extraction']['candidate_lowest_price']}")
    print(f"- candidate_listings = {web_preview['extraction']['candidate_listings']}")
    print("MCP client validation passed.")
    return 0


def main() -> int:
    """CLI entry point."""
    skip_reason = environment_error_message()
    if skip_reason:
        print(skip_reason)
        return 0
    try:
        return asyncio.run(run_validation())
    except Exception as exc:
        print(f"ERROR: MCP client validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
