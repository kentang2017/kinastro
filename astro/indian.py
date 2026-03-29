"""
印度占星排盤模組 (Indian/Vedic Astrology — Jyotish Chart Module)

使用 pyswisseph 以恆星黃道 (sidereal zodiac) 搭配 Lahiri 歲差
計算行星位置，包含 Nakshatra（二十七宿）與 Rashi（星座）資訊。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

from astro import sukkayodo

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

# 七曜名稱索引對照 (lord index → name string)
# 0=Ketu, 1=Venus, 2=Sun, 3=Moon, 4=Mars, 5=Rahu, 6=Jupiter, 7=Saturn, 8=Mercury
GRAHA_NAMES_BY_INDEX = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

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
# 每宿之主曜、符號、象徵、特性 (Lord, Symbol, Symbolism, Quality)
NAKSHATRA_PROPERTIES = [
    # (nak_name, lord, symbol, deity, quality, caste, nature)
    # lord: 0=Ketu, 1=Venus, 2=Sun, 3=Moon, 4=Mars, 5=Rahu, 6=Jupiter, 7=Saturn, 8=Mercury
    ("Ashwini",        0, "馬頭",   "Aswini Twins",  "Cheerful",    "Deva",  "Uttama"),
    ("Bharani",        1, "大陵",   "Yami (Death)",   "Passionate",  "Manushya","Kahara"),
    ("Krittika",       2, "昴宿",   "Agni",           "Fierce",      "Deva",  "Uttama"),
    ("Rohini",         3, "畢宿",   "Brahma/Prajna",  "Stable",      "Lunar", "Uttama"),
    ("Mrigashira",     4, "觜宿",   "Soma/Growth",    "Curious",     "Lunar", "Madhyama"),
    ("Ardra",          5, "參宿",   "Rudra (Storm)",  "Restless",    "Lunar", "Kahara"),
    ("Punarvasu",      6, "井宿",   "Aditi (Abode)",  "Renewing",    "Deva",  "Uttama"),
    ("Pushya",         7, "鬼宿",   "Brihaspati",     "Nurturing",   "Deva",  "Uttama"),
    ("Ashlesha",       8, "柳宿",   "Naga (Serpent)", "Seductive",   "Naga",  "Kahara"),
    ("Magha",          0, "星宿",   "Pitris (Ancestors)","Regal",   "Lunar", "Madhyama"),
    ("Purva Phalguni", 1, "張宿",   "Bhaga (Prosperity)","Loving",  "Lunar", "Madhyama"),
    ("Uttara Phalguni",2, "翼宿",   "Aryaman (Guardian)","Dutiful",  "Deva",  "Uttama"),
    ("Hasta",          3, "軫宿",   "Savitri (Creator)","Skillful",  "Lunar", "Madhyama"),
    ("Chitra",         4, "角宿",   "Tvashtar (Architect)","Radiant","Naga", "Uttama"),
    ("Swati",          5, "亢宿",   "Vayu (Wind)",    "Independent", "Naga",  "Madhyama"),
    ("Vishakha",       6, "氐宿",   "Indra/Agni",     "Multi-faceted","Lunar","Kahara"),
    ("Anuradha",       7, "房宿",   "Mitra (Friendship)","Balanced","Deva", "Uttama"),
    ("Jyeshtha",       8, "心宿",   "Indra (Chief)",  "Protective",  "Naga",  "Kahara"),
    ("Mula",           0, "尾宿",   "Nirriti (Destruction)","Deep","Naga",  "Kahara"),
    ("Purva Ashadha",  1, "箕宿",   "Apah (Water)",   "Victorious",  "Deva",  "Madhyama"),
    ("Uttara Ashadha", 2, "斗宿",   "Vishwa Devas",   "Truthful",    "Deva",  "Uttama"),
    ("Shravana",       3, "牛宿",   "Vishnu (Preserver)","Devoted",  "Lunar", "Uttama"),
    ("Dhanishta",      4, "女宿",   "Vasudev (Abundance)","Wealthy",  "Naga", "Madhyama"),
    ("Shatabhisha",    5, "虛宿",   "Varuna (Cosmic Waters)","Mysterious","Naga","Kahara"),
    ("Purva Bhadrapada",6,"危宿",  "Aja Ekapada",     "Heroic",      "Naga",  "Madhyama"),
    ("Uttara Bhadrapada",7,"室宿", "Ahir Budhya",    "Serene",      "Naga",  "Uttama"),
    ("Revati",         8, "壁宿",   "Pushan (Guardian)","Nurturing", "Lunar", "Uttama"),
]

NAKSHATRAS = [
    (prop[0], prop[2], prop[1])  # (name, chinese, lord_index)
    for prop in NAKSHATRA_PROPERTIES
]

# 七曜主宿對應表 (Graha → Nakshatras they rule)
GRAHA_NAKSHATRA_MAP = {
    "Ketu":     ["Ashwini", "Magha", "Mula"],
    "Venus":    ["Bharani", "Purva Phalguni", "Purva Ashadha"],
    "Sun":      ["Krittika", "Uttara Phalguni", "Uttara Ashadha"],
    "Moon":     ["Rohini", "Hasta", "Shravana"],
    "Mars":     ["Mrigashira", "Chitra", "Dhanishta"],
    "Rahu":     ["Ardra", "Swati", "Shatabhisha"],
    "Jupiter":  ["Punarvasu", "Vishakha", "Purva Bhadrapada"],
    "Saturn":   ["Pushya", "Anuradha", "Uttara Bhadrapada"],
    "Mercury":  ["Ashlesha", "Jyeshtha", "Revati"],
}

# 七曜與宿的吉凶屬性 (Graha's natural relationship with nakshatras)
GRAHA_NAKSHATRA_NATURE = {
    # 曜名: (吉宿數, 中宿數, 凶宿數)
    "Ketu":     (3, 0, 0),   # 3 個主宿皆為中凶
    "Venus":    (2, 1, 0),   # Venus 主 3 吉/中
    "Sun":      (1, 2, 0),   # Sun 主 1 吉 2 中
    "Moon":     (2, 1, 0),   # Moon 主 3 吉/中
    "Mars":     (1, 2, 0),   # Mars 主 1 吉 2 中
    "Rahu":     (0, 1, 2),   # Rahu 主 1 中 2 凶
    "Jupiter":  (3, 0, 0),   # Jupiter 3 個主宿皆吉
    "Saturn":   (1, 2, 0),   # Saturn 主 1 吉 2 中
    "Mercury":  (1, 2, 0),   # Mercury 主 1 吉 2 中
}

# 曜主與宿的守護關係說明 (Graha lord ↔ Nakshatra lord)
GRAHA_DESCRIPTION = {
    "Ketu":     "印度占星中的南交點，象徵解脫、業力。主管 Ashwini、Magha、Mula 三宿，帶有神秘與再生之力。",
    "Venus":    "愛與美之星，主管 Bharani、Purva Phalguni、Purva Ashadha。代表感情、藝術、繁榮，與親密關係密切。",
    "Sun":      "生命力與自我之星，主管 Krittika、Uttara Phalguni、Uttara Ashadha。象徵權威、領導力與靈魂之光。",
    "Moon":     "心意與情感之星，主管 Rohini、Hasta、Shravana。代表情緒、直覺、想象力，與内心世界最强聯結。",
    "Mars":     "能量與行動之星，主管 Mrigashira、Chitra、Dhanishta。象徵勇氣、戰鬥力與决断力。",
    "Rahu":     "印度占星中的北交點，主管 Ardra、Swati、Shatabhisha。代表野心、幻象與世俗成就。",
    "Jupiter":  "智慧與幸運之星，主管 Punarvasu、Vishakha、Purva Bhadrapada。象徵知識、豐盛與靈性成長。",
    "Saturn":   "業力與考驗之星，主管 Pushya、Anuradha、Uttara Bhadrapada。代表紀律、責任與生命的深度考驗。",
    "Mercury":  "溝通與智力之星，主管 Ashlesha、Jyeshtha、Revati。象徵心智、學習、商業技能與邏輯思維。",
}

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
    # 宿曜道 (Japanese 28 Mansions)
    sukkayodo_mansion: str = ""            # 宿曜道宿名
    sukkayodo_mansion_chinese: str = ""    # 中國星名
    sukkayodo_mansion_index: int = -1      # 宿曜道 28 宿索引 (0-27)
    sukkayodo_pada: int = 0                # 宿曜道四足


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
        sukk_idx, sukk_pada = sukkayodo.sukkayodo_info(lon)
        sukk = sukkayodo.SUKKAYODO_MANSION[sukk_idx]

        planets.append(VedicPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], sign_degree=_sign_degree(lon),
            nakshatra=nak[0], nakshatra_chinese=nak[1],
            nakshatra_lord=nak[2], nakshatra_pada=pada,
            retrograde=speed < 0,
            sukkayodo_mansion=sukk[0], sukkayodo_mansion_chinese=sukk[3],
            sukkayodo_mansion_index=sukk_idx, sukkayodo_pada=sukk_pada,
        ))

    # Rahu (Mean North Node)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = RASHIS[idx]
    nak_idx, pada = _nakshatra_info(rahu_lon)
    nak = NAKSHATRAS[nak_idx]
    sukk_idx, sukk_pada = sukkayodo.sukkayodo_info(rahu_lon)
    sukk = sukkayodo.SUKKAYODO_MANSION[sukk_idx]
    planets.append(VedicPlanet(
        name="Rahu (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(rahu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
        sukkayodo_mansion=sukk[0], sukkayodo_mansion_chinese=sukk[3],
        sukkayodo_mansion_index=sukk_idx, sukkayodo_pada=sukk_pada,
    ))

    # Ketu (South Node = Rahu + 180°)
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = RASHIS[idx]
    nak_idx, pada = _nakshatra_info(ketu_lon)
    nak = NAKSHATRAS[nak_idx]
    sukk_idx, sukk_pada = sukkayodo.sukkayodo_info(ketu_lon)
    sukk = sukkayodo.SUKKAYODO_MANSION[sukk_idx]
    planets.append(VedicPlanet(
        name="Ketu (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(ketu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
        sukkayodo_mansion=sukk[0], sukkayodo_mansion_chinese=sukk[3],
        sukkayodo_mansion_index=sukk_idx, sukkayodo_pada=sukk_pada,
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
    col1, col2 = st.columns(2)
    with col1:
        _render_south_indian_grid(chart)
    with col2:
        _render_north_indian_grid(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_nakshatra_graha_relation(chart)


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

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
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
                p_list = rashi_planets[idx]
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(full, "#c8c8c8")};'
                    f'font-weight:bold">{short}</span>'
                    for short, full in p_list
                ) if p_list else '<span style="color:#999">—</span>'
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


def _render_north_indian_grid(chart):
    """渲染北印度式方盤 (North Indian Chart)"""
    st.subheader("📊 北印度排盤 (North Indian Chart)")

    # North Indian chart: signs arranged in a ring clockwise from top
    # Position 0 (top)=Aries, 1=Cancer, 2=Libra, 3=Capricorn
    # Layout: each house cusp is shown on the border
    # Standard North Indian: 12 signs in order clockwise, ascendant highlighted

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name))

    asc_idx = _sign_index(chart.ascendant)

    # 北印度排盤佈局：12宮位以 Ascendant 為起點順時針排列
    # 常見格式：4x3 表格，數字為 rashi index
    # 以 Aries (0) 為頂端，按順時針方向排列
    # ni_order: 從頂端順時針
    ni_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    # 以 Ascendant 所在位置為起點重新排列
    asc_offset = asc_idx
    ni_ring = ni_order[asc_offset:] + ni_order[:asc_offset]

    # 4x3 grid: top row=Aries side, right=col4, bottom=Libra side, left=center
    # 北印度 Standard: 按 K.R. Scheme
    # Row 1: 11(Aquarius), 0(Aries), 1(Taurus), 2(Gemini)
    # Row 2: 10(Capricorn),  center, 3(Cancer)
    # Row 3: 9(Sagittarius), 8(Scorpio), 7(Libra), 6(Virgo)
    # Row 4:  -      5(Leo), 4(Libra)

    ni_grid = [
        [11, 0, 1, 2],
        [10, -1, -1, 3],
        [9, -1, -1, 4],
        [8, 7, 6, 5],
    ]

    # 標記 Lagna 位置
    lagna_style = " background:#3d3010;"
    cell_style = (
        "border:1px solid #444; padding:6px; text-align:center; "
        "vertical-align:top; min-width:110px; font-size:13px;"
    )
    center_style = (
        "border:1px solid #444; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a2a; "
        "color:#e0e0e0;"
    )

    html = '<table style="border-collapse:collapse; margin:auto; width:100%;">'
    for row_idx, row in enumerate(ni_grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    center_content = (
                        f"<b>北印度</b><br/>"
                        f"<small>North Indian</small><br/>"
                        f"{chart.asc_rashi} Lagna"
                    )
                    html += (
                        f'<td colspan="2" rowspan="2" '
                        f'style="{center_style}">{center_content}</td>'
                    )
                    col_idx += 2
                    continue
                elif row_idx == 2 and col_idx == 1:
                    col_idx += 2
                    continue
                else:
                    col_idx += 1
                    continue
            else:
                rashi = RASHIS[idx]
                # 判斷是否為 Lagna (Ascendant) 所在的宫
                is_lagna = (idx == asc_idx)
                style = cell_style + (" background:#3d3010;" if is_lagna else "")
                p_list = rashi_planets[idx]
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(full, "#c8c8c8")};'
                    f'font-weight:bold">{short}</span>'
                    for short, full in p_list
                ) if p_list else '<span style="color:#999">—</span>'
                marker = " 🔺" if is_lagna else ""
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

    # 說明
    st.caption(
        "▲ 🔺 = Lagna (命宮/Ascendant)　　"
        "南印度：宮位固定・行星流動；北印度：宮位固定・宮系統以 Lagna 為起點"
    )


def _render_planet_table(chart):
    st.subheader("🪐 行星位置 (Graha Positions)")
    header = ("| Graha | Rashi | Degree | Lord | "
              "Nakshatra | Pada | Nak Lord | R |")
    sep = ("|:-----:|:-----:|:------:|:----:|"
           ":--------:|:----:|:--------:|:-:|")
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


def _render_nakshatra_graha_relation(chart):
    """渲染 27 宿與七曜關係表 (Nakshatra-Graha Relationship)"""
    st.subheader("🌟 二十七宿與七曜 (27 Nakshatras & 7 Grahas)")

    # 說明
    st.markdown(
        "**二十七宿 (Nakshatra)** 每宿由一顆**曜 (Graha)** 主管，"
        "稱為 **Nakshatra Lord**，共 9 曜（太陽至計都）管 27 宿。\n"
        "每宿分 **四足 (Pada/Quarter)**，各宿之首為該曜所主。"
    )

    # ---- 七曜概述 ----
    st.markdown("### 七曜概述 (Navagraha Overview)")
    cols = st.columns(3)
    graha_keys = list(GRAHA_DESCRIPTION.keys())
    for i, graha in enumerate(graha_keys):
        with cols[i % 3]:
            nature = GRAHA_NAKSHATRA_NATURE.get(graha, (0, 0, 0))
            st.markdown(
                f"**{graha}**\n"
                f"├ 主宿數：3\n"
                f"├ 吉/中/凶：{nature[0]}吉/{nature[1]}中/{nature[2]}凶\n"
                f"└ {GRAHA_DESCRIPTION[graha][:40]}..."
            )

    # ---- 七曜主管宿列表 ----
    st.markdown("### 七曜主宿對照 (Graha → Nakshatra)")
    rows = [
        "| 曜 (Graha) | 主宿 Nakshatras | 中文 |",
        "|:-----------|:---------------|:-----|",
    ]
    for graha, naks in GRAHA_NAKSHATRA_MAP.items():
        color = PLANET_COLORS.get(graha + " (" + graha + ")",
                                  PLANET_COLORS.get(f"{graha}", "#c8c8c8"))
        nak_texts = []
        for n in naks:
            # 找中文名
            for prop in NAKSHATRA_PROPERTIES:
                if prop[0] == n:
                    nak_texts.append(f"{n} ({prop[2]})")
                    break
        rows.append(
            f"| **{graha}** | {'、'.join(nak_texts)} | "
            f"{'、'.join([n for n in GRAHA_NAKSHATRA_MAP[graha]])} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # ---- 完整 27 宿列表 ----
    st.markdown("### 二十七宿完整列表 (27 Nakshatras)")
    rows2 = [
        "| # | Nakshatra | 中國星名 | 主曜 Lord | 象徵 Symbol | 神祇 Deity | 特質 Quality |",
        "|:--:|:----------|:---------|:---------|:-----------|:-----------|:------------|",
    ]
    for i, prop in enumerate(NAKSHATRA_PROPERTIES):
        nak_name, chinese, lord_idx = prop[0], prop[2], prop[1]
        symbol, deity, quality = prop[3], prop[4], prop[5]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        color = PLANET_COLORS.get(lord_name, "#c8c8c8")
        rows2.append(
            f"| {i+1} | "
            f'<span style="color:{color};font-weight:bold">{nak_name}</span> | '
            f"{chinese} | {lord_name} | {symbol} | {deity} | {quality} |"
        )
    st.markdown("\n".join(rows2), unsafe_allow_html=True)

