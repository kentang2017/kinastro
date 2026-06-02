# -*- coding: utf-8 -*-
"""Khmer Reamker HTML/SVG renderer."""

from __future__ import annotations

from html import escape as html_escape
from typing import Any, Dict

_ARROW_DISPLAY_SEPARATOR = " · "

def _pick_text(
    data: Dict[str, Any],
    language: str,
    *,
    khmer_key: str,
    chinese_key: str,
    english_key: str | None = None,
) -> str:
    if language == "kh":
        return str(data.get(khmer_key) or data.get(chinese_key) or "")
    if language == "en" and english_key:
        return str(data.get(english_key) or data.get(chinese_key) or data.get(khmer_key) or "")
    return str(data.get(chinese_key) or data.get(khmer_key) or "")


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _format_arrow_value(arrow_number: Any, arrow_text: str) -> str:
    arrow_no_text = str(arrow_number or "")
    if arrow_no_text and arrow_text:
        return f"{arrow_no_text}{_ARROW_DISPLAY_SEPARATOR}{arrow_text}"
    return arrow_no_text or arrow_text


def render_reamker_grid_svg(reading: Dict[str, Any], size: int = 420, language: str = "zh") -> str:
    """Render the Reamker 32-cell marker as inline SVG."""
    rk = reading.get("reamker", {}) if isinstance(reading, dict) else {}
    cell = _coerce_int(rk.get("cell"), default=0)
    cell = max(0, min(31, cell))

    cols, rows = 8, 4
    pad = 16
    inner = size - pad * 2
    cw = inner / cols
    ch = inner / rows

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        'style="width:100%;height:auto;background:#0b1021;border-radius:12px;">',
        f'<rect x="1" y="1" width="{size - 2}" height="{size - 2}" rx="12" fill="#0b1021" stroke="#6b5ca5" stroke-width="1.5"/>',
    ]
    for i in range(32):
        x = pad + (i % cols) * cw
        y = pad + (i // cols) * ch
        is_hit = i == cell
        parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{cw:.2f}" height="{ch:.2f}" '
            f'fill="{ "#f6c85f" if is_hit else "#1c2343"}" '
            f'fill-opacity="{ "0.55" if is_hit else "0.7"}" stroke="#3f4b88" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x + cw / 2:.2f}" y="{y + ch / 2 + 4:.2f}" text-anchor="middle" '
            f'fill="{ "#fff9de" if is_hit else "#b8c0e8"}" font-size="12" font-weight="{ "700" if is_hit else "500"}">{i}</text>'
        )

    label = {
        "kh": "រាមកេរ្តិ៍ ៣២ ក្រឡា",
        "en": "Reamker 32 Cells",
    }.get(language, "Reamker 32 格")
    parts.append(
        f'<text x="{size / 2:.2f}" y="{size - 6:.2f}" text-anchor="middle" fill="#9da9dc" font-size="12">{html_escape(label)}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def render_khmer_chart(reading: Dict[str, Any], language: str = "zh") -> str:
    """Render Khmer reading as embeddable HTML."""
    if not isinstance(reading, dict):
        return '<div style="padding:12px;border:1px solid #c62828;color:#c62828;">Invalid Khmer chart data.</div>'

    rk = reading.get("reamker", {})
    if rk.get("error"):
        return (
            '<div style="padding:12px;border:1px solid #c62828;color:#c62828;background:#fff5f5;">'
            f'{html_escape(str(rk.get("error")))}'
            "</div>"
        )

    zodiac = reading.get("zodiac", {}) if isinstance(reading.get("zodiac"), dict) else {}
    element = reading.get("element", {}) if isinstance(reading.get("element"), dict) else {}
    character = rk.get("character", {}) if isinstance(rk.get("character"), dict) else {}
    direction = rk.get("direction", {}) if isinstance(rk.get("direction"), dict) else {}
    arrows = reading.get("rama_arrows", {}) if isinstance(reading.get("rama_arrows"), dict) else {}
    arrow_data = arrows.get("data", {}) if isinstance(arrows.get("data"), dict) else {}

    zodiac_text = _pick_text(zodiac, language, khmer_key="kh", chinese_key="zh", english_key="en")
    element_text = _pick_text(element, language, khmer_key="kh", chinese_key="zh", english_key="en")
    character_text = _pick_text(character, language, khmer_key="kh", chinese_key="zh", english_key="en")
    stage_text = _pick_text(rk, language, khmer_key="stage_kh", chinese_key="stage_zh", english_key="stage_en")
    prophecy_text = _pick_text(rk, language, khmer_key="prophecy_kh", chinese_key="prophecy_zh")
    remedy_text = _pick_text(rk, language, khmer_key="remedy_kh", chinese_key="remedy_zh")
    direction_text = _pick_text(direction, language, khmer_key="kh", chinese_key="zh", english_key="en")
    arrow_text = _pick_text(arrow_data, language, khmer_key="kh", chinese_key="zh", english_key="en")

    labels = {
        "zh": ("生肖", "元素", "命主", "階段", "方位", "羅摩之箭", "預言", "化解", "高棉 Reamker 占星"),
        "en": ("Zodiac", "Element", "Character", "Stage", "Direction", "Rama Arrow", "Prophecy", "Remedy", "Khmer Reamker Astrology"),
        "kh": ("ឆ្នាំជូត", "ធាតុ", "តួអង្គ", "ដំណាក់កាល", "ទិស", "ព្រួញព្រះរាម", "ទំនាយ", "ដោះស្រាយ", "ហោរាសាស្ត្រ Reamker"),
    }.get(language, ("生肖", "元素", "命主", "階段", "方位", "羅摩之箭", "預言", "化解", "高棉 Reamker 占星"))

    info_rows = [
        (labels[0], zodiac_text),
        (labels[1], element_text),
        (labels[2], character_text),
        (labels[3], stage_text),
        (labels[4], direction_text),
        (labels[5], _format_arrow_value(arrows.get("arrow", ""), arrow_text)),
    ]

    row_html = "".join(
        f'<tr><td style="padding:6px 8px;color:#9da9dc;">{html_escape(k)}</td>'
        f'<td style="padding:6px 8px;color:#f4f6ff;">{html_escape(str(v))}</td></tr>'
        for k, v in info_rows
    )
    note = _pick_text(reading, language, khmer_key="note_kh", chinese_key="note_zh")
    grid_svg = render_reamker_grid_svg(reading, language=language)

    return (
        '<div style="max-width:920px;margin:0 auto;padding:16px;background:#0b1021;'
        'border:1px solid #2d3769;border-radius:12px;color:#f4f6ff;">'
        f'<h3 style="margin:0 0 12px 0;color:#f6c85f;">🇰🇭 {html_escape(labels[8])}</h3>'
        '<div style="display:grid;grid-template-columns:1fr;gap:12px;">'
        f'<table style="width:100%;border-collapse:collapse;background:#151d39;border-radius:10px;overflow:hidden;">{row_html}</table>'
        f'<div>{grid_svg}</div>'
        f'<div style="padding:10px 12px;background:#151d39;border-radius:10px;"><b>{html_escape(labels[6])}：</b>{html_escape(prophecy_text or "-")}</div>'
        f'<div style="padding:10px 12px;background:#151d39;border-radius:10px;"><b>{html_escape(labels[7])}：</b>{html_escape(remedy_text or "-")}</div>'
        f'<div style="padding:8px 10px;color:#b8c0e8;font-size:13px;">{html_escape(note)}</div>'
        "</div></div>"
    )


__all__ = ["render_khmer_chart", "render_reamker_grid_svg"]
