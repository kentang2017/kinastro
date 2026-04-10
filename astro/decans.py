"""
Decanic Astrology 計算與渲染模組 (Decanic Astrology Computation & Rendering Module)

基於古埃及三十六十度區間 (36 Decans) 系統，結合迦勒底行星序 (Chaldean Order)、
三分主星 (Triplicity Rulers)、金色黎明塔羅對應 (Golden Dawn Tarot Correspondences)
以及本質尊貴 (Essential Dignities) 技法，提供出生圖 Decan 分析。

Sources: Neugebauer & Parker "Egyptian Astronomical Texts",
         Dendera zodiac ceiling, Ptolemy "Tetrabiblos",
         Golden Dawn tradition.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

import swisseph as swe
import streamlit as st
import plotly.graph_objects as go

from astro.decans_data import (
    DECANS_DATA,
    ZODIAC_SIGNS_DECAN,
    CHALDEAN_ORDER,
    CHALDEAN_ORDER_CN,
    CHALDEAN_ORDER_GLYPHS,
    ESSENTIAL_DIGNITIES,
    FACE_DIGNITY_SCORE,
    get_decan_by_longitude,
    get_decan_by_sign_and_degree,
)
from astro.egyptian_calendar import (
    gregorian_to_egyptian,
    get_night_hours,
    build_diagonal_star_table,
    get_heliacal_rising_approx,
    get_visibility_cycle,
    get_sothic_info,
    MODERN_STAR_IDS,
    build_transit_star_table,
    SOTHIC_CYCLE_YEARS,
    SIRIUS_HELIACAL_RISING_LATITUDE_30N,
)

# ============================================================
# 常量 (Constants)
# ============================================================

# 古典七星 + 現代三星 (Classical 7 + modern outer planets)
DECAN_PLANETS = {
    "Sun ☉": swe.SUN,
    "Moon ☽": swe.MOON,
    "Mercury ☿": swe.MERCURY,
    "Venus ♀": swe.VENUS,
    "Mars ♂": swe.MARS,
    "Jupiter ♃": swe.JUPITER,
    "Saturn ♄": swe.SATURN,
    "Uranus ♅": swe.URANUS,
    "Neptune ♆": swe.NEPTUNE,
    "Pluto ♇": swe.PLUTO,
}

# 行星英文短名映射 (planet display name -> bare English name for dignity lookups)
_PLANET_SHORT = {
    "Sun ☉": "Sun",
    "Moon ☽": "Moon",
    "Mercury ☿": "Mercury",
    "Venus ♀": "Venus",
    "Mars ♂": "Mars",
    "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn",
    "Uranus ♅": "Uranus",
    "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
}

# 埃及主題色彩 (Egyptian-themed colour palette)
EGYPTIAN_GOLD = "#C5A03F"
EGYPTIAN_BLUE = "#1B2A4A"
EGYPTIAN_TURQUOISE = "#40E0D0"
EGYPTIAN_PAPYRUS = "#F5E6C8"

# 元素對應花色 (Element -> Tarot suit)
ELEMENT_SUIT = {
    "Fire": ("Wands", "權杖"),
    "Water": ("Cups", "聖杯"),
    "Air": ("Swords", "寶劍"),
    "Earth": ("Pentacles", "錢幣"),
}

# ============================================================
# 資料類 (Data Classes)
# ============================================================


@dataclass
class DecanPlanetInfo:
    """A planet's decan placement (行星 Decan 位置)"""
    planet_name: str       # e.g. "Sun ☉"
    longitude: float
    sign_en: str
    sign_cn: str
    sign_glyph: str
    degree_in_sign: float
    decan_number: int
    decan_data: dict       # reference to the DECANS_DATA entry
    chaldean_ruler: str
    triplicity_ruler: str
    face_dignity: bool     # True if planet rules this Face
    retrograde: bool


