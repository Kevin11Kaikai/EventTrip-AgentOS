# Source-Backed Public Report

## Purpose

The source-backed public report is the shareable report for users who do not want local placeholder estimates in the visible output. It uses only curated public web, official, marketplace, and news evidence from `data/source_evidence.yaml`.

## Output

Each orchestrator run writes:

```text
10_source_backed_final_report.md
11_source_backed_final_report.html
```

The deterministic `08_final_report.md` remains an internal planning and regression artifact. The source-backed Markdown and HTML reports are public-facing artifacts.

Phase 7.5 also adds a short `Source-Backed Citation Summary` section to `08_final_report.md`. That internal section provides public-source context only. It does not turn deterministic ticket, flight, hotel, local transportation, or budget estimates into sourced claims.

Phase 7.6 adds an `Evidence Traceability Matrix` to `08_final_report.md`. The matrix marks each major claim as one of:

- `source_backed`: supported by registered public official, marketplace, or news evidence.
- `internal_estimate_not_source_backed`: produced by deterministic planning logic but not a public-source fact.
- `no_source_backed_data_found`: no registered public source supports the exact claim yet.

This is intentionally strict. If the project cannot verify a real public source for a value, the report says that directly rather than presenting a placeholder as real data.

## Evidence Sources

The registry currently includes:

- FIFA match preview / tickets pages
- FIFA resale/exchange support pages
- StubHub World Cup Tickets as a secondary-market marketplace reference
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
- `Secondary Marketplace Candidate`: StubHub monitoring guidance, clearly separated from official FIFA paths.
- `What Is Still Unknown`: values that remain unavailable from registered public sources.

The report keeps these sections separate from internal deterministic estimates. If a real public source is not registered, the report says the value is still unknown.

## HTML Report

Phase 7.8 adds `11_source_backed_final_report.html`, a static client-facing page generated from the same source registry and ticket-link data as the Markdown source-backed report.

The HTML report:

- is local and static,
- uses inline CSS only,
- does not call external scripts,
- does not fetch live APIs,
- does not scrape websites,
- includes evidence traceability claim IDs.

Phase 7.9 polishes the HTML report for client-facing review:

- cover-style summary header,
- section navigation,
- decision summary cards,
- color-coded traceability statuses,
- print-friendly CSS.

Phase 8.0 adds an `Opt-In Live Data Status` section. By default it states that no live API payload is attached. Future reviewed live snapshots can be displayed only when they carry source metadata and pass the opt-in provider path.

Phase 8.2 displays reviewed live/API snapshots in the HTML report only when their snapshot `source_type` is `reviewed_live_data`. Unreviewed API previews and ordinary mock/manual snapshots are not shown in the public live-data table.

Phase 8.3 switches the source-backed HTML report to a Chinese client-facing presentation and adds an inline SVG forecast section. The chart uses pressure indices for ticket, flight, hotel, and total-cost direction. If exact reviewed dollar prices are unavailable, the report says so directly and does not invent values.

Phase 8.4 adds field-level source attribution to the Chinese HTML report. Key fields now carry visible badges that distinguish:

- public-source-backed facts,
- human-reviewed live/API data,
- model-inferred pressure indices,
- internal trigger policies,
- values that remain unknown because no registered public source supports them.

The full `字段级来源标注` table links each visible field to source IDs where available. This keeps customer-facing recommendations readable while preserving a conservative audit trail.

Phase 8.5 polishes the same static HTML report for customer review:

- cleaner spacing and stronger visual hierarchy,
- a screenshot-friendly summary strip,
- responsive table handling for narrow screens,
- print-specific layout rules for cleaner PDF/export output.

These changes are presentation-only and do not modify the source-backed evidence model, deterministic estimates, or recommendation logic.

## Reviewed Source Intake

Phase 8.6 adds `eventtrip.source_intake_cli`, a guarded workflow for adding new public sources to `data/source_evidence.yaml`.

```powershell
python -m eventtrip.source_intake_cli validate --match portugal_dr_congo
python -m eventtrip.source_intake_cli preview --candidate examples\source_candidate.example.yaml --match portugal_dr_congo
python -m eventtrip.source_intake_cli add --candidate examples\source_candidate.example.yaml --match portugal_dr_congo --dry-run
```

The workflow validates required fields, supported `source_type`, known `evidence_tags`, citation group coverage, duplicate source IDs, and field-level attribution coverage before a source can be saved. It never fetches URLs or scrapes websites; it only reviews local YAML/JSON metadata supplied by the user. Full details are in `docs/source_intake_workflow.md`.

## Latest Report CLI

Print the latest source-backed report path:

```powershell
python -m eventtrip.source_report_cli latest
python -m eventtrip.source_report_cli latest --format html
```

Print and open the latest source-backed report with the local default application:

```powershell
python -m eventtrip.source_report_cli latest --format html --open
python -m eventtrip.source_report_cli open --format html
```

The CLI scans timestamped run directories under `runs/` and never generates or modifies report content.

## Rules

- Do not include local planning estimates unless a public source is registered.
- Do not claim sourced airfare, hotel, ticket price, or total trip budget when no source exists.
- Link every source in the report's source registry.
- Keep ticket purchase guidance manual only.
- Keep secondary-market guidance separate from official FIFA purchase paths.
- Do not automate ticket buying, login, checkout, payment, or CAPTCHA handling.

## Current Limitation

The source-backed report currently does not include sourced flight, hotel, or exact ticket price estimates for Portugal vs DR Congo. That is intentional: missing sourced data is omitted rather than filled with local estimates.
