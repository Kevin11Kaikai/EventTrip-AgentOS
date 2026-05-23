"""Local Streamlit dashboard for deterministic EventTrip-AgentOS demo data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.market_snapshots import (
    analyze_market_trend,
    default_snapshot_path,
    load_market_snapshots,
    snapshot_to_dict,
    trend_result_to_dict,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = PROJECT_ROOT / "runs"
DEFAULT_MATCH_ID = "portugal_dr_congo"
RECOMMENDED_PLAN = "Option A: One-night balanced plan"
TICKET_TIMING_LABEL = "Monitor with wait bias"


def load_dashboard_snapshot_summary(
    match_id: str = DEFAULT_MATCH_ID,
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load snapshot rows and deterministic trend summary for the dashboard."""
    snapshot_path = Path(path) if path else default_snapshot_path(match_id)
    snapshots = load_market_snapshots(snapshot_path, match_id=match_id)
    trend = analyze_market_trend(snapshots)
    rows = [snapshot_to_dict(snapshot) for snapshot in snapshots]
    latest = rows[-1] if rows else {}
    return {
        "match_id": match_id,
        "snapshot_path": str(snapshot_path),
        "snapshots": rows,
        "trend": trend_result_to_dict(trend),
        "latest": latest,
    }


def budget_table_rows() -> list[dict[str, Any]]:
    """Return current deterministic budget comparison values for the portfolio demo."""
    return [
        {
            "Option": "Option A: One-night balanced plan",
            "Traveler A": "$1120",
            "Traveler B": "$1220",
            "Score": 62.0,
        },
        {
            "Option": "Option D: Independent booking plan",
            "Traveler A": "$1120",
            "Traveler B": "$1220",
            "Score": 57.9,
        },
        {
            "Option": "Option C: Two-night comfortable plan",
            "Traveler A": "$1230",
            "Traveler B": "$1330",
            "Score": 43.9,
        },
        {
            "Option": "Option B: Same-day aggressive plan",
            "Traveler A": "$1120",
            "Traveler B": "$1220",
            "Score": 42.0,
        },
    ]


def find_latest_run(
    runs_root: str | Path = RUNS_ROOT,
    prefix: str = "portugal_dr_congo_houston_demo_",
) -> Path | None:
    """Return the latest timestamped run directory by deterministic name sort."""
    root = Path(runs_root)
    if not root.exists():
        return None
    candidates = [
        path for path in root.iterdir() if path.is_dir() and path.name.startswith(prefix)
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: path.name)[-1]


def latest_report_paths(runs_root: str | Path = RUNS_ROOT) -> dict[str, str | None]:
    """Return deterministic and polished report paths from the latest run, if present."""
    latest = find_latest_run(runs_root)
    if latest is None:
        return {"run_dir": None, "final_report": None, "polished_report": None}

    final_report = latest / "08_final_report.md"
    polished_report = latest / "09_final_report_polished.md"
    return {
        "run_dir": str(latest),
        "final_report": str(final_report) if final_report.exists() else None,
        "polished_report": str(polished_report) if polished_report.exists() else None,
    }


