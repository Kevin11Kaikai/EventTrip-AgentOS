# Source-Backed Public Report

## Purpose

The source-backed public report is the shareable report for users who do not want local placeholder estimates in the visible output. It uses only curated public web, official, and news evidence from `data/source_evidence.yaml`.

## Output

Each orchestrator run writes:

```text
10_source_backed_final_report.md
```

The deterministic `08_final_report.md` remains an internal planning and regression artifact. The source-backed report is the public-facing artifact.

## Evidence Sources

The registry currently includes:

- FIFA match preview / tickets pages
- FIFA resale/exchange support pages
- Axios Houston reporting on DR Congo's Houston base camp and Houston World Cup readiness
- Kiplinger and MoneyWeek reporting on World Cup ticket scam risks

## Rules

- Do not include local planning estimates unless a public source is registered.
- Do not claim sourced airfare, hotel, ticket price, or total trip budget when no source exists.
- Link every source in the report's source registry.
- Keep ticket purchase guidance manual only.
- Do not automate ticket buying, login, checkout, payment, or CAPTCHA handling.

## Current Limitation

The source-backed report currently does not include sourced flight, hotel, or exact ticket price estimates for Portugal vs DR Congo. That is intentional: missing sourced data is omitted rather than filled with local estimates.
