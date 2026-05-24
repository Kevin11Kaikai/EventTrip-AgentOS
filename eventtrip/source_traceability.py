"""Claim-level traceability helpers for public-source evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from eventtrip.source_evidence import citation_label, grouped_citations


@dataclass(frozen=True)
class EvidenceTraceabilityItem:
    """One report claim mapped to its evidence status."""

    claim_id: str
    claim: str
    status: str
    evidence_group: str
    evidence: list[str]
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim": self.claim,
            "status": self.status,
            "evidence_group": self.evidence_group,
            "evidence": list(self.evidence),
            "note": self.note,
        }


def build_evidence_traceability(match_sources: dict[str, Any]) -> list[EvidenceTraceabilityItem]:
    """Build deterministic claim-to-evidence mappings for the internal report.

    The matrix is intentionally conservative: values without a public source are
    marked as internal estimates or as not source-backed instead of being
    presented as real market facts.
    """
    groups = grouped_citations(match_sources)
    match_labels = _labels(groups.get("match_facts", []))
    ticket_sources = groups.get("ticket_safety", [])
    official_ticket_labels = _labels(
        [source for source in ticket_sources if "secondary_market" not in source.get("evidence_tags", [])]
    )
    secondary_ticket_labels = _labels(
        [source for source in ticket_sources if "secondary_market" in source.get("evidence_tags", [])]
    )
    logistics_labels = _labels(groups.get("houston_logistics", []))

    return [
        EvidenceTraceabilityItem(
            claim_id="claim-match-facts",
            claim="Portugal vs DR Congo 计划于 2026 年 6 月 17 日在 Houston 举行。",
            status="source_backed",
            evidence_group="比赛事实",
            evidence=match_labels,
            note="由已登记的官方、市场和新闻来源支持。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-official-ticket-paths",
            claim="人工购票应优先从 FIFA 官方票务或官方转售/换票路径开始。",
            status="source_backed",
            evidence_group="购票安全",
            evidence=official_ticket_labels,
            note="由 FIFA 票务/支持页面和公开购票安全报道支持。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-secondary-marketplace-stubhub",
            claim="StubHub 可以作为二级市场候选渠道监控，但不应被视为 FIFA 官方票务渠道。",
            status="source_backed",
            evidence_group="购票安全",
            evidence=secondary_ticket_labels,
            note="由已登记的市场来源和购票安全来源支持。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-houston-logistics",
            claim="出行前需要继续关注 Houston 本地交通和场馆准备情况。",
            status="source_backed",
            evidence_group="休斯顿交通与住宿",
            evidence=logistics_labels,
            note="由已登记的 Houston 公开报道支持。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-recommended-plan",
            claim="Option A: One-night balanced plan 是当前推荐旅行方案。",
            status="internal_estimate_not_source_backed",
            evidence_group="内部确定性规划",
            evidence=[],
            note="这是本地确定性规划逻辑给出的模型建议，不是公开来源事实。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-traveler-costs",
            claim="Traveler A 估算成本为 $1120，Traveler B 估算成本为 $1220。",
            status="internal_estimate_not_source_backed",
            evidence_group="内部确定性规划",
            evidence=[],
            note="这些是本地规划估算；目前没有登记公开来源支持完整机票、酒店、门票或总预算报价。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-ticket-timing",
            claim="当前购票时机判断是 Monitor with wait bias。",
            status="internal_estimate_not_source_backed",
            evidence_group="内部确定性规划",
            evidence=[],
            note="这结合了本地市场信号逻辑和人工 snapshot；不是已来源验证的实时市场建议。",
        ),
        EvidenceTraceabilityItem(
            claim_id="claim-unknown-exact-prices",
            claim="Portugal vs DR Congo 精确含税费门票价格、机票价格、酒店报价和总预算。",
            status="no_source_backed_data_found",
            evidence_group="未知或尚无来源支持",
            evidence=[],
            note="目前没有登记公开来源支持这些精确数值；报告会明确说明未知，而不是填入无来源数字。",
        ),
    ]


def format_traceability_markdown(items: list[EvidenceTraceabilityItem]) -> str:
    """Format traceability items as a compact Markdown table."""
    rows = [
        "| Claim ID | Claim | Evidence status | Source group | Evidence / note |",
        "|---|---|---|---|---|",
    ]
    for item in items:
        evidence_text = _evidence_text(item)
        rows.append(
            f"| <a id=\"{item.claim_id}\"></a>`{item.claim_id}` | {item.claim} | "
            f"{item.status} | {item.evidence_group} | {evidence_text} |"
        )
    return "\n".join(rows)


def _labels(sources: list[dict[str, Any]]) -> list[str]:
    return [citation_label(source) for source in sources]


def _evidence_text(item: EvidenceTraceabilityItem) -> str:
    if item.evidence:
        return "<br>".join(item.evidence)
    return item.note
