import pytest

from eventtrip.data_providers.config import get_provider
from eventtrip.data_providers.live_api_stubs import LiveProviderDisabledError
from eventtrip.data_providers.opt_in_http_provider import OptInHttpJsonProvider
from eventtrip import live_data_cli


def test_opt_in_provider_loads_local_fixture_without_live_http():
    provider = OptInHttpJsonProvider(input_path="examples/live_api_snapshot_response.json")
    preview = provider.preview(match_id="portugal_dr_congo")

    assert preview["status"] == "ok"
    assert preview["live_http"] is False
    assert preview["snapshot_count"] == 1
    assert preview["snapshots"][0]["lowest_price"] == 640
    assert preview["snapshots"][0]["source_type"] == "opt_in_api_fixture"


def test_opt_in_provider_rejects_http_without_live_flag(monkeypatch):
    monkeypatch.setenv("EVENTTRIP_ENABLE_LIVE_PROVIDERS", "true")
    provider = OptInHttpJsonProvider(
        endpoint_url="https://api.example.test/snapshots",
        allowed_hosts=["api.example.test"],
    )

    with pytest.raises(LiveProviderDisabledError, match="--live-http"):
        provider.preview(match_id="portugal_dr_congo", live_http=False)


def test_opt_in_provider_rejects_unallowed_host(monkeypatch):
    monkeypatch.setenv("EVENTTRIP_ENABLE_LIVE_PROVIDERS", "true")
    provider = OptInHttpJsonProvider(
        endpoint_url="https://api.example.test/snapshots",
        allowed_hosts=["other.example.test"],
    )

    with pytest.raises(LiveProviderDisabledError, match="allowlist"):
        provider.preview(match_id="portugal_dr_congo", live_http=True)


def test_get_provider_opt_in_http_json_works_with_fixture():
    provider = get_provider(
        "opt_in_http_json",
        input_path="examples/live_api_snapshot_response.json",
    )

    assert provider.preview("portugal_dr_congo")["snapshot_count"] == 1


def test_live_data_cli_preview_fixture_outputs_no_live_call(capsys):
    code = live_data_cli.main(
        [
            "preview",
            "--input",
            "examples/live_api_snapshot_response.json",
            "--match",
            "portugal_dr_congo",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert '"snapshot_count": 1' in output
    assert "No live HTTP call was made." in output
