"""
西洋占星排盤模組 (Western Astrology Chart Module)

使用 pyswisseph 以回歸黃道 (tropical zodiac) 計算行星位置，
包含天王星、海王星、冥王星等現代行星，並渲染西洋占星排盤。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

WESTERN_PLANETS = {
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

ZODIAC_SIGNS = [
    ("Aries", "♈", "白羊座", "Fire"),
    ("Taurus", "♉", "金牛座", "Earth"),
    ("Gemini", "♊", "雙子座", "Air"),
    ("Cancer", "♋", "巨蟹座", "Water"),
    ("Leo", "♌", "獅子座", "Fire"),
    ("Virgo", "♍", "處女座", "Earth"),
    ("Libra", "♎", "天秤座", "Air"),
    ("Scorpio", "♏", "天蠍座", "Water"),
    ("Sagittarius", "♐", "射手座", "Fire"),
    ("Capricorn", "♑", "摩羯座", "Earth"),
    ("Aquarius", "♒", "水瓶座", "Air"),
    ("Pisces", "♓", "雙魚座", "Water"),
]

ASPECT_TYPES = [
    {"name": "Conjunction (合)", "symbol": "☌", "angle": 0, "orb": 8},
    {"name": "Opposition (沖)", "symbol": "☍", "angle": 180, "orb": 8},
    {"name": "Trine (三合)", "symbol": "△", "angle": 120, "orb": 6},
    {"name": "Square (刑)", "symbol": "□", "angle": 90, "orb": 6},
    {"name": "Sextile (六合)", "symbol": "⚹", "angle": 60, "orb": 4},
]

PLANET_COLORS = {
    "Sun ☉": "#FF8C00",
    "Moon ☽": "#C0C0C0",
    "Mercury ☿": "#4169E1",
    "Venus ♀": "#FF69B4",
    "Mars ♂": "#DC143C",
    "Jupiter ♃": "#228B22",
    "Saturn ♄": "#8B4513",
    "Uranus ♅": "#00CED1",
    "Neptune ♆": "#7B68EE",
    "Pluto ♇": "#800080",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class WesternPlanet:
    """Western planet position"""
    name: str
    longitude: float
    latitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    element: str
    retrograde: bool
    house: int = 0


@dataclass
class WesternHouse:
    """Western house data"""
    number: int
    cusp: float
    sign: str
    sign_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class WesternChart:
    """Western astrology chart"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    planets: list
    houses: list
    ascendant: float
    midheaven: float
    asc_sign: str
    mc_sign: str


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

def _normalize(deg):
    return deg % 360.0


def _sign_index(deg):
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    return _normalize(deg) % 30.0


