"""Deterministic heuristic extraction from web evidence text."""

from __future__ import annotations

import re
from html.parser import HTMLParser

from eventtrip.web_collection.schemas import MarketEvidenceExtraction, to_dict


PRICE_RE = re.compile(r"\$\s*([0-9][0-9,]*(?:\.\d{1,2})?)")
LISTINGS_RE = re.compile(r"\b([0-9][0-9,]*)\s+(?:listings|tickets)\b", re.IGNORECASE)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        cleaned = data.strip()
        if cleaned:
            self.parts.append(cleaned)


def extract_text_from_html(html: str) -> str:
    """Strip HTML tags with the standard library and collapse whitespace."""
    parser = _TextExtractor()
    parser.feed(html)
    text = ". ".join(parser.parts)
    return re.sub(r"\s+", " ", text).strip()


def extract_market_evidence(text: str, match_id: str) -> MarketEvidenceExtraction:
    """Extract candidate prices/listings as unverified evidence, not facts."""
    normalized = re.sub(r"\s+", " ", text).strip()
    segments = _segments(normalized)
    lowest_price = _find_price_by_context(segments, include=("ticket", "lowest", "price"), exclude=("hotel", "night", "flight", "airfare"))
    hotel_price = _find_price_by_context(segments, include=("hotel", "night"), exclude=("flight", "airfare"))
    flight_price = _find_price_by_context(segments, include=("flight", "airfare"), exclude=("hotel", "night"))
    listings = _find_listing_count(normalized)

    if lowest_price is None:
        prices = _all_prices(normalized)
        lowest_price = prices[0] if prices else None

    warnings = [
        "Extracted values are heuristic candidates and require human review.",
    ]
    if lowest_price is None:
        warnings.append("No candidate ticket price found.")
    if listings is None:
        warnings.append("No candidate listings/tickets count found.")

    confidence = "medium" if lowest_price is not None and listings is not None else "low"
    summary_bits = []
    if lowest_price is not None:
        summary_bits.append(f"candidate lowest price ${lowest_price:.0f}")
    if listings is not None:
        summary_bits.append(f"candidate listings {listings}")
    if hotel_price is not None:
        summary_bits.append(f"candidate hotel price ${hotel_price:.0f}")
    if flight_price is not None:
        summary_bits.append(f"candidate flight price ${flight_price:.0f}")
    evidence_summary = "; ".join(summary_bits) if summary_bits else "No market candidates extracted."

    return MarketEvidenceExtraction(
        match_id=match_id,
        candidate_lowest_price=lowest_price,
        candidate_listings=listings,
        candidate_hotel_price=hotel_price,
        candidate_flight_price=flight_price,
        candidate_currency="USD" if any(value is not None for value in [lowest_price, hotel_price, flight_price]) else None,
        evidence_summary=evidence_summary,
        confidence=confidence,
        warnings=warnings,
    )


def extraction_to_dict(extraction: MarketEvidenceExtraction) -> dict:
    """Return a plain dictionary for an extraction result."""
    return to_dict(extraction)


def _segments(text: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", text) if segment.strip()]


def _all_prices(text: str) -> list[float]:
    return [float(match.group(1).replace(",", "")) for match in PRICE_RE.finditer(text)]


def _find_price_by_context(
    segments: list[str],
    include: tuple[str, ...],
    exclude: tuple[str, ...],
) -> float | None:
    for segment in segments:
        lowered = segment.lower()
        if not any(word in lowered for word in include):
            continue
        if any(word in lowered for word in exclude):
            continue
        prices = _all_prices(segment)
        if prices:
            return prices[0]
    return None


def _find_listing_count(text: str) -> int | None:
    match = LISTINGS_RE.search(text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))
