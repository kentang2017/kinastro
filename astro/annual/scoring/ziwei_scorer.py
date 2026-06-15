"""Ziwei annual snapshot scoring with 流年宮 / 小限宮 / 大限."""

from __future__ import annotations

from typing import Any

from astro.annual.adapters.ziwei_flow import ZiweiFlowPalaces, resolve_ziwei_flow_palaces
from astro.annual.models import ChineseSystemSnapshot
from astro.annual.scoring.levels import clamp_score, score_to_level

GOOD_STARS = {"紫微", "天府", "太陽", "太陰", "天同", "天相", "祿存", "左輔", "右弼"}
BAD_STARS = {"七殺", "破軍", "廉貞", "巨門", "擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"}
KEY_PALACES = {"命宮", "財帛", "官祿", "夫妻", "疾厄", "福德"}


def _score_palace_stars(stars: list[str], aux: list[str], base: float) -> float:
    score = base
    for star in stars:
        if star in GOOD_STARS:
            score += 5
        if star in BAD_STARS:
            score -= 5
    for star in aux:
        if star in {"文昌", "文曲", "天馬", "祿存"}:
            score += 3
        if star in {"擎羊", "陀羅", "火星", "鈴星"}:
            score -= 3
    return score


def score_ziwei_annual(
    chart: Any,
    virtual_age: int,
    liunian_gz: str,
    liunian_branch: str,
) -> ChineseSystemSnapshot:
    flow = resolve_ziwei_flow_palaces(chart, virtual_age, liunian_gz, liunian_branch)
    base = 50.0
    highlights: list[str] = []

    if flow.liunian_palace_name:
        highlights.append(f"流年宮：{flow.liunian_palace_name}（{flow.liunian_branch}）")
        base = _score_palace_stars(flow.liunian_stars, flow.liunian_aux_stars, base)
        if flow.liunian_palace_name in KEY_PALACES:
            base += 4

    if flow.xiaoxian_palace_name:
        highlights.append(f"小限宮：{flow.xiaoxian_palace_name}（{flow.xiaoxian_palace_branch}）")
        xiao_score = _score_palace_stars(flow.xiaoxian_stars, flow.xiaoxian_aux_stars, 50.0)
        base = (base * 0.55) + (xiao_score * 0.45)
        if flow.xiaoxian_palace_name in KEY_PALACES:
            base += 3

    if flow.daxian_palace_name:
        highlights.append(f"大限：{flow.daxian_palace_name}（{flow.daxian_range}）")

    ji_palace = flow.liunian_sihua.get("化忌落宮", "")
    lu_palace = flow.liunian_sihua.get("化祿落宮", "")
    if ji_palace in KEY_PALACES:
        base -= 10
        highlights.append(f"流年化忌入{ji_palace}")
    if lu_palace in {"財帛", "官祿", "命宮", "福德"}:
        base += 8
        highlights.append(f"流年化祿入{lu_palace}")

    if flow.liunian_palace_name and flow.xiaoxian_palace_name:
        if flow.liunian_palace_name == flow.xiaoxian_palace_name:
            base += 6
            highlights.append("流年小限同宮加力")

    score = clamp_score(base)
    summary = (
        f"虛歲{virtual_age}，流年{liunian_gz}。"
        f"流年宮{flow.liunian_palace_name or '—'}，"
        f"小限宮{flow.xiaoxian_palace_name or '—'}（{flow.direction}），"
        f"大限{flow.daxian_palace_name or '—'}。"
    )
    return ChineseSystemSnapshot(
        system="ziwei",
        score=score,
        level=score_to_level(score),
        summary=summary,
        highlights=highlights,
        raw={
            "liunian_palace": flow.liunian_palace_name,
            "liunian_branch": flow.liunian_branch,
            "liunian_stars": flow.liunian_stars,
            "xiaoxian_palace": flow.xiaoxian_palace_name,
            "xiaoxian_branch": flow.xiaoxian_palace_branch,
            "xiaoxian_stars": flow.xiaoxian_stars,
            "daxian_palace": flow.daxian_palace_name,
            "daxian_range": flow.daxian_range,
            "liunian_sihua": flow.liunian_sihua,
            "direction": flow.direction,
            "virtual_age": virtual_age,
            "liunian_gz": liunian_gz,
        },
    )