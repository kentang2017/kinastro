"""Personalized bilingual interpretation builders for Enochian Astrology."""

from __future__ import annotations

from typing import Dict, List, Tuple

MAX_GUARDIAN_ANGELS_DISPLAY = 4


def build_spiritual_path(
    dominant_watchtower: str,
    dominant_watchtower_zh: str,
    dominant_element: str,
    dominant_element_zh: str,
    primary_aethyr_name: str,
    primary_aethyr_name_zh: str,
    guardian_angels: List[str],
) -> Tuple[str, str]:
    angels = ", ".join(guardian_angels[:MAX_GUARDIAN_ANGELS_DISPLAY]) if guardian_angels else "your guardian choir"
    angels_zh = "、".join(guardian_angels[:MAX_GUARDIAN_ANGELS_DISPLAY]) if guardian_angels else "你的守護天使群"
    en = (
        f"Your spiritual path is anchored in the {dominant_watchtower} Watchtower and {dominant_element} element. "
        f"Aethyr {primary_aethyr_name} is your primary initiation field, guided by {angels}."
    )
    zh = (
        f"你的靈性路徑錨定於{dominant_watchtower_zh}守望塔與{dominant_element_zh}元素。"
        f"{primary_aethyr_name_zh}以太層是你的核心啟蒙場域，由{angels_zh}引導。"
    )
    return en, zh


def build_magical_purpose(
    dominant_watchtower: str,
    dominant_watchtower_zh: str,
    watchtower_purpose_en: str,
    watchtower_purpose_zh: str,
    strongest_planet: str,
) -> Tuple[str, str]:
    en = (
        f"Your magical purpose manifests through the {dominant_watchtower} Watchtower, "
        f"with {strongest_planet} as your strongest operational current. {watchtower_purpose_en}"
    )
    zh = (
        f"你的魔法目的透過{dominant_watchtower_zh}守望塔展現，"
        f"以{strongest_planet}作為最強行運電流。{watchtower_purpose_zh}"
    )
    return en, zh


def build_invocation(
    invocation_template_en: str,
    invocation_template_zh: str,
    angel_names: List[str],
    watchtower: str,
    watchtower_zh: str,
    aethyr_name: str,
    aethyr_name_zh: str,
) -> Dict[str, str]:
    angels_en = ", ".join(angel_names) if angel_names else "MICHAEL and GABRIEL"
    angels_zh = "、".join(angel_names) if angel_names else "米迦勒與加百列"
    return {
        "en": invocation_template_en.format(
            angel_names=angels_en,
            watchtower=watchtower,
            aethyr=aethyr_name,
        ),
        "zh": invocation_template_zh.format(
            angel_names=angels_zh,
            watchtower=watchtower_zh,
            aethyr=aethyr_name_zh,
        ),
    }
