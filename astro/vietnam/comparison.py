"""Comparison output between Chinese Ziwei and Vietnam Tử Vi views."""

from __future__ import annotations

from astro.vietnam.models import ComparisonItem


def build_comparison(
    *,
    chinese_emphasis: str,
    vietnam_emphasis: str,
    stars: list[str],
) -> list[ComparisonItem]:
    """Build structured comparison rows."""
    top_stars = "、".join(stars[:4]) if stars else "無"
    return [
        ComparisonItem(
            topic="核心視角",
            chinese_view=chinese_emphasis,
            vietnam_view=vietnam_emphasis,
            summary_diff="越南版加強心理/生理/後天努力；中式偏格局與傳統星性。",
        ),
        ComparisonItem(
            topic="關鍵星曜",
            chinese_view=f"以星曜本義判斷：{top_stars}",
            vietnam_view=f"保留星曜本義並加上生活實踐建議：{top_stars}",
            summary_diff="越南版把星曜解讀轉成可執行建議。",
        ),
    ]
