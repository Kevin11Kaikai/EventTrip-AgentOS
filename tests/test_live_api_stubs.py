import pytest

from eventtrip.data_providers.config import get_provider
from eventtrip.data_providers.import_provider import SnapshotImportProvider
from eventtrip.data_providers.live_api_stubs import (
    LiveProviderDisabledError,
    OfficialFlightAPIProvider,
    OfficialHotelAPIProvider,
    OfficialTicketAPIProvider,
)


def test_official_ticket_provider_is_disabled_by_default():
    provider = OfficialTicketAPIProvider()

    with pytest.raises(LiveProviderDisabledError, match="disabled by default"):
        provider.get_snapshots("portugal_dr_congo")


def test_official_hotel_provider_does_not_call_external_api(monkeypatch):
    monkeypatch.delenv("EVENTTRIP_HOTEL_API_KEY", raising=False)
    provider = OfficialHotelAPIProvider(enable_live=True)

    with pytest.raises(LiveProviderDisabledError, match="EVENTTRIP_HOTEL_API_KEY"):
        provider.get_hotel_quotes("Houston", "2026-06-16", "2026-06-17")


def test_official_flight_provider_does_not_call_external_api(monkeypatch):
    monkeypatch.delenv("EVENTTRIP_FLIGHT_API_KEY", raising=False)
    provider = OfficialFlightAPIProvider(enable_live=True)

    with pytest.raises(LiveProviderDisabledError, match="EVENTTRIP_FLIGHT_API_KEY"):
        provider.get_flight_quotes("PIT", "Houston", "2026-06-16", "2026-06-18")


def test_get_provider_official_ticket_fails_closed_by_default():
    with pytest.raises(LiveProviderDisabledError, match="disabled by default"):
        get_provider("official_ticket_api")


def test_get_provider_import_file_still_works():
    provider = get_provider("import_file", input_path="examples/external_snapshot_import.csv")

    assert isinstance(provider, SnapshotImportProvider)
    assert len(provider.load_snapshots("portugal_dr_congo")) == 2
