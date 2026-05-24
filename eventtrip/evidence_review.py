"""Human-reviewed conversion from web evidence candidates to market snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.market_snapshots import (
    default_snapshot_path,
    find_snapshot_index,
    load_market_snapshots,
    snapshot_to_dict,
    upsert_market_snapshot,
    validate_market_snapshot,
)
from eventtrip.schemas import MarketSnapshot
from eventtrip.web_collection.evidence_store import load_web_evidence
from eventtrip.web_collection.schemas import WebEvidence, to_dict


def load_evidence_for_review(path: str | Path) -> WebEvidence:
    """Load one structured web evidence file for human review."""
    return load_web_evidence(path)


def summarize_evidence_for_review(evidence: WebEvidence) -> dict[str, Any]:
    """Return a compact summary of evidence candidates for CLI output."""
    fields = evidence.extracted_fields
    return {
        "evidence_id": evidence.evidence_id,
        "target_id": evidence.target_id,
        "match_id": evidence.match_id,
        "source_url": evidence.source_url,
        "local_path": evidence.local_path,
        "extraction_confidence": evidence.extraction_confidence,
        "candidate_lowest_price": fields.get("candidate_lowest_price"),
        "candidate_listings": fields.get("candidate_listings"),
        "candidate_hotel_price": fields.get("candidate_hotel_price"),
        "candidate_flight_price": fields.get("candidate_flight_price"),
        "warnings": list(fields.get("warnings", [])),
        "notes": evidence.notes,
    }


def validate_evidence_for_snapshot(evidence: WebEvidence) -> list[str]:
    """Return errors that prevent evidence from becoming a snapshot candidate."""
    errors: list[str] = []
    fields = evidence.extracted_fields
    if not evidence.match_id.strip():
        errors.append("evidence match_id must not be empty.")
    if fields.get("candidate_lowest_price") is None:
        errors.append("evidence is missing candidate_lowest_price.")
    if fields.get("candidate_listings") is None:
        errors.append("evidence is missing candidate_listings.")
    return errors


def build_snapshot_candidate(
    evidence: WebEvidence,
    snapshot_date: str,
    category_3_low: float,
    category_3_high: float,
    hotel_availability_score: float,
    flight_price_pressure: float,
    social_buzz_score: float,
    days_before_event: int,
    source_type: str = "reviewed_web_evidence",
    notes: str = "",
) -> MarketSnapshot:
    """Build a MarketSnapshot from reviewed evidence and explicit human inputs."""
    errors = validate_evidence_for_snapshot(evidence)
    if errors:
        raise ValueError("; ".join(errors))

    fields = evidence.extracted_fields
    review_notes = notes.strip()
    evidence_note = f"Reviewed web evidence {evidence.evidence_id}; confidence={evidence.extraction_confidence}."
    combined_notes = f"{review_notes} {evidence_note}".strip() if review_notes else evidence_note

    return MarketSnapshot(
        snapshot_date=snapshot_date,
        match_id=evidence.match_id,
        lowest_price=float(fields["candidate_lowest_price"]),
        listings=int(fields["candidate_listings"]),
        category_3_low=category_3_low,
        category_3_high=category_3_high,
        hotel_availability_score=hotel_availability_score,
        flight_price_pressure=flight_price_pressure,
        social_buzz_score=social_buzz_score,
        days_before_event=days_before_event,
        source_type=source_type,
        notes=combined_notes,
    )


def validate_snapshot_candidate(snapshot: MarketSnapshot) -> list[str]:
    """Validate a reviewed snapshot candidate with existing snapshot rules."""
    return validate_market_snapshot(snapshot)


def convert_reviewed_evidence_to_snapshot(
    evidence_path: str | Path,
    snapshot_date: str,
    category_3_low: float,
    category_3_high: float,
    hotel_availability_score: float,
    flight_price_pressure: float,
    social_buzz_score: float,
    days_before_event: int,
    source_type: str = "reviewed_web_evidence",
    notes: str = "",
    destination_path: str | Path | None = None,
    save: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Validate and optionally save one reviewed web evidence snapshot."""
    evidence = load_evidence_for_review(evidence_path)
    try:
        snapshot = build_snapshot_candidate(
            evidence=evidence,
            snapshot_date=snapshot_date,
            category_3_low=category_3_low,
            category_3_high=category_3_high,
            hotel_availability_score=hotel_availability_score,
            flight_price_pressure=flight_price_pressure,
            social_buzz_score=social_buzz_score,
            days_before_event=days_before_event,
            source_type=source_type,
            notes=notes,
        )
    except ValueError as exc:
        return {
            "status": "evidence_error",
            "saved": False,
            "errors": [str(exc)],
            "evidence": to_dict(evidence),
            "snapshot": None,
            "path": None,
        }

    errors = validate_snapshot_candidate(snapshot)
    destination = Path(destination_path) if destination_path else default_snapshot_path(snapshot.match_id)
    if errors:
        return {
            "status": "validation_error",
            "saved": False,
            "errors": errors,
            "evidence": to_dict(evidence),
            "snapshot": snapshot_to_dict(snapshot),
            "path": str(destination),
        }

    existing = load_market_snapshots(destination)
    duplicate_index = find_snapshot_index(existing, snapshot.match_id, snapshot.snapshot_date)
    if duplicate_index is not None and not overwrite:
        return {
            "status": "duplicate",
            "saved": False,
            "errors": [
                (
                    "Snapshot already exists for "
                    f"{snapshot.match_id} on {snapshot.snapshot_date}; use --overwrite to replace it."
                )
            ],
            "evidence": to_dict(evidence),
            "snapshot": snapshot_to_dict(snapshot),
            "path": str(destination),
        }

    if not save:
        action = "overwrite" if duplicate_index is not None else "append"
        return {
            "status": "dry_run",
            "saved": False,
            "would": action,
            "errors": [],
            "evidence": to_dict(evidence),
            "snapshot": snapshot_to_dict(snapshot),
            "path": str(destination),
        }

    result = upsert_market_snapshot(destination, snapshot, overwrite=overwrite)
    result["evidence"] = to_dict(evidence)
    result["snapshot"] = snapshot_to_dict(snapshot)
    return result
