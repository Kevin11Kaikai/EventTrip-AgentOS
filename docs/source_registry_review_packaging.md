# Source Registry Review Packaging

## Purpose

Phase 8.7 adds an exportable review packet for `data/source_evidence.yaml`.
The packet is designed for pull requests, customer review, professor/advisor
review, and portfolio walkthroughs.

It summarizes:

- source registry validation status,
- source counts by type,
- evidence tag coverage,
- citation group coverage,
- field-level attribution coverage,
- a copy-paste pull request review checklist.

This workflow is metadata-only. It does not fetch URLs, scrape websites, verify
article contents automatically, or purchase tickets.

## Commands

Print a compact registry review summary:

```powershell
python -m eventtrip.source_review_cli summary --match portugal_dr_congo
```

Export a Markdown review packet:

```powershell
python -m eventtrip.source_review_cli export --match portugal_dr_congo --format md --output examples\source_registry_review_packet.md
```

A committed sample packet is available at:

```text
examples/source_registry_review_packet.md
```

Export a JSON validation summary:

```powershell
python -m eventtrip.source_review_cli export --match portugal_dr_congo --format json --output examples\source_registry_review_summary.json
```

If `--output` is omitted, the packet is printed to the terminal.

## What The Packet Checks

- Every source has required metadata fields.
- Every source uses `https://`.
- Every source has a supported `source_type`.
- Every source uses known `evidence_tags`.
- Every source maps into at least one citation group.
- Every citation group used by the public report has coverage.
- Field-level source IDs reference registered sources.
- Unknown and model-derived fields remain visually separated from source-backed facts.

## Pull Request Use

Recommended PR workflow for adding a new public source:

1. Create a local source candidate YAML or JSON file.
2. Run `source_intake_cli preview`.
3. Run `source_intake_cli add --dry-run`.
4. Save only after human review with `--save`.
5. Run `source_review_cli summary`.
6. Export a Markdown packet and attach or paste it into the PR.

## Safety Rules

- Do not add login, checkout, payment, account, CAPTCHA, private, or paywalled pages.
- Do not turn unsourced ticket, flight, hotel, local transport, or budget numbers into source-backed claims.
- Do not include secrets, local private files, generated run outputs, or `.env`.
- If a public source cannot support a value, keep it marked as unknown or internal.

## Relationship To Reports

The review packet does not replace the source-backed report. It is an audit
artifact that helps reviewers understand whether the source registry is safe to
use before generating or sharing:

```text
10_source_backed_final_report.md
11_source_backed_final_report.html
```
