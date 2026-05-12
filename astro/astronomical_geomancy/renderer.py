"""
astro/astronomical_geomancy/renderer.py
══════════════════════════════════════════════════════════════
Streamlit renderer for Astronomical Geomancy (天文幾何占卜).

Renders:
  - Input panel (question, question type, seed mode)
  - 12-house wheel SVG / visual chart
  - Mother figures panel
  - Planet placements table
  - House-by-house interpretation
  - AI reading button hook

IMPORTANT: Streamlit is imported only inside function bodies,
per CONTRIBUTING.md convention.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Optional

from .constants import (
    DOT_DOUBLE,
    DOT_SINGLE,
    GEOMANCY_THEME,
    QUESTION_TYPES,
    ZODIAC_SIGNS,
)
from .models import GeomancyChart, GeomancyFigure, HouseInfo


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

_CSS = """
<style>
.geo-header {
    background: linear-gradient(135deg,#050a14 0%,#0d1a35 50%,#050a14 100%);
    border:1px solid #C8A24A;
    border-radius:10px;
    padding:20px 28px;
    margin-bottom:16px;
    box-shadow:0 0 30px rgba(200,162,74,0.18);
}
.geo-header h2 { color:#EDD88A; margin:0; font-size:1.4rem; }
.geo-header p  { color:#B0B8C8; margin:4px 0 0; font-size:0.9rem; }

.geo-figure-card {
    background:#111827;
    border:1px solid #2A3A50;
    border-radius:8px;
    padding:14px;
    text-align:center;
}
.geo-figure-card .fig-name { color:#EDD88A; font-size:1rem; font-weight:600; }
.geo-figure-card .fig-zh   { color:#B0B8C8; font-size:0.85rem; }
.geo-figure-card .fig-dots { font-size:1.4rem; letter-spacing:4px; color:#C8A24A; font-family:monospace; }
.geo-figure-card .fig-sign { color:#7BAFD4; font-size:0.85rem; margin-top:4px; }
.geo-figure-card .fig-qual-fortunate   { color:#4CAF50; font-weight:600; }
.geo-figure-card .fig-qual-unfortunate { color:#EF5350; font-weight:600; }
.geo-figure-card .fig-qual-neutral     { color:#9E9E9E; font-weight:600; }

.geo-planet-row {
    display:flex; align-items:center; gap:10px;
    background:#111827; border:1px solid #1E2845;
    border-radius:6px; padding:8px 14px; margin:4px 0;
}
.geo-planet-glyph { font-size:1.3rem; width:30px; text-align:center; }
.geo-planet-name  { color:#EDD88A; font-size:0.95rem; min-width:80px; }
.geo-planet-house { color:#7BAFD4; font-size:0.9rem; }
.geo-planet-sign  { color:#B0B8C8; font-size:0.85rem; }

.geo-house-card {
    background:#111827;
    border:1px solid #1E2845;
    border-left:4px solid #C8A24A;
    border-radius:6px;
    padding:12px 16px;
    margin:6px 0;
}
.geo-house-title { color:#EDD88A; font-size:1rem; font-weight:600; }
.geo-house-sign  { color:#7BAFD4; font-size:0.9rem; }
.geo-house-topics{ color:#B0B8C8; font-size:0.85rem; margin-top:4px; }
.geo-house-gerard{ color:#A0907A; font-size:0.82rem; font-style:italic; margin-top:4px; }
.geo-house-planets{ color:#C8A24A; font-size:0.88rem; margin-top:4px; }
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# SVG wheel builder / 星盤輪圖
# ─────────────────────────────────────────────────────────────────────────────

def build_geomancy_wheel_svg(chart: GeomancyChart) -> str:
    """
    Build a 12-house geomantic wheel SVG showing:
    - Outer zodiac ring with sign glyphs
    - 12 house divisions with house numbers
    - Planet glyphs placed in their houses
    - Ascendant marker
    """
    cx, cy, r_outer, r_inner, r_label = 280, 280, 240, 160, 200
    r_planet = 125
    svg_parts = [
        f'<svg viewBox="0 0 560 560" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#0B0F1E;border-radius:50%;max-width:500px">',
        # Outer background circle
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#0D1529" stroke="#C8A24A" stroke-width="2"/>',
        # Inner circle
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#080D18" stroke="#2A3A50" stroke-width="1.5"/>',
        # Inner hub
        f'<circle cx="{cx}" cy="{cy}" r="55" fill="#0B0F1E" stroke="#C8A24A" stroke-width="1.5"/>',
        # Hub text
        f'<text x="{cx}" y="{cy-8}" text-anchor="middle" fill="#EDD88A" '
        f'font-size="11" font-family="serif">天文幾何</text>',
        f'<text x="{cx}" y="{cy+10}" text-anchor="middle" fill="#C8A24A" '
        f'font-size="9" font-family="serif">Geomantia</text>',
        f'<text x="{cx}" y="{cy+26}" text-anchor="middle" fill="#C8A24A" '
        f'font-size="9" font-family="serif">Astronomica</text>',
    ]

    # 12 house dividers and labels
    for i in range(12):
        # House divisions from ASC (left, 180° in SVG where 0°=right)
        # Traditional wheel: ASC at left (180°), houses go counter-clockwise
        angle_deg = 180.0 - i * 30.0  # house i starts at this angle
        angle_rad = math.radians(angle_deg)

        # Dividing line
        x1 = cx + r_inner * math.cos(angle_rad)
        y1 = cy - r_inner * math.sin(angle_rad)
        x2 = cx + r_outer * math.cos(angle_rad)
        y2 = cy - r_outer * math.sin(angle_rad)
        line_color = "#C8A24A" if i == 0 else "#2A3A50"
        line_width = "2.5" if i == 0 else "1"
        svg_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{line_color}" stroke-width="{line_width}"/>'
        )

        # House number label (mid-house angle)
        mid_angle_rad = math.radians(angle_deg - 15.0)
        lx = cx + r_planet * math.cos(mid_angle_rad)
        ly = cy - r_planet * math.sin(mid_angle_rad)
        house_num = i + 1
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="#7BAFD4" font-size="13" '
            f'font-family="serif" font-weight="bold">{house_num}</text>'
        )

        # Sign glyph in outer ring
        house_info = chart.houses[i]
        glyph = house_info.glyph
        sign_mid_rad = math.radians(angle_deg - 15.0)
        sx = cx + r_label * math.cos(sign_mid_rad)
        sy = cy - r_label * math.sin(sign_mid_rad)
        element_colors = {"Fire": "#FF6B6B", "Earth": "#8BC34A",
                          "Air": "#64B5F6", "Water": "#4DD0E1"}
        sign_color = element_colors.get(house_info.element, "#EDD88A")
        svg_parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{sign_color}" font-size="18">'
            f'{glyph}</text>'
        )

        # Planet glyphs in house
        if house_info.planets:
            # Place up to 3 planets, slightly offset
            pcount = len(house_info.planets)
            for pi, planet in enumerate(house_info.planets[:3]):
                offset = (pi - (pcount - 1) / 2.0) * 0.12  # radians offset
                p_angle = mid_angle_rad + offset
                pr = 90 - pi * 6  # vary radius slightly
                px = cx + pr * math.cos(p_angle)
                py = cy - pr * math.sin(p_angle)
                svg_parts.append(
                    f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
                    f'dominant-baseline="middle" fill="#C8A24A" font-size="14">'
                    f'{planet.glyph}</text>'
                )

    # ASC marker
    asc_angle = math.radians(180.0)
    ax = cx + (r_outer + 12) * math.cos(asc_angle)
    ay = cy - (r_outer + 12) * math.sin(asc_angle)
    svg_parts.append(
        f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" fill="#C8A24A" font-size="12" '
        f'font-weight="bold" font-family="serif">ASC</text>'
    )
    # ASC sign
    asc_sign_zh = chart.ascendant_sign_zh
    svg_parts.append(
        f'<text x="{cx}" y="{cy+52}" text-anchor="middle" '
        f'fill="#EDD88A" font-size="10" font-family="serif">'
        f'{chart.ascendant_sign_zh} {chart.houses[0].glyph}</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ─────────────────────────────────────────────────────────────────────────────
# Figure dot SVG
# ─────────────────────────────────────────────────────────────────────────────

def _figure_dots_svg(figure: GeomancyFigure, size: int = 80) -> str:
    """Render a geomantic figure as a small SVG dot pattern."""
    gold = GEOMANCY_THEME["gold"]
    bg = GEOMANCY_THEME["card"]
    row_h = size // 5
    svg = [
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{size}" height="{size}" rx="6" fill="{bg}"/>',
    ]
    for row_idx, single in enumerate(figure.dots):
        y = row_h * (row_idx + 1) - row_h // 4
        if single:
            # One dot, centred
            svg.append(
                f'<circle cx="{size//2}" cy="{y}" r="5" fill="{gold}"/>'
            )
        else:
            # Two dots
            svg.append(
                f'<circle cx="{size//2 - 10}" cy="{y}" r="5" fill="{gold}"/>'
            )
            svg.append(
                f'<circle cx="{size//2 + 10}" cy="{y}" r="5" fill="{gold}"/>'
            )
    svg.append("</svg>")
    return "".join(svg)


# ─────────────────────────────────────────────────────────────────────────────
# Input panel / 輸入面板
# ─────────────────────────────────────────────────────────────────────────────

def render_input_panel() -> Optional[dict]:
    """
    Render the input panel for the geomancy reading.
    Returns dict with user inputs, or None if not submitted yet.
    """
    import streamlit as st
    from astro.i18n import t, auto_cn

    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="geo-header">'
        f'<h2>🔮 {auto_cn("天文幾何占卜", "Astronomical Geomancy")}</h2>'
        f'<p>{auto_cn("Gerardus Cremonensis 地占占星系統（12世紀）", "Gerardus Cremonensis Geomantic Astrology System (12th c.)")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.form("geo_input_form"):
        question = st.text_area(
            auto_cn("你的問題", "Your Question"),
            placeholder=auto_cn(
                "請輸入你想問的問題，例如：我今年的財運如何？",
                "Enter your question, e.g.: What is my financial fortune this year?",
            ),
            height=90,
        )

        qt_labels = [f"{q['zh']}  /  {q['en']}" for q in QUESTION_TYPES]
        qt_keys = [q["key"] for q in QUESTION_TYPES]
        qt_idx = st.selectbox(
            auto_cn("問題類型", "Question Type"),
            options=range(len(qt_labels)),
            format_func=lambda i: qt_labels[i],
        )
        question_type = qt_keys[qt_idx]

        seed_mode = st.radio(
            auto_cn("起卦模式", "Casting Mode"),
            options=["random", "time_seed"],
            format_func=lambda v: {
                "random": auto_cn("🎲 純隨機（傳統方式）", "🎲 Pure Random (Traditional)"),
                "time_seed": auto_cn("🕐 時間種子（現代增強）", "🕐 Time Seed (Modern Enhanced)"),
            }[v],
            horizontal=True,
        )

        submitted = st.form_submit_button(
            auto_cn("🔮 起卦占卜", "🔮 Cast the Chart"),
            use_container_width=True,
        )

    if submitted:
        return {
            "question": question.strip() or auto_cn("未提供問題", "No question provided"),
            "question_type": question_type,
            "seed_mode": seed_mode,
        }
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Mother figures panel / 母親圖形展示
# ─────────────────────────────────────────────────────────────────────────────

def _render_mother_figures(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    st.markdown(
        f'<h3 style="color:#EDD88A">🌿 {auto_cn("母親圖形 / 上升圖形", "Mother Figures / Ascendant Figure")}</h3>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    qual_class = {"fortunate": "fig-qual-fortunate",
                  "unfortunate": "fig-qual-unfortunate",
                  "neutral": "fig-qual-neutral"}
    qual_label = {
        "fortunate": auto_cn("吉", "Fortunate"),
        "unfortunate": auto_cn("凶", "Unfortunate"),
        "neutral": auto_cn("中", "Neutral"),
    }
    for i, fig in enumerate(chart.mother_figures):
        with cols[i]:
            is_asc = (i == 0)
            label = auto_cn(f"母親 {i+1}", f"Mother {i+1}")
            if is_asc:
                label = auto_cn(f"母親 1 ★ 上升", "Mother 1 ★ ASC")
            dots_svg = _figure_dots_svg(fig, size=72)
            qc = qual_class.get(fig.quality, "fig-qual-neutral")
            ql = qual_label.get(fig.quality, "")
            border = "border:2px solid #C8A24A;" if is_asc else ""
            st.markdown(
                f'<div class="geo-figure-card" style="{border}">'
                f'<div style="font-size:0.75rem;color:#7BAFD4">{label}</div>'
                f'{dots_svg}'
                f'<div class="fig-name">{fig.name_en}</div>'
                f'<div class="fig-zh">{fig.name_zh}</div>'
                f'<div class="fig-sign">{fig.sign_zh} {ZODIAC_SIGNS[fig.sign_num]["glyph"]}</div>'
                f'<div class="{qc}">{ql}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Planet placements table / 行星落宮
# ─────────────────────────────────────────────────────────────────────────────

def _render_planet_table(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    st.markdown(
        f'<h3 style="color:#EDD88A">🪐 {auto_cn("行星落宮", "Planet House Placements")}</h3>',
        unsafe_allow_html=True,
    )
    rows_html = []
    for p in chart.planet_placements:
        house_info = chart.houses[p.house - 1]
        house_name = auto_cn(house_info.name_zh, house_info.name_en)
        rows_html.append(
            f'<div class="geo-planet-row">'
            f'<span class="geo-planet-glyph">{p.glyph}</span>'
            f'<span class="geo-planet-name">{p.planet_zh} / {p.planet_en}</span>'
            f'<span class="geo-planet-house">第{p.house}宮 &nbsp;{house_name}</span>'
            f'<span class="geo-planet-sign">{p.sign_zh} {ZODIAC_SIGNS[p.sign_num]["glyph"]}</span>'
            f'</div>'
        )
    st.markdown("\n".join(rows_html), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# House detail panel / 宮位詳解
# ─────────────────────────────────────────────────────────────────────────────

def _render_house_details(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    primary = chart.primary_house
    st.markdown(
        f'<h3 style="color:#EDD88A">🏛️ {auto_cn("十二宮詳解", "12 House Details")}</h3>'
        f'<p style="color:#B0B8C8;font-size:0.88rem">'
        f'{auto_cn(f"主要考察宮位：第{primary}宮（{chart.question_type_zh}）", f"Primary house: {primary} ({chart.question_type})")}'
        f'</p>',
        unsafe_allow_html=True,
    )

    for h in chart.houses:
        border_color = "#C8A24A" if h.house == primary else "#2A3A50"
        planet_names = "、".join(
            f"{p.glyph}{p.planet_zh}" for p in h.planets
        ) if h.planets else auto_cn("（空宮）", "(empty)")

        topics = auto_cn(h.topics_zh, h.topics_en)
        name = auto_cn(h.name_zh, h.name_en)
        st.markdown(
            f'<div class="geo-house-card" style="border-left-color:{border_color}">'
            f'<div class="geo-house-title">🏠 第{h.house}宮 — {name}</div>'
            f'<div class="geo-house-sign">{h.sign_zh} {h.glyph} ({h.sign}) · {h.element} · {h.quality}</div>'
            f'<div class="geo-house-topics">{topics}</div>'
            f'<div class="geo-house-gerard">{h.gerard_zh}</div>'
            f'<div class="geo-house-planets">🪐 {planet_names}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Primary house interpretation / 主要宮位解讀
# ─────────────────────────────────────────────────────────────────────────────

def _render_primary_interpretation(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    ph = chart.primary_house
    house_info = chart.houses[ph - 1]
    asc_fig = chart.ascendant_figure

    st.markdown(
        f'<h3 style="color:#EDD88A">📖 {auto_cn("核心解讀", "Core Interpretation")}</h3>',
        unsafe_allow_html=True,
    )

    # Ascendant figure interpretation
    quality_map = {
        "fortunate": auto_cn("吉象", "Fortunate Omen"),
        "unfortunate": auto_cn("凶象", "Unfortunate Omen"),
        "neutral": auto_cn("中性", "Neutral"),
    }
    q_label = quality_map.get(asc_fig.quality, "")
    st.markdown(
        f"""
**{auto_cn("上升圖形", "Ascendant Figure")}**: {asc_fig.name_en} / {asc_fig.name_zh}
- {auto_cn("星座：", "Sign: ")}{asc_fig.sign_zh} ({asc_fig.sign})
- {auto_cn("元素：", "Element: ")}{asc_fig.element_zh} ({asc_fig.element})
- {auto_cn("行星：", "Planet: ")}{asc_fig.planet_zh} ({asc_fig.planet})
- {auto_cn("吉凶：", "Quality: ")}{q_label}
- {auto_cn("關鍵詞：", "Keywords: ")}{asc_fig.keywords_zh}
"""
    )

    # Primary house details
    planet_in_primary = [
        p for p in chart.planet_placements if p.house == ph
    ]
    st.markdown(
        f"""
**{auto_cn(f"第{ph}宮（{house_info.name_zh}）", f"House {ph} ({house_info.name_en})")}**

- {auto_cn("星座：", "Sign: ")}{house_info.sign_zh} ({house_info.sign})
- {auto_cn("主題：", "Topics: ")}{auto_cn(house_info.topics_zh, house_info.topics_en)}
- {auto_cn("Gerard解說：", "Gerard's gloss: ")}{house_info.gerard_zh}
- {auto_cn("落宮行星：", "Planets in house: ")}{
    "、".join(f"{p.glyph}{p.planet_zh}" for p in planet_in_primary)
    if planet_in_primary else auto_cn("（空宮）", "(empty)")
}
"""
    )

    # Gerard general rules
    with st.expander(auto_cn("📜 Gerard Cremonensis 傳統判斷規則", "📜 Gerard Cremonensis Traditional Rules")):
        st.markdown(
            f"""
{auto_cn("""
**壽命判斷**：觀第1宮上升星座與上升圖形的吉凶，搭配第8宮（死亡宮）行星情況。
若上升為吉象（Fortuna Major / Laetitia / Acquisitio），命宮穩固，壽元充足；
若上升為凶象（Tristitia / Cauda Draconis / Rubeus），需特別留意健康與生命力。

**財富判斷**：第2宮星座與落宮行星決定財富豐寡。
木星（♃）在第2宮為大吉；土星（♄）在第2宮阻礙財運；金星（♀）帶來穩定收入。

**婚姻判斷**：第7宮主婚姻，觀上升（第1宮）與第7宮的行星關係。
若為友星（如木星↔金星），則婚姻和諧；若為敵星（如火星↔金星），則婚姻多波折。

**子女判斷**：第5宮主子女，木星在第5宮為多子多福；土星在第5宮則子嗣艱難。

**事業判斷**：第10宮主事業名譽，太陽（☉）在此宮位大吉，土星（♄）則阻礙晉升。

**旅行判斷**：第9宮主長途旅行，第3宮主短途。
月亮（☽）在旅行宮表示旅途順利；火星（♂）則有危險。
""", """
**Lifespan**: Observe House 1 sign and figure quality, combined with House 8 (Death).
Fortunate figures (Fortuna Major / Laetitia / Acquisitio) = strong vitality;
Unfortunate figures (Tristitia / Cauda Draconis / Rubeus) = health concerns.

**Wealth**: House 2 sign and planets determine financial fortune.
Jupiter (♃) in House 2 = great gain; Saturn (♄) = restriction; Venus (♀) = steady income.

**Marriage**: House 7 governs marriage. Check planet relationships between Houses 1 and 7.
Friendly planets = harmonious union; Hostile planets = turbulent relationship.

**Children**: House 5 governs offspring. Jupiter in House 5 = abundant children; Saturn = difficulty.

**Career**: House 10 governs career. Sun (☉) there is very fortunate; Saturn obstructs promotion.

**Travel**: House 9 = long journeys, House 3 = short journeys.
Moon (☽) = smooth travels; Mars (♂) = danger.
""")}
"""
        )


# ─────────────────────────────────────────────────────────────────────────────
# Main render entry point / 主渲染入口
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    chart: GeomancyChart,
    after_chart_hook: Optional[Callable] = None,
) -> None:
    """
    Render the full Astronomical Geomancy reading UI.

    Args:
        chart:            Computed GeomancyChart instance.
        after_chart_hook: Optional callback rendered after the wheel
                          (used for the AI reading button).
    """
    import streamlit as st
    from astro.i18n import auto_cn, t

    st.markdown(_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        f'<div class="geo-header">'
        f'<h2>🔮 {auto_cn("天文幾何占卜", "Astronomical Geomancy")} — '
        f'Gerardus Cremonensis</h2>'
        f'<p>{auto_cn(f"問題：{chart.question} ｜ {chart.timestamp}", f"Question: {chart.question} | {chart.timestamp}")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Tabs
    tab_labels = [
        auto_cn("🌐 星盤輪圖", "🌐 Wheel Chart"),
        auto_cn("🌿 母親圖形", "🌿 Mother Figures"),
        auto_cn("🪐 行星落宮", "🪐 Planet Placements"),
        auto_cn("🏛️ 宮位詳解", "🏛️ House Details"),
        auto_cn("📖 解讀", "📖 Reading"),
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        wheel_svg = build_geomancy_wheel_svg(chart)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(wheel_svg, unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"**{auto_cn('上升圖形', 'Ascendant Figure')}**: "
                f"{chart.ascendant_figure.name_en} / {chart.ascendant_figure.name_zh}"
            )
            st.markdown(
                f"**{auto_cn('上升星座', 'Ascendant Sign')}**: "
                f"{chart.ascendant_sign_zh} {chart.houses[0].glyph} ({chart.ascendant_sign})"
            )
            st.markdown(f"**{auto_cn('問題類型', 'Question Type')}**: {chart.question_type_zh}")
            st.markdown(
                f"**{auto_cn('主要考察宮位', 'Primary House')}**: "
                f"{auto_cn(f'第{chart.primary_house}宮', f'House {chart.primary_house}')}"
            )
            # House-sign quick reference
            st.markdown(f"**{auto_cn('十二宮星座一覽', 'House-Sign Overview')}**")
            for h in chart.houses:
                planet_txt = "  " + " ".join(p.glyph for p in h.planets) if h.planets else ""
                st.markdown(
                    f"- {auto_cn(f'第{h.house}宮', f'H{h.house}')} "
                    f"{h.sign_zh} {h.glyph}{planet_txt}"
                )

        if after_chart_hook:
            after_chart_hook()

    with tabs[1]:
        _render_mother_figures(chart)

    with tabs[2]:
        _render_planet_table(chart)

    with tabs[3]:
        _render_house_details(chart)

    with tabs[4]:
        _render_primary_interpretation(chart)
