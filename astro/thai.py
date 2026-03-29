"""
泰國占星排盤模組 (Thai Astrology Chart Module)

泰國占星以印度占星 (Jyotish) 為基礎，使用恆星黃道 (sidereal zodiac)，
加入泰國傳統命名與詮釋體系。本模組使用 pyswisseph 搭配 Lahiri 歲差計算行星位置。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

THAI_PLANETS = {
    "พระอาทิตย์ (太陽)": swe.SUN,
    "พระจันทร์ (月亮)": swe.MOON,
    "พระอังคาร (火星)": swe.MARS,
    "พระพุธ (水星)": swe.MERCURY,
    "พระพฤหัสบดี (木星)": swe.JUPITER,
    "พระศุกร์ (金星)": swe.VENUS,
    "พระเสาร์ (土星)": swe.SATURN,
}

# Thai names for the 12 Rashis
THAI_RASHIS = [
    ("เมษ (Mesha)", "♈", "白羊", "พระอังคาร"),
    ("พฤษภ (Vrishabha)", "♉", "金牛", "พระศุกร์"),
    ("เมถุน (Mithuna)", "♊", "雙子", "พระพุธ"),
    ("กรกฎ (Karka)", "♋", "巨蟹", "พระจันทร์"),
    ("สิงห์ (Simha)", "♌", "獅子", "พระอาทิตย์"),
    ("กันย์ (Kanya)", "♍", "處女", "พระพุธ"),
    ("ตุลย์ (Tula)", "♎", "天秤", "พระศุกร์"),
    ("พิจิก (Vrischika)", "♏", "天蠍", "พระอังคาร"),
    ("ธนู (Dhanu)", "♐", "射手", "พระพฤหัสบดี"),
    ("มกร (Makara)", "♑", "摩羯", "พระเสาร์"),
    ("กุมภ์ (Kumbha)", "♒", "水瓶", "พระเสาร์"),
    ("มีน (Meena)", "♓", "雙魚", "พระพฤหัสบดี"),
]

# Thai day-planet correspondences for interpretive context
THAI_DAY_PLANETS = {
    0: ("วันอาทิตย์ (Sunday)", "พระอาทิตย์"),
    1: ("วันจันทร์ (Monday)", "พระจันทร์"),
    2: ("วันอังคาร (Tuesday)", "พระอังคาร"),
    3: ("วันพุธ (Wednesday)", "พระพุธ"),
    4: ("วันพฤหัสบดี (Thursday)", "พระพฤหัสบดี"),
    5: ("วันศุกร์ (Friday)", "พระศุกร์"),
    6: ("วันเสาร์ (Saturday)", "พระเสาร์"),
}

PLANET_COLORS = {
    "พระอาทิตย์ (太陽)": "#FF8C00",
    "พระจันทร์ (月亮)": "#C0C0C0",
    "พระอังคาร (火星)": "#DC143C",
    "พระพุธ (水星)": "#4169E1",
    "พระพฤหัสบดี (木星)": "#FFD700",
    "พระศุกร์ (金星)": "#FF69B4",
    "พระเสาร์ (土星)": "#8B4513",
    "ราหู (羅睺)": "#800080",
    "เกตุ (計都)": "#4B0082",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ThaiPlanet:
    """Thai planet position"""
    name: str
    longitude: float
    latitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    rashi_lord: str
    sign_degree: float
    retrograde: bool
    house: int = 0


@dataclass
class ThaiHouse:
    """Thai bhava (house)"""
    number: int
    cusp: float
    rashi: str
    rashi_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class ThaiChart:
    """Thai astrology chart"""
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
    day_of_week: int
    day_planet: str
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


def compute_thai_chart(year, month, day, hour, minute, timezone,
                       latitude, longitude, location_name=""):
    """計算泰國占星排盤 (Sidereal / Lahiri Ayanamsa)"""
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Day of week: 0=Mon … 6=Sun in Python, but we need 0=Sun … 6=Sat
    import datetime as _dt
    dt = _dt.date(year, month, day)
    # isoweekday: 1=Mon … 7=Sun → convert to 0=Sun,1=Mon,...,6=Sat
    dow = dt.isoweekday() % 7
    day_name, day_planet = THAI_DAY_PLANETS[dow]

    # Compute sidereal house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P",
                                 swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    planets = []
    for name, pid in THAI_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        rashi = THAI_RASHIS[idx]

        planets.append(ThaiPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], sign_degree=_sign_degree(lon),
            retrograde=speed < 0,
        ))

    # Rahu (ราหู)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = THAI_RASHIS[idx]
    planets.append(ThaiPlanet(
        name="ราหู (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(rahu_lon),
        retrograde=False,
    ))

    # Ketu (เกตุ)
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = THAI_RASHIS[idx]
    planets.append(ThaiPlanet(
        name="เกตุ (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(ketu_lon),
        retrograde=False,
    ))

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        rashi = THAI_RASHIS[idx]
        houses.append(ThaiHouse(
            number=i + 1, cusp=cusp,
            rashi=rashi[0], rashi_glyph=rashi[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_rashi = THAI_RASHIS[_sign_index(ascendant)][0]

    return ThaiChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        day_of_week=dow, day_planet=day_planet,
        planets=planets, houses=houses,
        ascendant=ascendant, asc_rashi=asc_rashi,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_thai_chart(chart):
    """渲染完整的泰國占星排盤"""
    _render_info(chart)
    st.divider()
    _render_thai_grid(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)


def _render_info(chart):
    st.subheader("📋 ข้อมูลดวง (排盤資訊)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**วันที่ (日期):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**เวลา (時間):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**เขตเวลา (時區):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**สถานที่ (地點):** {chart.location_name}")
        day_name = THAI_DAY_PLANETS[chart.day_of_week][0]
        st.write(f"**{day_name}**")
        st.write(f"**ดาวประจำวัน (日主星):** {chart.day_planet}")
        st.write(f"**ลัคนา (命宮):** {chart.asc_rashi} "
                 f"{_format_deg(chart.ascendant)}")
        st.write(f"**Ayanamsa (歲差):** {chart.ayanamsa:.4f}°")


def _render_thai_grid(chart):
    """渲染泰國式方盤"""
    st.subheader("📊 ผังดวงชาตา (泰國排盤)")

    # Thai chart uses similar layout to South Indian
    grid = [
        [3, 2, 1, 0],
        [4, -1, -1, 11],
        [5, -1, -1, 10],
        [6, 7, 8, 9],
    ]

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        # Use short Thai name (first word)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name))

    asc_idx = _sign_index(chart.ascendant)

    cell_style = (
        "border:1px solid #444; padding:6px; text-align:center; "
        "vertical-align:top; min-width:120px; font-size:13px;"
    )
    asc_cell_style = cell_style + " background:#3d3010;"
    center_style = (
        "border:1px solid #444; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a2a; "
        "color:#e0e0e0;"
    )

    html = '<table style="border-collapse:collapse; margin:auto; width:100%;">'
    for row_idx, row in enumerate(grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    center_content = (
                        f"<b>ดวงชาตา 泰國占星</b><br/>"
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
                rashi = THAI_RASHIS[idx]
                style = asc_cell_style if idx == asc_idx else cell_style
                p_list = rashi_planets[idx]
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(full, "#e0e0e0")};'
                    f'font-weight:bold">{short}</span>'
                    for short, full in p_list
                ) if p_list else '<span style="color:#666">—</span>'
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
    st.subheader("🪐 ตำแหน่งดาว (行星位置)")
    header = "| ดาว (Planet) | ราศี (Rashi) | องศา (Degree) | เจ้าเรือน (Lord) | ภพ (House) | ℞ |"
    sep = "|:------------:|:------------:|:-------------:|:----------------:|:----------:|:-:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        rows.append(
            f"| {name_html} | {p.rashi_glyph} {p.rashi} ({p.rashi_chinese}) "
            f"| {p.sign_degree:.2f}° | {p.rashi_lord} "
            f"| {p.house} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ ภพ (宮位)")
    header = "| ภพ (Bhava) | จุดเริ่ม (Cusp) | ราศี (Rashi) | ดาวในภพ (Planets) |"
    sep = "|:----------:|:--------------:|:------------:|:-----------------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.rashi_glyph} {h.rashi} | {planets_str} |"
        )
    st.markdown("\n".join(rows))
