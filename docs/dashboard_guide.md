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

## Mockup Asset

The repository includes a lightweight static SVG mockup:

```text
docs/assets/dashboard_mockup.svg
```

This file is a labeled mockup, not a real screenshot. It is safe to render in README and GitHub docs because it contains only deterministic demo values and no local private data.

## Screenshot Instructions

Launch the dashboard with the command above, open the local Streamlit URL in a browser, and take a screenshot manually.

Optional screenshot path for GitHub documentation:

```text
docs/assets/dashboard_screenshot.png
```

Do not commit fake screenshots. Commit a screenshot only after it is captured from a real local dashboard run.

Before committing any real screenshot, confirm it does not contain secrets, private filesystem paths you do not want public, browser account information, or local private data.
