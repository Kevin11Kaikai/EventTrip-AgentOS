"""Source-backed quote intake and analysis utilities.

This module is intentionally conservative. It only works with local,
source-backed rows that include source metadata. It does not collect live data,
call APIs, scrape websites, or infer prices from text without a public source.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "reviewed_quotes"

QUOTE_COLUMNS = [
    "quote_date",
    "match_id",
    "component",
    "amount",
    "currency",
    "source_id",
    "source_url",
    "source_label",
    "origin",
    "confidence",
    "notes",
]

SUPPORTED_COMPONENTS = {
    "ticket",
    "pit_flight",
    "sea_flight",
    "hotel",
    "local_transport",
}

COMPONENT_LABELS = {
    "ticket": "门票",
    "pit_flight": "PIT 出发机票",
    "sea_flight": "SEA 出发机票",
    "hotel": "酒店人均分摊",
    "local_transport": "本地交通人均分摊",
}

SUPPORTED_CONFIDENCE = {"high", "medium", "low"}


@dataclass(frozen=True)
class ReviewedQuote:
    """One source-backed quote row with field-level source metadata."""

    quote_date: str
    match_id: str
    component: str
    amount: float
    currency: str = "USD"
    source_id: str = ""
    source_url: str = ""
    source_label: str = ""
    origin: str = ""
    confidence: str = "medium"
    notes: str = ""


def default_reviewed_quotes_path(match_id: str = "portugal_dr_congo") -> Path:
    """Return the default local source-backed quote CSV path for a match."""
    return DATA_DIR / f"{match_id}_quotes.csv"


def quote_to_dict(quote: ReviewedQuote) -> dict[str, Any]:
    """Return a JSON-serializable dictionary for a source-backed quote."""
    return {
        "quote_date": quote.quote_date,
        "match_id": quote.match_id,
        "component": quote.component,
        "amount": quote.amount,
        "currency": quote.currency,
        "source_id": quote.source_id,
        "source_url": quote.source_url,
        "source_label": quote.source_label,
        "origin": quote.origin,
        "confidence": quote.confidence,
        "notes": quote.notes,
    }


def load_reviewed_quotes(
    path: str | Path | None = None,
    match_id: str | None = None,
) -> list[ReviewedQuote]:
    """Load source-backed quote rows from CSV or JSON.

    Missing files return an empty list. Invalid rows raise ``ValueError`` so bad
    data cannot silently enter customer-facing reports.
    """
    quote_path = Path(path) if path is not None else default_reviewed_quotes_path(match_id or "portugal_dr_congo")
    if not quote_path.exists():
        return []

    suffix = quote_path.suffix.lower()
    if suffix == ".csv":
        rows = _read_csv_rows(quote_path)
    elif suffix == ".json":
        rows = _read_json_rows(quote_path)
    else:
        raise ValueError(f"Unsupported source-backed quote file type: {quote_path.suffix}")

    quotes: list[ReviewedQuote] = []
    for row_number, row in enumerate(rows, start=2):
        quote = _quote_from_mapping(row)
        errors = validate_reviewed_quote(quote)
        if errors:
            joined = "; ".join(errors)
            raise ValueError(f"Invalid source-backed quote row {row_number}: {joined}")
        if match_id is None or quote.match_id == match_id:
            quotes.append(quote)
    return sorted(quotes, key=lambda item: (item.quote_date, item.component, item.origin))


def save_reviewed_quotes(path: str | Path, quotes: list[ReviewedQuote]) -> None:
    """Save source-backed quotes to CSV with stable column order."""
    quote_path = Path(path)
    quote_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(quotes, key=lambda item: (item.quote_date, item.component, item.origin))
    with quote_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUOTE_COLUMNS)
        writer.writeheader()
        for quote in ordered:
            writer.writerow(quote_to_dict(quote))


def validate_reviewed_quote(quote: ReviewedQuote) -> list[str]:
    """Return validation errors for one source-backed quote."""
    errors: list[str] = []
    if not quote.match_id.strip():
        errors.append("match_id is required.")
    if quote.component not in SUPPORTED_COMPONENTS:
        errors.append(
            "component must be one of: " + ", ".join(sorted(SUPPORTED_COMPONENTS)) + "."
        )
    try:
        datetime.strptime(quote.quote_date, "%Y-%m-%d")
    except ValueError:
        errors.append("quote_date must use YYYY-MM-DD.")
    if quote.amount <= 0:
        errors.append("amount must be positive.")
    if quote.currency.upper() != "USD":
        errors.append("currency must be USD for the current customer report.")
    if quote.confidence not in SUPPORTED_CONFIDENCE:
        errors.append("confidence must be one of: high, medium, low.")
    if not quote.source_id.strip():
        errors.append("source_id is required for field-level attribution.")
    if not quote.source_label.strip():
        errors.append("source_label is required.")
    if not quote.source_url.startswith("https://"):
        errors.append("source_url must be an https URL.")
    return errors


def find_reviewed_quote_index(
    quotes: list[ReviewedQuote],
    match_id: str,
    quote_date: str,
    component: str,
    origin: str = "",
) -> int | None:
    """Return the index for a duplicate quote key, if present."""
    for index, quote in enumerate(quotes):
        if (
            quote.match_id == match_id
            and quote.quote_date == quote_date
            and quote.component == component
            and quote.origin == origin
        ):
            return index
    return None


def upsert_reviewed_quote(
    path: str | Path,
    quote: ReviewedQuote,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Append or replace one source-backed quote row."""
    errors = validate_reviewed_quote(quote)
    if errors:
        return {"status": "validation_error", "saved": False, "errors": errors}

    quote_path = Path(path)
    quotes = load_reviewed_quotes(quote_path) if quote_path.exists() else []
    duplicate_index = find_reviewed_quote_index(
        quotes,
        quote.match_id,
        quote.quote_date,
        quote.component,
        quote.origin,
    )
    if duplicate_index is not None and not overwrite:
        return {
            "status": "duplicate",
            "saved": False,
            "errors": [
                "Source-backed quote already exists for "
                f"{quote.match_id} {quote.quote_date} {quote.component} {quote.origin}; "
                "use --overwrite to replace it."
            ],
        }
    if duplicate_index is None:
        quotes.append(quote)
        status = "appended"
    else:
        quotes[duplicate_index] = quote
        status = "overwritten"
    save_reviewed_quotes(quote_path, quotes)
    return {"status": status, "saved": True, "errors": []}


