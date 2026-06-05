"""Interpretation logic for traditional and Trung Châu modes."""

from __future__ import annotations

from astro.vietnam.data.trung_chau_rules import (
    DAI_HAN_STYLE_GUIDE,
    LUU_NIEN_STYLE_GUIDE,
    TRUNG_CHAU_CORE_THEMES,
    TRUNG_CHAU_PATTERNS,
)
from astro.vietnam.models import InterpretationBlock


def _match_patterns(stars: set[str]) -> list[dict[str, object]]:
    matched: list[dict[str, object]] = []
    for pattern in TRUNG_CHAU_PATTERNS:
        required = set(pattern.get("requires", {}).get("all_of", []))
        if required and required.issubset(stars):
            matched.append(pattern)
    return matched


def build_interpretation(
    *,
    stars: list[str],
    ming_palace_name: str,
    da_xian: str,
    interpret_mode: str,
    lang: str,
) -> InterpretationBlock:
    """Generate interpretation block based on selected mode."""
    star_set = set(stars)

    if interpret_mode == "traditional_cn":
        return InterpretationBlock(
            personality=f"命宮{ming_palace_name}，主星組合為{('、'.join(stars[:4]) or '平衡')}，以傳統星曜格局判斷性格主軸。",
            physiology="生理面以疾厄宮與煞曜輕重作傳統評估，建議規律作息為先。",
            self_effort="後天可透過修德、慎言、穩健財務策略提升整體運勢。",
            dai_han=f"大限重點：{da_xian} 期間以宮位主題推進長期目標。",
            luu_nien="流年採傳統四化與宮位互動觀察，宜年度滾動調整。",
            key_points=["重視格局", "觀察四化", "趨吉避凶"],
        )

    matched = _match_patterns(star_set)
    pattern_notes = [f"{m['name']}：{m['insight']}" for m in matched]
    effort_notes = [str(m["effort"]) for m in matched]

    personality = (
        f"Trung Châu 心理取向：{TRUNG_CHAU_CORE_THEMES['psychology']}"
        + (f" 已成格：{'；'.join(pattern_notes)}" if pattern_notes else " 目前未成明顯專格，以穩定節奏累積。")
    )
    physiology = f"Trung Châu 生理取向：{TRUNG_CHAU_CORE_THEMES['physiology']}"
    self_effort = (
        f"Trung Châu 後天取向：{TRUNG_CHAU_CORE_THEMES['self_effort']}"
        + (f" 執行焦點：{'；'.join(effort_notes)}" if effort_notes else " 執行焦點：先強化日常習慣與技能堆疊。")
    )

    return InterpretationBlock(
        personality=personality,
        physiology=physiology,
        self_effort=self_effort,
        dai_han=DAI_HAN_STYLE_GUIDE.get(lang, DAI_HAN_STYLE_GUIDE["zh"]),
        luu_nien=LUU_NIEN_STYLE_GUIDE.get(lang, LUU_NIEN_STYLE_GUIDE["zh"]),
        key_points=["心理韌性", "生理節律", "後天努力"],
    )
