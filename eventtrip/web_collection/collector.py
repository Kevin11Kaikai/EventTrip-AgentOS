"""Safe opt-in web evidence collector."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from urllib.request import Request, urlopen

from eventtrip.web_collection.extractor import extract_market_evidence, extract_text_from_html
from eventtrip.web_collection.policies import normalize_url, validate_collection_target
from eventtrip.web_collection.schemas import WebCollectionTarget, WebEvidence, to_dict


DEFAULT_USER_AGENT = "EventTrip-AgentOS research prototype; contact: local user"


class WebCollector:
    """Collect one local file or one explicitly enabled public HTTP page."""

    def __init__(self, timeout_seconds: int = 10, user_agent: str = DEFAULT_USER_AGENT) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def collect_target(
        self,
        target: WebCollectionTarget,
        cache_dir: Path | str,
        live_http: bool = False,
        save_raw: bool = False,
    ) -> WebEvidence:
        """Collect a target and return structured evidence without writing snapshots."""
        errors = validate_collection_target(target)
        if errors:
            raise ValueError("; ".join(errors))

        collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if target.local_path:
            raw_text = Path(target.local_path).read_text(encoding="utf-8")
            source_url = None
            local_path = str(Path(target.local_path))
        elif target.url:
            if not live_http:
                raise ValueError("Live HTTP collection is disabled unless --live-http is explicitly passed.")
            source_url = normalize_url(target.url)
            local_path = None
            raw_text = self._collect_http(source_url)
        else:  # pragma: no cover - validation already catches this
            raise ValueError("No collection source provided.")

        readable_text = extract_text_from_html(raw_text) if _looks_like_html(raw_text) else raw_text
        extraction = extract_market_evidence(readable_text, target.match_id)
        evidence_id = _safe_evidence_id(target.target_id, collected_at)
        raw_cache_path = None
        if save_raw:
            raw_cache_path = str(_write_raw_cache(cache_dir, evidence_id, raw_text))

        return WebEvidence(
            evidence_id=evidence_id,
            target_id=target.target_id,
            match_id=target.match_id,
            source_url=source_url,
            local_path=local_path,
            collected_at=collected_at,
            title=_extract_title(raw_text),
            text_excerpt=readable_text[:500],
            raw_cache_path=raw_cache_path,
            extraction_confidence=extraction.confidence,
            extracted_fields=to_dict(extraction),
            notes=target.notes,
        )

    def _collect_http(self, url: str) -> str:
        _ensure_robots_allows(url, self.user_agent)
        request = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise ValueError(f"HTTP collection failed with status {status}.")
            return response.read().decode("utf-8", errors="replace")


def _looks_like_html(text: str) -> bool:
    lowered = text[:500].lower()
    return "<html" in lowered or "<p" in lowered or "<h1" in lowered or "<body" in lowered


def _safe_evidence_id(target_id: str, collected_at: str) -> str:
    stem = "".join(char if char.isalnum() or char in "-_" else "_" for char in target_id.lower())
    digest = hashlib.sha1(f"{target_id}:{collected_at}".encode("utf-8")).hexdigest()[:10]
    return f"{stem}_{digest}"


def _write_raw_cache(cache_dir: Path | str, evidence_id: str, raw_text: str) -> Path:
    raw_dir = Path(cache_dir) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{evidence_id}.txt"
    path.write_text(raw_text, encoding="utf-8")
    return path


def _extract_title(raw_text: str) -> str | None:
    if not _looks_like_html(raw_text):
        return None
    lowered = raw_text.lower()
    start = lowered.find("<title")
    if start == -1:
        return None
    start_close = lowered.find(">", start)
    end = lowered.find("</title>", start_close)
    if start_close == -1 or end == -1:
        return None
    title = raw_text[start_close + 1 : end].strip()
    return title or None


def _ensure_robots_allows(url: str, user_agent: str) -> None:
    parsed = urlparse(url)
    robots_url = urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception as exc:
        raise ValueError(f"Could not verify robots.txt for live collection: {exc}") from exc
    if not parser.can_fetch(user_agent, url):
        raise ValueError("robots.txt does not allow this URL for the EventTrip-AgentOS collector.")
