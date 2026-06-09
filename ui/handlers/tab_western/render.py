"""
ui/handlers/tab_western/render.py — Streamlit renderer for Western Astrology
=============================================================================

Renders the complete Western natal chart UI including:
  • SVG Western Wheel — 4×4 grid with house cusps, planet markers,
    birth info in the centre
  • Chart Information table (date, time, timezone, ASC, MC)
  • Planet Positions table — sign, degree, element, house, dignity, joy
  • House Cusps table
  • Aspects table (major 5 — conjunction, opposition, trine, square, sextile)
  • Essential Dignities & Debilities (with sect/joy icons)
  • Day/Night Sect indicator
  • Chart Ruler block (exaltation co-ruler, first-house planets, Moon as body)
  • Arabic Parts / Lots (Fortune, Spirit, Marriage, Children, Mother, Father)
  • Fixed Star Conjunctions (Aldebaran, Regulus, Antares, Spica, Sirius …)

IMPORTANT: ``import streamlit`` is done inside the function bodies
(per CONTRIBUTING.md convention) so this module can be safely imported
in unit-test contexts where Streamlit is not present.  The compute
functions and dataclasses live in :mod:`astro.western.western`.

西洋占星 Streamlit 渲染模組。所有 streamlit import 均在函數體內，
符合 CONTRIBUTING.md 規範；計算邏輯與資料類別位於 astro/western/western.py。
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from astro.i18n import auto_cn
from astro.western.western import (
    ASPECT_TYPES,
    CLASSICAL_DIGNITIES,
    PLANET_COLORS,
    WESTERN_ARABIC_PARTS,
    ZODIAC_SIGNS,
    WesternChart,
)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — pure (no streamlit), so they can be unit-tested
# ─────────────────────────────────────────────────────────────────────────────

def _sign_index(deg: float) -> int:
    return int((deg % 360.0) / 30.0)


def _sign_degree(deg: float) -> float:
    return (deg % 360.0) % 30.0


def _format_deg(deg: float) -> str:
    deg = deg % 360.0
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _xml_escape(text: str) -> str:
    """Escape special XML characters for safe SVG text content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _wheel_themes() -> dict[str, dict[str, str]]:
    """Professional wheel themes for the natal renderer."""
    return {
        "modern": {
            "page_bg": "#0f1220",
            "caption_text": "#e0e0e0",
            "muted_text": "#aaa",
            "panel_fill": "#1e1e2e",
            "center_fill": "#1a1a2e",
            "border": "#444",
            "asc_fill": "#3d3010",
            "mc_fill": "#1a2a3d",
            "empty_text": "#555",
        },
        "classic": {
            "page_bg": "#fcfcfa",
            "caption_text": "#1f1f1f",
            "muted_text": "#5f5f5f",
            "panel_fill": "#ffffff",
            "center_fill": "#f6f4ef",
            "border": "#5d5d5d",
            "asc_fill": "#ece7db",
            "mc_fill": "#e9edf1",
            "empty_text": "#8a8a8a",
        },
        "hellenistic": {
            "page_bg": "#f3ead6",
            "caption_text": "#3d2412",
            "muted_text": "#7a6041",
            "panel_fill": "#f8f1df",
            "center_fill": "#efe2c2",
            "border": "#8b6b39",
            "asc_fill": "#ead3a2",
            "mc_fill": "#dbc596",
            "empty_text": "#9a845e",
        },
    }


def _orb_strength_label(orb: float, max_orb: float) -> str:
    """Human-friendly orb strength label."""
    ratio = 0.0 if max_orb <= 0 else orb / max_orb
    if ratio <= 0.2:
        return auto_cn("極緊", "Exact")
    if ratio <= 0.45:
        return auto_cn("緊密", "Tight")
    if ratio <= 0.75:
        return auto_cn("中等", "Moderate")
    return auto_cn("寬鬆", "Wide")


