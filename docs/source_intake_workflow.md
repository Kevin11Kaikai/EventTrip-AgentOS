# Reviewed Source Intake Workflow

## Purpose

Phase 8.6 adds a guided workflow for adding new public sources to
`data/source_evidence.yaml` without weakening the source-backed report model.

The workflow validates source metadata before a source can be published into
the registry. It checks:

- required source fields,
- supported `source_type` values,
- known `evidence_tags`,
- citation group coverage,
- field-level attribution coverage for the HTML report,
- duplicate `source_id` values.

This is a metadata review workflow only. It does not fetch URLs, scrape pages,
verify article contents automatically, or buy tickets.

## Candidate Format

Create a local YAML or JSON file using this shape:

```yaml
match_id: portugal_dr_congo
source:
  source_id: example_public_ticket_safety_source
  title: Example Public Ticket Safety Source
  publisher: Example Publisher
  published_date: 2026-05-24
  url: https://example.com/world-cup-ticket-safety
  source_type: news
  evidence_tags:
    - tickets
    - ticket_safety
  summary: Short human-reviewed summary of what this source supports.
```

A safe example is committed at:

```text
examples/source_candidate.example.yaml
```

## Commands

Print a template:

```powershell
python -m eventtrip.source_intake_cli template
```

Validate the current registry:

```powershell
python -m eventtrip.source_intake_cli validate --match portugal_dr_congo
```

Preview a candidate:

```powershell
python -m eventtrip.source_intake_cli preview --candidate examples\source_candidate.example.yaml --match portugal_dr_congo
```

Dry-run adding a candidate:

```powershell
python -m eventtrip.source_intake_cli add --candidate examples\source_candidate.example.yaml --match portugal_dr_congo --dry-run
```

Save only after human review:

```powershell
python -m eventtrip.source_intake_cli add --candidate path\to\reviewed_source.yaml --match portugal_dr_congo --save
```

After saving or reviewing a registry change, export a review packet:

```powershell
python -m eventtrip.source_review_cli summary --match portugal_dr_congo
python -m eventtrip.source_review_cli export --match portugal_dr_congo --format md --output examples\source_registry_review_packet.md
```

The review packet gives pull request reviewers a compact validation summary, citation group coverage table, field-level attribution table, and checklist. See `docs/source_registry_review_packaging.md`.

## Supported Source Types

- `official`
- `news`
- `government`
- `transportation`
- `marketplace`
- `travel_data`

## Supported Evidence Tags

Evidence tags must map to at least one citation group:

- Match facts: `match`, `date`, `venue`
- Ticket safety: `tickets`, `official_purchase`, `official_resale`, `ticket_safety`, `resale_risk`, `secondary_market`
- Houston logistics: `houston`, `local_transport`, `venue_readiness`, `team_base_camp`
- Cost trend evidence: `airfare_trend`, `hotel_trend`, `ticket_market_pressure`

Unknown tags fail validation. This prevents new sources from silently falling
outside the citation grouping used by the report.

## Field-Level Attribution Check

The intake validator checks that the source-backed HTML report can still build
the expected field-level attribution map. Required fields include:

- match name, date, and venue,
- official ticket path,
- StubHub secondary-market candidate,
- Houston logistics,
- reviewed live/API snapshot status,
- forecast chart,
- PIT and SEA timing guidance,
- trigger policy,
- values that remain unknown because no source supports them.

If a source change breaks these field-level mappings, the intake workflow fails
before the registry is saved.

## Safety Rules

- Use `--dry-run` or `preview` before writing.
- Use `--save` only after a human has reviewed the source and summary.
- Do not add private, authenticated, paywalled, checkout, login, or CAPTCHA pages.
- Do not add unsupported ticket, hotel, flight, or budget numbers as sourced claims.
- If no public source supports a value, keep it unknown.
- Do not commit secrets or local generated run outputs.
