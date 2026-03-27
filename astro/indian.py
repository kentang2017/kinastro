"""
印度占星排盤模組 (Indian/Vedic Astrology — Jyotish Chart Module)

使用 pyswisseph 以恆星黃道 (sidereal zodiac) 搭配 Lahiri 歲差
計算行星位置，包含 Nakshatra（二十七宿）與 Rashi（星座）資訊。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

VEDIC_PLANETS = {
    "Surya (太陽)": swe.SUN,
    "Chandra (月亮)": swe.MOON,
    "Mangal (火星)": swe.MARS,
    "Budha (水星)": swe.MERCURY,
    "Guru (木星)": swe.JUPITER,
    "Shukra (金星)": swe.VENUS,
    "Shani (土星)": swe.SATURN,
}

RASHIS = [
    ("Mesha", "♈", "白羊", "Mars", "火"),
    ("Vrishabha", "♉", "金牛", "Venus", "地"),
    ("Mithuna", "♊", "雙子", "Mercury", "風"),
    ("Karka", "♋", "巨蟹", "Moon", "水"),
    ("Simha", "♌", "獅子", "Sun", "火"),
    ("Kanya", "♍", "處女", "Mercury", "地"),
    ("Tula", "♎", "天秤", "Venus", "風"),
    ("Vrischika", "♏", "天蠍", "Mars", "水"),
    ("Dhanu", "♐", "射手", "Jupiter", "火"),
    ("Makara", "♑", "摩羯", "Saturn", "地"),
    ("Kumbha", "♒", "水瓶", "Saturn", "風"),
    ("Meena", "♓", "雙魚", "Jupiter", "水"),
]

# 二十七宿 (27 Nakshatras) — each spans 13°20'
NAKSHATRAS = [
    ("Ashwini", "馬頭", "Ketu"),
    ("Bharani", "大陵", "Venus"),
    ("Krittika", "昴宿", "Sun"),
    ("Rohini", "畢宿", "Moon"),
    ("Mrigashira", "觜宿", "Mars"),
    ("Ardra", "參宿", "Rahu"),
    ("Punarvasu", "井宿", "Jupiter"),
    ("Pushya", "鬼宿", "Saturn"),
    ("Ashlesha", "柳宿", "Mercury"),
    ("Magha", "星宿", "Ketu"),
    ("Purva Phalguni", "張宿", "Venus"),
    ("Uttara Phalguni", "翼宿", "Sun"),
    ("Hasta", "軫宿", "Moon"),
    ("Chitra", "角宿", "Mars"),
    ("Swati", "亢宿", "Rahu"),
    ("Vishakha", "氐宿", "Jupiter"),
    ("Anuradha", "房宿", "Saturn"),
    ("Jyeshtha", "心宿", "Mercury"),
    ("Mula", "尾宿", "Ketu"),
    ("Purva Ashadha", "箕宿", "Venus"),
    ("Uttara Ashadha", "斗宿", "Sun"),
    ("Shravana", "牛宿", "Moon"),
    ("Dhanishta", "女宿", "Mars"),
    ("Shatabhisha", "虛宿", "Rahu"),
    ("Purva Bhadrapada", "危宿", "Jupiter"),
    ("Uttara Bhadrapada", "室宿", "Saturn"),
    ("Revati", "壁宿", "Mercury"),
]

PLANET_COLORS = {
    "Surya (太陽)": "#FF8C00",
    "Chandra (月亮)": "#C0C0C0",
    "Mangal (火星)": "#DC143C",
    "Budha (水星)": "#4169E1",
    "Guru (木星)": "#FFD700",
    "Shukra (金星)": "#FF69B4",
    "Shani (土星)": "#8B4513",
    "Rahu (羅睺)": "#800080",
    "Ketu (計都)": "#4B0082",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class VedicPlanet:
    """Vedic planet position"""
    name: str
    longitude: float
    latitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    rashi_lord: str
    sign_degree: float
    nakshatra: str
    nakshatra_chinese: str
    nakshatra_lord: str
    nakshatra_pada: int
    retrograde: bool
    house: int = 0


@dataclass
class VedicHouse:
    """Vedic bhava (house)"""
    number: int
    cusp: float
    rashi: str
    rashi_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class VedicChart:
    """Indian / Vedic astrology chart"""
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
    ayanamsa: float
    planets: list
    houses: list
    ascendant: float
    asc_rashi: str


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

def _normalize(deg):
    return deg % 360.0


def _sign_index(deg):
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    return _normalize(deg) % 30.0


def _nakshatra_info(deg):
    """Return (nakshatra_index, pada) for a given sidereal longitude."""
    deg = _normalize(deg)
    nak_span = 360.0 / 27.0  # 13°20'
    idx = int(deg / nak_span) % 27
    pada = int((deg % nak_span) / (nak_span / 4.0)) + 1
    return idx, min(pada, 4)


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


def compute_vedic_chart(year, month, day, hour, minute, timezone,
                        latitude, longitude, location_name=""):
    """計算印度占星排盤 (Sidereal / Lahiri Ayanamsa)"""
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Compute sidereal house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P",
                                 swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    planets = []
    for name, pid in VEDIC_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        rashi = RASHIS[idx]
        nak_idx, pada = _nakshatra_info(lon)
        nak = NAKSHATRAS[nak_idx]

        planets.append(VedicPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], sign_degree=_sign_degree(lon),
            nakshatra=nak[0], nakshatra_chinese=nak[1],
            nakshatra_lord=nak[2], nakshatra_pada=pada,
            retrograde=speed < 0,
        ))

    # Rahu (Mean North Node)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = RASHIS[idx]
    nak_idx, pada = _nakshatra_info(rahu_lon)
    nak = NAKSHATRAS[nak_idx]
    planets.append(VedicPlanet(
        name="Rahu (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(rahu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
    ))

    # Ketu (South Node = Rahu + 180°)
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = RASHIS[idx]
    nak_idx, pada = _nakshatra_info(ketu_lon)
    nak = NAKSHATRAS[nak_idx]
    planets.append(VedicPlanet(
        name="Ketu (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(ketu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
    ))

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        rashi = RASHIS[idx]
        houses.append(VedicHouse(
            number=i + 1, cusp=cusp,
            rashi=rashi[0], rashi_glyph=rashi[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_rashi = RASHIS[_sign_index(ascendant)][0]

    return VedicChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        planets=planets, houses=houses,
        ascendant=ascendant, asc_rashi=asc_rashi,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_vedic_chart(chart):
    """渲染完整的印度占星排盤"""
    _render_info(chart)
    st.divider()
    _render_south_indian_grid(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)


def _render_info(chart):
    st.subheader("📋 排盤資訊 (Chart Information)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間 (Time):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區 (TZ):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點 (Location):** {chart.location_name}")
        st.write(f"**Ayanamsa (歲差):** {chart.ayanamsa:.4f}°")
        st.write(f"**Lagna (命宮):** {chart.asc_rashi} "
                 f"{_format_deg(chart.ascendant)}")


def _render_south_indian_grid(chart):
    """渲染南印度式方盤 (South Indian Chart)"""
    st.subheader("📊 南印度排盤 (South Indian Chart)")

    # South Indian chart: fixed rashi positions in 4×4 grid
    # Mapping: each cell corresponds to a rashi index (0-11)
    si_grid = [
        [3, 2, 1, 0],      # Cancer Gemini Taurus Aries
        [4, -1, -1, 11],    # Leo [center] Pisces
        [5, -1, -1, 10],    # Virgo [center] Aquarius
        [6, 7, 8, 9],       # Libra Scorpio Sagittarius Capricorn
    ]

    # Build rashi -> planets mapping
    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        rashi_planets[idx].append(p.name.split(" ")[0])

    # Find ascendant rashi for highlight
    asc_idx = _sign_index(chart.ascendant)

    cell_style = (
        "border:1px solid #666; padding:6px; text-align:center; "
        "vertical-align:top; min-width:120px; font-size:13px;"
    )
    asc_cell_style = cell_style + " background:#fffde7;"
    center_style = (
        "border:1px solid #666; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#f8f8f0;"
    )

    html = '<table style="border-collapse:collapse; margin:auto; width:100%;">'
    for row_idx, row in enumerate(si_grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    center_content = (
                        f"<b>Jyotish 印度占星</b><br/>"
                        f"{chart.year}/{chart.month}/{chart.day}<br/>"
                        f"{chart.hour:02d}:{chart.minute:02d} "
                        f"UTC{chart.timezone:+.1f}<br/>"
                        f"{chart.location_name}<br/>"
                        f"Ayanamsa: {chart.ayanamsa:.2f}°"
                    )
                    html += (
                        f'<td colspan="2" rowspan="2" '
                        f'style="{center_style}">{center_content}</td>'
                    )
                    col_idx += 2
                    continue
                else:
                    col_idx += 1
                    continue
            else:
                rashi = RASHIS[idx]
                style = asc_cell_style if idx == asc_idx else cell_style
                p_names = rashi_planets[idx]
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(full, "#000")};'
                    f'font-weight:bold">{n}</span>'
                    for n in p_names
                    for full in [next(
                        (k for k in PLANET_COLORS if k.startswith(n)), "")]
                ) if p_names else '<span style="color:#999">—</span>'
                marker = " 🔺" if idx == asc_idx else ""
                cell_content = (
                    f"<b>{rashi[0]}{marker}</b><br/>"
                    f'<small style="color:#888">{rashi[1]} {rashi[2]}</small>'
                    f"<br/>{p_html}"
                )
                html += f'<td style="{style}">{cell_content}</td>'
            col_idx += 1
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


def _render_planet_table(chart):
    st.subheader("🪐 行星位置 (Graha Positions)")
    header = ("| Graha | Rashi | Degree | Lord | "
              "Nakshatra | Pada | Nak Lord | R |")
    sep = ("|:-----:|:-----:|:------:|:----:|"
           ":--------:|:----:|:--------:|:-:|")
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#000000")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        rows.append(
            f"| {name_html} | {p.rashi_glyph} {p.rashi} ({p.rashi_chinese}) "
            f"| {p.sign_degree:.2f}° | {p.rashi_lord} "
            f"| {p.nakshatra} ({p.nakshatra_chinese}) "
            f"| {p.nakshatra_pada} | {p.nakshatra_lord} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ 宮位 (Bhava)")
    header = "| Bhava | Cusp | Rashi | Planets |"
    sep = "|:-----:|:----:|:-----:|:-------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.rashi_glyph} {h.rashi} | {planets_str} |"
        )
    st.markdown("\n".join(rows))
