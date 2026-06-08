"""Structured educational guides for individual astrology systems."""
# pylint: disable=too-many-instance-attributes

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SystemGuide:
    """Educational metadata shown alongside a system UI."""

    principle_zh: str
    principle_en: str
    use_cases_zh: list[str] = field(default_factory=list)
    use_cases_en: list[str] = field(default_factory=list)
    differences_zh: list[str] = field(default_factory=list)
    differences_en: list[str] = field(default_factory=list)
    related_systems_zh: list[str] = field(default_factory=list)
    related_systems_en: list[str] = field(default_factory=list)


_GUIDES: dict[str, SystemGuide] = {
    "tab_enochian": SystemGuide(
        principle_zh=(
            "伊諾克占星把西方本命盤映射到守望塔、Aethyr 與天使體系，"
            "核心不是單看吉凶，而是辨識你命盤與哪一組靈性力量場最共振。"
        ),
        principle_en=(
            "Enochian Astrology maps a Western natal chart into Watchtowers, "
            "Aethyrs, and angelic intelligences to identify which spiritual force "
            "field your chart resonates with most strongly."
        ),
        use_cases_zh=[
            "靈性修持或冥想主題排序",
            "將西方占星的生命課題轉譯為天使工作方向",
            "為儀式、守望塔或 Aethyr 工作建立優先級",
        ],
        use_cases_en=[
            "Prioritizing spiritual practice and meditation themes",
            "Translating Western natal challenges into angelic work streams",
            "Choosing which Watchtower or Aethyr to work with first",
        ],
        differences_zh=[
            "相較一般西方占星，重點不只在事件預測，而是靈性對應與儀式工作。",
            "相較 Goetia，伊諾克更偏向天使層級、守望塔與意識階梯。",
        ],
        differences_en=[
            "Unlike standard Western astrology, the focus is spiritual "
            "correspondence and ritual work rather than only event timing.",
            "Compared with Goetia, Enochian emphasizes angelic hierarchies, "
            "Watchtowers, and consciousness ladders.",
        ],
        related_systems_zh=["西洋占星", "所羅門占星", "Picatrix 占星魔法"],
        related_systems_en=[
            "Western Astrology",
            "Goetia / Solomonic Astrology",
            "Picatrix Star Magic",
        ],
    ),
    "tab_goetia": SystemGuide(
        principle_zh=(
            "所羅門占星把本命盤的行星、星座、宮位與元素平衡，"
            "映射到 72 靈體的功能、行星統攝與儀式用途，形成動態推薦。"
        ),
        principle_en=(
            "Goetia / Solomonic Astrology maps natal planets, signs, houses, and "
            "elemental balance to the 72 spirits' offices, planetary rulerships, "
            "and ritual functions to produce dynamic recommendations."
        ),
        use_cases_zh=[
            "依本命盤挑選最適合合作的靈體與目的",
            "把西方盤中的強勢行星轉譯為儀式／召請方向",
            "配合選時窗口安排更適合的工作時間",
        ],
        use_cases_en=[
            "Selecting the spirits and ritual aims most aligned with a natal chart",
            "Translating dominant Western natal signatures into ritual directions",
            "Combining recommendation ranking with electional timing windows",
        ],
        differences_zh=[
            "相較 Enochian，所羅門占星更偏向任務導向、功能性與儀式用途。",
            "相較單純魔法書表列，這裡的推薦會根據本命盤動態排序，而非固定指派。",
        ],
        differences_en=[
            "Compared with Enochian, Goetia is more task-oriented, "
            "operational, and purpose-driven.",
            "Compared with static grimoire tables, rankings here are "
            "dynamically derived from natal structure rather than fixed "
            "assignments.",
        ],
        related_systems_zh=["西洋占星", "伊諾克占星", "擇日占星"],
        related_systems_en=[
            "Western Astrology",
            "Enochian Astrology",
            "Electional Astrology",
        ],
    ),
}


def get_system_guide(system_id: str) -> SystemGuide | None:
    """Return educational metadata for a system, if available."""
    return _GUIDES.get(system_id)
