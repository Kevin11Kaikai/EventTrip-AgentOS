"""Schemas for safe web evidence collection."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class WebCollectionTarget:
    target_id: str
    url: str | None = None
    local_path: str | None = None
    match_id: str = "portugal_dr_congo"
    source_type: str = "public_web"
    notes: str = ""


@dataclass
class WebEvidence:
    evidence_id: str
    target_id: str
    match_id: str
    source_url: str | None
    local_path: str | None
    collected_at: str
    title: str | None
    text_excerpt: str
    raw_cache_path: str | None
    extraction_confidence: str
    extracted_fields: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class MarketEvidenceExtraction:
    match_id: str
    candidate_lowest_price: float | None
    candidate_listings: int | None
    candidate_hotel_price: float | None
    candidate_flight_price: float | None
    candidate_currency: str | None
    evidence_summary: str
    confidence: str
    warnings: list[str] = field(default_factory=list)


def to_dict(value: Any) -> dict[str, Any]:
    """Return a JSON-serializable dictionary for web collection dataclasses."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return dict(value)
