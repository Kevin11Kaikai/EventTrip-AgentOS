"""Conservative safety policy helpers for web collection.

These helpers reduce accidental misuse. They are not a legal guarantee and do
not replace source-specific terms of service or robots.txt review.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse, urlunparse

from eventtrip.web_collection.schemas import WebCollectionTarget


SUSPICIOUS_URL_WORDS = [
    "login",
    "checkout",
    "cart",
    "account",
    "payment",
    "captcha",
    "auth",
    "session",
]
LIVE_COLLECTION_POLICY = {
    "max_pages_per_command": 1,
    "robots_txt_required": True,
    "javascript_execution": False,
    "login_or_cookie_session": False,
    "max_response_bytes": 1_000_000,
    "default_live_http": False,
}


def normalize_url(url: str) -> str:
    """Normalize a public HTTP(S) URL without bypassing access controls."""
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def is_probably_disallowed_url(url: str) -> tuple[bool, str]:
    """Return whether a URL appears unsafe for this conservative collector."""
    if not url or not url.strip():
        return True, "URL must not be empty."

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        return True, "Live collection only supports http and https URLs."
    lowered = url.lower()
    for word in SUSPICIOUS_URL_WORDS:
        if word in lowered:
            return True, f"URL contains sensitive path word: {word}."
    return False, ""


def validate_collection_target(target: WebCollectionTarget) -> list[str]:
    """Validate a collection target with a conservative no-bypass policy."""
    errors: list[str] = []
    if not target.target_id.strip():
        errors.append("target_id must not be empty.")
    if not target.match_id.strip():
        errors.append("match_id must not be empty.")
    if bool(target.url) == bool(target.local_path):
        errors.append("Provide exactly one of url or local_path.")

    if target.url:
        disallowed, reason = is_probably_disallowed_url(target.url)
        if disallowed:
            errors.append(reason)
    if target.local_path:
        local_path = Path(target.local_path)
        if str(target.local_path).lower().startswith("file://"):
            errors.append("Use local_path directly; file:// URLs are not accepted.")
        elif not local_path.exists():
            errors.append(f"local_path does not exist: {target.local_path}")
    return errors


def collection_policy_summary() -> dict[str, object]:
    """Return the conservative live collection policy for CLI/docs/tests."""
    return dict(LIVE_COLLECTION_POLICY)
