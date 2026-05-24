"""Reviewed import flow for opt-in live/API snapshot previews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.data_providers.opt_in_http_provider import OptInHttpJsonProvider
from eventtrip.market_snapshots import (
    default_snapshot_path,
    find_snapshot_index,
    load_market_snapshots,
    snapshot_to_dict,
    upsert_market_snapshot,
    validate_market_snapshot,
)
from eventtrip.schemas import MarketSnapshot


def reviewed_live_snapshot(
    snapshot: MarketSnapshot,
    review_notes: str = "",
    source_type: str = "reviewed_live_data",
) -> MarketSnapshot:
    """Return a snapshot marked as human-reviewed live/API data."""
    original_note = snapshot.notes.strip()
    review_note = review_notes.strip()
    note_parts = [
        part
        for part in [
            review_note,
            (
                "Human-reviewed opt-in live/API preview; "
                f"original_source_type={snapshot.source_type}."
            ),
            original_note,
        ]
        if part
    ]
    return MarketSnapshot(
        snapshot_date=snapshot.snapshot_date,
        match_id=snapshot.match_id,
        lowest_price=snapshot.lowest_price,
        listings=snapshot.listings,
        category_3_low=snapshot.category_3_low,
        category_3_high=snapshot.category_3_high,
        hotel_availability_score=snapshot.hotel_availability_score,
        flight_price_pressure=snapshot.flight_price_pressure,
        social_buzz_score=snapshot.social_buzz_score,
        days_before_event=snapshot.days_before_event,
        source_type=source_type,
        notes=" ".join(note_parts),
    )


def import_reviewed_live_snapshots(
    *,
    input_path: str | Path | None = None,
    endpoint_url: str | None = None,
    match_id: str | None = "portugal_dr_congo",
    api_key_env: str | None = None,
    allowed_hosts: list[str] | None = None,
    live_http: bool = False,
    destination_path: str | Path | None = None,
    save: bool = False,
    reviewed: bool = False,
    overwrite: bool = False,
    review_notes: str = "",
) -> dict[str, Any]:
    """Validate and optionally save reviewed opt-in live/API snapshots.

    The function intentionally fails closed: writes require both ``save=True``
    and ``reviewed=True``. Dry-run mode is the default and never writes files.
    """
    provider = OptInHttpJsonProvider(
        input_path=input_path,
        endpoint_url=endpoint_url,
        api_key_env=api_key_env,
        allowed_hosts=allowed_hosts,
    )
    raw_snapshots = provider.load_snapshots(match_id=match_id, live_http=live_http)
    snapshots = [reviewed_live_snapshot(snapshot, review_notes=review_notes) for snapshot in raw_snapshots]
    source = str(input_path) if input_path else endpoint_url

    if not snapshots:
        return _result(
            status="no_data",
            saved=False,
            source=source,
            destination=destination_path,
            snapshots=[],
            errors=["No snapshots matched the requested match_id."],
            live_http=bool(live_http and endpoint_url),
        )

    destination = Path(destination_path) if destination_path else default_snapshot_path(snapshots[0].match_id)
    validation_errors = _validation_errors(snapshots)
    if validation_errors:
        return _result(
            status="validation_error",
            saved=False,
            source=source,
            destination=destination,
            snapshots=snapshots,
            errors=validation_errors,
            live_http=bool(live_http and endpoint_url),
        )

    duplicate_errors = _duplicate_errors(destination, snapshots, overwrite=overwrite)
    if duplicate_errors:
        return _result(
            status="duplicate",
            saved=False,
            source=source,
            destination=destination,
            snapshots=snapshots,
            errors=duplicate_errors,
            live_http=bool(live_http and endpoint_url),
        )

    if save and not reviewed:
        return _result(
            status="review_required",
            saved=False,
            source=source,
            destination=destination,
            snapshots=snapshots,
            errors=["Writing live/API-derived snapshots requires --reviewed."],
            live_http=bool(live_http and endpoint_url),
        )

    if not save:
        existing = load_market_snapshots(destination)
        would = "overwrite" if any(
            find_snapshot_index(existing, snapshot.match_id, snapshot.snapshot_date) is not None
            for snapshot in snapshots
        ) else "append"
        return _result(
            status="dry_run",
            saved=False,
            source=source,
            destination=destination,
            snapshots=snapshots,
            errors=[],
            live_http=bool(live_http and endpoint_url),
            extra={"would": would},
        )

    for snapshot in snapshots:
        upsert_market_snapshot(destination, snapshot, overwrite=overwrite)

    return _result(
        status="saved",
        saved=True,
        source=source,
        destination=destination,
        snapshots=snapshots,
        errors=[],
        live_http=bool(live_http and endpoint_url),
    )


def _validation_errors(snapshots: list[MarketSnapshot]) -> list[str]:
    errors: list[str] = []
    for snapshot in snapshots:
        for error in validate_market_snapshot(snapshot):
            errors.append(f"{snapshot.match_id}/{snapshot.snapshot_date}: {error}")
    return errors


def _duplicate_errors(
    destination: Path,
    snapshots: list[MarketSnapshot],
    overwrite: bool,
) -> list[str]:
    if overwrite:
        return []
    existing = load_market_snapshots(destination)
    errors = []
    for snapshot in snapshots:
        if find_snapshot_index(existing, snapshot.match_id, snapshot.snapshot_date) is not None:
            errors.append(
                "Snapshot already exists for "
                f"{snapshot.match_id} on {snapshot.snapshot_date}; use --overwrite to replace it."
            )
    return errors


def _result(
    *,
    status: str,
    saved: bool,
    source: str | None,
    destination: str | Path | None,
    snapshots: list[MarketSnapshot],
    errors: list[str],
    live_http: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "status": status,
        "saved": saved,
        "source": source,
        "destination": str(destination) if destination else None,
        "live_http": live_http,
        "snapshot_count": len(snapshots),
        "snapshots": [snapshot_to_dict(snapshot) for snapshot in snapshots],
        "errors": errors,
    }
    if extra:
        result.update(extra)
    return result