def _collect_aspects(chart: WesternChart) -> list[dict[str, Any]]:
    """Collect chart aspects once so UI sections can reuse them."""
    aspects: list[dict[str, Any]] = []
    for i in range(len(chart.planets)):
        for j in range(i + 1, len(chart.planets)):
            p1 = chart.planets[i]
            p2 = chart.planets[j]
            diff = abs(p1.longitude - p2.longitude)
            if diff > 180:
                diff = 360 - diff
            for asp in ASPECT_TYPES:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    aspects.append(
                        {
                            "p1": p1.name,
                            "p2": p2.name,
                            "aspect": asp["name"],
                            "symbol": asp["symbol"],
                            "angle": asp["angle"],
                            "orb": orb,
                            "max_orb": asp["orb"],
                            "strength": _orb_strength_label(orb, asp["orb"]),
                        }
                    )
                    break
    aspects.sort(key=lambda item: item["orb"])
    return aspects


# ─────────────────────────────────────────────────────────────────────────────
# SVG / HTML builders — pure, return strings
# ─────────────────────────────────────────────────────────────────────────────

def build_western_wheel_svg(
    chart: WesternChart,
    gender: Optional[str] = None,
    theme: str = "modern",
) -> str:
    """Return the SVG markup string for the Western Wheel visualisation.

    產生西洋占星輪盤 SVG 標記字串（4×4 格子 + 中央出生資訊），
    可單獨測試或嵌入到非 streamlit 環境中。

    Args:
        chart:  Computed WesternChart.
        gender: "male" / "female" / None — displayed in the centre.

    Returns:
        A self-contained ``<div><svg>…</svg></div>`` string.
    """
    palette = _wheel_themes().get(theme, _wheel_themes()["modern"])
    planet_map = {p.name: p for p in chart.planets}

    asc_idx = _sign_index(chart.ascendant)
    mc_idx = _sign_index(chart.midheaven)
    house_signs = {h.number: _sign_index(h.cusp) for h in chart.houses}
    asc_info = ZODIAC_SIGNS[asc_idx]
    mc_info = ZODIAC_SIGNS[mc_idx]

    wheel_grid = [
        [10, 11, 12, 1],
        [9, -1, -1, 2],
        [8, -1, -1, 3],
        [7, 6, 5, 4],
    ]

    # SVG layout constants
    W = 560
    CAP_H = 44
    CW = W / 4          # cell width  = 140
    CH = 110            # cell height = 110
    H = CAP_H + CH * 4  # total height

    parts: list[str] = []
    parts.append(
        f'<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" '
        f'style="background:{palette["page_bg"]};border-radius:14px;'
        f'width:100%;max-width:{W}px;display:block;margin:auto;'
        f'font-family:sans-serif;">'
    )

    # Caption
    asc_deg = f"{_sign_degree(chart.ascendant):.1f}"
    mc_deg = f"{_sign_degree(chart.midheaven):.1f}"
    parts.append(
        f'<text x="{W / 2}" y="17" text-anchor="middle" '
        f'fill="{palette["caption_text"]}" font-size="14" font-weight="bold">'
        f'Western Wheel Chart</text>'
    )
    parts.append(
        f'<text x="{W / 2}" y="36" text-anchor="middle" '
        f'fill="{palette["muted_text"]}" font-size="11">'
        f'\u0020\u25B2 ASC {_xml_escape(asc_info[1])}{_xml_escape(asc_info[0])} {asc_deg}\u00B0'
        f'\u2003\u2B21 MC {_xml_escape(mc_info[1])}{_xml_escape(mc_info[0])} {mc_deg}\u00B0'
        f'</text>'
    )

    center_rendered = False
    for r, row_data in enumerate(wheel_grid):
        for c, idx in enumerate(row_data):
            x = c * CW
            y = CAP_H + r * CH
            cx = x + CW / 2

            if idx == -1:
                if center_rendered:
                    continue
                # Merge four centre cells into one — show birth info
                center_rendered = True
                mx = 1 * CW       # col 1
                my = CAP_H + 1 * CH  # row 1
                mw = CW * 2       # span 2 cols
                mh = CH * 2       # span 2 rows
                mcx = mx + mw / 2
                mcy = my + mh / 2

                parts.append(
                    f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" '
                    f'fill="{palette["center_fill"]}" stroke="{palette["border"]}" stroke-width="1" rx="2"/>'
                )

                # Birth date line
                date_str = f'{chart.year}/{chart.month:02d}/{chart.day:02d}'
                time_str = f'{chart.hour:02d}:{chart.minute:02d}'
                tz_str = f'UTC{chart.timezone:+.1f}'
                parts.append(
                    f'<text x="{mcx}" y="{mcy - 28}" text-anchor="middle" '
                    f'fill="{palette["caption_text"]}" font-size="12">'
                    f'{_xml_escape(date_str)}  {_xml_escape(time_str)}</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy - 10}" text-anchor="middle" '
                f'fill="{palette["muted_text"]}" font-size="11">{_xml_escape(tz_str)}</text>'
                )

                # Gender line
                if gender:
                    gender_label = "男命" if gender == "male" else "女命"
                    parts.append(
                        f'<text x="{mcx}" y="{mcy + 10}" text-anchor="middle" '
                        f'fill="{palette["caption_text"]}" font-size="12">{_xml_escape(gender_label)}</text>'
                    )

                # Location line
                if chart.location_name:
                    parts.append(
                        f'<text x="{mcx}" y="{mcy + 30}" text-anchor="middle" '
                        f'fill="{palette["muted_text"]}" font-size="11">{_xml_escape(chart.location_name)}</text>'
                    )
                continue

            h = next((hh for hh in chart.houses if hh.number == idx), None)
            if h is None:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" '
                    f'fill="{palette["panel_fill"]}" stroke="{palette["border"]}" stroke-width="1"/>'
                )
                continue

            sign_idx = house_signs.get(idx, _sign_index(h.cusp))
            sign_info = ZODIAC_SIGNS[sign_idx]
            planets_in_house = h.planets

            is_asc = idx == 1
            is_mc = idx == 10
            fill = (
                palette["asc_fill"] if is_asc
                else (palette["mc_fill"] if is_mc else palette["panel_fill"])
            )
            house_title = _xml_escape(
                f"House {idx} / 第{idx}宮 • {sign_info[0]} {sign_info[1]} • "
                f"Cusp {_format_deg(h.cusp)} • "
                f"Planets: {', '.join(planets_in_house) if planets_in_house else '—'}"
            )

            parts.append(
                f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" '
                f'fill="{fill}" stroke="{palette["border"]}" stroke-width="1" rx="2">'
                f'<title>{house_title}</title></rect>'
            )

            # House number + marker
            marker = " \u25B2" if is_asc else (" \u2B21" if is_mc else "")
            parts.append(
                f'<text x="{cx}" y="{y + 18}" text-anchor="middle" '
                f'fill="{palette["caption_text"]}" font-size="13" font-weight="bold">'
                f'{idx}{marker}</text>'
            )

            # Sign glyph + name
            parts.append(
                f'<text x="{cx}" y="{y + 34}" text-anchor="middle" '
                f'fill="{palette["caption_text"]}" font-size="11">'
                f'{_xml_escape(sign_info[1])} {_xml_escape(sign_info[0])}</text>'
            )

            # Degree
            parts.append(
                f'<text x="{cx}" y="{y + 48}" text-anchor="middle" '
                f'fill="{palette["muted_text"]}" font-size="10">{_xml_escape(_format_deg(h.cusp))}</text>'
            )

            # Planets – laid out in rows of up to 3
            if planets_in_house:
                n = len(planets_in_house)
                font_size = 11 if n <= 2 else (10 if n <= 3 else 9)
                names = [p.split(" ")[0] for p in planets_in_house]
                per_row = min(n, 3)
                p_spacing = 44   # horizontal gap between planet labels
                p_base_y = 66    # vertical offset for first planet row
                p_row_h = 16     # vertical gap between planet rows
                for i, (short, full) in enumerate(
                    zip(names, planets_in_house)
                ):
                    row_i = i // per_row
                    col_i = i % per_row
                    row_count = min(per_row, n - row_i * per_row)
                    px = cx + (col_i - (row_count - 1) / 2) * p_spacing
                    py = y + p_base_y + row_i * p_row_h
                    color = PLANET_COLORS.get(full, "#c8c8c8")
                    planet = planet_map.get(full)
                    if planet:
                        planet_title = _xml_escape(
                            f"{full} • {planet.sign_glyph} {planet.sign} "
                            f"{planet.sign_degree:.2f}° • House {planet.house} / 第{planet.house}宮 • "
                            f"{planet.essential_dignity} • {planet.joy_status}"
                        )
                    else:
                        planet_title = _xml_escape(full)
                    parts.append(
                        f'<text x="{px}" y="{py}" text-anchor="middle" '
                        f'fill="{color}" font-size="{font_size}" '
                        f'font-weight="bold">{_xml_escape(short)}'
                        f'<title>{planet_title}</title></text>'
                    )
            else:
                parts.append(
                    f'<text x="{cx}" y="{y + 68}" text-anchor="middle" '
                    f'fill="{palette["empty_text"]}" font-size="11">\u2014</text>'
                )

    parts.append("</svg></div>")
    return "".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit sub-renderers — each calls ``st`` inside the body
