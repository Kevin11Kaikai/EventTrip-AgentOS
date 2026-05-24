"""Safe, opt-in web evidence collection helpers."""

from eventtrip.web_collection.collector import WebCollector
from eventtrip.web_collection.extractor import extract_market_evidence, extract_text_from_html
from eventtrip.web_collection.schemas import (
    MarketEvidenceExtraction,
    WebCollectionTarget,
    WebEvidence,
)

__all__ = [
    "WebCollector",
    "extract_market_evidence",
    "extract_text_from_html",
    "MarketEvidenceExtraction",
    "WebCollectionTarget",
    "WebEvidence",
]
