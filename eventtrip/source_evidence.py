"""Source-backed evidence registry for public web/news report artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_EVIDENCE_PATH = PROJECT_ROOT / "data" / "source_evidence.yaml"
ALLOWED_SOURCE_TYPES = {
    "official",
    "news",
    "government",
    "transportation",
    "marketplace",
    "travel_data",
}
SOURCE_CITATION_GROUPS: dict[str, dict[str, Any]] = {
    "match_facts": {
        "title": "Match facts",
        "tags": {"match", "date", "venue"},
    },
    "ticket_safety": {
        "title": "Ticket safety",
        "tags": {
            "tickets",
            "official_purchase",
            "official_resale",
            "ticket_safety",
            "resale_risk",
            "secondary_market",
        },
    },
    "houston_logistics": {
        "title": "Houston logistics",
        "tags": {"houston", "local_transport", "venue_readiness", "team_base_camp"},
    },
    "cost_trends": {
        "title": "Cost trend evidence",
        "tags": {"airfare_trend", "hotel_trend", "ticket_market_pressure"},
    },
}


@dataclass(frozen=True)
class FieldSourceAttribution:
    """Field-level source status for customer-facing report values."""

    field_id: str
    label: str
    status: str
    source_group: str
    source_ids: list[str]
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "label": self.label,
            "status": self.status,
            "source_group": self.source_group,
            "source_ids": list(self.source_ids),
            "note": self.note,
        }


def load_source_evidence(path: str | Path = SOURCE_EVIDENCE_PATH) -> dict[str, Any]:
    """Load public source evidence from the local curated registry."""
    source_path = Path(path)
    return yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}


def get_match_sources(match_id: str, path: str | Path = SOURCE_EVIDENCE_PATH) -> dict[str, Any]:
    """Return source evidence for one match."""
    registry = load_source_evidence(path)
    return dict(registry.get(match_id, {}))


def validate_source_evidence(path: str | Path = SOURCE_EVIDENCE_PATH) -> list[str]:
    """Return validation errors for the source evidence registry."""
    errors: list[str] = []
    registry = load_source_evidence(path)
    for match_id, match_data in registry.items():
        if not match_data.get("sources"):
            errors.append(f"{match_id} has no sources.")
        for source in match_data.get("sources", []):
            source_id = source.get("source_id", "")
            url = source.get("url", "")
            if not source_id:
                errors.append(f"{match_id} has source without source_id.")
            if not source.get("title"):
                errors.append(f"{match_id}/{source_id} missing title.")
            if not source.get("publisher"):
                errors.append(f"{match_id}/{source_id} missing publisher.")
            if not url.startswith("https://"):
                errors.append(f"{match_id}/{source_id} URL must use https.")
            if source.get("source_type") not in ALLOWED_SOURCE_TYPES:
                errors.append(f"{match_id}/{source_id} has unsupported source_type.")
            if not source.get("summary"):
                errors.append(f"{match_id}/{source_id} missing summary.")
    return errors


def sources_by_tag(match_sources: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    """Return sources with a given evidence tag."""
    return [
        dict(source)
        for source in match_sources.get("sources", [])
        if tag in source.get("evidence_tags", [])
    ]


def sources_by_any_tag(match_sources: dict[str, Any], tags: set[str]) -> list[dict[str, Any]]:
    """Return sources that include at least one tag from a tag group."""
    grouped: list[dict[str, Any]] = []
    for source in match_sources.get("sources", []):
        source_tags = set(source.get("evidence_tags", []))
        if source_tags.intersection(tags):
            grouped.append(dict(source))
    return grouped


def grouped_citations(match_sources: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return report-ready citation groups for source-backed public reports."""
    return {
        group_key: sources_by_any_tag(match_sources, set(group_config["tags"]))
        for group_key, group_config in SOURCE_CITATION_GROUPS.items()
    }