# ─────────────────────────────────────────────────────────────────────────────

def _render_wheel_chart(chart: WesternChart, gender: Optional[str] = None) -> None:
    """Render the Western Wheel Chart (SVG)."""
    import streamlit as st
    st.subheader(auto_cn("🔮 西洋占星輪盤", "🔮 Western Wheel"))
    theme_items = [
        ("modern", auto_cn("現代彩色", "Modern Color")),
        ("classic", auto_cn("古典黑白", "Classic B&W")),
        ("hellenistic", auto_cn("希臘化風格", "Hellenistic Style")),
    ]
    label_to_key = {label: key for key, label in theme_items}
    selected_label = st.selectbox(
        auto_cn("圖盤主題", "Wheel Theme"),
        options=[label for _, label in theme_items],
        index=0,
        key="western_wheel_theme",
    )
    theme_key = label_to_key[selected_label]
    st.markdown(
        build_western_wheel_svg(chart, gender=gender, theme=theme_key),
        unsafe_allow_html=True,
    )
    st.caption(
        auto_cn(
            "▲ = 第 1 宮（上升） · ⬡ = 第 10 宮（中天） · 可懸停查看宮位與行星摘要",
            "▲ = House 1 (Ascendant) · ⬡ = House 10 (Midheaven) · Hover for house and planet summaries",
        )
    )
    st.caption(
        auto_cn(
            f"目前盤面引擎：{'恆星黃道 Lahiri' if chart.sidereal_mode else '回歸黃道 Tropical'} · 宮制：Placidus · 相位容許度：合沖 8°／拱刑 6°／六合 4°",
            f"Current engine: {'Sidereal Lahiri' if chart.sidereal_mode else 'Tropical'} · Houses: Placidus · Orbs: 8° conj/opp, 6° trine/square, 4° sextile",
        )
    )


