# Source-Backed Quantitative Quotes

## Purpose

This layer fixes the customer-facing gap between a good narrative report and a defensible quantitative report.

EventTrip-AgentOS now separates three kinds of numbers:

- public-source facts, such as match date, venue, official ticketing paths, and safety guidance;
- source-backed quote rows, such as a ticket, flight, hotel, or local-transport price with a public source URL;
- unknown values, where no reliable public source has been registered yet.

The customer-facing HTML report only shows dollar price curves and traveler total-cost rows when source-backed quote rows exist. If the project cannot verify a ticket, flight, hotel, transport, or total-cost value, the HTML says so directly.

## Data Model

Source-backed quote rows use this CSV/JSON schema:

```text
quote_date,match_id,component,amount,currency,source_id,source_url,source_label,origin,confidence,notes
```

Supported components:

- `ticket`
- `pit_flight`
- `sea_flight`
- `hotel`
- `local_transport`

For the current customer report, `hotel` and `local_transport` are treated as per-person shared-cost values for the recommended one-night plan. The row must include an `https://` source URL and a `source_id` for field-level attribution. Saved `WebEvidence` with a public HTTPS URL can also be converted into reportable quote rows; local fixtures and evidence without a public URL are ignored.

## CLI Workflow

Preview a local source-backed quote file:

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
python -m eventtrip.source_backed_quotes_cli import --input examples\reviewed_quote_import.csv --match portugal_dr_congo --dry-run
```

Import source-backed rows into the local ignored data file:

```powershell
python -m eventtrip.source_backed_quotes_cli import --input examples\reviewed_quote_import.csv --match portugal_dr_congo
```

Summarize currently available source-backed quotes:

```powershell
python -m eventtrip.source_backed_quotes_cli summary --match portugal_dr_congo
```

## HTML Behavior

The generated customer HTML includes `来源支撑报价与总成本曲线`.

If no source-backed quote rows exist, it states:

```text
目前没有可引用的来源支撑真实报价，因此不生成美元价格曲线。
```

If source-backed rows exist, it shows:

- latest ticket, PIT flight, SEA flight, hotel, and local transport rows;
- source links and `source_id` values for each quote;
- PIT and SEA source-backed total costs only when all required components are present;
- a dollar-value line chart using only source-backed quote rows.

## Safety Rules

- No web scraping.
- No automated purchasing.
- No automatic checkout or login.
- No price is inferred from local fixtures or evidence without a public source URL.
- Missing values stay unknown.
- `data/reviewed_quotes/*.csv` and `*.json` are ignored by Git by default.

## Why This Matters

This makes the HTML closer to a client-ready consulting artifact: it can show quantitative values when they are sourced, but it does not pretend incomplete data is complete.