def build_field_source_attributions(
    match_sources: dict[str, Any],
) -> dict[str, FieldSourceAttribution]:
    """Return source status for individual visible report fields."""
    groups = grouped_citations(match_sources)
    match_source_ids = _source_ids(groups.get("match_facts", []))
    ticket_source_ids = _source_ids(groups.get("ticket_safety", []))
    official_ticket_source_ids = _source_ids(
        [
            source
            for source in groups.get("ticket_safety", [])
            if "secondary_market" not in source.get("evidence_tags", [])
        ]
    )
    secondary_ticket_source_ids = _source_ids(
        [
            source
            for source in groups.get("ticket_safety", [])
            if "secondary_market" in source.get("evidence_tags", [])
        ]
    )
    logistics_source_ids = _source_ids(groups.get("houston_logistics", []))
    trend_source_ids = _source_ids(groups.get("cost_trends", []))

    return {
        "match_name": FieldSourceAttribution(
            field_id="match_name",
            label="比赛名称",
            status="source_backed",
            source_group="比赛事实",
            source_ids=match_source_ids,
            note="比赛名称来自已登记的公开来源。",
        ),
        "match_date": FieldSourceAttribution(
            field_id="match_date",
            label="比赛日期",
            status="source_backed",
            source_group="比赛事实",
            source_ids=match_source_ids,
            note="比赛日期来自已登记的公开来源。",
        ),
        "match_venue": FieldSourceAttribution(
            field_id="match_venue",
            label="比赛场馆",
            status="source_backed",
            source_group="比赛事实",
            source_ids=match_source_ids,
            note="场馆名称来自已登记的公开来源；Houston Stadium 是 FIFA 场馆命名，NRG Stadium 是本地常用名称。",
        ),
        "official_ticket_path": FieldSourceAttribution(
            field_id="official_ticket_path",
            label="官方购票路径",
            status="source_backed",
            source_group="购票安全",
            source_ids=official_ticket_source_ids or ticket_source_ids,
            note="官方优先路径由 FIFA 票务/支持页面和公开购票安全来源支持。",
        ),
        "secondary_market_stubhub": FieldSourceAttribution(
            field_id="secondary_market_stubhub",
            label="StubHub 二级市场候选",
            status="source_backed",
            source_group="购票安全",
            source_ids=secondary_ticket_source_ids,
            note="StubHub 是二级市场候选渠道，不是 FIFA 官方票务来源。",
        ),
        "unknown_exact_prices": FieldSourceAttribution(
            field_id="unknown_exact_prices",
            label="精确价格与总预算",
            status="no_source_backed_data_found",
            source_group="未知或尚无来源支持",
            source_ids=[],
            note="精确含税费门票、机票、酒店和总预算没有登记公开来源支持，因此保持未知。",
        ),
        "reviewed_live_snapshots": FieldSourceAttribution(
            field_id="reviewed_live_snapshots",
            label="人工审核 Live/API snapshot",
            status="human_reviewed_data",
            source_group="人工审核数据",
            source_ids=[],
            note="只显示 source_type=reviewed_live_data 的行；未审核预览和普通手工行不会进入公开表格。",
        ),
        "forecast_chart": FieldSourceAttribution(
            field_id="forecast_chart",
            label="成本压力指数折线图",
            status="model_inference",
            source_group="价格趋势依据",
            source_ids=trend_source_ids,
            note="折线图是基于公开趋势来源和本地规则的压力指数，不是未核验的真实美元报价。",
        ),
        "pit_recommendation": FieldSourceAttribution(
            field_id="pit_recommendation",
            label="PIT 出发建议",
            status="model_inference",
            source_group="价格趋势依据 + 内部规划",
            source_ids=trend_source_ids,
            note="PIT 建议结合公开趋势来源、已审核 snapshot（如有）和内部旅行风险规则。",
        ),
        "sea_recommendation": FieldSourceAttribution(
            field_id="sea_recommendation",
            label="SEA 出发建议",
            status="model_inference",
            source_group="价格趋势依据 + 内部规划",
            source_ids=trend_source_ids,
            note="SEA 建议结合公开趋势来源、已审核 snapshot（如有）和更长航程风险。",
        ),
        "trigger_policy": FieldSourceAttribution(
            field_id="trigger_policy",
            label="触发价策略",
            status="internal_policy",
            source_group="内部确定性策略",
            source_ids=[],
            note="触发价是项目内置决策规则，不是公开市场价格事实。",
        ),
        "houston_logistics": FieldSourceAttribution(
            field_id="houston_logistics",
            label="休斯顿本地后勤",
            status="source_backed",
            source_group="休斯顿交通与住宿",
            source_ids=logistics_source_ids,
            note="本地交通、场馆和住宿压力背景来自已登记公开报道。",
        ),
    }


def citation_label(source: dict[str, Any]) -> str:
    """Return a concise Markdown citation label."""
    return f"[{source['publisher']}: {source['title']}]({source['url']})"


def _source_ids(sources: list[dict[str, Any]]) -> list[str]:
    return [str(source["source_id"]) for source in sources if source.get("source_id")]
