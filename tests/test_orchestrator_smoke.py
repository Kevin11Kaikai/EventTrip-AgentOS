from eventtrip.orchestrator import run_demo


def test_orchestrator_creates_final_report(tmp_path):
    result = run_demo("portugal_dr_congo_houston", use_llm=False, runs_root=tmp_path)
    final_report = result["final_report_path"]

    assert final_report.exists()
    assert final_report.name == "08_final_report.md"
    assert result["recommended_option"] == "Option A: One-night balanced plan"
    assert result["ticket_timing_recommendation"] == "monitor"
    output_names = {path.name for path in result["run_dir"].glob("*.md")}
    assert output_names == {
        "00_user_request.md",
        "01_ticket_agent.md",
        "02_flight_agent.md",
        "03_hotel_agent.md",
        "04_snapshot_agent.md",
        "05_market_agent.md",
        "06_budget_agent.md",
        "07_risk_agent.md",
        "08_final_report.md",
    }
