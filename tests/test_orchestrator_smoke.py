from eventtrip.orchestrator import run_demo


def test_orchestrator_creates_final_report(tmp_path):
    result = run_demo("portugal_dr_congo_houston", use_llm=False, runs_root=tmp_path)
    final_report = result["final_report_path"]

    assert final_report.exists()
    assert final_report.name == "07_final_report.md"
    assert result["recommended_option"] == "Option A: One-night balanced plan"
    assert result["ticket_timing_recommendation"] == "monitor"
    assert len(list(result["run_dir"].glob("*.md"))) == 8

