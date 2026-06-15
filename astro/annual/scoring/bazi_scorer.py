"""Bazi annual snapshot scoring at solar-return reference date."""

from __future__ import annotations

from astro.annual.models import ChineseSystemSnapshot
from astro.annual.scoring.levels import clamp_score, score_to_level
from astro.bazi.calculator import BaziChart


def score_bazi_annual(chart: BaziChart) -> ChineseSystemSnapshot:
    base = 50.0
    highlights: list[str] = []

    if chart.current_dayun:
        highlights.append(f"大運：{chart.current_dayun.ganzhi}")
        dayun_shishen = chart.current_dayun.shishen_stem
        if dayun_shishen in {"正官", "正印", "食神"}:
            base += 8
        if dayun_shishen in {"七殺", "傷官", "梟神"}:
            base -= 6

    highlights.append(f"流年：{chart.current_liunian}")
    liunian_stem = chart.current_liunian[0] if chart.current_liunian else ""
    if chart.yongshen and liunian_stem:
        from astro.bazi.calculator import WUXING_TG

        liunian_wx = WUXING_TG.get(liunian_stem, "")
        if liunian_wx == chart.yongshen:
            base += 10
            highlights.append("流年五行助用神")
        if liunian_wx == chart.jishen:
            base -= 8
            highlights.append("流年五行犯忌神")

    if chart.day_master_strength in {"身強", "中和"}:
        base += 3

    score = clamp_score(base)
    summary = (
        f"{chart.current_liunian_year}年流年{chart.current_liunian}，"
        f"大運{chart.current_dayun.ganzhi if chart.current_dayun else '—'}，"
        f"日主{chart.day_master_strength}。"
    )
    return ChineseSystemSnapshot(
        system="bazi",
        score=score,
        level=score_to_level(score),
        summary=summary,
        highlights=highlights,
        raw={
            "current_liunian": chart.current_liunian,
            "current_dayun": chart.current_dayun.ganzhi if chart.current_dayun else "",
            "day_master_strength": chart.day_master_strength,
            "yongshen": chart.yongshen,
        },
    )