def _format_deg(deg):
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _find_house(lon, cusps):
    lon = _normalize(lon)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def compute_western_chart(year, month, day, hour, minute, timezone,
                          latitude, longitude, location_name=""):
    """計算西洋占星排盤 (Tropical Zodiac, Placidus Houses)"""
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    ascendant = ascmc[0]
    midheaven = ascmc[1]

    planets = []
    for name, planet_id in WESTERN_PLANETS.items():
        result, flags = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]

        pos = WesternPlanet(
            name=name,
            longitude=lon,
            latitude=lat,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(lon),
            element=sign_info[3],
            retrograde=speed < 0,
        )
        planets.append(pos)

    # North Node (Rahu)
    rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = _normalize(rahu[0])
    idx = _sign_index(rahu_lon)
    sign_info = ZODIAC_SIGNS[idx]
    planets.append(WesternPlanet(
        name="North Node ☊",
        longitude=rahu_lon,
        latitude=rahu[1],
        sign=sign_info[0],
        sign_glyph=sign_info[1],
        sign_chinese=sign_info[2],
        sign_degree=_sign_degree(rahu_lon),
        element=sign_info[3],
        retrograde=False,
    ))

    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        sign_info = ZODIAC_SIGNS[idx]
        houses.append(WesternHouse(
            number=i + 1,
            cusp=cusp,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_idx = _sign_index(ascendant)
    mc_idx = _sign_index(midheaven)

    return WesternChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        planets=planets, houses=houses,
        ascendant=ascendant, midheaven=midheaven,
        asc_sign=ZODIAC_SIGNS[asc_idx][0],
        mc_sign=ZODIAC_SIGNS[mc_idx][0],
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_western_chart(chart):
    """渲染完整的西洋占星排盤"""
    _render_info(chart)
    st.divider()
    _render_wheel_chart(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_aspects(chart)


def _render_info(chart):
    st.subheader("📋 Chart Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Date:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**Time:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**Timezone:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**Location:** {chart.location_name}")
        st.write(f"**Ascendant:** {chart.asc_sign} {_format_deg(chart.ascendant)}")
        st.write(f"**Midheaven:** {chart.mc_sign} {_format_deg(chart.midheaven)}")


def _render_wheel_chart(chart):
    """渲染西洋占星輪圖 (Western Wheel Chart)"""
    st.subheader("🔮 西洋占星輪盤 (Western Wheel)")

    # 建立行星→星座映射
    sign_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        sign_planets[idx].append(p.name)

    asc_idx = _sign_index(chart.ascendant)
    mc_idx = _sign_index(chart.midheaven)

    # 宮位 → 星座 mapping
    house_signs = {}
    for h in chart.houses:
        house_signs[h.number] = _sign_index(h.cusp)

    cell_style = (
        "border:1px solid #444; padding:6px 4px; text-align:center; "
        "vertical-align:top; font-size:11px; min-width:90px;"
    )
    asc_cell = cell_style + " background:#3d3010;"
    mc_cell = cell_style + " background:#1a2a3d;"

    # wheel_grid: 順時針從左側 ASC 開始
    # 左列→右列對應 house 1→12 順時針
    # row0: [1(left/top), 10(top), 11(top), 12(top), 2(right/top)]
    # row1: [center col span, house 11, 12, house 3]
    # row2: [center col span, house 9, 8, house 5]
    # row3: [6, 7, 8, 9]
    # 使用 5 列讓佈局更均匀

    # 重新設計：每個 cell = 一個宮位
    # 宮位沿順時針排列：左上(1) → 上(10) → 右上(11) → 右(12) → 右下(2) → 下(3) → 左下(4) → 左(5,6,7,8,9)
    # 4x4 grid 佈局
    #        col0   col1   col2   col3
    # row0   10     11     12      1
    # row1    9    center   2      3
    # row2    8    center   4      5
    # row3    7      6      5      4   <- 這個不對

    # 標準西占輪盤佈局（從上方俯視，北方在上）：
    #               house2
    #         house3  house1  house11
    #      house4              house12
    #         house5    house6    house7
    #               house8
    # 4x3 表格，宮位分佈：
    #   [10, 11, 12, 1]
    #   [ 9, --,  --, 2]
    #   [ 8, --,  --, 3]
    #   [ 7,  6,   5, 4]
    wheel_grid = [
        [10, 11, 12,  1],
        [ 9, -1,  -1,  2],
        [ 8, -1,  -1,  3],
        [ 7,  6,   5,  4],
    ]

    html = (
        '<table style="border-collapse:collapse; margin:auto; width:100%; max-width:560px;">'
        '<caption style="caption-side:top; font-size:14px; padding:4px;">'
        '<b>Western Wheel Chart</b> — '
        '🔺 ASC ' + ZODIAC_SIGNS[asc_idx][1] + ZODIAC_SIGNS[asc_idx][0] + ' '
        + f'{_sign_degree(chart.ascendant):.1f}° &nbsp; '
        '⬡ MC ' + ZODIAC_SIGNS[mc_idx][1] + ZODIAC_SIGNS[mc_idx][0] + ' '
        + f'{_sign_degree(chart.midheaven):.1f}°'
        '</caption>'
    )
    for row in wheel_grid:
        html += "<tr>"
        for idx in row:
            if idx == -1:
                # 中心格
                html += (
                    '<td style="'
                    'border:1px solid #444; padding:10px; text-align:center; '
                    'vertical-align:middle; background:#2a2a2a; font-size:13px; '
                    'color:#e0e0e0;">'
                    '<b>Kin<br/>Astro</b><br/>'
                    '<small>Western</small>'
                    '</td>'
                )
            else:
                h = next((x for x in chart.houses if x.number == idx), None)
                if h is None:
                    html += '<td style="' + cell_style + '"></td>'
                    continue
                sign_idx = house_signs.get(idx, _sign_index(h.cusp))
                sign_info = ZODIAC_SIGNS[sign_idx]
                planets_in_house = h.planets
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(p, "#c8c8c8")};font-weight:bold">'
                    f'{p.split(" ")[0]}</span>'
                    for p in planets_in_house
                ) if planets_in_house else '<span style="color:#ccc">—</span>'
                is_asc_house = (idx == 1)
                is_mc_house = (idx == 10)
                style = asc_cell if is_asc_house else (mc_cell if is_mc_house else cell_style)
                marker = " 🔺" if is_asc_house else (" ⬡" if is_mc_house else "")
                html += (
                    f'<td style="{style}">'
                    f'<b>{idx}</b>{marker}<br/>'
                    f'{sign_info[1]} {sign_info[0]}<br/>'
                    f'<small>{_format_deg(h.cusp)}</small><br/>'
                    f'{p_html}'
                    '</td>'
                )
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
    st.caption("🔺 = House 1 (Ascendant)   ⬡ = House 10 (Midheaven)")


def _render_planet_table(chart):
    st.subheader("🪐 Planet Positions")
    header = "| Planet | Sign | Degree | Element | House | Retrograde |"
    sep = "|:------:|:----:|:------:|:-------:|:-----:|:----------:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        rows.append(
            f"| {name_html} | {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° | {p.element} "
            f"| {p.house} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
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


def _render_aspects(chart):
    st.subheader("🔗 Aspects")
    aspects = []
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
                    aspects.append({
                        "p1": p1.name, "p2": p2.name,
                        "aspect": asp["name"], "symbol": asp["symbol"],
                        "orb": orb,
                    })
                    break
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
