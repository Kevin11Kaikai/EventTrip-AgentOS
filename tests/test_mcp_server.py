from eventtrip.mcp_server import server


EXPECTED_TOOLS = {
    "get_ticket_market",
    "get_flight_quotes",
    "get_hotel_quotes",
    "get_market_signals",
    "compute_aa_split",
    "compute_scalper_stress_index",
    "rank_budget_options",
}


def test_server_imports_and_registers_expected_tool_names():
    assert set(server.EXPECTED_TOOL_NAMES) == EXPECTED_TOOLS
    assert set(server.TOOL_REGISTRY) == EXPECTED_TOOLS
    assert {tool["name"] for tool in server.list_tools_payload()["tools"]} == EXPECTED_TOOLS


def test_mcp_wrappers_return_mock_data_directly():
    ticket = server.get_ticket_market("portugal_dr_congo")
    flights = server.get_flight_quotes("PIT", "Houston", "2026-06-16", "2026-06-18")
    hotels = server.get_hotel_quotes("Houston", "2026-06-16", "2026-06-17", beds=2)
    market = server.get_market_signals("portugal_dr_congo")
    split = server.compute_aa_split(160, people=2)
    stress = server.compute_scalper_stress_index(ticket, market)

    assert ticket["lowest_price"] == 700
    assert flights[0]["trip_type"] == "one_night_balanced"
    assert hotels[0]["beds"] == 2
    assert market["match_id"] == "portugal_dr_congo"
    assert split["per_person"] == 80
    assert stress["score"] == 41.9
