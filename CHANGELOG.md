# Changelog

## Unreleased

### Added

- Hardened OhMyGPT polished-report validation with protected metadata repair.
- Added local Streamlit dashboard for deterministic snapshot and recommendation viewing.
- Added local dashboard guide and release-page draft.
- Added CSV/JSON snapshot import provider and CLI import command.
- Added safe provider registry for manual, mock, and import-file data providers.
- Added dashboard mockup asset and README preview wiring.
- Added API adapter design doc and disabled official-provider stubs.
- Added local project health check script.
- Added safe web collection layer.
- Added local HTML fixture evidence extraction.
- Added preview-only MCP web evidence tools.
- Added reviewed evidence to snapshot conversion CLI with dry-run and duplicate protection.
- Added official-first ticket link registry, Ticket Link Agent, report section, dashboard section, and MCP link recommendation tools.
- Added source-backed public report generated from official/news evidence registry.
- Added grouped source-backed citation sections and a CLI for printing/opening the latest public source-backed report.
- Added optional source-backed citation summary to the internal deterministic final report.
- Added claim-level evidence traceability matrix that marks unsupported values as not source-backed.
- Added source-backed public report usability sections for next actions, official purchase paths, and still-unknown values.
- Added static HTML source-backed report output with claim anchors for client-facing presentation.
- Polished HTML report with section navigation, decision summary cards, color-coded traceability, and print-friendly styling.
- Added opt-in HTTP JSON provider, fixture preview CLI, and HTML live data status section.
- Added StubHub as a separated secondary-market ticket candidate while keeping FIFA official paths first.
- Added reviewed live/API snapshot import requiring explicit `--save --reviewed` before writing.
- Added source-backed HTML display for reviewed live/API snapshots only.
- Added Chinese HTML forecast charts with PIT/SEA purchase timing guidance.
- Hardened web collection policy output and live HTTP response-size limits.
- Added field-level source attribution badges and an audit table to the Chinese source-backed HTML report.
- Polished customer-facing HTML spacing, screenshot-friendly summary badges, responsive tables, and print layout.
- Added reviewed source intake CLI with source tag, citation group, duplicate ID, and field-level attribution checks.
- Added source registry review packet export with Markdown/JSON validation summary and PR checklist.

## v0.1.0 - 2026-05-23

Initial portfolio release of EventTrip-AgentOS.

### Added

- Deterministic multi-agent event travel planning workflow.
- Markdown shared memory with YAML frontmatter.
- Portugal vs DR Congo 2026 World Cup Houston demo.
- Ticket, flight, hotel, market, budget, risk, snapshot, and report agents.
- MCP server wrapper and official MCP client validation.
- Manual market snapshot tracker and snapshot CLI.
- Trend-based ticket timing with Monitor with wait bias recommendation.
- Optional OhMyGPT report-polishing layer with invariant validation.
- Documentation: architecture, MCP validation, roadmap, demo walkthrough, project summary.

### Safety / Scope

- No live travel APIs.
- No web scraping.
- No required API keys for default demo.
- No committed secrets.
