"""Opt-in HTTP JSON provider for future official/search API integrations."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from eventtrip.data_providers.live_api_stubs import LiveProviderDisabledError
from eventtrip.market_snapshots import snapshot_to_dict, validate_market_snapshot
from eventtrip.schemas import MarketSnapshot


ENABLE_LIVE_ENV = "EVENTTRIP_ENABLE_LIVE_PROVIDERS"
ALLOWED_HOSTS_ENV = "EVENTTRIP_LIVE_API_ALLOWED_HOSTS"
DEFAULT_USER_AGENT = "EventTrip-AgentOS opt-in API client; contact: local user"


class OptInHttpJsonProvider:
    """Load snapshot-like JSON from a local fixture or an explicitly enabled HTTP API.

    Live HTTP is disabled unless all of these are true:
    - caller passes live_http=True
    - EVENTTRIP_ENABLE_LIVE_PROVIDERS=true
    - endpoint host is in the explicit allowlist

    This provider does not scrape HTML, automate checkout, or call any endpoint
    during the default demo/test/dashboard paths.
    """

    def __init__(
        self,
        *,
        input_path: str | Path | None = None,
        endpoint_url: str | None = None,
        api_key_env: str | None = None,
        allowed_hosts: list[str] | None = None,
        timeout_seconds: int = 10,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        if not input_path and not endpoint_url:
            raise ValueError("input_path or endpoint_url is required.")
        self.input_path = Path(input_path) if input_path else None
        self.endpoint_url = endpoint_url
        self.api_key_env = api_key_env
        self.allowed_hosts = allowed_hosts or _allowed_hosts_from_env()
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def load_payload(self, live_http: bool = False) -> Any:
        """Return JSON payload from a local file or explicitly enabled HTTP endpoint."""
        if self.input_path:
            return json.loads(self.input_path.read_text(encoding="utf-8"))
        if not self.endpoint_url:
            raise ValueError("endpoint_url is not configured.")
        if not live_http:
            raise LiveProviderDisabledError("Live HTTP API loading requires --live-http.")
        _require_live_enabled()
        _validate_endpoint_allowed(self.endpoint_url, self.allowed_hosts)

        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        if self.api_key_env:
            api_key = os.getenv(self.api_key_env)
            if not api_key:
                raise LiveProviderDisabledError(f"{self.api_key_env} is required for this provider.")
            headers["Authorization"] = f"Bearer {api_key}"
        request = Request(self.endpoint_url, headers=headers)
        with urlopen(request, timeout=self.timeout_seconds) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise ValueError(f"API request failed with status {status}.")
            return json.loads(response.read().decode("utf-8", errors="replace"))

    def load_snapshots(
        self,
        match_id: str | None = None,
        live_http: bool = False,
    ) -> list[MarketSnapshot]:
        """Normalize JSON payload to validated MarketSnapshot objects."""
        payload = self.load_payload(live_http=live_http)
        snapshots = [_snapshot_from_dict(item) for item in _snapshot_items(payload)]
        filtered = [snapshot for snapshot in snapshots if match_id is None or snapshot.match_id == match_id]
        errors: list[str] = []
        for snapshot in filtered:
            errors.extend(validate_market_snapshot(snapshot))
        if errors:
            raise ValueError("; ".join(errors))
        return sorted(filtered, key=lambda snapshot: snapshot.snapshot_date)

    def preview(self, match_id: str | None = None, live_http: bool = False) -> dict[str, Any]:
        """Return a JSON-serializable preview without writing project data files."""
        snapshots = self.load_snapshots(match_id=match_id, live_http=live_http)
        return {
            "status": "ok",
            "source": str(self.input_path) if self.input_path else self.endpoint_url,
            "live_http": bool(live_http and self.endpoint_url),
            "snapshot_count": len(snapshots),
            "snapshots": [snapshot_to_dict(snapshot) for snapshot in snapshots],
        }


def _snapshot_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict) and isinstance(payload.get("snapshots"), list):
        return [dict(item) for item in payload["snapshots"]]
    if isinstance(payload, dict):
        return [dict(payload)]
    raise ValueError("Payload must be a snapshot object, list, or object with snapshots list.")


def _snapshot_from_dict(item: dict[str, Any]) -> MarketSnapshot:
    return MarketSnapshot(
        snapshot_date=str(item["snapshot_date"]),
        match_id=str(item["match_id"]),
        lowest_price=float(item["lowest_price"]),
        listings=int(item["listings"]),
        category_3_low=float(item["category_3_low"]),
        category_3_high=float(item["category_3_high"]),
        hotel_availability_score=float(item["hotel_availability_score"]),
        flight_price_pressure=float(item["flight_price_pressure"]),
        social_buzz_score=float(item["social_buzz_score"]),
        days_before_event=int(item["days_before_event"]),
        source_type=str(item.get("source_type", "opt_in_api")),
        notes=str(item.get("notes", "")),
    )


def _require_live_enabled() -> None:
    if os.getenv(ENABLE_LIVE_ENV, "").lower() != "true":
        raise LiveProviderDisabledError(
            f"Live API providers are disabled. Set {ENABLE_LIVE_ENV}=true and pass --live-http."
        )


def _allowed_hosts_from_env() -> list[str]:
    raw = os.getenv(ALLOWED_HOSTS_ENV, "")
    return [host.strip().lower() for host in raw.split(",") if host.strip()]


def _validate_endpoint_allowed(endpoint_url: str, allowed_hosts: list[str]) -> None:
    parsed = urlparse(endpoint_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("endpoint_url must use http or https.")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("endpoint_url must include a hostname.")
    allowed = {item.lower() for item in allowed_hosts}
    if host not in allowed:
        raise LiveProviderDisabledError(
            f"Host {host} is not in the live API allowlist. "
            f"Set {ALLOWED_HOSTS_ENV} or pass an explicit allowlist."
        )
