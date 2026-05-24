# Opt-In Live Data Integration

## Purpose

Phase 8.0 adds a safe provider path for future official or search API data. The default EventTrip-AgentOS demo remains deterministic and offline.

## What Is Implemented

- `OptInHttpJsonProvider` can normalize snapshot-shaped JSON into `MarketSnapshot` objects.
- Local JSON fixtures can be previewed without network access.
- Real HTTP JSON endpoints require explicit opt-in.
- Reviewed live/API snapshots can be imported only after explicit human approval.
- The HTML report includes an `Opt-In Live Data Status` section.

## Safety Rules

- No live API call happens in the default orchestrator, dashboard, tests, or MCP validation.
- Live HTTP requires `--live-http`.
- Live HTTP also requires `EVENTTRIP_ENABLE_LIVE_PROVIDERS=true`.
- Endpoint hosts must be explicitly allowlisted.
- Optional API tokens must come from environment variables.
- Snapshot CSV writes require `--save --reviewed`.
- Dry-run is the default review behavior.
- Source-backed HTML displays only rows that were saved as `reviewed_live_data`.
- Missing or unverifiable values stay unknown; they are not invented.

## Fixture Preview

```powershell
conda activate eventtrip_mcp
cd D:\others\Eventrip_agentos
python -m eventtrip.live_data_cli preview --input examples\live_api_snapshot_response.json --match portugal_dr_congo
```

This command does not make a network call.

## Reviewed Import Workflow

Preview and validate a local API-shaped payload without writing:

```powershell
python -m eventtrip.live_data_cli import --input examples\live_api_snapshot_response.json --match portugal_dr_congo --dry-run
```

If a human has checked the source, match, date, price, listing count, and notes, save it explicitly:

```powershell
python -m eventtrip.live_data_cli import --input examples\live_api_snapshot_response.json --match portugal_dr_congo --save --reviewed
```

Duplicate match/date rows fail safely unless `--overwrite` is provided. Use `--destination` for testing against a temporary CSV before touching the default manual snapshot file.

The reviewed import path marks saved rows with `source_type=reviewed_live_data` and preserves the original provider source type in the notes.

## Source-Backed HTML Display

Phase 8.2 adds a reviewed live-data section to the source-backed HTML report.

Only snapshots with:

```text
source_type=reviewed_live_data
```

are shown in that section. Unreviewed live/API previews, local fixture previews, and ordinary manual/mock snapshots remain out of the public live-data table.

If no reviewed live/API snapshots exist, the HTML report says no opt-in live API payload is attached.

The Chinese HTML report also includes a forecast section. Exact dollar prices are displayed only when reviewed source-backed data exists. Otherwise the page uses pressure-index charts and says that unverifiable values remain unknown.

## Live HTTP Preview

Only use this with an endpoint you are allowed to call:

```powershell
$env:EVENTTRIP_ENABLE_LIVE_PROVIDERS="true"
$env:EVENTTRIP_LIVE_API_ALLOWED_HOSTS="api.example.com"
python -m eventtrip.live_data_cli preview --endpoint-url https://api.example.com/snapshots --allow-host api.example.com --match portugal_dr_congo --live-http
```

If an API key is required:

```powershell
$env:EVENTTRIP_TICKET_API_KEY="..."
python -m eventtrip.live_data_cli preview --endpoint-url https://api.example.com/snapshots --allow-host api.example.com --api-key-env EVENTTRIP_TICKET_API_KEY --match portugal_dr_congo --live-http
```

Do not commit API keys or `.env`.

## Expected JSON Shape

The provider accepts either a single snapshot object, a list of snapshot objects, or an object with a `snapshots` list.

Required fields:

- `snapshot_date`
- `match_id`
- `lowest_price`
- `listings`
- `category_3_low`
- `category_3_high`
- `hotel_availability_score`
- `flight_price_pressure`
- `social_buzz_score`
- `days_before_event`

Optional fields:

- `source_type`
- `notes`

## What This Does Not Do

- No web scraping.
- No login bypass.
- No CAPTCHA bypass.
- No automated purchase.
- No high-frequency polling.
- No default live calls.
