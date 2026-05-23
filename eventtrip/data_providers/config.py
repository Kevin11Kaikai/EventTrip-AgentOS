"""Deterministic provider registry for snapshot data sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eventtrip.data_providers.import_provider import SnapshotImportProvider
from eventtrip.data_providers.manual_snapshot_provider import ManualSnapshotProvider
from eventtrip.data_providers.mock_live_provider import MockLiveProvider


SUPPORTED_PROVIDER_TYPES = ["manual_csv", "mock_live", "import_file"]
DEFERRED_PROVIDER_TYPES = ["official_api", "web_scraper"]


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
    if provider_type == "official_api":
        raise NotImplementedError(
            "official_api providers are intentionally deferred and are not used by default."
        )
    if provider_type == "web_scraper":
        raise NotImplementedError(
            "web_scraper providers are intentionally deferred; Phase 6 does not scrape websites."
        )
    raise ValueError(
        f"Unsupported provider_type: {provider_type}. "
        f"Supported provider types: {SUPPORTED_PROVIDER_TYPES}."
    )
