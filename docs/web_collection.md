# Web Collection Layer

## Purpose

Phase 7.0 adds safe, opt-in public web evidence collection and deterministic local evidence extraction. The goal is to collect auditable evidence candidates, not to automate purchases or replace human review.

The default demo, tests, dashboard, and MCP validation still run offline and do not perform live HTTP collection.

## What It Does

- Collects local HTML/text fixtures.
- Optionally collects a single public HTTP page only when `--live-http` is explicitly passed and robots.txt allows it.
- Extracts candidate prices and listing counts using deterministic heuristics.
- Saves structured evidence JSON only when `--save` is explicitly passed.
- Preserves raw evidence in a local ignored cache when saving.
- Feeds future human review and snapshot import workflows.

## What It Does Not Do

- No login bypass.
- No CAPTCHA bypass.
- No paywall bypass.
- No high-frequency polling.
- No automated ticket purchasing.
- No scraping private or authenticated pages.
- No default live HTTP in tests, dashboard, MCP validation, or the main demo.

## Commands

Preview extraction from the deterministic local fixture:

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
python -m eventtrip.web_collect_cli extract --local-path examples\sample_ticket_market_page.html --match portugal_dr_congo
```

Collect the local fixture without writing evidence:

```powershell
python -m eventtrip.web_collect_cli collect --target-id sample_fixture --local-path examples\sample_ticket_market_page.html --match portugal_dr_congo --dry-run
```

Collect and save local evidence JSON and raw cache:

```powershell
python -m eventtrip.web_collect_cli collect --target-id sample_fixture --local-path examples\sample_ticket_market_page.html --match portugal_dr_congo --save
```

Optional single-page public HTTP smoke test:

```powershell
python -m eventtrip.web_collect_cli collect --target-id example_public --url https://example.com --match portugal_dr_congo --live-http --dry-run
```

Live HTTP is disabled unless `--live-http` is passed. Do not use this collector on login, checkout, cart, account, payment, CAPTCHA, or authenticated pages.

## Evidence Schema

`WebEvidence` stores collection metadata:

- target ID
- match ID
- source URL or local path
- collection timestamp
- title
- text excerpt
- raw cache path
- extraction confidence
- extracted fields
- notes

`MarketEvidenceExtraction` stores candidate market fields:

- candidate lowest price
- candidate listings
- candidate hotel price
- candidate flight price
- currency
- evidence summary
- confidence
- warnings

Extracted values are heuristic candidates and require human review before any snapshot import.

## Safety Model

- `--dry-run` previews evidence and writes nothing.
- `--save` is required to write evidence JSON and raw cache files.
- Generated evidence under `data/web_evidence/` is ignored by Git except `.gitkeep`.
- Live HTTP requires explicit `--live-http`.
- Live HTTP remains one page per command and has a conservative response-size cap.
- Live HTTP checks robots.txt before collection and fails closed if it cannot verify access.
- The collector uses simple HTTP GET only; it does not execute JavaScript, use browser automation, manage sessions, or handle login cookies.
- MCP web evidence tools are preview-only and do not write evidence or snapshots.

Print the current conservative policy:

```powershell
python -m eventtrip.web_collect_cli policy
```

Phase 8.3 keeps this layer conservative: one page per command, robots.txt required, no JavaScript execution, no cookie/login sessions, no default live HTTP, and a 1 MB response-size cap.

## Reviewed Evidence to Snapshot Conversion

Phase 7.1 adds a human-review step between extracted evidence and the source-of-truth snapshot CSV.

```text
Structured WebEvidence JSON
   |
   v
Human review + explicit missing fields
   |
   v
evidence_review_cli convert --dry-run
   |
   v
Optional --save into manual snapshot CSV
```

Preview a curated evidence file:

```powershell
python -m eventtrip.evidence_review_cli preview --evidence examples\sample_web_evidence.json
```

Build a reviewed snapshot candidate without writing:

```powershell
python -m eventtrip.evidence_review_cli convert --evidence examples\sample_web_evidence.json --snapshot-date 2026-05-22 --category-3-low 400 --category-3-high 750 --hotel-availability-score 0.50 --flight-price-pressure 0.55 --social-buzz-score 0.86 --days-before-event 26 --dry-run
```

Write only after review:

```powershell
python -m eventtrip.evidence_review_cli convert --evidence examples\sample_web_evidence.json --snapshot-date 2026-05-22 --category-3-low 400 --category-3-high 750 --hotel-availability-score 0.50 --flight-price-pressure 0.55 --social-buzz-score 0.86 --days-before-event 26 --save
```

The conversion requires explicit human-provided fields that web evidence cannot reliably infer, including Category 3 range, hotel availability proxy, flight pressure, social buzz, and days before event. Duplicate match/date rows fail safely unless `--overwrite` is supplied.
