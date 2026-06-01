"""
astro/arabic/renderer — Streamlit renderer for Arabic Astrology
================================================================

Renders the complete Arabic astrology UI:
  • 🕌 阿拉伯占星方盤 (Arabic House Chart 4×4 grid)
  • 📋 排盤資訊 (Chart Information)
  • ☪ 阿拉伯點 (Arabic Parts / Lots) table
  • 🪐 行星位置與廟旺落陷 (Planet Positions & Essential Dignities)
  • 🏛️ 宮位 (House Cusps) table
  • 🔗 行星相位 (Planetary Aspects) table

UI 層模組。所有 streamlit import 都集中在頂部 (per 任務規範)。
Compute 邏輯 (ArabicChart dataclass、compute_arabic_chart、
helper 計算函式) 仍保留於 ``astro/arabic/arabic.py``。
"""
from __future__ import annotations

import streamlit as st
from typing import Callable, Optional

from astro.arabic.arabic import (
    ZODIAC_SIGNS,
    PLANET_COLORS,
    ArabicChart,
    _sign_index,
    _sign_degree,
    _format_deg,
)


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_arabic_chart(chart, after_chart_hook=None):
    """渲染完整的阿拉伯占星排盤"""
    _render_house_grid(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_arabic_parts_table(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_aspects(chart)


def _render_info(chart):
    st.subheader("📋 排盤資訊 (Chart Information)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間 (Time):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區 (Timezone):** UTC{chart.timezone:+.1f}")
        sect = "☀️ 日盤 (Day Chart)" if chart.is_day_chart else "🌙 夜盤 (Night Chart)"
        st.write(f"**盤型 (Sect):** {sect}")
    with col2:
        st.write(f"**地點 (Location):** {chart.location_name}")
        asc_info = ZODIAC_SIGNS[_sign_index(chart.ascendant)]
        mc_info = ZODIAC_SIGNS[_sign_index(chart.midheaven)]
        st.write(
            f"**上升點 (Ascendant):** {chart.asc_sign} "
            f"{_format_deg(chart.ascendant)} — "
            f"{asc_info[4]}"
        )
        st.write(
            f"**天頂 (Midheaven):** {chart.mc_sign} "
            f"{_format_deg(chart.midheaven)} — "
            f"{mc_info[4]}"
        )


def _render_arabic_parts_table(chart):
    st.subheader("☪ 阿拉伯點 (Arabic Parts / Lots)")
    sect_label = "☀️ 日盤" if chart.is_day_chart else "🌙 夜盤"
    st.caption(f"當前盤型：{sect_label}　—　公式依日夜盤自動切換")
    header = (
        "| 阿拉伯名 | 中文名 | 英文名 | 星座 (Sign) "
        "| 度數 (Degree) | 宮位 (House) |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for part in chart.arabic_parts:
        rows.append(
            f"| {part.arabic_name} "
            f"| {part.chinese_name} "
            f"| {part.english_name} "
            f"| {part.sign_glyph} {part.sign} ({part.sign_chinese}) "
            f"| {part.sign_degree:.2f}° "
            f"| {part.house} |"
        )
    st.markdown("\n".join(rows))


def _render_planet_table(chart):
    st.subheader("🪐 行星位置與廟旺落陷 (Planet Positions & Essential Dignities)")
    header = (
        "| 行星 (Planet) | 阿拉伯名 (Arabic) | 星座 (Sign) | 度數 (Degree) "
        "| 元素 (Element) | 宮位 (House) | 廟旺 (Dignity) | ℞ |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        rows.append(
            f"| {name_html} "
            f"| {p.arabic_sign} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° "
            f"| {p.element} "
            f"| {p.house} "
            f"| {p.dignity} "
            f"| {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ 宮位 (House Cusps)")
    header = (
        "| 宮位 (House) | 宮頭 (Cusp) | 星座 (Sign) "
        "| 阿拉伯名 (Arabic) | 行星 (Planets) |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for h in chart.houses:
        idx = _sign_index(h.cusp)
        sign_info = ZODIAC_SIGNS[idx]
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} "
            f"| {_format_deg(h.cusp)} "
            f"| {h.sign_glyph} {h.sign} "
            f"| {sign_info[4]} "
            f"| {planets_str} |"
        )
    st.markdown("\n".join(rows))


def _render_house_grid(chart):
    """渲染阿拉伯占星方盤 (Arabic Astrology House Grid)"""
    st.subheader("🕌 阿拉伯占星方盤 (Arabic House Chart)")

    asc_idx = _sign_index(chart.ascendant)
    mc_idx = _sign_index(chart.midheaven)

    # Build parts-per-house lookup for display in grid
    house_parts = {i: [] for i in range(1, 13)}
    for part in chart.arabic_parts:
        house_parts[part.house].append(part.chinese_name)

    cell_style = (
        "border:1px solid #555; padding:6px 4px; text-align:center; "
        "vertical-align:top; font-size:11px;"
    )
    asc_cell = cell_style + " background:#3d3010;"
    mc_cell = cell_style + " background:#1a2a3d;"

    # 4×4 grid: outer 12 cells = houses, center 2×2 = chart info
    grid = [
        [10, 11, 12,  1],
        [ 9, -1, -1,  2],
        [ 8, -1, -1,  3],
        [ 7,  6,  5,  4],
    ]

    sect_icon = "☀️" if chart.is_day_chart else "🌙"
    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:collapse; margin:auto; '
        'width:100%; max-width:600px; table-layout:fixed;">'
        '<caption style="caption-side:top; font-size:14px; padding:4px;">'
        '<b>Arabic House Chart</b> — '
        f'🔺 ASC {ZODIAC_SIGNS[asc_idx][1]}{ZODIAC_SIGNS[asc_idx][0]} '
        f'{_sign_degree(chart.ascendant):.1f}° &nbsp; '
        f'⬡ MC {ZODIAC_SIGNS[mc_idx][1]}{ZODIAC_SIGNS[mc_idx][0]} '
        f'{_sign_degree(chart.midheaven):.1f}° &nbsp; '
        f'{sect_icon}'
        '</caption>'
    )

    for row_idx, row in enumerate(grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    sect_text = "Day 日盤" if chart.is_day_chart else "Night 夜盤"
                    html += (
                        f'<td colspan="2" rowspan="2" style="'
                        f'border:1px solid #444; padding:10px; text-align:center; '
                        f'vertical-align:middle; background:#2a2a2a; '
                        f'font-size:13px; color:#e0e0e0;">'
                        f'<b>☪ Arabic<br/>Astrology</b><br/>'
                        f'<small>{chart.year}/{chart.month}/{chart.day}<br/>'
                        f'{chart.hour:02d}:{chart.minute:02d} '
                        f'UTC{chart.timezone:+.1f}<br/>'
                        f'{chart.location_name}<br/>'
                        f'{sect_icon} {sect_text}</small>'
                        f'</td>'
                    )
                    col_idx += 2
                    continue
                else:
                    col_idx += 1
                    continue
            else:
                h = next((x for x in chart.houses if x.number == idx), None)
                if h is None:
                    html += f'<td style="{cell_style}"></td>'
                    col_idx += 1
                    continue
                sign_idx_h = _sign_index(h.cusp)
                sign_info = ZODIAC_SIGNS[sign_idx_h]
                # Planets in this house
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(p, "#c8c8c8")};'
                    f'font-weight:bold">{p.split(" (")[0]}</span>'
                    for p in h.planets
                ) if h.planets else ""
                # Arabic parts in this house (abbreviated)
                parts_in = house_parts.get(idx, [])
                parts_html = (
                    '<br/><span style="color:#b8860b; font-size:10px;">'
                    + " ".join(parts_in) + '</span>'
                ) if parts_in else ""
                is_asc = (idx == 1)
                is_mc = (idx == 10)
                style = asc_cell if is_asc else (mc_cell if is_mc else cell_style)
                marker = " 🔺" if is_asc else (" ⬡" if is_mc else "")
                html += (
                    f'<td style="{style}">'
                    f'<b>{idx}</b>{marker}<br/>'
                    f'{sign_info[1]} {sign_info[0]}<br/>'
                    f'<small>{sign_info[4]}</small><br/>'
                    f'<small>{_format_deg(h.cusp)}</small><br/>'
                    f'{p_html}'
                    f'{parts_html}'
                    f'</td>'
                )
            col_idx += 1
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)
    st.caption(
        "🔺 = House 1 (上升點 Ascendant)　"
        "⬡ = House 10 (天頂 Midheaven)　"
        "金色文字 = 阿拉伯點 (Arabic Parts)"
    )


