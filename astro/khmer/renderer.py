# -*- coding: utf-8 -*-
"""Khmer Reamker HTML/SVG renderer."""

from __future__ import annotations

from html import escape as html_escape
from typing import Any, Dict


def _pick_text(data: Dict[str, Any], language: str, *, kh: str, zh: str, en: str | None = None) -> str:
    if language == "kh":
        return str(data.get(kh) or data.get(zh) or "")
    if language == "en" and en:
        return str(data.get(en) or data.get(zh) or data.get(kh) or "")
    return str(data.get(zh) or data.get(kh) or "")


def render_reamker_grid_svg(reading: Dict[str, Any], size: int = 420, language: str = "zh") -> str:
    """Render the Reamker 32-cell marker as inline SVG."""
    rk = reading.get("reamker", {}) if isinstance(reading, dict) else {}
    cell = int(rk.get("cell", 0)) if isinstance(rk.get("cell", 0), int | float | str) else 0
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

    label = "Reamker 32 格" if language != "kh" else "រាមកេរ្តិ៍ ៣២ ក្រឡា"
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
    if isinstance(rk, dict) and rk.get("error"):
        return (
            '<div style="padding:12px;border:1px solid #c62828;color:#c62828;background:#fff5f5;">'
            f'{html_escape(str(rk.get("error")))}'
            "</div>"
        )

    zodiac = reading.get("zodiac", {}) if isinstance(reading.get("zodiac"), dict) else {}
    element = reading.get("element", {}) if isinstance(reading.get("element"), dict) else {}
    character = rk.get("character", {}) if isinstance(rk, dict) and isinstance(rk.get("character"), dict) else {}
    direction = rk.get("direction", {}) if isinstance(rk, dict) and isinstance(rk.get("direction"), dict) else {}
    arrows = reading.get("rama_arrows", {}) if isinstance(reading.get("rama_arrows"), dict) else {}
    arrow_data = arrows.get("data", {}) if isinstance(arrows.get("data"), dict) else {}

    zodiac_text = _pick_text(zodiac, language, kh="kh", zh="zh", en="en")
    element_text = _pick_text(element, language, kh="kh", zh="zh", en="en")
    character_text = _pick_text(character, language, kh="kh", zh="zh", en="en")
    stage_text = str(rk.get("stage_zh") or rk.get("stage_kh") or rk.get("stage_en") or "")
    prophecy_text = str(rk.get("prophecy_zh") or rk.get("prophecy_kh") or "")
    remedy_text = str(rk.get("remedy_zh") or rk.get("remedy_kh") or "")
    direction_text = _pick_text(direction, language, kh="kh", zh="zh", en="en")
    arrow_text = _pick_text(arrow_data, language, kh="kh", zh="zh", en="en")

    info_rows = [
        ("生肖", zodiac_text),
        ("元素", element_text),
        ("命主", character_text),
        ("階段", stage_text),
        ("方位", direction_text),
        ("羅摩之箭", f"{arrows.get('arrow', '')} · {arrow_text}".strip(" ·")),
    ]

    row_html = "".join(
        f'<tr><td style="padding:6px 8px;color:#9da9dc;">{html_escape(k)}</td>'
        f'<td style="padding:6px 8px;color:#f4f6ff;">{html_escape(str(v))}</td></tr>'
        for k, v in info_rows
    )
    note = str(reading.get("note_zh") or reading.get("note_kh") or "")
    grid_svg = render_reamker_grid_svg(reading, language=language)

    return (
        '<div style="max-width:920px;margin:0 auto;padding:16px;background:#0b1021;'
        'border:1px solid #2d3769;border-radius:12px;color:#f4f6ff;">'
        '<h3 style="margin:0 0 12px 0;color:#f6c85f;">🇰🇭 高棉 Reamker 占星</h3>'
        '<div style="display:grid;grid-template-columns:1fr;gap:12px;">'
        f'<table style="width:100%;border-collapse:collapse;background:#151d39;border-radius:10px;overflow:hidden;">{row_html}</table>'
        f'<div>{grid_svg}</div>'
        f'<div style="padding:10px 12px;background:#151d39;border-radius:10px;"><b>預言：</b>{html_escape(prophecy_text or "-")}</div>'
        f'<div style="padding:10px 12px;background:#151d39;border-radius:10px;"><b>化解：</b>{html_escape(remedy_text or "-")}</div>'
        f'<div style="padding:8px 10px;color:#b8c0e8;font-size:13px;">{html_escape(note)}</div>'
        "</div></div>"
    )


__all__ = ["render_khmer_chart", "render_reamker_grid_svg"]