def _render_info(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("📋 Chart Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Date:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**Time:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**Timezone:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**Location:** {chart.location_name}")
        asc_info = ZODIAC_SIGNS[_sign_index(chart.ascendant)]
        mc_info = ZODIAC_SIGNS[_sign_index(chart.midheaven)]
        st.write(
            f"**Ascendant:** {asc_info[1]} {chart.asc_sign} "
            f"({asc_info[2]}) "
            f"{_format_deg(chart.ascendant)}"
        )
        st.write(
            f"**Midheaven:** {mc_info[1]} {chart.mc_sign} {_format_deg(chart.midheaven)}"
        )
    if chart.sidereal_mode:
        st.info(f"⚙️ **Sidereal Mode (Lahiri Ayanamsa):** {chart.ayanamsa:.2f}°")


def _render_planet_table(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("🪐 Planet Positions")
    header = (
        "| Planet | Sign | Degree | Element | House | Retrograde "
        "| Essential Dignity | Joy Status |"
    )
    sep = (
        "|:------:|:----:|:------:|:-------:|:-----:|:----------:"
        "|:---------------:|:---------:|"
    )
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° "
            f"| {p.element} "
            f"| {p.house} "
            f"| {retro} "
            f"| {p.essential_dignity} "
            f"| {p.joy_status} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("🏛️ House Cusps")
    header = "| House | Cusp | Sign | Planets |"
    sep = "|:-----:|:----:|:----:|:-------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.sign_glyph} {h.sign} | {planets_str} |"
        )
    st.markdown("\n".join(rows))


def _render_aspects(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("🔗 Aspects")
    aspects = _collect_aspects(chart)
    if not aspects:
        st.info("No significant aspects found.")
        return
    header = "| Planet 1 | Aspect | Planet 2 | Orb |"
    sep = "|:--------:|:------:|:--------:|:---:|"
    rows = [header, sep]
    for a in aspects:
        rows.append(
            f"| {a['p1']} | {a['symbol']} {a['aspect']} "
            f"| {a['p2']} | {a['orb']:.1f}° |"
        )
    st.markdown("\n".join(rows))


def _render_classical_dignities(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("🏛️ 本質廟旺落陷 (Essential Dignities & Debilities)")
    rows = [
        "| Planet | Sign | House | Dignity | Joy |",
        "|:------:|:----:|:-----:|:-------:|:---:|",
    ]
    for p in chart.planets:
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        dignity_icon = ""
        if "入廟" in p.essential_dignity:
            dignity_icon = "♔"
        elif "入旺" in p.essential_dignity:
            dignity_icon = "↑"
        elif "落陷" in p.essential_dignity:
            dignity_icon = "♕"
        elif "入弱" in p.essential_dignity:
            dignity_icon = "↓"
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.house} "
            f"| {dignity_icon} {p.essential_dignity} "
            f"| {'⭐' if '喜樂' in p.joy_status else '—'} {p.joy_status} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    st.markdown("**符號說明:** ♔ 入廟 | ↑ 入旺 | ♕ 落陷 | ↓ 入弱 | ⭐ 喜樂")


def _render_day_night_sect(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("☀️ 🌙 日夜盤判定 (Day & Night Sect)")
    if chart.is_day_chart:
        st.success(
            "**日盤 (Day Chart)** — 太陽位於地平線以上（House 7–12）\n\n"
            "日盤中，太陽作為主要主宰，行星若在日間位置（晝行星，如 Sun、Jupiter、Saturn）效力更強。\n\n"
            "⚠️ 本盤 Venus、Moon 等夜行星在此盤中效力減弱。"
        )
    else:
        st.info(
            "**夜盤 (Night Chart)** — 太陽位於地平線以下（House 1–6）\n\n"
            "夜盤中，月亮作為主要主宰，夜行星（如 Moon、Venus）效力更強。\n\n"
            "⚠️ 本盤 Sun、Jupiter 等日行星在此盤中效力減弱。"
        )


def _render_chart_ruler(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("👑 命度主星 (Chart Ruler)")
    asc_idx = _sign_index(chart.ascendant)
    asc_sign_info = ZODIAC_SIGNS[asc_idx]
    ruler_info = CLASSICAL_DIGNITIES[asc_idx]
    ruler_name = ruler_info.get("domicile", "—")

    dignity_icon = ""
    dignity_text = chart.chart_ruler_dignity
    if "入廟" in dignity_text:
        dignity_icon = "♔"
    elif "入旺" in dignity_text:
        dignity_icon = "↑"
    elif "落陷" in dignity_text:
        dignity_icon = "♕"
    elif "入弱" in dignity_text:
        dignity_icon = "↓"

    st.markdown(
        f"**上升星座:** {asc_sign_info[1]} {asc_sign_info[0]}（{asc_sign_info[2]}）\n\n"
        f"**命度主星:** {chart.chart_ruler} — {dignity_icon} {dignity_text}\n\n"
        f"**主星守護:** {ruler_name or '—'} 守護 {asc_sign_info[0]}\n\n"
        f"命度主星是全盤最重要的行星，它的吉凶、廟旺落陷、飛遊狀態\n"
        f"決定了命主一生的主要命運走向。"
    )

    # Also show the main significators
    st.markdown("**主要象徵星:**")
    sig_cols = st.columns(3)
    with sig_cols[0]:
        st.markdown(f"**命度主星:** {chart.chart_ruler}")
    with sig_cols[1]:
        st.markdown(f"**助產星 (Exaltation):** "
                    f"{ruler_info.get('exaltation', '—') or '—'}")
    with sig_cols[2]:
        first_house_planets = next(
            (", ".join(h.planets) for h in chart.houses if h.number == 1), "空"
        )
        moon_name = next((p.name for p in chart.planets if "Moon" in p.name), "—")
        st.markdown(
            f"**命宮行星:** {first_house_planets}\n\n"
            f"**身宮 (Moon):** {moon_name}"
        )


def _render_arabic_parts(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("🔮 阿拉伯點 / 幸運點 (Arabic Parts / Lots)")

    # Day/Night indicator
    sect = "日盤公式" if chart.is_day_chart else "夜盤公式"
    st.caption(f"計算方式: {sect} — Lot of Fortune = ASC + {'Moon - Sun' if chart.is_day_chart else 'Sun - Moon'}")

    header = "| Lot | Sign | Degree | House |"
    sep = "|:---|:----:|:------:|:-----:|"
    rows = [header, sep]
    for part in chart.arabic_parts:
        rows.append(
            f"| **{part.chinese_name}** ({part.english_name}) "
            f"| {part.sign_glyph} {part.sign} "
            f"| {part.sign_degree:.2f}° "
            f"| {part.house} |"
        )
    st.markdown("\n".join(rows))

    st.markdown(
        "**說明:** 阿拉伯點是古典占星的重要技法，"
        "透過上升點與行星經度的加減運算推導各生活領域的敏感度數。"
    )


def _render_fixed_stars(chart: WesternChart) -> None:
    import streamlit as st
    st.subheader("⭐ 恆星相位 (Fixed Star Conjunctions)")

    if not chart.fixed_star_conjunctions:
        st.info("本盤無恆星與行星形成緊密合相（orb ≤ 1°）。")
        return

    header = "| Planet | Fixed Star | Chinese | Orb | 恆星意義 |"
    sep = "|:------:|:----------:|:-------:|:---:|:------:|"
    rows = [header, sep]
    for fc in chart.fixed_star_conjunctions:
        p_color = PLANET_COLORS.get(fc.planet_name, "#c8c8c8")
        planet_html = f'<span style="color:{p_color};font-weight:bold">{fc.planet_name}</span>'
        rows.append(
            f"| {planet_html} "
            f"| {fc.star_name} "
            f"| {fc.star_name_cn} "
            f"| {fc.orb:.2f}° "
            f"| {fc.meaning} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    st.markdown(
        "**恆星說明:** 恆星（Fixed Stars）與行星合相時，"
        "會赋予行星特殊的影響力，其效力較一般行星相位更為強烈且恆定。\n\n"
        "主要恆星：\n"
        "- **Aldebaran (畢宿五)** — 勇氣、好戰\n"
        "- **Regulus (軒轅十四)** — 王權、吉祥\n"
        "- **Antares (心宿二)** — 膽識、軍事\n"
        "- **Spica (角宿一)** — 財富、創造\n"
        "- **Sirius (天狼星)** — 榮耀、財富\n"
    )


def _render_interactive_explorer(chart: WesternChart) -> None:
    """Interactive detail explorer for natal-chart objects."""
    import streamlit as st

    st.subheader(auto_cn("🧭 互動命盤導覽", "🧭 Interactive Chart Explorer"))
    st.caption(
        auto_cn(
            "點擊下列行星、宮位、相位、阿拉伯點或恆星按鈕，即可查看更細的命盤說明。",
            "Click the planet, house, aspect, lot, or fixed-star buttons below to inspect detailed chart notes.",
        )
    )

    aspect_items = _collect_aspects(chart)
    explorer_tabs = st.tabs(
        [
            auto_cn("行星", "Planets"),
            auto_cn("宮位", "Houses"),
            auto_cn("相位", "Aspects"),
            auto_cn("阿拉伯點", "Arabic Parts"),
            auto_cn("恆星", "Fixed Stars"),
        ]
    )

    with explorer_tabs[0]:
        planet_cols = st.columns(4)
        for idx, planet in enumerate(chart.planets):
            color = PLANET_COLORS.get(planet.name, "#c8c8c8")
            with planet_cols[idx % 4]:
                with st.popover(planet.name, use_container_width=True):
                    st.markdown(
                        f"### {planet.name}\n"
                        f"- **{auto_cn('位置', 'Position')}**: {planet.sign_glyph} {planet.sign} {planet.sign_degree:.2f}°\n"
                        f"- **{auto_cn('宮位', 'House')}**: {planet.house}\n"
                        f"- **{auto_cn('元素', 'Element')}**: {planet.element}\n"
                        f"- **{auto_cn('逆行', 'Retrograde')}**: "
                        f"{auto_cn('是', 'Yes') if planet.retrograde else auto_cn('否', 'No')}\n"
                        f"- **{auto_cn('本質尊貴', 'Essential dignity')}**: {planet.essential_dignity}\n"
                        f"- **{auto_cn('喜樂宮', 'Planetary joy')}**: {planet.joy_status}"
                    )
                    if planet.fixed_star_conjunctions:
                        st.markdown(f"**{auto_cn('恆星合相', 'Fixed-star conjunctions')}**")
                        for item in planet.fixed_star_conjunctions:
                            st.write(f"- {item.star_name} / {item.star_name_cn} ({item.orb:.2f}°)")
                    else:
                        st.caption(auto_cn("此行星無緊密恆星合相。", "No tight fixed-star conjunctions for this planet."))
                st.markdown(
                    f"<div style='margin-top:6px;text-align:center;color:{color};font-weight:700;'>"
                    f"{planet.sign_glyph} {planet.sign} {planet.sign_degree:.1f}°</div>",
                    unsafe_allow_html=True,
                )

    with explorer_tabs[1]:
        house_cols = st.columns(4)
        for idx, house in enumerate(chart.houses):
            with house_cols[idx % 4]:
                with st.popover(f"{auto_cn('第', 'House ')}{house.number}{auto_cn('宮', '')}", use_container_width=True):
                    st.markdown(
                        f"### {auto_cn('第', 'House ')}{house.number}{auto_cn('宮', '')}\n"
                        f"- **{auto_cn('宮頭', 'Cusp')}**: {house.sign_glyph} {house.sign} {_format_deg(house.cusp)}\n"
                        f"- **{auto_cn('宮內行星', 'Planets inside')}**: {', '.join(house.planets) if house.planets else '—'}"
                    )

    with explorer_tabs[2]:
        if not aspect_items:
            st.info(auto_cn("此命盤無顯著主要相位。", "No major aspects found for this chart."))
        else:
            aspect_cols = st.columns(2)
            for idx, aspect in enumerate(aspect_items):
                with aspect_cols[idx % 2]:
                    label = f"{aspect['p1']} {aspect['symbol']} {aspect['p2']}"
                    with st.popover(label, use_container_width=True):
                        st.markdown(
                            f"### {label}\n"
                            f"- **{auto_cn('相位', 'Aspect')}**: {aspect['aspect']}\n"
                            f"- **{auto_cn('精確角度', 'Exact angle')}**: {aspect['angle']}°\n"
                            f"- **{auto_cn('容許度', 'Orb')}**: {aspect['orb']:.2f}° / {aspect['max_orb']:.1f}°\n"
                            f"- **{auto_cn('強度', 'Strength')}**: {aspect['strength']}"
                        )
                    st.caption(
                        f"{auto_cn('容許度', 'Orb')} {aspect['orb']:.2f}° · "
                        f"{auto_cn('強度', 'Strength')} {aspect['strength']}"
                    )

    with explorer_tabs[3]:
        if not chart.arabic_parts:
            st.info(auto_cn("此命盤未產生阿拉伯點資料。", "No Arabic-part data was produced for this chart."))
        else:
            part_cols = st.columns(3)
            for idx, part in enumerate(chart.arabic_parts):
                with part_cols[idx % 3]:
                    with st.popover(part.chinese_name, use_container_width=True):
                        st.markdown(
                            f"### {part.chinese_name} / {part.english_name}\n"
                            f"- **{auto_cn('位置', 'Position')}**: {part.sign_glyph} {part.sign} {part.sign_degree:.2f}°\n"
                            f"- **{auto_cn('宮位', 'House')}**: {part.house}\n"
                            f"- **{auto_cn('盤別公式', 'Sect formula')}**: "
                            f"{auto_cn('日盤', 'Day chart') if chart.is_day_chart else auto_cn('夜盤', 'Night chart')}"
                        )

    with explorer_tabs[4]:
        if not chart.fixed_star_conjunctions:
            st.info(auto_cn("此命盤無緊密恆星合相。", "No tight fixed-star conjunctions were found."))
        else:
            star_cols = st.columns(2)
            for idx, item in enumerate(chart.fixed_star_conjunctions):
                with star_cols[idx % 2]:
                    with st.popover(f"{item.star_name} · {item.planet_name}", use_container_width=True):
                        st.markdown(
                            f"### {item.star_name} / {item.star_name_cn}\n"
                            f"- **{auto_cn('相合行星', 'Conjunct planet')}**: {item.planet_name}\n"
                            f"- **{auto_cn('容許度', 'Orb')}**: {item.orb:.2f}°\n"
                            f"- **{auto_cn('古典含義', 'Traditional meaning')}**: {item.meaning}"
                        )


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    chart: WesternChart,
    after_chart_hook: Optional[Callable[[], None]] = None,
    gender: Optional[str] = None,
) -> None:
    """Render the complete Western natal chart UI in Streamlit.

    渲染完整西洋占星排盤 UI。包含輪盤、行星表、宮位表、相位、本質廟旺、
    日夜盤判定、命度主星、阿拉伯點、恆星相位九大區塊。

    All ``streamlit`` imports are deferred to function bodies so this
    module remains import-safe in streamlit-less contexts (the audit
    guard in ``scripts/check_no_streamlit_in_astro.py`` will not flag
    ``astro/western/western.py`` any more).

    Args:
        chart:            Computed :class:`WesternChart` instance.
        after_chart_hook: Optional callable invoked after the wheel chart,
                          before the first ``st.divider()``.  Typically
                          used to inject AI-analysis buttons.
        gender:           "male" / "female" / None — shown in the wheel
                          centre.
    """
    import streamlit as st

    _render_wheel_chart(chart, gender=gender)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_interactive_explorer(chart)
    st.divider()
    _render_info(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_aspects(chart)
    st.divider()
    _render_classical_dignities(chart)
    st.divider()
    _render_day_night_sect(chart)
    st.divider()
    _render_chart_ruler(chart)
    st.divider()
    _render_arabic_parts(chart)
    st.divider()
    _render_fixed_stars(chart)