def _render_aspects(chart):
    """渲染行星相位表 (Planetary Aspects)"""
    st.subheader("🔗 行星相位 (Planetary Aspects)")
    if not chart.aspects:
        st.write("無相位 (No aspects found)")
        return
    header = (
        "| 行星 1 (Planet 1) | 相位 (Aspect) | 阿拉伯名 "
        "| 行星 2 (Planet 2) | 實際角距 (Angle) | 容許度 (Orb) |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for a in chart.aspects:
        c1 = PLANET_COLORS.get(a.planet1, "#c8c8c8")
        c2 = PLANET_COLORS.get(a.planet2, "#c8c8c8")
        p1_html = (
            f'<span style="color:{c1};font-weight:bold">'
            f'{a.planet1.split(" (")[0]}</span>'
        )
        p2_html = (
            f'<span style="color:{c2};font-weight:bold">'
            f'{a.planet2.split(" (")[0]}</span>'
        )
        rows.append(
            f"| {p1_html} "
            f"| {a.chinese_name} ({a.aspect_name}) "
            f"| {a.arabic_name} "
            f"| {p2_html} "
            f"| {a.angle:.2f}° "
            f"| {a.orb:.2f}° |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# Streamlit 入口
# ============================================================

def render_streamlit(
    chart,
    after_chart_hook: Optional[Callable] = None,
) -> None:
    """Streamlit 入口：渲染完整的阿拉伯占星排盤 UI。

    Args:
        chart: 從 ``astro.arabic.arabic.compute_arabic_chart`` 取得的
            ``ArabicChart`` 物件。
        after_chart_hook: 選用 hook,於方盤渲染後、表格前觸發 (例如
            share/export 按鈕)。
    """
    render_arabic_chart(chart, after_chart_hook=after_chart_hook)
