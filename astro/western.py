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


def _render_planet_table(chart):
    st.subheader("🪐 Planet Positions")
    header = "| Planet | Sign | Degree | Element | House | Retrograde |"
    sep = "|:------:|:----:|:------:|:-------:|:-----:|:----------:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#000000")
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