def import_reviewed_quotes(
    input_path: str | Path,
    destination_path: str | Path,
    match_id: str | None = "portugal_dr_congo",
    overwrite: bool = False,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Validate and optionally import source-backed quote rows into a local CSV."""
    incoming = load_reviewed_quotes(input_path, match_id=match_id)
    if not incoming:
        return {
            "status": "no_data",
            "saved": False,
            "quote_count": 0,
            "errors": ["No source-backed quotes matched the requested match_id."],
            "quotes": [],
        }

    destination = Path(destination_path)
    existing = load_reviewed_quotes(destination) if destination.exists() else []
    duplicate_errors = []
    for quote in incoming:
        if (
            find_reviewed_quote_index(
                existing,
                quote.match_id,
                quote.quote_date,
                quote.component,
                quote.origin,
            )
            is not None
            and not overwrite
        ):
            duplicate_errors.append(
                f"{quote.match_id} {quote.quote_date} {quote.component} {quote.origin}"
            )
    if duplicate_errors:
        return {
            "status": "duplicate",
            "saved": False,
            "quote_count": len(incoming),
            "errors": ["Duplicate source-backed quote rows: " + ", ".join(duplicate_errors)],
            "quotes": [quote_to_dict(quote) for quote in incoming],
        }

    if dry_run:
        return {
            "status": "dry_run",
            "saved": False,
            "quote_count": len(incoming),
            "errors": [],
            "quotes": [quote_to_dict(quote) for quote in incoming],
        }

    for quote in incoming:
        result = upsert_reviewed_quote(destination, quote, overwrite=overwrite)
        if not result["saved"]:
            return {
                "status": result["status"],
                "saved": False,
                "quote_count": len(incoming),
                "errors": result["errors"],
                "quotes": [quote_to_dict(item) for item in incoming],
            }
    return {
        "status": "saved",
        "saved": True,
        "quote_count": len(incoming),
        "errors": [],
        "quotes": [quote_to_dict(quote) for quote in incoming],
    }


def analyze_reviewed_quotes(quotes: list[ReviewedQuote]) -> dict[str, Any]:
    """Analyze source-backed quotes for component coverage and traveler totals."""
    ordered = sorted(quotes, key=lambda item: (item.quote_date, item.component, item.origin))
    latest_by_component = _latest_by_component(ordered)
    required_pit = ["ticket", "pit_flight", "hotel", "local_transport"]
    required_sea = ["ticket", "sea_flight", "hotel", "local_transport"]
    pit_missing = [component for component in required_pit if component not in latest_by_component]
    sea_missing = [component for component in required_sea if component not in latest_by_component]
    pit_total = _component_total(latest_by_component, required_pit)
    sea_total = _component_total(latest_by_component, required_sea)
    timeline = _cost_timeline(ordered)
    return {
        "quote_count": len(ordered),
        "components_present": sorted(latest_by_component),
        "latest_by_component": {
            component: quote_to_dict(quote)
            for component, quote in latest_by_component.items()
        },
        "missing_components": {
            "pit": pit_missing,
            "sea": sea_missing,
        },
        "latest_totals": {
            "pit": pit_total,
            "sea": sea_total,
        },
        "timeline": timeline,
    }


def _latest_by_component(quotes: list[ReviewedQuote]) -> dict[str, ReviewedQuote]:
    latest: dict[str, ReviewedQuote] = {}
    for quote in quotes:
        latest[quote.component] = quote
    return latest


def _component_total(
    latest_by_component: dict[str, ReviewedQuote],
    components: list[str],
) -> float | None:
    if any(component not in latest_by_component for component in components):
        return None
    return round(sum(latest_by_component[component].amount for component in components), 2)


def _cost_timeline(quotes: list[ReviewedQuote]) -> list[dict[str, Any]]:
    dates = sorted({quote.quote_date for quote in quotes})
    timeline: list[dict[str, Any]] = []
    latest: dict[str, ReviewedQuote] = {}
    for quote_date in dates:
        for quote in [item for item in quotes if item.quote_date == quote_date]:
            latest[quote.component] = quote
        pit_total = _component_total(latest, ["ticket", "pit_flight", "hotel", "local_transport"])
        sea_total = _component_total(latest, ["ticket", "sea_flight", "hotel", "local_transport"])
        timeline.append(
            {
                "quote_date": quote_date,
                "ticket": _amount_or_none(latest.get("ticket")),
                "pit_flight": _amount_or_none(latest.get("pit_flight")),
                "sea_flight": _amount_or_none(latest.get("sea_flight")),
                "hotel": _amount_or_none(latest.get("hotel")),
                "local_transport": _amount_or_none(latest.get("local_transport")),
                "pit_total": pit_total,
                "sea_total": sea_total,
            }
        )
    return timeline


def _amount_or_none(quote: ReviewedQuote | None) -> float | None:
    return quote.amount if quote else None


def _quote_from_mapping(row: dict[str, Any]) -> ReviewedQuote:
    return ReviewedQuote(
        quote_date=str(row.get("quote_date", "")).strip(),
        match_id=str(row.get("match_id", "")).strip(),
        component=str(row.get("component", "")).strip().lower(),
        amount=float(str(row.get("amount", "0")).replace(",", "")),
        currency=str(row.get("currency", "USD")).strip().upper() or "USD",
        source_id=str(row.get("source_id", "")).strip(),
        source_url=str(row.get("source_url", "")).strip(),
        source_label=str(row.get("source_label", "")).strip(),
        origin=str(row.get("origin", "")).strip(),
        confidence=str(row.get("confidence", "medium")).strip().lower() or "medium",
        notes=str(row.get("notes", "")).strip(),
    )


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            dict(row)
            for row in csv.DictReader(handle)
            if any(str(value).strip() for value in row.values())
        ]


def _read_json_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Source-backed quote JSON must contain a list of objects.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError("Source-backed quote JSON rows must be objects.")
    return [dict(item) for item in data]
