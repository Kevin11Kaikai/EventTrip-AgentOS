from eventtrip.orchestrator import run_demo
from eventtrip.report_polisher import (
    extract_report_invariants,
    polish_report,
    validate_polished_report,
)


SAMPLE_REPORT = """# EventTrip-AgentOS Final Report

Recommended plan: Option A: One-night balanced plan.

- Traveler A: $1120
- Traveler B: $1220

Overall ticket timing recommendation: Monitor with wait bias.

The scenario includes only Portugal vs DR Congo on 2026-06-17 at NRG Stadium in Houston.

Scalper Stress Index: 41.9/100.

Latest snapshot Scalper Stress Index: 71.4/100.

Buy immediately at $550. Strongly consider buying below $600. Do not panic buy in the $680-$700 range.

- No web scraping, no browser automation, and no real paid travel APIs are used.
- No live market, flight, hotel, or ticket APIs are used.
- The demo is decision support, not financial, legal, or travel advice.
"""


def test_extract_report_invariants_finds_protected_values():
    invariants = extract_report_invariants(SAMPLE_REPORT)

    protected = invariants["protected_values"]
    assert "Portugal vs DR Congo" in protected
    assert "2026-06-17" in protected
    assert "NRG Stadium" in protected
    assert "Option A: One-night balanced plan" in protected
    assert "$1120" in protected
    assert "$1220" in protected
    assert "Monitor with wait bias" in protected
    assert "41.9/100" in protected
    assert "71.4/100" in protected


def test_validate_polished_report_passes_when_values_remain():
    invariants = extract_report_invariants(SAMPLE_REPORT)

    ok, issues = validate_polished_report(SAMPLE_REPORT, SAMPLE_REPORT, invariants)

    assert ok
    assert issues == []


def test_validate_polished_report_fails_when_cost_changes():
    invariants = extract_report_invariants(SAMPLE_REPORT)
    changed = SAMPLE_REPORT.replace("$1120", "$999")

    ok, issues = validate_polished_report(SAMPLE_REPORT, changed, invariants)

    assert not ok
    assert any("$1120" in issue or "$999" in issue for issue in issues)


def test_validate_polished_report_fails_when_recommendation_changes():
    invariants = extract_report_invariants(SAMPLE_REPORT)
    changed = SAMPLE_REPORT.replace("Option A: One-night balanced plan", "Option B: Same-day aggressive plan")

    ok, issues = validate_polished_report(SAMPLE_REPORT, changed, invariants)

    assert not ok
    assert any("Option A: One-night balanced plan" in issue for issue in issues)


def test_validate_polished_report_fails_when_limitations_removed():
    invariants = extract_report_invariants(SAMPLE_REPORT)
    changed = SAMPLE_REPORT.replace(
        "- No live market, flight, hotel, or ticket APIs are used.\n",
        "",
    )

    ok, issues = validate_polished_report(SAMPLE_REPORT, changed, invariants)

    assert not ok
    assert any("No live market" in issue for issue in issues)


def test_polish_report_with_mocked_llm_writes_safe_output(tmp_path, monkeypatch):
    original_path = tmp_path / "08_final_report.md"
    output_path = tmp_path / "09_final_report_polished.md"
    original_path.write_text(SAMPLE_REPORT, encoding="utf-8")

    def fake_generate_text(system_prompt, user_prompt):
        assert "Preserve every protected value" in user_prompt
        return SAMPLE_REPORT.replace("# EventTrip-AgentOS Final Report", "# Polished EventTrip-AgentOS Report")

    monkeypatch.setattr("eventtrip.report_polisher.llm_client.generate_text", fake_generate_text)

    result = polish_report(original_path, output_path)

    assert result["status"] == "completed"
    assert result["output_path"] == output_path
    assert output_path.exists()


def test_orchestrator_use_llm_missing_key_keeps_deterministic_report(tmp_path, monkeypatch):
    monkeypatch.delenv("OHMYGPT_API_KEY", raising=False)

    result = run_demo("portugal_dr_congo_houston", use_llm=True, runs_root=tmp_path)

    assert result["final_report_path"].exists()
    assert result["polished_report"]["status"] == "llm_error"
    assert not (result["run_dir"] / "09_final_report_polished.md").exists()
