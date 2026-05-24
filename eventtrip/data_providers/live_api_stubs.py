"""Disabled-by-default stubs for future official API providers.

These classes define the intended adapter surface without making network calls,
requiring API keys, or adding provider-specific dependencies.
"""

from __future__ import annotations

import os
from typing import Any


class LiveProviderDisabledError(RuntimeError):
    """Raised when a future live provider is requested without safe implementation."""


class _DisabledOfficialProvider:
    provider_name = "official_provider"
    api_key_env = ""

    def __init__(self, enable_live: bool = False, **config: Any) -> None:
        self.enable_live = enable_live
        self.config = dict(config)
        self.api_key_present = bool(os.getenv(self.api_key_env)) if self.api_key_env else False

    def _raise_unavailable(self) -> None:
        if not self.enable_live:
            raise LiveProviderDisabledError(
                f"{self.provider_name} is disabled by default. "
                "Phase 6.1 defines the adapter contract only and does not make live API calls."
            )
        if not self.api_key_present:
            raise LiveProviderDisabledError(
                f"{self.provider_name} is not available because {self.api_key_env} is not configured."
            )
        raise NotImplementedError(
            f"{self.provider_name} integration is not implemented yet. "
            "Add an official API adapter in a future opt-in phase."
        )


class OfficialTicketAPIProvider(_DisabledOfficialProvider):
    """Future official ticket/resale API adapter stub."""

    provider_name = "official_ticket_api"
    api_key_env = "EVENTTRIP_TICKET_API_KEY"

    def get_snapshots(self, match_id: str):
        """Future method for normalized ticket market snapshots."""
        self._raise_unavailable()


class OfficialHotelAPIProvider(_DisabledOfficialProvider):
    """Future official hotel availability/quote API adapter stub."""

    provider_name = "official_hotel_api"
    api_key_env = "EVENTTRIP_HOTEL_API_KEY"

    def get_hotel_quotes(self, city: str, checkin: str, checkout: str, beds: int = 2):
        """Future method for normalized hotel quote data."""
        self._raise_unavailable()


class OfficialFlightAPIProvider(_DisabledOfficialProvider):
    """Future official flight quote API adapter stub."""

    provider_name = "official_flight_api"
    api_key_env = "EVENTTRIP_FLIGHT_API_KEY"

    def get_flight_quotes(self, origin: str, destination: str, depart_date: str, return_date: str):
        """Future method for normalized flight quote data."""
        self._raise_unavailable()
