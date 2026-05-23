# EventTrip-AgentOS v0.1.0

## Summary

EventTrip-AgentOS is a deterministic, MCP-enabled multi-agent system for collaborative event travel planning under ticket-market uncertainty. The first demo plans a budget-first Houston trip for Portugal vs DR Congo on June 17, 2026.

## What Is Included

- Deterministic multi-agent workflow
- Markdown shared memory
- MCP server wrapper and official MCP client validation
- Market snapshot tracker
- Snapshot CLI
- OhMyGPT optional report polishing with invariant guard
- Local Streamlit dashboard
- Documentation package

## Demo Commands

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
python -m eventtrip.orchestrator --demo portugal_dr_congo_houston
python -m eventtrip.snapshots_cli analyze --match portugal_dr_congo
streamlit run app\streamlit_app.py
```

## Safety And Scope

- No live APIs by default
- No scraping
- No required paid APIs
- No committed secrets
- Local deterministic demo

## Known Limitations

- No production dashboard
- No real travel API integration yet
- Manual/mock snapshots only by default

## Recommended Next Work

- Optional provider adapters through official APIs
- Richer dashboard screenshots
- Multi-event templates
