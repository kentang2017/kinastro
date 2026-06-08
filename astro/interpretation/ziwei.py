"""Structured Ziwei interpretation engine with traditional and AI modes."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from astro.models import KinAstroModel, ZiweiChartResult

from .providers import (
    InterpretationProviderConfig,
    InterpretationProviderError,
    get_provider_label,
    request_llm_completion,
)
from .ziwei_prompt_templates import build_ziwei_ai_messages

EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WU_XING_JU_NAMES = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}
STAR_TRAITS = {
    "紫微": ("土", "帝座"),
    "天機": ("木", "機巧"),
    "太陽": ("火", "光明"),
    "武曲": ("金", "財星"),
    "天同": ("水", "福星"),
    "廉貞": ("火", "節制"),
    "天府": ("土", "府庫"),
    "太陰": ("水", "陰柔"),
    "貪狼": ("木", "欲望"),
    "巨門": ("水", "口才"),
    "天相": ("水", "輔弼"),
    "天梁": ("土", "蔭庇"),
    "七殺": ("金", "將星"),
    "破軍": ("水", "變革"),
}


class ZiweiInterpretationResult(KinAstroModel):
    """Structured Ziwei interpretation output for UI and export."""

    system: Literal["ziwei"] = "ziwei"
    mode: Literal["traditional", "hybrid", "ai"] = "traditional"
    provider: str = "traditional"
    summary: str
    ming_gong_analysis: str
    shen_gong_analysis: str
    si_hua_effects: str
    major_star_combinations: list[str] = Field(default_factory=list)
    da_xian_overview: list[str] = Field(default_factory=list)
    ai_enhanced_notes: str = ""
    final_text: str = ""
    sections: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


def _find_palace_by_name(chart: ZiweiChartResult, name: str):
    return next((palace for palace in chart.palaces if palace.name == name), None)


def _find_palace_by_branch(chart: ZiweiChartResult, branch: int):
    return next((palace for palace in chart.palaces if palace.branch == branch), None)


def _branch_name(branch: int) -> str:
    return EARTHLY_BRANCHES[branch % 12]


def _palace_star_summary(palace) -> str:
    stars = "、".join(palace.stars) if palace and palace.stars else "無十四主星同守"
    aux = "、".join(palace.auxiliary_stars[:4]) if palace and palace.auxiliary_stars else "輔星訊號較輕"
    return f"{palace.name}在{palace.branch_name}位，主星為{stars}；輔星以{aux}為主。"


def _brightness_summary(palace) -> str:
    if palace is None or not palace.brightness:
        return "目前沒有足夠的主星亮度資訊。"
    bright = [
        f"{star}{level}"
        for star, level in palace.brightness.items()
        if level
    ]
    return "亮度重點：" + ("、".join(bright[:5]) if bright else "未見明顯廟旺平陷訊號。")


def _star_traits(star_names: list[str]) -> str:
    traits: list[str] = []
    for star in star_names:
        if star not in STAR_TRAITS:
            continue
        element, title = STAR_TRAITS[star]
        traits.append(f"{star}偏{title}、{element}性")
    return "；".join(traits[:4]) if traits else "主題偏向在宮位互動中展開。"


def _summarize_ming_gong(chart: ZiweiChartResult) -> str:
    palace = _find_palace_by_name(chart, "命宮")
    if palace is None:
        return "命宮資料暫缺，無法完成傳統命宮解讀。"
    wu_xing_ju_name = WU_XING_JU_NAMES.get(chart.wu_xing_ju, f"{chart.wu_xing_ju}局")
    return (
        f"{_palace_star_summary(palace)}{_brightness_summary(palace)}"
        f" 命主為{chart.ming_zhu}，五行局屬{wu_xing_ju_name}，"
        f"整體氣質可先從 {_star_traits(palace.stars)} 觀察。"
    )


def _summarize_shen_gong(chart: ZiweiChartResult) -> str:
    palace = _find_palace_by_branch(chart, chart.shen_gong_branch)
    if palace is None:
        return "身宮資料暫缺。"
    return (
        f"身宮落在{palace.name}（{palace.branch_name}位），身主為{chart.shen_zhu}。"
        f"{_palace_star_summary(palace)} 這表示人生實際投入與行動慣性，"
        f"常會把命宮的主題拉向 {palace.name} 所代表的生活領域。"
    )


def _summarize_sihua(chart: ZiweiChartResult) -> str:
    if not chart.sihua:
        return "此盤未提供四化資料。"
    palace_hits: list[str] = []
    for palace in chart.palaces:
        if not palace.sihua:
            continue
        palace_hits.append(
            f"{palace.name}見"
            + "、".join(f"{star}化{transform}" for star, transform in palace.sihua.items())
        )
    global_sihua = "、".join(
        f"{star}化{transform}" for star, transform in chart.sihua.items()
    )
    local_notes = "；".join(palace_hits[:4]) if palace_hits else "宮位層尚未見四化落點。"
    return (
        f"本命四化主軸為：{global_sihua}。"
        f" 宮位互動上，{local_notes}"
        "，解讀時應優先觀察化祿的資源流向、化權的主導位置、"
        "化科的名聲與緩衝，以及化忌所形成的壓力焦點。"
    )


def _summarize_major_combinations(chart: ZiweiChartResult) -> list[str]:
    ming_palace = _find_palace_by_name(chart, "命宮")
    if ming_palace is None:
        return ["命宮資料不足，無法建立星曜組合解讀。"]
    combinations = [
        (
            f"命宮主星：{'、'.join(ming_palace.stars) if ming_palace.stars else '空宮'}，"
            f"代表性格核心與人生主軸。"
        ),
        (
            f"三方四正基礎：命宮在{ming_palace.branch_name}，"
            f"可延伸觀察 branch "
            f"{_branch_name(ming_palace.branch + 4)} 與 {_branch_name(ming_palace.branch + 8)}"
            " 的呼應，以判斷資源、事業與外界互動。"
        ),
    ]
    if ming_palace.auxiliary_stars:
        combinations.append(
            "命宮輔星組合："
            + "、".join(ming_palace.auxiliary_stars[:5])
            + "，可作為吉凶緩衝與行事風格修飾。"
        )
    if any("忌" in palace.sihua.values() for palace in chart.palaces):
        combinations.append("化忌已落入特定宮位，解讀時要同步評估壓力轉移與人際牽動。")
    return combinations


def _summarize_da_xian(chart: ZiweiChartResult) -> list[str]:
    ordered = sorted(chart.palaces, key=lambda palace: palace.da_xian_start)
    overview: list[str] = []
    for palace in ordered[:4]:
        overview.append(
            f"{palace.da_xian} 行運落在{palace.name}（{palace.branch_name}），"
            f"主題受 {'、'.join(palace.stars) if palace.stars else '該宮宮性'} 牽動。"
        )
    return overview


def _build_traditional_interpretation(
    chart: ZiweiChartResult,
    mode: Literal["traditional", "hybrid", "ai"],
) -> ZiweiInterpretationResult:
    """Create the structured traditional Ziwei interpretation scaffold."""
    summary = (
        f"此盤命宮在{_branch_name(chart.ming_gong_branch)}，身宮在{_branch_name(chart.shen_gong_branch)}，"
        f"五行局為{WU_XING_JU_NAMES.get(chart.wu_xing_ju, f'{chart.wu_xing_ju}局')}。"
        f" 命主{chart.ming_zhu}、身主{chart.shen_zhu}，屬於以宮位互動與四化流向來判斷主題的結構。"
    )
    ming = _summarize_ming_gong(chart)
    shen = _summarize_shen_gong(chart)
    si_hua = _summarize_sihua(chart)
    combinations = _summarize_major_combinations(chart)
    da_xian = _summarize_da_xian(chart)
    sections = {
        "summary": summary,
        "ming_gong_analysis": ming,
        "shen_gong_analysis": shen,
        "si_hua_effects": si_hua,
        "major_star_combinations": "\n".join(f"- {item}" for item in combinations),
        "da_xian_overview": "\n".join(f"- {item}" for item in da_xian),
    }
    result = ZiweiInterpretationResult(
        mode=mode,
        provider="traditional",
        summary=summary,
        ming_gong_analysis=ming,
        shen_gong_analysis=shen,
        si_hua_effects=si_hua,
        major_star_combinations=combinations,
        da_xian_overview=da_xian,
        sections=sections,
    )
    return result.model_copy(update={"final_text": ziwei_interpretation_to_markdown(result)})


def _enhance_with_ai(
    chart: ZiweiChartResult,
    traditional: ZiweiInterpretationResult,
    provider_config: InterpretationProviderConfig,
    user_instruction: str = "",
) -> ZiweiInterpretationResult:
    """Overlay AI-enhanced notes onto the traditional interpretation."""
    provider_label = get_provider_label(provider_config)
    try:
        ai_text = request_llm_completion(
            messages=build_ziwei_ai_messages(
                chart=chart,
                traditional_markdown=traditional.final_text,
                user_instruction=user_instruction,
            ),
            config=provider_config,
        )
        enriched = traditional.model_copy(
            update={
                "provider": provider_label,
                "ai_enhanced_notes": ai_text,
                "warnings": list(traditional.warnings),
            }
        )
        return enriched.model_copy(
            update={"final_text": ziwei_interpretation_to_markdown(enriched)}
        )
    except InterpretationProviderError as exc:
        fallback = traditional.model_copy(
            update={
                "provider": provider_label,
                "warnings": [*traditional.warnings, str(exc)],
            }
        )
        return fallback.model_copy(
            update={"final_text": ziwei_interpretation_to_markdown(fallback)}
        )


def generate_ziwei_interpretation(
    chart: ZiweiChartResult,
    mode: str = "hybrid",
    *,
    provider_config: InterpretationProviderConfig | None = None,
    user_instruction: str = "",
) -> ZiweiInterpretationResult:
    """Generate structured Ziwei interpretation output.

    Modes:
    - ``traditional``: pure rule-based traditional template output
    - ``hybrid``: traditional structure with AI enhancement notes appended
    - ``ai``: same as hybrid for now, but intended for stronger future RAG/LLM flow
    """
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"traditional", "hybrid", "ai"}:
        raise ValueError("mode must be one of: traditional, hybrid, ai")
    traditional = _build_traditional_interpretation(
        chart,
        "traditional" if normalized_mode == "traditional" else normalized_mode,
    )
    if normalized_mode == "traditional":
        return traditional
    return _enhance_with_ai(
        chart,
        traditional,
        provider_config or InterpretationProviderConfig(),
        user_instruction=user_instruction,
    )


def interpret_ziwei_chart(
    chart: ZiweiChartResult,
    mode: str = "hybrid",
    *,
    provider_config: InterpretationProviderConfig | None = None,
    user_instruction: str = "",
) -> ZiweiInterpretationResult:
    """Backward-friendly alias for Ziwei interpretation generation."""
    return generate_ziwei_interpretation(
        chart,
        mode=mode,
        provider_config=provider_config,
        user_instruction=user_instruction,
    )


def ziwei_interpretation_to_markdown(result: ZiweiInterpretationResult) -> str:
    """Flatten structured interpretation output into editable markdown."""
    lines = [
        "## Summary",
        result.summary,
        "",
        "## Ming Gong Analysis",
        result.ming_gong_analysis,
        "",
        "## Shen Gong Analysis",
        result.shen_gong_analysis,
        "",
        "## Si Hua Effects",
        result.si_hua_effects,
        "",
        "## Major Star Combinations",
        *[f"- {item}" for item in result.major_star_combinations],
        "",
        "## Da Xian Overview",
        *[f"- {item}" for item in result.da_xian_overview],
    ]
    if result.ai_enhanced_notes:
        lines.extend(["", "## AI Enhanced Notes", result.ai_enhanced_notes])
    if result.warnings:
        lines.extend(["", "## Warnings", *[f"- {item}" for item in result.warnings]])
    return "\n".join(lines).strip()


__all__ = [
    "ZiweiInterpretationResult",
    "generate_ziwei_interpretation",
    "interpret_ziwei_chart",
    "ziwei_interpretation_to_markdown",
]
