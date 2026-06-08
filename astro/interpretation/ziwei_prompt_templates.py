"""Prompt templates for Ziwei interpretation providers."""

from __future__ import annotations

from astro.models import ZiweiChartResult


ZIWEI_BASE_SYSTEM_PROMPT = """
You are a senior Ziwei Dou Shu interpreter.

Rules:
1. Follow traditional Ziwei Dou Shu logic first, then add cautious modern phrasing.
2. Explicitly mention Ming Gong, key main stars, Si Hua, palace interactions, and Da Xian direction.
3. Do not invent stars or palaces that are not present in the chart summary.
4. Avoid fatalistic language; emphasize tendencies, timing, cultivation, and context.
5. Keep terminology culturally accurate: 命宮, 身宮, 四化, 三方四正, 廟旺平陷, 大限.
6. Cite why a conclusion is made, e.g. "because 紫微 sits in 命宮 and 化祿 falls on..."
7. Output concise markdown sections only.
""".strip()


ZIWEI_FEW_SHOTS = [
    {
        "user": (
            "Chart pattern: 命宮在辰，紫微、天府同宮，化祿入命，三方見左輔右弼。\n"
            "Need: summary + traditional reading."
        ),
        "assistant": (
            "## Summary\n"
            "此盤命宮主軸穩健而帶管理氣質，因紫微、天府同宮，格局偏向統籌、資源配置與承擔責任。\n\n"
            "## Ming Gong\n"
            "紫微、天府同守命宮，多主器度、自尊與主事能力。若化祿同時引動命宮，常見資源整合能力強、容易得人和與實際助力。\n\n"
            "## Traditional note\n"
            "三方再見左輔右弼，屬於輔佐星群拱命，較利組織、制度、管理與長期經營。"
        ),
    },
    {
        "user": (
            "Chart pattern: 命宮見廉貞、破軍，化忌牽動遷移宮，身宮落官祿。\n"
            "Need: cautionary but traditional analysis."
        ),
        "assistant": (
            "## Summary\n"
            "此盤的生命節奏偏向變動、破舊立新與外界刺激帶來的成長。\n\n"
            "## Ming Gong\n"
            "廉貞、破軍同見時，多有強烈主觀、改革衝動與不願受制的特質。若化忌再牽動遷移宮，常表示外部環境、移動、人際場域容易成為壓力來源。\n\n"
            "## Traditional note\n"
            "身宮在官祿，代表人生重心仍會回到事業與定位，宜以紀律與策略消化破軍之動，而非只憑情緒決斷。"
        ),
    },
]


def build_ziwei_ai_messages(
    *,
    chart: ZiweiChartResult,
    traditional_markdown: str,
    user_instruction: str = "",
) -> list[dict[str, str]]:
    """Build prompt messages for Ziwei AI enhancement."""
    chart_summary = (
        f"System: Ziwei Dou Shu\n"
        f"Lunar date: {chart.lunar_date.year} year, month {chart.lunar_date.month}, "
        f"day {chart.lunar_date.day}, leap={chart.lunar_date.is_leap_month}\n"
        f"Ming Gong branch: {chart.ming_gong_branch}\n"
        f"Shen Gong branch: {chart.shen_gong_branch}\n"
        f"Wu Xing Ju: {chart.wu_xing_ju}\n"
        f"Ming Zhu: {chart.ming_zhu}\n"
        f"Shen Zhu: {chart.shen_zhu}\n"
        f"Si Hua: {chart.sihua}\n"
        f"Palaces: "
        + "; ".join(
            f"{palace.name}({palace.branch_name}) main={','.join(palace.stars) or '-'} "
            f"aux={','.join(palace.auxiliary_stars) or '-'} sihua={palace.sihua or {}} "
            f"da_xian={palace.da_xian}"
            for palace in chart.palaces
        )
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": ZIWEI_BASE_SYSTEM_PROMPT},
    ]
    for shot in ZIWEI_FEW_SHOTS:
        messages.append({"role": "user", "content": shot["user"]})
        messages.append({"role": "assistant", "content": shot["assistant"]})
    messages.append(
        {
            "role": "user",
            "content": (
                "Use the following traditional scaffold and chart facts to produce "
                "a more polished Ziwei interpretation.\n\n"
                f"Traditional scaffold:\n{traditional_markdown}\n\n"
                f"Chart facts:\n{chart_summary}\n\n"
                f"Extra user instruction:\n{user_instruction or 'None'}"
            ),
        }
    )
    return messages


__all__ = [
    "ZIWEI_BASE_SYSTEM_PROMPT",
    "ZIWEI_FEW_SHOTS",
    "build_ziwei_ai_messages",
]