def main() -> None:
    """Render the local-only Streamlit dashboard."""
    try:
        import streamlit as st
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime guidance
        raise SystemExit("Streamlit is not installed. Run: pip install -r requirements.txt") from exc

    st.set_page_config(page_title="EventTrip-AgentOS Dashboard", layout="wide")
    st.title("EventTrip-AgentOS Dashboard")
    st.caption("Local portfolio view for deterministic event-trip decision support.")
    st.write(
        "Local deterministic dashboard for manual market snapshots, trend analysis, "
        "and portfolio demo recommendations. No live APIs, no web scraping, and no "
        "OhMyGPT key are required."
    )

    match_id = st.sidebar.selectbox("Match", [DEFAULT_MATCH_ID], index=0)
    snapshot_path = default_snapshot_path(match_id)
    st.sidebar.caption("Snapshot data path")
    st.sidebar.code(str(snapshot_path))
    show_raw = st.sidebar.checkbox("Show raw snapshot data", value=True)
    show_architecture = st.sidebar.checkbox("Show project architecture summary", value=False)

    summary = load_dashboard_snapshot_summary(match_id)
    trend = summary["trend"]
    snapshots = summary["snapshots"]

    metric_cols = st.columns(4)
    metric_cols[0].metric("Recommended travel plan", RECOMMENDED_PLAN)
    metric_cols[1].metric("Ticket timing", TICKET_TIMING_LABEL)
    metric_cols[2].metric("Traveler A cost", "$1120")
    metric_cols[3].metric("Traveler B cost", "$1220")
    st.caption(
        "Monitor with wait bias means the single-day market says monitor, while "
        "multi-snapshot trend data supports disciplined waiting with trigger prices."
    )

    snapshot_cols = st.columns(3)
    snapshot_cols[0].metric("Latest snapshot price", f"${trend['latest_price']:.0f}")
    snapshot_cols[1].metric("Latest listings", f"{trend['latest_listings']}")
    snapshot_cols[2].metric("Latest snapshot SSI", f"{trend['latest_scalper_stress_index']:.1f}/100")

    if show_architecture:
        st.subheader("Architecture Summary")
        st.code(
            "User Request -> Orchestrator -> Markdown Shared Memory -> "
            "Ticket -> Flight -> Hotel -> Snapshot -> Market -> Budget -> Risk -> Report"
        )

    st.subheader("Snapshot Trend")
    if not snapshots:
        st.warning("Snapshot CSV is missing or no rows are available for this match.")
    else:
        if show_raw:
            st.dataframe(snapshots, use_container_width=True)
        _render_charts(st, snapshots)

    st.subheader("Trend Analysis")
    st.write(f"Snapshot count: {trend['snapshot_count']}")
    st.write(f"Price change: ${trend['price_change_abs']:.0f} ({trend['price_change_pct']:+.1f}%)")
    st.write(
        f"Listings change: {trend['listings_change_abs']:+d} "
        f"({trend['listings_change_pct']:+.1f}%)"
    )
    st.write(f"Recommendation: {trend['recommendation']}")
    st.write(f"Trigger status: {trend['trigger_status']}")
    for item in trend["explanation"]:
        st.write(f"- {item}")

    st.subheader("Budget Comparison")
    st.table(budget_table_rows())

    st.subheader("Reports")
    st.code("python -m eventtrip.orchestrator --demo portugal_dr_congo_houston", language="powershell")
    report_paths = latest_report_paths()
    if report_paths["run_dir"]:
        st.write(f"Latest run directory: `{report_paths['run_dir']}`")
        st.write(f"Deterministic report: `{report_paths['final_report'] or 'not found'}`")
        st.write(f"Polished report: `{report_paths['polished_report'] or 'not generated'}`")
    else:
        st.info("No generated run directories found yet.")

    st.subheader("Project Links")
    st.markdown(
        "- `docs/demo_walkthrough.md`\n"
        "- `docs/architecture.md`\n"
        "- `docs/mcp_validation.md`\n"
        "- `docs/dashboard_guide.md`\n"
        "- `docs/release_v0_1_0.md`"
    )


def _render_charts(st: Any, snapshots: list[dict[str, Any]]) -> None:
    """Render simple built-in charts without adding charting dependencies."""
    try:
        import pandas as pd
    except ModuleNotFoundError:  # pragma: no cover - Streamlit usually includes pandas
        st.info("Install pandas via Streamlit dependencies to view line charts.")
        return

    frame = pd.DataFrame(snapshots)
    if frame.empty:
        return
    frame = frame.set_index("snapshot_date")
    chart_cols = st.columns(2)
    chart_cols[0].line_chart(frame[["lowest_price"]])
    chart_cols[1].line_chart(frame[["listings"]])


if __name__ == "__main__":
    main()