@dataclass
class DecanChart:
    """Complete Decan chart (完整 Decan 排盤)"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    planets: list          # list of DecanPlanetInfo
    ascendant_decan: dict  # DECANS_DATA entry for ASC
    asc_longitude: float
    today_sun_decan: dict  # today's Sun decan
    today_sun_longitude: float
    essential_dignities_summary: list = field(default_factory=list)


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_normalize(deg) / 30.0)


def _degree_in_sign(deg: float) -> float:
    return _normalize(deg) % 30.0


def _format_deg(deg: float) -> str:
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _check_face_dignity(planet_name: str, decan_data: dict) -> bool:
    """行星是否位於自己的 Face (Chaldean ruler == planet)"""
    short = _PLANET_SHORT.get(planet_name, planet_name.split(" ")[0])
    return decan_data["chaldean_ruler_en"] == short


def _build_dignity_row(planet_name: str, sign_idx: int, decan_data: dict) -> dict:
    """為一顆行星建立本質尊貴摘要行"""
    short = _PLANET_SHORT.get(planet_name, planet_name.split(" ")[0])
    dig = ESSENTIAL_DIGNITIES.get(sign_idx, {})

    domicile = (dig.get("domicile") == short)
    exaltation = (dig.get("exaltation") == short)
    detriment = (dig.get("detriment") == short)
    fall = (dig.get("fall") == short)
    triplicity_day = (dig.get("triplicity_day") == short)
    triplicity_night = (dig.get("triplicity_night") == short)
    face = (decan_data["chaldean_ruler_en"] == short)

    score = 0
    if domicile:
        score += 5
    if exaltation:
        score += 4
    if triplicity_day or triplicity_night:
        score += 3
    if face:
        score += FACE_DIGNITY_SCORE
    if detriment:
        score -= 5
    if fall:
        score -= 4

    return {
        "planet": planet_name,
        "domicile": domicile,
        "exaltation": exaltation,
        "detriment": detriment,
        "fall": fall,
        "triplicity_day": triplicity_day,
        "triplicity_night": triplicity_night,
        "face": face,
        "score": score,
    }


# ============================================================
# 計算函數 (Computation Function)
# ============================================================

def compute_decan_chart(year, month, day, hour, minute, timezone,
                        latitude, longitude, location_name="", **kwargs):
    """計算 Decan 排盤

    Args:
        year, month, day, hour, minute: 出生日期時間
        timezone: UTC 時差 (e.g. +8 for CST)
        latitude, longitude: 出生地座標
        location_name: 地點名稱
        **kwargs: 保留給未來擴展
    Returns:
        DecanChart 資料類實例
    """
    swe.set_ephe_path("")

    # Julian day
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Ascendant
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc = _normalize(ascmc[0])
    asc_decan = get_decan_by_longitude(asc)

    # 行星計算
    planets: list[DecanPlanetInfo] = []
    for name, planet_id in DECAN_PLANETS.items():
        pos, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(pos[0])
        speed = pos[3]
        sidx = _sign_index(lon)
        deg_in = _degree_in_sign(lon)
        decan = get_decan_by_longitude(lon)
        sign_info = ZODIAC_SIGNS_DECAN[sidx]

        planets.append(DecanPlanetInfo(
            planet_name=name,
            longitude=lon,
            sign_en=sign_info[0],
            sign_cn=sign_info[1],
            sign_glyph=sign_info[2],
            degree_in_sign=deg_in,
            decan_number=decan["decan_number"],
            decan_data=decan,
            chaldean_ruler=decan["chaldean_ruler_en"],
            triplicity_ruler=decan["triplicity_ruler_en"],
            face_dignity=_check_face_dignity(name, decan),
            retrograde=(speed < 0),
        ))

    # 今日太陽 Decan
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    sun_now, _ = swe.calc_ut(now_jd, swe.SUN)
    today_sun_lon = _normalize(sun_now[0])
    today_sun_decan = get_decan_by_longitude(today_sun_lon)

    # 本質尊貴摘要
    dignities: list[dict] = []
    for p in planets:
        sidx = _sign_index(p.longitude)
        dignities.append(_build_dignity_row(p.planet_name, sidx, p.decan_data))

    return DecanChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        location_name=location_name,
        planets=planets,
        ascendant_decan=asc_decan,
        asc_longitude=asc,
        today_sun_decan=today_sun_decan,
        today_sun_longitude=today_sun_lon,
        essential_dignities_summary=dignities,
    )


# ============================================================
# 渲染：CSS 樣式 (Rendering: CSS Styles)
# ============================================================

_EGYPTIAN_CSS = f"""
<style>
.decan-card {{
    background: linear-gradient(135deg, {EGYPTIAN_BLUE} 0%, #2a3d5a 100%);
    border: 1px solid {EGYPTIAN_GOLD};
    border-radius: 8px;
    padding: 12px;
    margin: 4px 0;
    color: {EGYPTIAN_PAPYRUS};
}}
.decan-card h4 {{
    color: {EGYPTIAN_GOLD};
    margin: 0 0 6px 0;
}}
.decan-card .meta {{
    font-size: 0.85em;
    opacity: 0.9;
}}
.decan-highlight {{
    border: 2px solid {EGYPTIAN_TURQUOISE};
    box-shadow: 0 0 8px {EGYPTIAN_TURQUOISE}44;
}}
.decan-today {{
    background: linear-gradient(135deg, #2a3d1a 0%, #1a2a0a 100%);
    border: 2px solid {EGYPTIAN_GOLD};
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    color: {EGYPTIAN_PAPYRUS};
}}
.decan-today h3 {{
    color: {EGYPTIAN_GOLD};
    margin: 0 0 8px 0;
}}
.color-swatch {{
    display: inline-block;
    width: 16px; height: 16px;
    border-radius: 3px;
    border: 1px solid #888;
    vertical-align: middle;
    margin-right: 4px;
}}
</style>
"""


# ============================================================
# 渲染：Plotly 輪圖 (Rendering: Plotly Wheel Chart)
# ============================================================

def _render_decan_wheel(highlight_index: int | None = None):
    """繪製三十六 Decan 甜甜圈輪圖"""
    labels = []
    colors = []
    hover_texts = []
    pulls = []
    for d in DECANS_DATA:
        lbl = f"{d['sign_glyph']} {d['decan_number']}"
        labels.append(lbl)
        colors.append(d["color"])
        hover_texts.append(
            f"{d['sign_en']} ({d['sign_cn']}) Decan {d['decan_number']}<br>"
            f"{d['degree_start']}°–{d['degree_end']}°<br>"
            f"Egyptian: {d['egyptian_hieroglyphic']} {d['egyptian_name']}"
            f" ({d['egyptian_transliteration']})<br>"
            f"Deity: {d['egyptian_deity']}<br>"
            f"Chaldean Ruler: {d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"
        )
        pulls.append(0.06 if d["index"] == highlight_index else 0)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=[1] * 36,
        hole=0.45,
        marker=dict(colors=colors, line=dict(color=EGYPTIAN_GOLD, width=1)),
        textinfo="label",
        textfont=dict(size=10, color=EGYPTIAN_PAPYRUS),
        hovertext=hover_texts,
        hoverinfo="text",
        pull=pulls,
        direction="clockwise",
        sort=False,
    )])
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=480,
        title=dict(
            text="𓂀 Dendera Decan Wheel — 丹德拉十度區間輪",
            font=dict(color=EGYPTIAN_GOLD, size=14),
        ),
        annotations=[dict(
            text="36<br>Decans",
            x=0.5, y=0.5,
            font=dict(size=16, color=EGYPTIAN_GOLD),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 渲染：今日 Decan 卡片 (Today's Decan Card)
# ============================================================

def _render_today_card(sun_lon: float, decan: dict, lang: str = "cn"):
    """顯示今日太陽 Decan 卡片"""
    deg_str = f"{sun_lon:.2f}°"
    if lang == "cn":
        sign = decan["sign_cn"]
        ruler = f"{decan['chaldean_ruler_cn']} {decan['chaldean_ruler_glyph']}"
        trip = decan["triplicity_ruler_cn"]
        personality = decan["personality_cn"]
    else:
        sign = decan["sign_en"]
        ruler = f"{decan['chaldean_ruler_en']} {decan['chaldean_ruler_glyph']}"
        trip = decan["triplicity_ruler_en"]
        personality = decan["personality_en"]

    html = f"""
    <div class="decan-today">
        <h3>☀️ {"今日 Decan" if lang == "cn" else "Today's Decan"}
            — {decan['sign_glyph']} {sign} Decan {decan['decan_number']}</h3>
        <p><b>{"太陽經度" if lang == "cn" else "Sun Longitude"}:</b> {deg_str} &nbsp;
           <b>{"度數範圍" if lang == "cn" else "Degree Range"}:</b>
           {decan['degree_start']}°–{decan['degree_end']}°</p>
        <p><b>{"迦勒底主星" if lang == "cn" else "Chaldean Ruler"}:</b> {ruler} &nbsp;
           <b>{"三分主星" if lang == "cn" else "Triplicity Ruler"}:</b> {trip}</p>
        <p><b>{"埃及名稱" if lang == "cn" else "Egyptian Name"}:</b>
           <span style="font-size:1.3em;">{decan['egyptian_hieroglyphic']}</span>
           {decan['egyptian_name']} ({decan['egyptian_transliteration']})
           &nbsp; <b>{"守護神" if lang == "cn" else "Deity"}:</b> {decan['egyptian_deity']}</p>
        <p><b>{"塔羅" if lang == "cn" else "Tarot"}:</b>
           {decan['tarot_card_cn'] if lang == "cn" else decan['tarot_card_en']}</p>
        <p style="font-style:italic; opacity:0.9;">{personality}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 渲染：Decan 網格 (Decan Grid)
# ============================================================

def _render_decan_grid(lang: str = "cn", highlight_index: int | None = None):
    """以 3 欄網格顯示全部 36 Decans"""
    cols_per_row = 3
    for i in range(0, 36, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= 36:
                break
            d = DECANS_DATA[idx]
            hl_class = " decan-highlight" if d["index"] == highlight_index else ""
            if lang == "cn":
                sign = d["sign_cn"]
                ruler = f"{d['chaldean_ruler_cn']} {d['chaldean_ruler_glyph']}"
                trip = d["triplicity_ruler_cn"]
                tarot = d["tarot_card_cn"]
            else:
                sign = d["sign_en"]
                ruler = f"{d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"
                trip = d["triplicity_ruler_en"]
                tarot = d["tarot_card_en"]

            card_html = f"""
            <div class="decan-card{hl_class}">
                <h4>{d['sign_glyph']} {sign} — Decan {d['decan_number']}</h4>
                <div class="meta">
                    {d['degree_start']}°–{d['degree_end']}° &nbsp;
                    <span class="color-swatch" style="background:{d['color']};"></span>
                    {d['color']}<br/>
                    <b>{"迦勒底" if lang == "cn" else "Chaldean"}:</b> {ruler}<br/>
                    <b>{"三分" if lang == "cn" else "Triplicity"}:</b> {trip}<br/>
                    <b>{"埃及" if lang == "cn" else "Egyptian"}:</b>
                    <span style="font-size:1.2em;">{d['egyptian_hieroglyphic']}</span>
                    {d['egyptian_name']} ({d['egyptian_transliteration']})
                    · {d['egyptian_deity']}<br/>
                    <b>{"礦石" if lang == "cn" else "Mineral"}:</b> {d['mineral']}
                    &nbsp; <b>{"植物" if lang == "cn" else "Plant"}:</b> {d['plant']}<br/>
                    <b>{"塔羅" if lang == "cn" else "Tarot"}:</b> {tarot}
                </div>
            </div>
            """
            with col:
                st.markdown(card_html, unsafe_allow_html=True)
                hist_label = (
                    f"📜 {d['sign_glyph']} {sign} D{d['decan_number']} "
                    f"{'歷史' if lang == 'cn' else 'History'}"
                )
                with st.expander(hist_label):
                    if lang == "cn":
                        st.write(d["history_cn"])
                        st.write(f"**性格：** {d['personality_cn']}")
                        st.write(f"**優勢：** {d['strengths_cn']}")
                        st.write(f"**挑戰：** {d['challenges_cn']}")
                    else:
                        st.write(d["history_en"])
                        st.write(f"**Personality:** {d['personality_en']}")
                        st.write(f"**Strengths:** {d['strengths_en']}")
                        st.write(f"**Challenges:** {d['challenges_en']}")


# ============================================================
# 渲染：行星 Decan 表格 (Planet Decan Table)
# ============================================================

def _render_planet_table(chart: DecanChart, ruler_system: str, lang: str = "cn"):
    """渲染行星 Decan 位置表"""
    if lang == "cn":
        st.subheader("🪐 行星 Decan 位置")
        hdr = (
            "| 行星 | 經度 | 星座 | Decan | "
            f"{'迦勒底主星' if ruler_system == 'Chaldean' else '三分主星'} | "
            "Face 尊貴 | 塔羅牌 |"
        )
    else:
        st.subheader("🪐 Planet Decan Positions")
        hdr = (
            "| Planet | Longitude | Sign | Decan | "
            f"{'Chaldean Ruler' if ruler_system == 'Chaldean' else 'Triplicity Ruler'} | "
            "Face Dignity | Tarot Card |"
        )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [hdr, sep]

    for p in chart.planets:
        retro = " ℞" if p.retrograde else ""
        face_str = f"✦ +{FACE_DIGNITY_SCORE}" if p.face_dignity else "—"
        if ruler_system == "Chaldean":
            ruler = (p.decan_data["chaldean_ruler_cn"] if lang == "cn"
                     else p.decan_data["chaldean_ruler_en"])
            ruler += f" {p.decan_data['chaldean_ruler_glyph']}"
        else:
            ruler = (p.decan_data["triplicity_ruler_cn"] if lang == "cn"
                     else p.decan_data["triplicity_ruler_en"])

        sign = p.sign_cn if lang == "cn" else p.sign_en
        tarot = (p.decan_data["tarot_card_cn"] if lang == "cn"
                 else p.decan_data["tarot_card_en"])

        rows.append(
            f"| {p.planet_name}{retro} "
            f"| {p.longitude:.2f}° "
            f"| {p.sign_glyph} {sign} {p.degree_in_sign:.1f}° "
            f"| {p.decan_number} "
            f"| {ruler} "
            f"| {face_str} "
            f"| {tarot} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# 渲染：上升 Decan 卡片 (Ascendant Decan Card)
# ============================================================

def _render_ascendant_card(chart: DecanChart, lang: str = "cn"):
    """顯示上升點 Decan 資訊卡"""
    d = chart.ascendant_decan
    deg_str = f"{chart.asc_longitude:.2f}°"
    if lang == "cn":
        st.subheader("🔺 上升 Decan")
        sign = d["sign_cn"]
        ruler = f"{d['chaldean_ruler_cn']} {d['chaldean_ruler_glyph']}"
        personality = d["personality_cn"]
    else:
        st.subheader("🔺 Ascendant Decan")
        sign = d["sign_en"]
        ruler = f"{d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"
        personality = d["personality_en"]

    html = f"""
    <div class="decan-card decan-highlight">
        <h4>{d['sign_glyph']} {sign} — Decan {d['decan_number']}</h4>
        <div class="meta">
            <b>ASC:</b> {deg_str} &nbsp;
            <b>{"迦勒底主星" if lang == "cn" else "Chaldean Ruler"}:</b> {ruler}<br/>
            <b>{"埃及" if lang == "cn" else "Egyptian"}:</b>
            <span style="font-size:1.2em;">{d['egyptian_hieroglyphic']}</span>
            {d['egyptian_name']} ({d['egyptian_transliteration']})
            · {d['egyptian_deity']}<br/>
            <b>{"塔羅" if lang == "cn" else "Tarot"}:</b>
            {d['tarot_card_cn'] if lang == "cn" else d['tarot_card_en']}<br/>
            <p style="font-style:italic; margin-top:6px;">{personality}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 渲染：本質尊貴摘要 (Essential Dignities Summary)
# ============================================================

def _render_dignities_table(chart: DecanChart, lang: str = "cn"):
    """渲染本質尊貴分數表"""
    if lang == "cn":
        st.subheader("🏛️ 本質尊貴摘要 (Essential Dignities)")
        hdr = "| 行星 | 入廟 | 入旺 | 落陷 | 入弱 | 日三分 | 夜三分 | Face | 總分 |"
    else:
        st.subheader("🏛️ Essential Dignities Summary")
        hdr = "| Planet | Domicile | Exaltation | Detriment | Fall | Trip Day | Trip Night | Face | Score |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [hdr, sep]

    def yn(v):
        return "✓" if v else "—"

    for row in chart.essential_dignities_summary:
        rows.append(
            f"| {row['planet']} "
            f"| {yn(row['domicile'])} "
            f"| {yn(row['exaltation'])} "
            f"| {yn(row['detriment'])} "
            f"| {yn(row['fall'])} "
            f"| {yn(row['triplicity_day'])} "
            f"| {yn(row['triplicity_night'])} "
            f"| {yn(row['face'])} "
            f"| **{row['score']:+d}** |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# 渲染：日月 Decan 性格解讀 (Sun & Moon Decan Personality)
# ============================================================

def _render_personality(chart: DecanChart, lang: str = "cn"):
    """顯示太陽與月亮 Decan 性格解讀"""
    if lang == "cn":
        st.subheader("🌟 日月 Decan 性格解讀")
    else:
        st.subheader("🌟 Sun & Moon Decan Personality")

    for p in chart.planets:
        if p.planet_name not in ("Sun ☉", "Moon ☽"):
            continue
        d = p.decan_data
        if lang == "cn":
            label = "太陽" if "Sun" in p.planet_name else "月亮"
            sign = d["sign_cn"]
            personality = d["personality_cn"]
            strengths = d["strengths_cn"]
            challenges = d["challenges_cn"]
        else:
            label = "Sun" if "Sun" in p.planet_name else "Moon"
            sign = d["sign_en"]
            personality = d["personality_en"]
            strengths = d["strengths_en"]
            challenges = d["challenges_en"]

        html = f"""
        <div class="decan-card">
            <h4>{p.planet_name} — {d['sign_glyph']} {sign} Decan {d['decan_number']}</h4>
            <div class="meta">
                <p>{personality}</p>
                <p><b>{"優勢" if lang == "cn" else "Strengths"}:</b> {strengths}</p>
                <p><b>{"挑戰" if lang == "cn" else "Challenges"}:</b> {challenges}</p>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 渲染：塔羅對應 (Tarot Correspondences)
# ============================================================

def _render_tarot_tab(chart: DecanChart | None, lang: str = "cn"):
    """顯示 36 Decans 與小阿爾卡那塔羅牌對應"""
    if lang == "cn":
        st.subheader("🃏 Decan 塔羅對應 (Minor Arcana)")
    else:
        st.subheader("🃏 Decan ↔ Tarot Minor Arcana")

    # Build set of decan indices where user has planets
    user_indices: set[int] = set()
    if chart is not None:
        for p in chart.planets:
            user_indices.add(p.decan_data["index"])

    for element, (suit_en, suit_cn) in ELEMENT_SUIT.items():
        suit_label = suit_cn if lang == "cn" else suit_en
        st.markdown(f"#### {suit_label} ({element})")
        matching = [d for d in DECANS_DATA if d["element"] == element]
        cols = st.columns(min(len(matching), 3))
        for i, d in enumerate(matching):
            col = cols[i % 3]
            hl_class = " decan-highlight" if d["index"] in user_indices else ""
            if lang == "cn":
                sign = d["sign_cn"]
                tarot = d["tarot_card_cn"]
                ruler = f"{d['chaldean_ruler_cn']} {d['chaldean_ruler_glyph']}"
            else:
                sign = d["sign_en"]
                tarot = d["tarot_card_en"]
                ruler = f"{d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"

            # Show which planets the user has in this decan
            planet_badges = ""
            if chart is not None:
                in_this = [p.planet_name for p in chart.planets
                           if p.decan_data["index"] == d["index"]]
                if in_this:
                    planet_badges = (
                        "<br/><b>"
                        + ("你的行星" if lang == "cn" else "Your planets")
                        + ":</b> " + ", ".join(in_this)
                    )

            card_html = f"""
            <div class="decan-card{hl_class}">
                <h4>🃏 {tarot}</h4>
                <div class="meta">
                    {d['sign_glyph']} {sign} Decan {d['decan_number']}<br/>
                    {d['degree_start']}°–{d['degree_end']}°<br/>
                    <b>{"主星" if lang == "cn" else "Ruler"}:</b> {ruler}
                    {planet_badges}
                </div>
            </div>
            """
            with col:
                st.markdown(card_html, unsafe_allow_html=True)


# ============================================================
# 渲染：文化尊重聲明 (Cultural Respect Footer)
# ============================================================

def _render_footer(lang: str = "cn"):
    st.divider()
    if lang == "cn":
        st.caption(
            "𓂀 本模組所呈現之古埃及 Decan 資料係基於學術文獻（Neugebauer & Parker、"
            "丹德拉黃道天花板）進行彙整，旨在教育與文化傳承。"
            "我們尊重古埃及文明的歷史遺產，使用資料時請懷抱敬意。"
        )
    else:
        st.caption(
            "𓂀 The ancient Egyptian Decan data presented here is compiled from academic "
            "sources (Neugebauer & Parker, Dendera Zodiac ceiling) for educational and "
            "cultural purposes. We respect the heritage of ancient Egyptian civilisation "
            "and encourage respectful engagement with this material."
        )


# ============================================================
# 渲染：埃及曆法 (Egyptian Civil Calendar)
# ============================================================

def _render_egyptian_calendar(chart: DecanChart, lang: str = "cn"):
    """渲染埃及三季曆法資訊"""
    if lang == "cn":
        st.subheader("📅 古埃及民用曆法")
    else:
        st.subheader("📅 Ancient Egyptian Civil Calendar")

    cal = gregorian_to_egyptian(chart.month, chart.day)

    if cal["is_epagomenal"]:
        _render_epagomenal_card(cal, lang)
    else:
        season_str = (f"{cal['season_emoji']} {cal['season_cn']} ({cal['season_en']})"
                      if lang == "cn"
                      else f"{cal['season_emoji']} {cal['season_en']}")
        month_str = (f"{cal['month_name_cn']} ({cal['month_name_en']})"
                     if lang == "cn" else cal["month_name_en"])
        html = f"""
        <div class="decan-card">
            <h4>{"出生日對應的埃及曆" if lang == "cn" else "Birth Date in Egyptian Calendar"}</h4>
            <div class="meta">
                <p><b>{"季節" if lang == "cn" else "Season"}:</b> {season_str}</p>
                <p><b>{"月份" if lang == "cn" else "Month"}:</b> {month_str}
                   （{"第" if lang == "cn" else "Month "}{cal['month_number']}{"月" if lang == "cn" else ""}）</p>
                <p><b>{"月中第" if lang == "cn" else "Day in Month"}:</b> {cal['day_in_month']}{"日" if lang == "cn" else ""} &nbsp;
                   <b>{"旬" if lang == "cn" else "Decade (Week)"}:</b>
                   {"第" if lang == "cn" else ""}{cal['decade']}{"旬" if lang == "cn" else ""}</p>
                <p><b>{"年中第" if lang == "cn" else "Day of Year"}:</b> {cal['day_of_year']}{"日" if lang == "cn" else ""}</p>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    # Educational overview
    if lang == "cn":
        st.markdown("#### 📖 三季制度")
        st.markdown(
            "古埃及民用曆以天狼星偕日升為新年起點（約7月20日），全年分為三季，"
            "每季4個月，每月30天，加上年末5天五日節，共365天。一「週」為10天（旬）。"
        )
    else:
        st.markdown("#### 📖 Three-Season System")
        st.markdown(
            "The Egyptian civil calendar begins at the heliacal rising of Sirius "
            "(~July 20). The year has 3 seasons of 4 months × 30 days, plus 5 "
            "epagomenal days = 365 days. A 'week' (decade) is 10 days."
        )

    # Season table
    if lang == "cn":
        hdr = "| 季節 | 含義 | 月份 | 月名 |"
    else:
        hdr = "| Season | Meaning | Months | Month Names |"
    sep = "|:---:|:---:|:---:|:---|"
    rows = [hdr, sep]
    season_data = [
        ("🌊 Akhet", "泛濫季 / Inundation", "1-4",
         "Thoth, Phaophi, Athyr, Choiak"),
        ("🌱 Peret", "生長季 / Growth", "5-8",
         "Tybi, Mechir, Phamenoth, Pharmuthi"),
        ("🌾 Shemu", "收穫季 / Harvest", "9-12",
         "Pachons, Payni, Epiphi, Mesore"),
    ]
    for s_name, s_meaning, s_months, s_names in season_data:
        rows.append(f"| {s_name} | {s_meaning} | {s_months} | {s_names} |")
    st.markdown("\n".join(rows))


def _render_epagomenal_card(cal: dict, lang: str = "cn"):
    """渲染五日節（Epagomenal Days）卡片"""
    day_num = cal["epagomenal_day"]
    deity_en = cal["epagomenal_deity_en"]
    deity_cn = cal["epagomenal_deity_cn"]
    story = cal["epagomenal_story_cn"] if lang == "cn" else cal["epagomenal_story_en"]

    html = f"""
    <div class="decan-card decan-highlight">
        <h4>🎭 {"五日節" if lang == "cn" else "Epagomenal Days"} —
            {"第" if lang == "cn" else "Day "}{day_num}{"天" if lang == "cn" else ""}</h4>
        <div class="meta">
            <p><b>{"守護神" if lang == "cn" else "Deity"}:</b>
               {deity_cn if lang == "cn" else deity_en}
               ({deity_en if lang == "cn" else deity_cn})</p>
            <p style="font-style:italic;">{story}</p>
            <p style="font-size:0.85em; opacity:0.8;">
                {"古埃及年末的5個補充日，每天對應一位重要神祇的誕生日。"
                 if lang == "cn" else
                 "The 5 extra days at the end of the Egyptian year, each "
                 "celebrating the birth of a major deity."}
            </p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # Show all 5 epagomenal deities
    if lang == "cn":
        st.markdown("#### 🎭 五日節神祇一覽")
        ep_hdr = "| 天數 | 神祇 | 簡介 |"
    else:
        st.markdown("#### 🎭 All Epagomenal Deities")
        ep_hdr = "| Day | Deity | Description |"
    ep_sep = "|:---:|:---:|:---|"
    ep_rows = [ep_hdr, ep_sep]
    from astro.egyptian_calendar import _EPAGOMENAL_DEITIES
    for i, d in enumerate(_EPAGOMENAL_DEITIES):
        deity_name = d["deity_cn"] if lang == "cn" else d["deity_en"]
        desc = d["story_cn"][:60] + "..." if lang == "cn" else d["story_en"][:80] + "..."
        marker = " ⬅️" if (i + 1) == day_num else ""
        ep_rows.append(f"| {i+1}{marker} | {deity_name} | {desc} |")
    st.markdown("\n".join(ep_rows))


# ============================================================
# 渲染：夜間十二時 (Egyptian Night Hours)
# ============================================================

def _render_night_hours(chart: DecanChart, lang: str = "cn"):
    """渲染夜間十二時資訊"""
    if lang == "cn":
        st.subheader("🌙 夜間十二時 — Decan 守護星")
    else:
        st.subheader("🌙 Twelve Hours of Night — Decan Guardians")

    # Determine birth decan index (from Sun's decan)
    sun_p = next(p for p in chart.planets if "Sun" in p.planet_name)
    birth_decan_idx = sun_p.decan_data["index"]

    hours = get_night_hours(birth_decan_idx)

    if lang == "cn":
        st.markdown(
            f"根據出生日太陽所在 Decan（**{DECANS_DATA[birth_decan_idx]['egyptian_name']}**，"
            f"Decan {birth_decan_idx}），計算該夜12小時各由哪顆 Decan 星主管。"
        )
        hdr = "| 時辰 | 名稱 | Decan 星 | 聖書體 | 守護神 |"
    else:
        st.markdown(
            f"Based on the Sun's birth decan "
            f"(**{DECANS_DATA[birth_decan_idx]['egyptian_name']}**, "
            f"Decan {birth_decan_idx}), "
            f"the 12 night hours are ruled by consecutive decan stars."
        )
        hdr = "| Hour | Name | Decan Star | Hieroglyphic | Deity |"
    sep = "|:---:|:---|:---|:---:|:---:|"
    rows = [hdr, sep]

    for h in hours:
        d = DECANS_DATA[h["decan_index"]]
        name = h["hour_name_cn"] if lang == "cn" else h["hour_name_en"]
        rows.append(
            f"| {h['hour']} | {name} "
            f"| {d['egyptian_name']} ({d['egyptian_transliteration']}) "
            f"| {d['egyptian_hieroglyphic']} "
            f"| {d['egyptian_deity']} |"
        )
    st.markdown("\n".join(rows))

    if lang == "cn":
        st.info(
            "💡 古埃及人將夜晚分為12個小時，每小時由一顆 Decan 星的升起來標記。"
            "這套系統來自中王國時期（約公元前2055-1650年）棺蓋上的對角星表。"
        )
    else:
        st.info(
            "💡 Ancient Egyptians divided the night into 12 hours, each marked "
            "by the rising of a decan star. This system originates from the "
            "diagonal star tables on Middle Kingdom coffin lids (c. 2055-1650 BCE)."
        )


# ============================================================
# 渲染：對角星表 (Diagonal Star Table)
# ============================================================

def _render_star_table(chart: DecanChart | None, lang: str = "cn"):
    """渲染互動式對角星表"""
    if lang == "cn":
        st.subheader("📊 對角星表（Decanal Star Clock）")
        st.markdown(
            "古埃及對角星表是12行（夜間小時）× 36列（年中旬）的表格。"
            "每個格子顯示該時段升起的 Decan 星。對角線模式源於每10天"
            "就有一顆新 Decan 星偕日升。"
        )
    else:
        st.subheader("📊 Diagonal Star Table (Decanal Star Clock)")
        st.markdown(
            "The diagonal star table is a 12-row (night hours) × 36-column "
            "(decades) grid. Each cell shows the decan star rising during "
            "that time period. The diagonal pattern arises because a new "
            "decan has its heliacal rising every 10 days."
        )

    table = build_diagonal_star_table()

    # Determine current decade if chart available
    hl_decade = None
    if chart is not None:
        cal = gregorian_to_egyptian(chart.month, chart.day)
        if not cal["is_epagomenal"]:
            hl_decade = (cal["day_of_year"] - 1) // 10

    # Build plotly heatmap
    z_data = []
    hover_data = []
    for h in range(12):
        z_row = []
        hover_row = []
        for d_col in range(36):
            decan_idx = table[h][d_col]
            z_row.append(decan_idx)
            decan = DECANS_DATA[decan_idx]
            hover_row.append(
                f"Hour {h+1}, Decade {d_col+1}<br>"
                f"{decan['egyptian_name']} ({decan['egyptian_transliteration']})<br>"
                f"{decan['sign_glyph']} {decan['sign_en']} D{decan['decan_number']}<br>"
                f"Deity: {decan['egyptian_deity']}"
            )
        z_data.append(z_row)
        hover_data.append(hover_row)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=[f"D{i+1}" for i in range(36)],
        y=[f"H{i+1}" for i in range(12)],
        text=[[DECANS_DATA[table[h][d]]["egyptian_name"][:6]
               for d in range(36)] for h in range(12)],
        texttemplate="%{text}",
        textfont=dict(size=7),
        hovertext=hover_data,
        hoverinfo="text",
        colorscale=[
            [0, EGYPTIAN_BLUE],
            [0.5, EGYPTIAN_TURQUOISE],
            [1, EGYPTIAN_GOLD],
        ],
        showscale=False,
    ))
    fig.update_layout(
        title=dict(
            text="𓂀 " + ("對角星表" if lang == "cn" else "Diagonal Star Table"),
            font=dict(color=EGYPTIAN_GOLD, size=14),
        ),
        xaxis_title="Decade" + (" (旬)" if lang == "cn" else ""),
        yaxis_title="Night Hour" + (" (夜時)" if lang == "cn" else ""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=50, r=20, t=40, b=50),
        yaxis=dict(autorange="reversed"),
    )

    if hl_decade is not None:
        fig.add_vline(
            x=hl_decade, line_width=2, line_dash="dash",
            line_color=EGYPTIAN_GOLD,
            annotation_text="Birth" if lang != "cn" else "出生",
            annotation_font_color=EGYPTIAN_GOLD,
        )

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 渲染：偕日升 & 可見性週期 (Heliacal Rising & Visibility)
# ============================================================

def _render_heliacal_visibility(chart: DecanChart | None, lang: str = "cn"):
    """渲染偕日升日期和可見性週期"""
    if lang == "cn":
        st.subheader("🌅 偕日升日期 & 可見性週期")
        st.markdown(
            "每顆 Decan 星每年有一次「偕日升」——在經過約70天不可見（進入冥界）後，"
            "首次在黎明前出現。這是古埃及天文學的核心觀測。"
        )
        hdr = ("| # | Decan 名 | 偕日升 | 可見結束 | 不可見期 | "
               "現代恒星 | 確定度 |")
    else:
        st.subheader("🌅 Heliacal Rising & Visibility Cycles")
        st.markdown(
            "Each decan star has an annual heliacal rising — its first dawn "
            "appearance after ~70 days of invisibility (descent into the Duat). "
            "This was the core observation of Egyptian astronomy."
        )
        hdr = ("| # | Decan Name | Heliacal Rising | Visible Until | "
               "Invisible Period | Modern Star | Certainty |")
    sep = "|:---:|:---|:---:|:---:|:---:|:---|:---:|"
    rows = [hdr, sep]

    # Highlight birth decan
    birth_idx = None
    if chart is not None:
        sun_p = next(p for p in chart.planets if "Sun" in p.planet_name)
        birth_idx = sun_p.decan_data["index"]

    for i in range(36):
        d = DECANS_DATA[i]
        rising = get_heliacal_rising_approx(i)
        vis = get_visibility_cycle(i)
        star = MODERN_STAR_IDS[i]

        rising_str = f"{rising[0]}/{rising[1]}"
        vis_end_str = f"{vis['visible_end'][0]}/{vis['visible_end'][1]}"
        invis_str = (f"{vis['invisible_start'][0]}/{vis['invisible_start'][1]} — "
                     f"{vis['invisible_end'][0]}/{vis['invisible_end'][1]}")
        star_str = star["star_cn"] if lang == "cn" else star["star_en"]

        cert_emoji = {"confirmed": "✅", "probable": "🟡",
                      "uncertain": "❓", "debated": "⚖️"}.get(star["certainty"], "❓")

        marker = " ⬅️" if i == birth_idx else ""
        rows.append(
            f"| {i}{marker} | {d['egyptian_name']} "
            f"| {rising_str} | {vis_end_str} | {invis_str} "
            f"| {star_str} | {cert_emoji} {star['certainty']} |"
        )
    st.markdown("\n".join(rows))

    # Duat mythology explanation
    st.divider()
    if lang == "cn":
        st.markdown("#### 🏛️ 冥界（杜阿特）與重生")
        st.markdown(
            "每顆 Decan 星約有 **70天不可見期**，古埃及人認為此時星辰降入冥界"
            "（𓇼 Duat）。這70天恰好對應木乃伊化的儀式周期。星辰的偕日升"
            "——首次在黎明前重新出現——被視為從冥界的「重生」，象徵著宇宙"
            "永恆循環的更新。"
        )
    else:
        st.markdown("#### 🏛️ The Duat (Underworld) & Rebirth")
        st.markdown(
            "Each decan star has an ~**70-day invisible period**, during which "
            "the ancient Egyptians believed it descended into the Duat "
            "(𓇼 underworld). These 70 days correspond to the mummification "
            "ritual period. The heliacal rising — the star's first reappearance "
            "at dawn — was seen as 'rebirth' from the Duat, symbolising the "
            "eternal cosmic renewal."
        )


# ============================================================
# 渲染：天狼星/索提斯週期 (Sothic Cycle)
# ============================================================

def _render_sothic_cycle(lang: str = "cn"):
    """渲染索提斯週期資訊"""
    if lang == "cn":
        st.subheader("⭐ 天狼星 & 索提斯週期")
    else:
        st.subheader("⭐ Sirius & the Sothic Cycle")

    info = get_sothic_info()

    html = f"""
    <div class="decan-card">
        <h4>𓇼 {"天狼星（Sopdet / Sothis）" if lang == "cn"
               else "Sirius (Sopdet / Sothis)"}</h4>
        <div class="meta">
            <p><b>{"偕日升日期" if lang == "cn" else "Heliacal Rising"}:</b>
               ~{"7月19日" if lang == "cn" else "July 19"}
               （{"北緯30°，孟菲斯/開羅" if lang == "cn"
                  else "Latitude 30°N, Memphis/Cairo"}）</p>
            <p><b>{"週期長度" if lang == "cn" else "Cycle Length"}:</b>
               {SOTHIC_CYCLE_YEARS} {"埃及民用年" if lang == "cn"
               else "Egyptian civil years"} = 1460
               {"儒略年" if lang == "cn" else "Julian years"}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    desc = info["description_cn"] if lang == "cn" else info["description_en"]
    sig = info["significance_cn"] if lang == "cn" else info["significance_en"]
    st.markdown(f"**{'描述' if lang == 'cn' else 'Description'}:** {desc}")
    st.markdown(f"**{'意義' if lang == 'cn' else 'Significance'}:** {sig}")

    # Historical records
    if lang == "cn":
        st.markdown("#### 📜 歷史記錄的天狼星偕日升")
        hdr = "| 年份 | 說明 |"
    else:
        st.markdown("#### 📜 Historical Sothic Rising Records")
        hdr = "| Year | Description |"
    sep = "|:---:|:---|"
    rows = [hdr, sep]
    for rec in info["known_cycles"]:
        if "year_bce" in rec:
            year_str = f"{rec['year_bce']} BCE"
        else:
            year_str = f"{rec['year_ce']} CE"
        desc_text = rec["description_cn"] if lang == "cn" else rec["description_en"]
        rows.append(f"| {year_str} | {desc_text} |")
    st.markdown("\n".join(rows))


# ============================================================
# 渲染：現代恒星對應 (Modern Star Identifications)
# ============================================================

def _render_modern_stars(lang: str = "cn"):
    """渲染現代恒星對應表"""
    if lang == "cn":
        st.subheader("🔭 現代恒星對應")
        st.markdown(
            "學者們（特別是 Neugebauer & Parker）嘗試將古代 Decan 名稱"
            "對應到現代已知恒星。許多對應仍有爭議。"
        )
        hdr = "| # | 埃及名 | 聖書體 | 現代恒星 | 星座 | 確定度 |"
    else:
        st.subheader("🔭 Modern Star Identifications")
        st.markdown(
            "Scholars (especially Neugebauer & Parker) have attempted to "
            "identify ancient decan stars with modern known stars. Many "
            "identifications remain uncertain or debated."
        )
        hdr = "| # | Egyptian Name | Hieroglyphic | Modern Star | Constellation | Certainty |"
    sep = "|:---:|:---|:---:|:---|:---|:---:|"
    rows = [hdr, sep]

    for i in range(36):
        d = DECANS_DATA[i]
        star = MODERN_STAR_IDS[i]
        star_str = star["star_cn"] if lang == "cn" else star["star_en"]
        const_str = star["constellation_cn"] if lang == "cn" else star["constellation_en"]
        cert_emoji = {"confirmed": "✅", "probable": "🟡",
                      "uncertain": "❓", "debated": "⚖️"}.get(star["certainty"], "❓")
        rows.append(
            f"| {i} | {d['egyptian_name']} "
            f"| {d['egyptian_hieroglyphic']} "
            f"| {star_str} | {const_str} "
            f"| {cert_emoji} {star['certainty']} |"
        )
    st.markdown("\n".join(rows))

    # Legend
    if lang == "cn":
        st.caption("✅ 已確認 · 🟡 很可能 · ❓ 不確定 · ⚖️ 有爭議")
    else:
        st.caption("✅ Confirmed · 🟡 Probable · ❓ Uncertain · ⚖️ Debated")


# ============================================================
# 渲染：丹德拉黃道天花板 (Dendera Zodiac Map)
# ============================================================

def _render_dendera_map(lang: str = "cn"):
    """渲染丹德拉黃道天花板示意圖"""
    if lang == "cn":
        st.subheader("🏛️ 丹德拉黃道天花板")
        st.markdown(
            "丹德拉神廟天花板（約公元前50年）是現存最完整的古埃及黃道圖。"
            "36顆 Decan 星圍繞北極排列，配合黃道十二宮和行星形象。"
        )
    else:
        st.subheader("🏛️ Dendera Zodiac Ceiling")
        st.markdown(
            "The Dendera zodiac ceiling (c. 50 BCE) is the most complete "
            "surviving ancient Egyptian zodiac. The 36 decan stars are "
            "arranged around the north pole, alongside the zodiac signs "
            "and planetary figures."
        )

    # Create interactive polar chart showing decan positions
    r_vals = [1] * 36
    theta_vals = [(i * 10 + 5) for i in range(36)]  # center of each 10° segment
    labels = [DECANS_DATA[i]["egyptian_name"] for i in range(36)]
    colors = [DECANS_DATA[i]["color"] for i in range(36)]
    hover_texts = []
    for i in range(36):
        d = DECANS_DATA[i]
        star = MODERN_STAR_IDS[i]
        hover_texts.append(
            f"<b>{d['egyptian_name']}</b> ({d['egyptian_transliteration']})<br>"
            f"{d['egyptian_hieroglyphic']}<br>"
            f"{d['sign_glyph']} {d['sign_en']} D{d['decan_number']}<br>"
            f"Deity: {d['egyptian_deity']}<br>"
            f"Modern: {star['star_en']}<br>"
            f"Constellation: {star['constellation_en']}"
        )

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=r_vals,
        theta=theta_vals,
        width=[10] * 36,
        marker=dict(color=colors, line=dict(color=EGYPTIAN_GOLD, width=1)),
        text=labels,
        hovertext=hover_texts,
        hoverinfo="text",
    ))

    # Add zodiac sign annotations
    for i, (sign_en, sign_cn, glyph, _) in enumerate(ZODIAC_SIGNS_DECAN):
        angle = i * 30 + 15
        fig.add_annotation(
            x=0.5 + 0.35 * go.Figure()._data if False else None,
            text=glyph,
            showarrow=False,
            font=dict(size=16, color=EGYPTIAN_GOLD),
            xref="paper", yref="paper",
        ) if False else None

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(
                tickmode="array",
                tickvals=[i * 30 for i in range(12)],
                ticktext=[f"{s[2]} {s[0]}" for s in ZODIAC_SIGNS_DECAN],
                tickfont=dict(color=EGYPTIAN_GOLD, size=10),
                direction="clockwise",
                rotation=90,
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=500,
        title=dict(
            text="𓂀 " + ("丹德拉 Decan 星圖" if lang == "cn"
                          else "Dendera Decan Star Map"),
            font=dict(color=EGYPTIAN_GOLD, size=14),
        ),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    if lang == "cn":
        st.caption(
            "此圖以現代極座標方式呈現36顆 Decan 的分佈，模擬丹德拉天花板"
            "的環形佈局。點擊各區段可查看 Decan 詳情。"
        )
    else:
        st.caption(
            "This chart presents the 36 decans in a polar layout inspired by "
            "the Dendera ceiling's circular arrangement. Click segments for details."
        )


# ============================================================
# 渲染：拉美西斯過境星鐘 (Ramesside Transit Star Clocks)
# ============================================================

def _render_transit_clocks(lang: str = "cn"):
    """渲染拉美西斯時期過境星鐘"""
    if lang == "cn":
        st.subheader("⏰ 拉美西斯過境星鐘")
    else:
        st.subheader("⏰ Ramesside Transit Star Clocks")

    info = build_transit_star_table()

    desc = info["description_cn"] if lang == "cn" else info["description_en"]
    method = info["method_cn"] if lang == "cn" else info["method_en"]
    diffs = info["differences_cn"] if lang == "cn" else info["differences_en"]
    date_range = info["date_range_cn"] if lang == "cn" else info["date_range_en"]

    st.markdown(f"**{'年代' if lang == 'cn' else 'Date Range'}:** {date_range}")
    st.markdown(f"**{'描述' if lang == 'cn' else 'Description'}:** {desc}")
    st.markdown(f"**{'觀測方法' if lang == 'cn' else 'Method'}:** {method}")
    st.markdown(f"**{'與對角星表的差異' if lang == 'cn' else 'Differences from Diagonal Star Tables'}:** {diffs}")

    # Body positions diagram
    body_positions = [
        ("Right Shoulder", "右肩"),
        ("Right Ear", "右耳"),
        ("Right Eye", "右眼"),
        ("Center-Right", "中偏右"),
        ("Center", "正中"),
        ("Center-Left", "中偏左"),
        ("Left Eye", "左眼"),
        ("Left Ear", "左耳"),
        ("Left Shoulder", "左肩"),
        ("Above Right", "右上方"),
        ("Directly Above", "正上方"),
        ("Above Left", "左上方"),
        ("Below", "下方"),
    ]

    if lang == "cn":
        st.markdown("#### 👤 十三個身體參考位置")
        hdr = "| # | 位置（英） | 位置（中） |"
    else:
        st.markdown("#### 👤 Thirteen Body Reference Positions")
        hdr = "| # | Position (EN) | Position (CN) |"
    sep = "|:---:|:---|:---|"
    rows = [hdr, sep]
    for i, (en, cn) in enumerate(body_positions):
        rows.append(f"| {i+1} | {en} | {cn} |")
    st.markdown("\n".join(rows))

    # Sample transit table as heatmap
    sample = info["sample_table"]
    fig = go.Figure(data=go.Heatmap(
        z=sample,
        x=[f"P{i+1}" for i in range(24)],
        y=[f"B{i+1}" for i in range(13)],
        colorscale=[
            [0, EGYPTIAN_BLUE],
            [0.5, EGYPTIAN_TURQUOISE],
            [1, EGYPTIAN_GOLD],
        ],
        showscale=False,
        hovertemplate=(
            "Body Position %{y}<br>Half-Month Period %{x}<br>"
            "Decan Index: %{z}<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=dict(
            text="𓂀 " + ("過境星鐘模式（簡化）" if lang == "cn"
                          else "Transit Star Clock Pattern (Simplified)"),
            font=dict(color=EGYPTIAN_GOLD, size=14),
        ),
        xaxis_title="Half-Month Period" + (" (半月期)" if lang == "cn" else ""),
        yaxis_title="Body Position" + (" (身體位置)" if lang == "cn" else ""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=50, r=20, t=40, b=50),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 公開渲染函數：完整排盤 (Public: Full Chart Rendering)
# ============================================================

def render_decan_chart(chart: DecanChart, lang: str = "cn"):
    """渲染完整 Decan 排盤 UI（含多個子分頁）"""
    st.markdown(_EGYPTIAN_CSS, unsafe_allow_html=True)

    tab_labels = (
        ["古埃及 Decans 瀏覽", "個人出生圖 Decan 計算", "塔羅連結",
         "埃及曆法 & 五日節", "夜間十二時", "對角星表",
         "偕日升 & 可見性", "天狼星 & 索提斯", "現代恒星",
         "丹德拉星圖", "過境星鐘"]
        if lang == "cn"
        else ["Browse Decans", "Birth Chart Analysis", "Tarot",
              "Egyptian Calendar", "Night Hours", "Star Table",
              "Heliacal Rising", "Sirius & Sothic", "Modern Stars",
              "Dendera Map", "Transit Clocks"]
    )
    (tab_browse, tab_birth, tab_tarot, tab_calendar, tab_night,
     tab_star_table, tab_heliacal, tab_sothic, tab_modern_stars,
     tab_dendera, tab_transit) = st.tabs(tab_labels)

    # --------------------------------------------------
    # Sub-tab 1: Browse Decans
    # --------------------------------------------------
    with tab_browse:
        _render_today_card(chart.today_sun_longitude, chart.today_sun_decan, lang)
        _render_decan_wheel(highlight_index=chart.today_sun_decan["index"])
        _render_decan_grid(lang=lang,
                           highlight_index=chart.today_sun_decan["index"])

    # --------------------------------------------------
    # Sub-tab 2: Birth Chart Analysis
    # --------------------------------------------------
    with tab_birth:
        ruler_system = st.radio(
            "⚙️ " + ("主星系統" if lang == "cn" else "Ruler System"),
            ["Chaldean", "Triplicity"],
            horizontal=True,
            key="decan_ruler_system",
        )
        _render_planet_table(chart, ruler_system, lang)
        st.divider()
        _render_ascendant_card(chart, lang)
        st.divider()
        _render_dignities_table(chart, lang)
        st.divider()
        _render_personality(chart, lang)

    # --------------------------------------------------
    # Sub-tab 3: Tarot Correspondences
    # --------------------------------------------------
    with tab_tarot:
        _render_tarot_tab(chart, lang)

    # --------------------------------------------------
    # Sub-tab 4: Egyptian Calendar & Epagomenal Days
    # --------------------------------------------------
    with tab_calendar:
        _render_egyptian_calendar(chart, lang)

    # --------------------------------------------------
    # Sub-tab 5: Night Hours
    # --------------------------------------------------
    with tab_night:
        _render_night_hours(chart, lang)

    # --------------------------------------------------
    # Sub-tab 6: Diagonal Star Table
    # --------------------------------------------------
    with tab_star_table:
        _render_star_table(chart, lang)

    # --------------------------------------------------
    # Sub-tab 7: Heliacal Rising & Visibility
    # --------------------------------------------------
    with tab_heliacal:
        _render_heliacal_visibility(chart, lang)

    # --------------------------------------------------
    # Sub-tab 8: Sothic Cycle
    # --------------------------------------------------
    with tab_sothic:
        _render_sothic_cycle(lang)

    # --------------------------------------------------
    # Sub-tab 9: Modern Star Identifications
    # --------------------------------------------------
    with tab_modern_stars:
        _render_modern_stars(lang)

    # --------------------------------------------------
    # Sub-tab 10: Dendera Map
    # --------------------------------------------------
    with tab_dendera:
        _render_dendera_map(lang)

    # --------------------------------------------------
    # Sub-tab 11: Transit Star Clocks
    # --------------------------------------------------
    with tab_transit:
        _render_transit_clocks(lang)

    _render_footer(lang)


# ============================================================
# 公開渲染函數：獨立瀏覽模式 (Public: Standalone Browse)
# ============================================================

def render_decan_browse(lang: str = "cn"):
    """渲染 Decan 瀏覽器（不需要出生資料）"""
    st.markdown(_EGYPTIAN_CSS, unsafe_allow_html=True)

    # 計算今日太陽位置
    swe.set_ephe_path("")
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    sun_now, _ = swe.calc_ut(now_jd, swe.SUN)
    today_sun_lon = _normalize(sun_now[0])
    today_sun_decan = get_decan_by_longitude(today_sun_lon)

    tab_labels = (
        ["古埃及 Decans 瀏覽", "偕日升 & 可見性", "天狼星 & 索提斯",
         "現代恒星", "對角星表", "丹德拉星圖", "過境星鐘"]
        if lang == "cn"
        else ["Browse Decans", "Heliacal Rising", "Sirius & Sothic",
              "Modern Stars", "Star Table", "Dendera Map", "Transit Clocks"]
    )
    (tab_browse, tab_heliacal, tab_sothic, tab_modern,
     tab_star_table, tab_dendera, tab_transit) = st.tabs(tab_labels)

    with tab_browse:
        _render_today_card(today_sun_lon, today_sun_decan, lang)
        _render_decan_wheel(highlight_index=today_sun_decan["index"])
        _render_decan_grid(lang=lang, highlight_index=today_sun_decan["index"])

    with tab_heliacal:
        _render_heliacal_visibility(None, lang)

    with tab_sothic:
        _render_sothic_cycle(lang)

    with tab_modern:
        _render_modern_stars(lang)

    with tab_star_table:
        _render_star_table(None, lang)

    with tab_dendera:
        _render_dendera_map(lang)

    with tab_transit:
        _render_transit_clocks(lang)

    _render_footer(lang)
