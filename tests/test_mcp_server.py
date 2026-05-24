from eventtrip.mcp_server import server


EXPECTED_TOOLS = {
    "get_ticket_market",
    "get_ticket_links",
    "recommend_ticket_links",
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


def test_server_imports_and_registers_expected_tool_names():
    assert set(server.EXPECTED_TOOL_NAMES) == EXPECTED_TOOLS
    assert set(server.TOOL_REGISTRY) == EXPECTED_TOOLS
    assert {tool["name"] for tool in server.list_tools_payload()["tools"]} == EXPECTED_TOOLS


def test_mcp_wrappers_return_mock_data_directly():
    ticket = server.get_ticket_market("portugal_dr_congo")
    ticket_links = server.recommend_ticket_links("portugal_dr_congo", "monitor_with_wait_bias")
    flights = server.get_flight_quotes("PIT", "Houston", "2026-06-16", "2026-06-18")
    hotels = server.get_hotel_quotes("Houston", "2026-06-16", "2026-06-17", beds=2)
    market = server.get_market_signals("portugal_dr_congo")
    split = server.compute_aa_split(160, people=2)
    stress = server.compute_scalper_stress_index(ticket, market)
    snapshots = server.get_market_snapshots("portugal_dr_congo")
    trend = server.analyze_market_snapshots("portugal_dr_congo")
    preview = server.preview_snapshot_import(
        "examples/external_snapshot_import.csv",
        "portugal_dr_congo",
    )
    web_preview = server.preview_web_evidence_from_local_file(
        "examples/sample_ticket_market_page.html",
        "portugal_dr_congo",
    )

    assert ticket["lowest_price"] == 700
    assert ticket_links["primary_links"][0]["source_type"] == "official_primary"
    assert "FIFA" in ticket_links["primary_links"][0]["label"]
    assert flights[0]["trip_type"] == "one_night_balanced"
    assert hotels[0]["beds"] == 2
    assert market["match_id"] == "portugal_dr_congo"
    assert split["per_person"] == 80
    assert stress["score"] == 41.9
    assert len(snapshots) >= 5
    assert trend["match_id"] == "portugal_dr_congo"
    assert preview["validation_status"] == "valid"
    assert preview["count"] == 2
    assert web_preview["validation_status"] == "valid"
    assert web_preview["extraction"]["candidate_lowest_price"] == 680.0
    assert web_preview["extraction"]["candidate_listings"] == 340
