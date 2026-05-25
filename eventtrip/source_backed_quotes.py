"""Convert source-backed web evidence into reportable quote rows.

This layer intentionally avoids a manual review gate, but it remains strict:
only evidence with a public HTTPS source URL can become a customer-facing quote.
Local fixtures, examples, and evidence without a source URL are ignored.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from eventtrip.reviewed_quotes import ReviewedQuote
from eventtrip.web_collection.evidence_store import list_web_evidence
from eventtrip.web_collection.schemas import WebEvidence


def load_source_backed_quotes_from_web_evidence(
    match_id: str = "portugal_dr_congo",
) -> list[ReviewedQuote]:
    """Load reportable quote rows from saved web evidence JSON files."""
    evidence_items = list_web_evidence(match_id=match_id)
    return quotes_from_web_evidence(evidence_items, match_id=match_id)


def quotes_from_web_evidence(
    evidence_items: list[WebEvidence],
    match_id: str = "portugal_dr_congo",
) -> list[ReviewedQuote]:
    """Convert source-backed evidence extraction fields into quote rows.

    The conversion is conservative. A quote row is created only when:
    - the evidence item matches ``match_id``;
    - the evidence has a public HTTPS ``source_url``;
    - the extracted amount is positive; and
    - the target/component can be represented by the current quote schema.
    """
    quotes: list[ReviewedQuote] = []
    for evidence in evidence_items:
        if evidence.match_id != match_id:
            continue
        if not evidence.source_url or not evidence.source_url.startswith("https://"):
            continue
        quote_date = _date_from_collected_at(evidence.collected_at)
        source_id = f"web_evidence:{evidence.evidence_id}"
        source_label = evidence.title or evidence.source_url
        fields = evidence.extracted_fields

        ticket_price = _positive_float(fields.get("candidate_lowest_price"))
        if ticket_price is not None:
            quotes.append(
                _quote(
                    quote_date=quote_date,
                    match_id=match_id,
                    component="ticket",
                    amount=ticket_price,
                    evidence=evidence,
                    source_id=source_id,
                    source_label=source_label,
                    notes="Source-backed web evidence extraction: candidate ticket price.",
                )
            )

        hotel_price = _positive_float(fields.get("candidate_hotel_price"))
        if hotel_price is not None:
            quotes.append(
                _quote(
                    quote_date=quote_date,
                    match_id=match_id,
                    component="hotel",
                    amount=hotel_price,
                    evidence=evidence,
                    source_id=source_id,
                    source_label=source_label,
                    notes="Source-backed web evidence extraction: candidate hotel price.",
                )
            )

        flight_price = _positive_float(fields.get("candidate_flight_price"))
        flight_component = _infer_flight_component(evidence)
        if flight_price is not None and flight_component is not None:
            quotes.append(
                _quote(
                    quote_date=quote_date,
                    match_id=match_id,
                    component=flight_component,
                    amount=flight_price,
                    evidence=evidence,
                    source_id=source_id,
                    source_label=source_label,
                    origin="PIT" if flight_component == "pit_flight" else "SEA",
                    notes="Source-backed web evidence extraction: candidate flight price.",
                )
            )
    return merge_quote_rows(quotes)


def merge_quote_rows(quotes: list[ReviewedQuote]) -> list[ReviewedQuote]:
    """Return deterministic quote rows with exact duplicates removed."""
    seen: set[tuple[Any, ...]] = set()
    merged: list[ReviewedQuote] = []
    for quote in sorted(quotes, key=lambda item: (item.quote_date, item.component, item.origin, item.source_id)):
        key = (
            quote.quote_date,
            quote.match_id,
            quote.component,
            quote.origin,
            quote.amount,
            quote.source_id,
            quote.source_url,
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(quote)
    return merged


def _quote(
    *,
    quote_date: str,
    match_id: str,
    component: str,
    amount: float,
    evidence: WebEvidence,
    source_id: str,
    source_label: str,
    origin: str = "",
    notes: str,
) -> ReviewedQuote:
    return ReviewedQuote(
        quote_date=quote_date,
        match_id=match_id,
        component=component,
        amount=amount,
        currency="USD",
        source_id=source_id,
        source_url=evidence.source_url or "",
        source_label=source_label,
        origin=origin,
        confidence=evidence.extraction_confidence if evidence.extraction_confidence in {"high", "medium", "low"} else "low",
        notes=notes,
    )


def _date_from_collected_at(value: str) -> str:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value[:10] if len(value) >= 10 else "1970-01-01"


def _positive_float(value: Any) -> float | None:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount if amount > 0 else None


def _infer_flight_component(evidence: WebEvidence) -> str | None:
    haystack = " ".join(
        str(part or "")
        for part in [
            evidence.target_id,
            evidence.title,
            evidence.source_url,
            evidence.local_path,
            evidence.notes,
            evidence.text_excerpt,
        ]
    ).lower()
    if "pit" in haystack or "pittsburgh" in haystack:
        return "pit_flight"
    if "sea" in haystack or "seattle" in haystack:
        return "sea_flight"
    return None
