"""Deterministic provider registry for snapshot data sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.data_providers.import_provider import SnapshotImportProvider
from eventtrip.data_providers.live_api_stubs import (
    LiveProviderDisabledError,
    OfficialFlightAPIProvider,
    OfficialHotelAPIProvider,
    OfficialTicketAPIProvider,
)
from eventtrip.data_providers.manual_snapshot_provider import ManualSnapshotProvider
from eventtrip.data_providers.mock_live_provider import MockLiveProvider
from eventtrip.data_providers.opt_in_http_provider import OptInHttpJsonProvider


SUPPORTED_PROVIDER_TYPES = [
    "manual_csv",
    "mock_live",
    "import_file",
    "opt_in_http_json",
    "official_ticket_api",
    "official_hotel_api",
    "official_flight_api",
]
DEFERRED_PROVIDER_TYPES = ["official_api", "search_api_snapshot", "web_scraper"]
OFFICIAL_PROVIDER_TYPES = {
    "official_ticket_api": OfficialTicketAPIProvider,
    "official_hotel_api": OfficialHotelAPIProvider,
    "official_flight_api": OfficialFlightAPIProvider,
}


def get_provider(provider_type: str, **kwargs: Any):
    """Return a deterministic provider instance or raise for deferred provider types."""
    if provider_type == "manual_csv":
        snapshot_dir = kwargs.get("snapshot_dir")
        return ManualSnapshotProvider(Path(snapshot_dir) if snapshot_dir else None)
    if provider_type == "mock_live":
        return MockLiveProvider()
    if provider_type == "import_file":
        input_path = kwargs.get("input_path")
        if not input_path:
            raise ValueError("input_path is required for provider_type='import_file'.")
        return SnapshotImportProvider(input_path)
    if provider_type == "opt_in_http_json":
        return OptInHttpJsonProvider(
            input_path=kwargs.get("input_path"),
            endpoint_url=kwargs.get("endpoint_url"),
            api_key_env=kwargs.get("api_key_env"),
            allowed_hosts=kwargs.get("allowed_hosts"),
            timeout_seconds=int(kwargs.get("timeout_seconds", 10)),
        )
    if provider_type in OFFICIAL_PROVIDER_TYPES:
        enable_live = bool(kwargs.get("enable_live", False))
        if not enable_live:
            raise LiveProviderDisabledError(
                f"{provider_type} is disabled by default. "
                "Use deterministic manual/import providers unless a future phase explicitly enables live APIs."
            )
        return OFFICIAL_PROVIDER_TYPES[provider_type](**kwargs)
    if provider_type == "official_api":
        raise NotImplementedError(
            "official_api providers are intentionally deferred and are not used by default."
        )
    if provider_type == "search_api_snapshot":
        raise NotImplementedError(
            "search_api_snapshot is intentionally deferred and is not used by default."
        )
    if provider_type == "web_scraper":
        raise NotImplementedError(
            "web_scraper providers are intentionally deferred; Phase 6 does not scrape websites."
        )
    raise ValueError(
        f"Unsupported provider_type: {provider_type}. "
        f"Supported provider types: {SUPPORTED_PROVIDER_TYPES}."
    )
