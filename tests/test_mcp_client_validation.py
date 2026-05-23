from scripts import validate_mcp_client


EXPECTED_TOOLS = {
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
}


def test_expected_tool_names_are_declared():
    assert validate_mcp_client.EXPECTED_TOOL_NAMES == EXPECTED_TOOLS


def test_python_version_guard_handles_python_39():
    message = validate_mcp_client.environment_error_message(
        version_info=(3, 9, 23),
        sdk_available=False,
    )

    assert message == validate_mcp_client.PYTHON_39_MESSAGE


def test_python_version_guard_handles_missing_sdk_on_python_310():
    message = validate_mcp_client.environment_error_message(
        version_info=(3, 10, 0),
        sdk_available=False,
    )

    assert "official MCP SDK is not installed" in message


def test_extract_tool_payload_from_text_content():
    class TextContent:
        text = '{"lowest_price": 700, "listings": 300}'

    class ToolResult:
        content = [TextContent()]

    payload = validate_mcp_client.extract_tool_payload(ToolResult())

    assert payload["lowest_price"] == 700
    assert payload["listings"] == 300


def test_extract_tool_payload_unwraps_structured_result():
    class ToolResult:
        structuredContent = {"result": [{"beds": 2}]}
        content = []

    payload = validate_mcp_client.extract_tool_payload(ToolResult())

    assert payload == [{"beds": 2}]
