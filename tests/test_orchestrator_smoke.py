from eventtrip.orchestrator import run_demo


def test_orchestrator_creates_final_report(tmp_path):
    result = run_demo("portugal_dr_congo_houston", use_llm=False, runs_root=tmp_path)
    final_report = result["final_report_path"]
    source_report = result["source_backed_report_path"]

    assert final_report.exists()
    assert source_report.exists()
    assert final_report.name == "08_final_report.md"
    assert source_report.name == "10_source_backed_final_report.md"
    assert result["recommended_option"] == "Option A: One-night balanced plan"
    assert result["ticket_timing_recommendation"] == "monitor_with_wait_bias"
    assert result["ticket_timing_label"] == "Monitor with wait bias"
    assert "Overall ticket timing recommendation: Monitor with wait bias." in final_report.read_text(
        encoding="utf-8"
    )
    assert "## Recommended Ticket Links" in final_report.read_text(encoding="utf-8")
    assert "## Source-Backed Citation Summary" in final_report.read_text(encoding="utf-8")
    assert "Use `10_source_backed_final_report.md`" in final_report.read_text(encoding="utf-8")
    assert "## Evidence Traceability Matrix" in final_report.read_text(encoding="utf-8")
    assert "no_source_backed_data_found" in final_report.read_text(encoding="utf-8")
    assert "mock" not in source_report.read_text(encoding="utf-8").lower()
    output_names = {path.name for path in result["run_dir"].glob("*.md")}
    assert output_names == {
        "00_user_request.md",
        "01_ticket_agent.md",
        "01b_ticket_link_agent.md",
        "02_flight_agent.md",
        "03_hotel_agent.md",
        "04_snapshot_agent.md",
        "05_market_agent.md",
        "06_budget_agent.md",
        "07_risk_agent.md",
        "08_final_report.md",
        "10_source_backed_final_report.md",
    }
