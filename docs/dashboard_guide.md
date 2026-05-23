# Dashboard Guide

## Purpose

The EventTrip-AgentOS dashboard is a local portfolio/demo view for deterministic market snapshots and recommendations. It helps reviewers inspect the manual snapshot history, trend analysis, budget comparison, and generated report paths without running live APIs or web scraping.

## Run Command

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
streamlit run app\streamlit_app.py
```

## What It Shows

- Recommendation summary
- Traveler A/B estimated costs
- Ticket timing stance
- Manual snapshot table
- Price and listings trend
- Trend analysis
- Budget comparison
- Latest report paths

## Screenshot Instructions

Launch the dashboard with the command above, open the local Streamlit URL in a browser, and take a screenshot manually.

Optional screenshot path for GitHub documentation:

```text
docs/assets/dashboard_screenshot.png
```

Do not commit fake screenshots. Commit a screenshot only after it is captured from a real local dashboard run.
