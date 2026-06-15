"""Qizheng annual scoring from full natal chart + compute_dasha."""

from __future__ import annotations

from astro.annual.adapters.qizheng import QizhengAnnualContext
from astro.annual.models import ChineseSystemSnapshot
from astro.annual.scoring.levels import clamp_score, score_to_level

GOOD_LORDS = {"太陽", "太陰", "木星", "金星"}
CAUTION_LORDS = {"火星", "土星"}
KEY_PALACES = {"命宮", "財帛", "官祿", "夫妻", "疾厄", "福德", "遷移"}


def score_qizheng_annual(context: QizhengAnnualContext) -> ChineseSystemSnapshot:
    base = 50.0
    highlights: list[str] = [
        f"歲君：{context.flow_year_branch}",
        f"流年宮：{context.flow_year_palace or '—'}",
    ]

    if context.current_period_lord:
        highlights.append(
            f"大運：{context.current_period_palace}（主星{context.current_period_lord}）"
        )
        if context.current_period_lord in GOOD_LORDS:
            base += 8
        if context.current_period_lord in CAUTION_LORDS:
            base -= 5

    if context.flow_year_palace in {"命宮", "官祿", "財帛", "福德"}:
        base += 8
    elif context.flow_year_palace in KEY_PALACES:
        base += 4
    if context.flow_year_palace in {"疾厄", "奴僕"}:
        base -= 6

    if context.current_period_palace and context.flow_year_palace:
        if context.current_period_palace == context.flow_year_palace:
            base += 6
            highlights.append("大運流年同宮")

    if 0 <= context.dasha.current_period_idx < len(context.dasha.periods):
        period = context.dasha.periods[context.dasha.current_period_idx]
        highlights.append(f"行限年數：{period.years}年（{period.start_age}-{period.end_age}歲）")

    if context.resonance_hits:
        top = context.resonance_hits[0]
        highlights.append(
            f"守照共振：{top.get('star')} {top.get('aspect')} ({top.get('score', 0):+d})"
        )
        base += max(-12.0, min(15.0, context.resonance_score * 0.8))
        positive = sum(1 for hit in context.resonance_hits if hit.get("score", 0) > 0)
        negative = sum(1 for hit in context.resonance_hits if hit.get("score", 0) < 0)
        if positive >= 2:
            base += 4
        if negative >= 2:
            base -= 5

    score = clamp_score(base)
    summary = (
        f"歲君{context.flow_year_branch}臨{context.flow_year_palace or '—'}，"
        f"大運{context.current_period_palace or '—'}主{context.current_period_lord or '—'}。"
    )
    return ChineseSystemSnapshot(
        system="qizheng",
        score=score,
        level=score_to_level(score),
        summary=summary,
        highlights=highlights,
        raw={
            "flow_year_branch": context.flow_year_branch,
            "flow_year_palace": context.flow_year_palace,
            "current_period_lord": context.current_period_lord,
            "current_period_palace": context.current_period_palace,
            "current_age": context.current_age,
            "current_period_idx": context.dasha.current_period_idx,
            "periods_count": len(context.dasha.periods),
            "resonance_hits": context.resonance_hits[:6],
            "resonance_score": context.resonance_score,
        },
    )