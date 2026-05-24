"""Deterministic ticket link registry and recommendation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICKET_LINKS_PATH = PROJECT_ROOT / "data" / "ticket_links.yaml"
OFFICIAL_SOURCE_TYPES = {
    "official_primary",
    "official_resale",
    "official_info",
    "official_hospitality",
    "secondary_market",
}


def load_ticket_link_registry(path: str | Path = TICKET_LINKS_PATH) -> dict[str, Any]:
    """Load the deterministic local ticket link registry."""
    registry_path = Path(path)
    return yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}


def get_ticket_links(match_id: str, path: str | Path = TICKET_LINKS_PATH) -> list[dict[str, Any]]:
    """Return sorted ticket links for a match from the local registry."""
    registry = load_ticket_link_registry(path)
    match_data = registry.get(match_id)
    if not match_data:
        return []
    links = [dict(link) for link in match_data.get("links", [])]
    return sorted(links, key=lambda item: int(item.get("priority", 999)))


def recommend_ticket_links(
    match_id: str,
    ticket_timing: str = "monitor_with_wait_bias",
    path: str | Path = TICKET_LINKS_PATH,
) -> dict[str, Any]:
    """Return official-first ticket link recommendations for manual purchase."""
    registry = load_ticket_link_registry(path)
    match_data = registry.get(match_id, {})
    links = get_ticket_links(match_id, path)
    primary_links = [
        link
        for link in links
        if link.get("purchase_role")
        in {"recommended_official_entry", "recommended_verified_resale_entry"}
    ]
    info_links = [link for link in links if link.get("purchase_role") in {"info_only", "caution_reference"}]
    optional_links = [link for link in links if link.get("purchase_role") == "optional_official_premium_entry"]
    secondary_links = [link for link in links if link.get("purchase_role") == "secondary_market_candidate"]
    warnings = [
        "EventTrip-AgentOS recommends navigation links only; it does not purchase tickets.",
        "Prefer FIFA official ticketing and FIFA official resale/exchange before any non-FIFA source.",
        "StubHub can be monitored as a secondary marketplace, but it is not the FIFA official ticketing channel.",
        "Manually verify match, date, venue, category, quantity, all-in price, fees, transfer policy, and refund policy before paying.",
    ]
    if ticket_timing == "monitor_with_wait_bias":
        warnings.append(
            "Current timing remains Monitor with wait bias; use these links for monitoring and trigger-based purchase decisions."
        )

    return {
        "match_id": match_id,
        "verified_at": match_data.get("verified_at"),
        "ticket_timing": ticket_timing,
        "primary_links": primary_links,
        "info_links": info_links,
        "optional_links": optional_links,
        "secondary_links": secondary_links,
        "all_links": links,
        "warnings": warnings,
        "manual_purchase_checklist": manual_purchase_checklist(),
    }


def manual_purchase_checklist() -> list[str]:
    """Return the standard human checklist before buying tickets manually."""
    return [
        "Confirm the seller/page is official FIFA ticketing or official FIFA resale/exchange.",
        "Confirm the match is Portugal vs DR Congo.",
        "Confirm the date is June 17, 2026.",
        "Confirm the venue is NRG Stadium / Houston Stadium in Houston.",
        "Confirm seat category, quantity, all-in price, fees, transfer policy, and refund policy.",
        "Compare all-in price against the $550 buy trigger and $600 strong-consider trigger.",
        "If using StubHub or another third-party marketplace, confirm the ticket transfer method and buyer protection terms manually.",
        "Do not share payment details through unofficial links or messages.",
    ]


def validate_ticket_link_registry(path: str | Path = TICKET_LINKS_PATH) -> list[str]:
    """Return validation errors for the local ticket link registry."""
    errors: list[str] = []
    registry = load_ticket_link_registry(path)
    for match_id, match_data in registry.items():
        links = match_data.get("links", [])
        if not links:
            errors.append(f"{match_id} has no ticket links.")
        for link in links:
            link_id = link.get("link_id", "")
            url = link.get("url", "")
            source_type = link.get("source_type", "")
            if not link_id:
                errors.append(f"{match_id} has a link without link_id.")
            if not url.startswith("https://"):
                errors.append(f"{match_id}/{link_id} URL must use https.")
            if source_type not in OFFICIAL_SOURCE_TYPES:
                errors.append(f"{match_id}/{link_id} has unsupported source_type: {source_type}.")
            if not link.get("manual_checks"):
                errors.append(f"{match_id}/{link_id} must include manual_checks.")
    return errors
