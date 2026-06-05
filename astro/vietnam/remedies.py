"""Remedy recommendation logic for Vietnam Tử Vi module."""

from __future__ import annotations

from astro.vietnam.data.stars import STAR_PROFILES_VN

MALEFIC_STARS = {"火星", "鈴星", "地空", "地劫", "七殺", "破軍"}


def suggest_remedies(stars: list[str], lang: str = "zh") -> list[str]:
    """Generate practical remedies based on star composition."""
    suggestions: list[str] = []
    seen: set[str] = set()

    for star in stars:
        profile = STAR_PROFILES_VN.get(star)
        if not profile:
            continue
        for remedy in profile.remedies:
            if remedy not in seen:
                suggestions.append(remedy)
                seen.add(remedy)

    if any(star in MALEFIC_STARS for star in stars):
        extra = {
            "zh": "每季做一次風險盤點（健康/財務/關係）並訂定備援方案。",
            "vi": "Mỗi quý rà soát rủi ro sức khỏe/tài chính/quan hệ và chuẩn bị phương án dự phòng.",
            "en": "Run a quarterly risk review (health/finance/relationships) with backup plans.",
        }
        suggestions.append(extra.get(lang, extra["zh"]))

    if not suggestions:
        defaults = {
            "zh": ["保持規律作息與運動", "每月設定可量化成長目標"],
            "vi": ["Giữ nhịp sinh hoạt và tập luyện đều đặn", "Đặt mục tiêu phát triển định lượng mỗi tháng"],
            "en": ["Keep consistent sleep and exercise habits", "Set measurable monthly growth goals"],
        }
        return defaults.get(lang, defaults["zh"])

    return suggestions[:8]
