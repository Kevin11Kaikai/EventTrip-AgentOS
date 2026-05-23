from app import streamlit_app


def test_dashboard_snapshot_summary_loads_seed_data():
    summary = streamlit_app.load_dashboard_snapshot_summary("portugal_dr_congo")

    assert summary["match_id"] == "portugal_dr_congo"
    assert summary["trend"]["snapshot_count"] == 5
    assert summary["trend"]["latest_price"] == 680
    assert summary["trend"]["latest_listings"] == 340


def test_dashboard_budget_rows_include_expected_options():
    rows = streamlit_app.budget_table_rows()

    assert rows[0]["Option"] == "Option A: One-night balanced plan"
    assert rows[0]["Traveler A"] == "$1120"
    assert rows[0]["Traveler B"] == "$1220"
    assert {row["Option"] for row in rows} >= {
        "Option A: One-night balanced plan",
        "Option B: Same-day aggressive plan",
        "Option C: Two-night comfortable plan",
        "Option D: Independent booking plan",
    }


def test_find_latest_run_uses_deterministic_name_sort(tmp_path):
    older = tmp_path / "portugal_dr_congo_houston_demo_20260523_100000"
    newer = tmp_path / "portugal_dr_congo_houston_demo_20260523_110000"
    unrelated = tmp_path / "other_run"
    older.mkdir()
    newer.mkdir()
    unrelated.mkdir()

    latest = streamlit_app.find_latest_run(tmp_path)

    assert latest == newer


def test_latest_report_paths_handles_missing_runs(tmp_path):
    report_paths = streamlit_app.latest_report_paths(tmp_path)

    assert report_paths == {"run_dir": None, "final_report": None, "polished_report": None}
