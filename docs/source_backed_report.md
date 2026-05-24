# Source-Backed Public Report

## Purpose

The source-backed public report is the shareable report for users who do not want local placeholder estimates in the visible output. It uses only curated public web, official, and news evidence from `data/source_evidence.yaml`.

## Output

Each orchestrator run writes:

```text
10_source_backed_final_report.md
```

The deterministic `08_final_report.md` remains an internal planning and regression artifact. The source-backed report is the public-facing artifact.

Phase 7.5 also adds a short `Source-Backed Citation Summary` section to `08_final_report.md`. That internal section provides public-source context only. It does not turn deterministic ticket, flight, hotel, local transportation, or budget estimates into sourced claims.

Phase 7.6 adds an `Evidence Traceability Matrix` to `08_final_report.md`. The matrix marks each major claim as one of:

- `source_backed`: supported by registered public official/news evidence.
- `internal_estimate_not_source_backed`: produced by deterministic planning logic but not a public-source fact.
- `no_source_backed_data_found`: no registered public source supports the exact claim yet.

This is intentionally strict. If the project cannot verify a real public source for a value, the report says that directly rather than presenting a placeholder as real data.

## Evidence Sources

The registry currently includes:

- FIFA match preview / tickets pages
- FIFA resale/exchange support pages
- Axios Houston reporting on DR Congo's Houston base camp and Houston World Cup readiness
- Kiplinger and MoneyWeek reporting on World Cup ticket scam risks

## Citation Grouping

`10_source_backed_final_report.md` groups citations into reader-facing sections:

- What To Do Next
- Recommended Official Purchase Paths
- What Is Still Unknown
- Match facts
- Ticket safety
- Houston logistics
- Unknown or not source-backed yet

The final group is deliberate. If a claim such as exact airfare, exact hotel quote, exact ticket price, local transportation price, or total trip budget does not have a registered public citation, the source-backed report lists it as not source-backed instead of filling the gap with local estimates.

## Usability Sections

Phase 7.7 adds reader-facing guidance at the top of the source-backed report:

- `What To Do Next`: practical manual checks before any purchase decision.
- `Recommended Official Purchase Paths`: FIFA official ticketing and FIFA resale/exchange references.
- `What Is Still Unknown`: values that remain unavailable from registered public sources.

The report keeps these sections separate from internal deterministic estimates. If a real public source is not registered, the report says the value is still unknown.

## Latest Report CLI

Print the latest source-backed report path:

```powershell
python -m eventtrip.source_report_cli latest
```

Print and open the latest source-backed report with the local default application:

```powershell
python -m eventtrip.source_report_cli latest --open
```

The CLI scans timestamped run directories under `runs/` and never generates or modifies report content.

## Rules

- Do not include local planning estimates unless a public source is registered.
- Do not claim sourced airfare, hotel, ticket price, or total trip budget when no source exists.
- Link every source in the report's source registry.
- Keep ticket purchase guidance manual only.
- Do not automate ticket buying, login, checkout, payment, or CAPTCHA handling.

## Current Limitation

The source-backed report currently does not include sourced flight, hotel, or exact ticket price estimates for Portugal vs DR Congo. That is intentional: missing sourced data is omitted rather than filled with local estimates.
