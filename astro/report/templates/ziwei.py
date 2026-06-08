"""Ziwei PDF report template settings and chart visual helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Iterable

from astro.interpretation.ziwei import ZiweiInterpretationResult
from astro.models import ZiweiChartResult

try:  # pragma: no cover - import guard depends on installed extras
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - handled by runtime usage
    Image = None
    ImageDraw = None
    ImageFont = None

FONT_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "fonts" / "NotoSansCJKtc-Regular.otf"
)
PALACE_GRID_LAYOUT = [
    (1, 1, 5), (1, 2, 6), (1, 3, 7), (1, 4, 8),
    (2, 1, 4), (2, 4, 9),
    (3, 1, 3), (3, 4, 10),
    (4, 1, 2), (4, 2, 1), (4, 3, 0), (4, 4, 11),
]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WU_XING_JU_NAMES = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}


@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ZiweiReportTheme:
    """Reusable visual theme for printable Ziwei reports."""

    page_background: str = "#F6F1E7"
    header_background: str = "#1C2333"
    title_color: str = "#D7B26D"
    accent_color: str = "#7B4F2A"
    panel_background: str = "#FBF8F1"
    panel_border: str = "#D8C7A5"
    palace_background: str = "#1A1F2B"
    palace_border: str = "#4E5568"
    ming_border: str = "#C95F5F"
    shen_border: str = "#4FAAA2"
    text_primary: str = "#1D2432"
    text_muted: str = "#5D6778"
    star_primary: str = "#F7E1A1"
    star_auxiliary: str = "#B9C0CE"
    footer_text: str = "#6E5840"


@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ZiweiReportOptions:
    """Configurable options for professional Ziwei PDF reports."""

    title: str = "KinAstro Ziwei Professional Report / 堅占星紫微專業報告"
    subtitle: str = (
        "Structured natal reading with palace grid, interpretation, "
        "and export-ready layout."
    )
    generated_label: str = "Generated at / 生成時間"
    include_ai_notes: bool = True
    include_final_text: bool = True
    include_chart_visual: bool = True
    include_warnings: bool = True
    show_preview_image: bool = True
    template_name: str = "ziwei-professional-v1"
    branding: str = "KinAstro · 堅占星"
    disclaimer_lines: tuple[str, ...] = (
        "This report is for reflective and educational astrology use.",
        "本報告供占星研究、諮詢與自我反思參考，並不取代醫療、法律或財務建議。",
    )
    theme: ZiweiReportTheme = field(default_factory=ZiweiReportTheme)


def build_ziwei_report_sections(
    interpretation: ZiweiInterpretationResult,
    *,
    include_ai_notes: bool,
    include_final_text: bool,
) -> list[tuple[str, str | list[str]]]:
    """Return ordered report sections from structured interpretation data."""
    sections: list[tuple[str, str | list[str]]] = [
        ("Summary / 摘要", interpretation.summary),
        ("Ming Gong Analysis / 命宮分析", interpretation.ming_gong_analysis),
        ("Shen Gong Analysis / 身宮分析", interpretation.shen_gong_analysis),
        ("Si Hua Effects / 四化影響", interpretation.si_hua_effects),
        (
            "Major Star Combinations / 主要星群組合",
            interpretation.major_star_combinations,
        ),
        ("Da Xian Overview / 大限概述", interpretation.da_xian_overview),
    ]
    if include_ai_notes and interpretation.ai_enhanced_notes:
        sections.append(
            ("AI Enhanced Notes / AI 增強說明", interpretation.ai_enhanced_notes)
        )
    if include_final_text and interpretation.final_text:
        sections.append(("Final Interpretation / 最終解讀", interpretation.final_text))
    return sections


def render_ziwei_report_chart_png(
    chart: ZiweiChartResult,
    *,
    theme: ZiweiReportTheme | None = None,
    width: int = 1600,
    height: int = 1600,
) -> bytes:
    """Render a clean Ziwei palace-grid PNG optimized for PDF embedding."""
    # pylint: disable=too-many-locals
    if Image is None or ImageDraw is None or ImageFont is None:
        raise RuntimeError(
            "Pillow is required to render Ziwei report chart images."
        )
    active_theme = theme or ZiweiReportTheme()
    image = Image.new("RGB", (width, height), active_theme.page_background)
    draw = ImageDraw.Draw(image)

    title_font = _load_font(60)
    body_font = _load_font(26)
    small_font = _load_font(20)
    star_font = _load_font(28)

    margin = 60
    grid_top = 160
    grid_width = width - (margin * 2)
    grid_height = height - grid_top - margin
    cell_width = grid_width // 4
    cell_height = grid_height // 4

    draw.rounded_rectangle(
        (margin, 24, width - margin, 120),
        radius=24,
        fill=active_theme.header_background,
        outline=active_theme.title_color,
        width=3,
    )
    draw.text(
        (margin + 28, 42),
        "Ziwei Palace Grid / 紫微命盤方格",
        fill=active_theme.title_color,
        font=title_font,
    )

    palace_by_branch = {palace.branch: palace for palace in chart.palaces}
    center_box = (
        margin + cell_width,
        grid_top + cell_height,
        margin + (cell_width * 3),
        grid_top + (cell_height * 3),
    )
    draw.rounded_rectangle(
        center_box,
        radius=28,
        fill=active_theme.panel_background,
        outline=active_theme.panel_border,
        width=3,
    )
    _draw_center_block(draw, center_box, chart, title_font, body_font, small_font, active_theme)

    for row, col, branch in PALACE_GRID_LAYOUT:
        palace = palace_by_branch.get(branch)
        if palace is None:
            continue
        x1 = margin + ((col - 1) * cell_width)
        y1 = grid_top + ((row - 1) * cell_height)
        x2 = x1 + cell_width - 8
        y2 = y1 + cell_height - 8
        border_color = active_theme.palace_border
        if branch == chart.ming_gong_branch:
            border_color = active_theme.ming_border
        if branch == chart.shen_gong_branch:
            border_color = (
                active_theme.shen_border
                if branch != chart.ming_gong_branch
                else active_theme.title_color
            )
        draw.rounded_rectangle(
            (x1, y1, x2, y2),
            radius=18,
            fill=active_theme.palace_background,
            outline=border_color,
            width=4,
        )
        _draw_palace_block(
            draw,
            (x1, y1, x2, y2),
            palace,
            chart,
            body_font,
            small_font,
            star_font,
            active_theme,
        )

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def _draw_center_block(
    draw,
    box: tuple[int, int, int, int],
    chart: ZiweiChartResult,
    title_font,
    body_font,
    small_font,
    theme: ZiweiReportTheme,
) -> None:
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    x1, y1, _, _ = box
    lines = [
        "KinAstro · 堅占星",
        (
            f"命宮 {EARTHLY_BRANCHES[chart.ming_gong_branch]} / "
            f"身宮 {EARTHLY_BRANCHES[chart.shen_gong_branch]}"
        ),
        (
            f"{WU_XING_JU_NAMES.get(chart.wu_xing_ju, f'{chart.wu_xing_ju}局')} "
            f"· 命主 {chart.ming_zhu}"
        ),
        f"身主 {chart.shen_zhu} · {chart.yin_yang}",
        (
            f"農曆 {chart.lunar_date.year}年 "
            f"{chart.lunar_date.month}月"
            f"{' (閏)' if chart.lunar_date.is_leap_month else ''} "
            f"{chart.lunar_date.day}日"
        ),
        "四化：" + "、".join(
            f"{star}化{transform}" for star, transform in chart.sihua.items()
        ),
    ]
    y = y1 + 42
    for index, line in enumerate(lines):
        font = title_font if index == 0 else body_font
        fill = theme.accent_color if index == 0 else theme.text_primary
        if index >= 4:
            font = small_font
            fill = theme.text_muted
        draw.text((x1 + 28, y), line, font=font, fill=fill)
        y += 52 if index == 0 else 42


def _draw_palace_block(
    draw,
    box: tuple[int, int, int, int],
    palace,
    chart: ZiweiChartResult,
    body_font,
    small_font,
    star_font,
    theme: ZiweiReportTheme,
) -> None:
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    x1, y1, _, y2 = box
    y = y1 + 14
    label_parts = [f"{palace.stem_name}{palace.branch_name}", palace.name]
    if palace.branch == chart.ming_gong_branch:
        label_parts.append("命")
    if palace.branch == chart.shen_gong_branch:
        label_parts.append("身")
    draw.text(
        (x1 + 14, y),
        " · ".join(label_parts),
        font=body_font,
        fill=theme.star_primary,
    )
    y += 42
    for line in _wrap_items(palace.stars, per_line=2, empty_text="空宮"):
        draw.text((x1 + 16, y), line, font=star_font, fill=theme.star_primary)
        y += 36
    y += 8
    draw.text(
        (x1 + 14, y),
        "輔星 " + "、".join(palace.auxiliary_stars[:4] or ["—"]),
        font=small_font,
        fill=theme.star_auxiliary,
    )
    y += 30
    draw.text(
        (x1 + 14, y),
        "亮度 " + "、".join(
            f"{star}{level}" for star, level in list(palace.brightness.items())[:3]
        ) if palace.brightness else "亮度 —",
        font=small_font,
        fill=theme.star_auxiliary,
    )
    y += 30
    draw.text(
        (x1 + 14, y),
        "四化 " + "、".join(
            f"{star}化{transform}"
            for star, transform in list(palace.sihua.items())[:2]
        ) if palace.sihua else "四化 —",
        font=small_font,
        fill=theme.star_auxiliary,
    )
    draw.text(
        (x1 + 14, y2 - 34),
        f"大限 {palace.da_xian or '—'}",
        font=small_font,
        fill=theme.text_muted,
    )


def _wrap_items(items: Iterable[str], *, per_line: int, empty_text: str) -> list[str]:
    values = list(items)
    if not values:
        return [empty_text]
    return [
        "、".join(values[index:index + per_line])
        for index in range(0, len(values), per_line)
    ]


def _load_font(size: int):
    if ImageFont is None:
        raise RuntimeError("Pillow font support is unavailable.")
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size=size)
    return ImageFont.load_default()


__all__ = [
    "ZiweiReportOptions",
    "ZiweiReportTheme",
    "build_ziwei_report_sections",
    "render_ziwei_report_chart_png",
]
