"""
西洋占星排盤模組 (Western Astrology Chart Module)

使用 pyswisseph 以回歸黃道 (tropical zodiac) 或恆星黃道 (sidereal zodiac) 計算行星位置，
包含天王星、海王星、冥王星等現代行星，並渲染西洋占星排盤。

本模組整合占星四書（Ptolemy Tetrabiblos、Firmicus Mathesis、
Lilly Christian Astrology）所包含的古典占星技法：
- 本質廟旺落陷（Essential Dignities & Debilities）
- 行星喜樂宮（Planetary Joy）
- 阿拉伯點（Arabic Parts / Lots）
- 恆星相位（Fixed Star Conjunctions）
- 命度主星（Chart Ruler）
- 日夜盤判定（Day/Night Sect）
- 恆星黃道選項（Sidereal Zodiac with Lahiri Ayanamsa）
"""

import swisseph as swe
from core.cache import cache_data, cache_resource
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
# 古典占星常數（占星四書技法）
# ============================================================

# Essential Dignities — sign_index (0=Aries..11=Pisces)
# Each sign has domicile ruler, exaltation, fall, and detriment
# Detriment = opposite sign of domicile ((idx + 6) % 12)
# Fall = opposite sign of exaltation ((idx + 6) % 12)
CLASSICAL_DIGNITIES = {
    0:  {"domicile": "Mars ♂",    "exaltation": "Sun ☉"},
    1:  {"domicile": "Venus ♀",   "exaltation": "Moon ☽"},
    2:  {"domicile": "Mercury ☿", "exaltation": None},
    3:  {"domicile": "Moon ☽",    "exaltation": "Jupiter ♃"},
    4:  {"domicile": "Sun ☉",     "exaltation": "Pluto ♇"},
    5:  {"domicile": "Mercury ☿", "exaltation": "Mercury ☿"},
    6:  {"domicile": "Venus ♀",   "exaltation": "Saturn ♄"},
    7:  {"domicile": "Mars ♂",    "exaltation": "Uranus ♅"},
    8:  {"domicile": "Jupiter ♃", "exaltation": "Neptune ♆"},
    9:  {"domicile": "Saturn ♄",  "exaltation": "Mars ♂"},
    10: {"domicile": "Saturn ♄",  "exaltation": None},
    11: {"domicile": "Jupiter ♃", "exaltation": "Venus ♀"},
}

# Planetary Joy — each planet rejoices in a particular house (Lilly tradition)
# Sun joy 9th, Moon joy 4th, Mercury joy 1st, Venus joy 5th,
# Mars joy 6th, Jupiter joy 11th, Saturn joy 12th
PLANETAL_JOY = {
    "Sun ☉": 9,
    "Moon ☽": 4,
    "Mercury ☿": 1,
    "Venus ♀": 5,
    "Mars ♂": 6,
    "Jupiter ♃": 11,
    "Saturn ♄": 12,
}

# Dignity scores for weighting (Lilly/Ptolemy system)
DIGNITY_SCORES = {
    "domicile": 5,
    "exaltation": 4,
    "triplicity_day": 3,
    "triplicity_night": 3,
    "term": 2,
    "face": 1,
    "detriment": -5,
    "fall": -4,
}

# Fixed Stars — name, SwissEph star key, Chinese name, magnitude, classical meaning
# Orb is the conjunction orb in degrees; swe.fixstar2() used for positions
FIXED_STARS = [
    ("Aldebaran",   "Aldebaran",    "畢宿五",   0.85, "勇氣、好戰、軍事事務"),
    ("Regulus",     "Regulus",      "軒轅十四", 1.35, "王權、領袖、吉祥"),
    ("Antares",     "Antares",      "心宿二",   0.96, "膽識、軍事榮譽、火災危險"),
    ("Spica",       "Spica",        "角宿一",   0.97, "財富、創造天賦、學術之愛"),
    ("Pollux",      "Pollux",       "北河三",   1.14, "勇氣、保護、旅行者"),
    ("Procyon",     "Procyon",      "南河三",   0.34, "名聲、活力、變革"),
    ("Sirius",      "Sirius",       "天狼星",   -1.46, "榮耀、財富、高貴"),
    ("Castor",      "Castor",       "北河二",   1.93, "才智、技藝、旅行"),
    ("Vega",        "Vega",         "織女星",   0.03, "藝術、純潔、幸運"),
    ("Fomalhaut",   "Fomalhaut",    "北落師門", 1.16, "獨立、理想、變革"),
    ("Deneb",       "Deneb",        "天津四",   1.25, "飛行、創造力、皇室"),
    ("Altair",      "Altair",       "牛郎星",   0.76, "行動力、勇氣、軍事"),
    ("Betelgeuse",  "Betelgeuse",   "參宿四",   0.50, "野心、創造力、巨變"),
    ("Rigel",       "Rigel",        "參宿七",   0.13, "名聲、財富、技藝"),
    ("Capella",     "Capella",      "五車五",   0.08, "成功、財富、道德"),
    ("Proxima",     "Proxima Cen",  "比鄰星",   11.05, "親密關係、隱藏力量"),
    ("Alcyone",     "Alcyone",      "昴宿六",   2.87, "豐盛、領導力、神秘"),
    ("Algol",       "Algol",        "大陵五",   2.12, "危險、暴力、死亡"),
    ("Alphard",     "Alphard",      "星宿一",   2.00, "孤獨、秘密、旅行"),
    ("Bellatrix",   "Bellatrix",    "參宿三",   1.64, "勇敢、戰士、演說家"),
]

# Fixed star orbs (degrees) — custom per star brightness
FIXED_STAR_ORBS = {
    "Aldebaran": 1.0, "Regulus": 1.0, "Antares": 1.0, "Spica": 1.0,
    "Pollux": 1.0, "Procyon": 1.0, "Sirius": 1.0, "Castor": 1.0,
    "Vega": 1.0, "Fomalhaut": 1.0, "Deneb": 1.0, "Altair": 1.0,
    "Betelgeuse": 1.0, "Rigel": 1.0, "Capella": 1.0, "Alcyone": 1.0,
    "Algol": 0.5, "Alphard": 1.0, "Bellatrix": 1.0,
}

# Arabic Parts for Western module — (english, chinese, day_formula, night_formula)
# Formula: Part = ASC + A - B (normalize 0-360)
WESTERN_ARABIC_PARTS = [
    ("Lot of Fortune",  "幸運點",  ("Moon ☽", "Sun ☉"), ("Sun ☉", "Moon ☽")),
    ("Lot of Spirit",   "精神點",  ("Sun ☉",  "Moon ☽"), ("Moon ☽", "Sun ☉")),
    ("Lot of Marriage", "婚姻點",  ("Venus ♀", "Saturn ♄"), ("Saturn ♄", "Venus ♀")),
    ("Lot of Children", "子女點",  ("Jupiter ♃", "Moon ☽"), ("Moon ☽", "Jupiter ♃")),
    ("Lot of Mother",   "母親點",  ("Moon ☽", "Saturn ♄"), ("Saturn ♄", "Moon ☽")),
    ("Lot of Father",   "父親點",  ("Sun ☉",  "Saturn ♄"), ("Saturn ♄", "Sun ☉")),
]

# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class WesternPlanet:
    """西洋占星行星位置"""
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
    essential_dignity: str = "—"
    joy_status: str = "—"
    fixed_star_conjunctions: list = field(default_factory=list)


@dataclass
class WesternHouse:
    """西洋占星宮位"""
    number: int
    cusp: float
    sign: str
    sign_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class ArabicPart:
    """阿拉伯點"""
    english_name: str
    chinese_name: str
    longitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    house: int = 0


@dataclass
class FixedStarConjunction:
    """恆星相位"""
    star_name: str
    star_name_cn: str
    star_longitude: float
    planet_name: str
    orb: float
    meaning: str


@dataclass
class WesternChart:
    """西洋占星排盤"""
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
    is_day_chart: bool = False
    chart_ruler: str = "—"
    chart_ruler_dignity: str = "—"
    lot_of_fortune: float = 0.0
    arabic_parts: list = field(default_factory=list)
    fixed_star_conjunctions: list = field(default_factory=list)
    sidereal_mode: bool = False
    ayanamsa: float = 0.0


# ============================================================
# 輔助函數 (Helper Functions)
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


def _get_essential_dignity(planet_name, sign_idx):
    """計算本質廟旺落陷"""
    short = planet_name.split(" ")[0]
    dig = CLASSICAL_DIGNITIES[sign_idx]
    # Domicile
    if dig["domicile"] and short == dig["domicile"].split(" ")[0]:
        return "入廟 (Domicile)"
    # Exaltation
    if dig["exaltation"] and short == dig["exaltation"].split(" ")[0]:
        return "入旺 (Exaltation)"
    # Detriment: opposite of domicile
    opp = (sign_idx + 6) % 12
    if CLASSICAL_DIGNITIES[opp]["domicile"] and short == CLASSICAL_DIGNITIES[opp]["domicile"].split(" ")[0]:
        return "落陷 (Detriment)"
    # Fall: opposite of exaltation
    if dig["exaltation"]:
        opp_ex = (sign_idx + 6) % 12
        if CLASSICAL_DIGNITIES[opp_ex]["exaltation"] and short == CLASSICAL_DIGNITIES[opp_ex]["exaltation"].split(" ")[0]:
            return "入弱 (Fall)"
    return "—"


def _get_joy_status(planet_name, house):
    """計算行星喜樂宮狀態"""
    short = planet_name.split(" ")[0]
    for pname, joy_house in PLANETAL_JOY.items():
        if pname.split(" ")[0] == short and joy_house == house:
            return "喜樂 (Joy)"
    return "—"


def _is_day_chart(sun_lon, cusps):
    """判斷日夜盤：Sun 在 7-12 宮 = 日盤"""
    sun_house = _find_house(sun_lon, cusps)
    return sun_house >= 7


def _get_chart_ruler(asc_idx, planets):
    """找命度主星及其 dignity"""
    ruler_name = CLASSICAL_DIGNITIES[asc_idx]["domicile"]
    if ruler_name:
        short = ruler_name.split(" ")[0]
        for p in planets:
            if p.name.split(" ")[0] == short:
                dignity = _get_essential_dignity(p.name, _sign_index(p.longitude))
                return p.name, dignity
    return "—", "—"


def _compute_arabic_part(ascendant, planet_lons, key_a, key_b, is_day):
    """計算單個阿拉伯點"""
    lon_a = planet_lons.get(key_a, 0.0)
    lon_b = planet_lons.get(key_b, 0.0)
    if is_day:
        lon = _normalize(ascendant + lon_a - lon_b)
    else:
        lon = _normalize(ascendant + lon_b - lon_a)
    return lon


def _compute_arabic_parts(ascendant, sun_lon, moon_lon, saturn_lon, jupiter_lon,
                          venus_lon, mercury_lon, is_day, cusps):
    """計算所有阿拉伯點"""
    planet_lons = {
        "Sun ☉": sun_lon,
        "Moon ☽": moon_lon,
        "Saturn ♄": saturn_lon,
        "Jupiter ♃": jupiter_lon,
        "Venus ♀": venus_lon,
        "Mercury ☿": mercury_lon,
    }
    parts = []
    for english, chinese, day_f, night_f in WESTERN_ARABIC_PARTS:
        key_a, key_b = day_f if is_day else night_f
        lon = _compute_arabic_part(ascendant, planet_lons, key_a, key_b, is_day)
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]
        house = _find_house(lon, cusps)
        parts.append(ArabicPart(
            english_name=english,
            chinese_name=chinese,
            longitude=lon,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(lon),
            house=house,
        ))
    return parts


def _compute_fixed_star_conjunctions(planets, jd):
    """計算恆星相位（合相）

    優化：先一次性計算所有恆星位置，再與行星比對，
    避免對每顆行星重複呼叫 swe.fixstar2（從 O(planets×stars) 降為 O(stars) 次 swe 呼叫）。
    """
    results = []
    swe.set_ephe_path("")

    # Pre-compute all fixed star positions once
    star_positions = []
    for star_key, star_name, star_cn, _, meaning in FIXED_STARS:
        try:
            star_res, _ = swe.fixstar2(star_name, jd, swe.FLG_SWIEPH)
            star_lon = _normalize(star_res[0])
            orb = FIXED_STAR_ORBS.get(star_key, 1.0)
            star_positions.append((star_name, star_cn, star_lon, orb, meaning))
        except Exception:
            continue

    # Compare each planet against pre-computed star positions
    for p in planets:
        p_lon = _normalize(p.longitude)
        for star_name, star_cn, star_lon, orb, meaning in star_positions:
            diff = abs(p_lon - star_lon)
            if diff > 180:
                diff = 360 - diff
            if diff <= orb:
                results.append(FixedStarConjunction(
                    star_name=star_name,
                    star_name_cn=star_cn,
                    star_longitude=star_lon,
                    planet_name=p.name,
                    orb=round(diff, 2),
                    meaning=meaning,
                ))
    return results


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

@cache_data(ttl=3600, show_spinner=False)
def compute_western_chart(year, month, day, hour, minute, timezone,
                          latitude, longitude, location_name="",
                          sidereal=False):
    """計算西洋占星排盤

    Args:
        sidereal: 若為 True，使用恆星黃道（Lahiri Ayanamsa）
    """
    swe.set_ephe_path("")

    # Sidereal mode
    sidereal_flag = 0
    if sidereal:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        sidereal_flag = swe.FLG_SIDEREAL

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    if sidereal:
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", sidereal_flag)
        ayanamsa = swe.get_ayanamsa_ut(jd)
    else:
        cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
        ayanamsa = 0.0
    ascendant = _normalize(ascmc[0])
    midheaven = _normalize(ascmc[1])

    planet_lons = {}
    planets = []
    for name, planet_id in WESTERN_PLANETS.items():
        if sidereal:
            result, _ = swe.calc_ut(jd, planet_id, sidereal_flag)
        else:
            result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]

        planet_lons[name] = lon
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
            essential_dignity=_get_essential_dignity(name, idx),
        )
        planets.append(pos)

    # North Node (Rahu)
    if sidereal:
        rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE, sidereal_flag)
    else:
        rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = _normalize(rahu[0])
    idx = _sign_index(rahu_lon)
    sign_info = ZODIAC_SIGNS[idx]
    planet_lons["North Node ☊"] = rahu_lon
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
        p.joy_status = _get_joy_status(p.name, h)
        houses[h - 1].planets.append(p.name)

    asc_idx = _sign_index(ascendant)
    mc_idx = _sign_index(midheaven)

    sun_lon = planet_lons.get("Sun ☉", 0.0)
    moon_lon = planet_lons.get("Moon ☽", 0.0)
    is_day = _is_day_chart(sun_lon, cusps)
    chart_ruler, chart_ruler_dignity = _get_chart_ruler(asc_idx, planets)
    lot_of_fortune = _normalize(ascendant + moon_lon - sun_lon) if is_day \
        else _normalize(ascendant + sun_lon - moon_lon)

    # Arabic Parts
    arabic_parts = _compute_arabic_parts(
        ascendant, sun_lon, moon_lon,
        planet_lons.get("Saturn ♄", 0.0),
        planet_lons.get("Jupiter ♃", 0.0),
        planet_lons.get("Venus ♀", 0.0),
        planet_lons.get("Mercury ☿", 0.0),
        is_day, cusps,
    )

    # Fixed Star Conjunctions
    fixed_star_conjunctions = _compute_fixed_star_conjunctions(planets, jd)

    return WesternChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        planets=planets, houses=houses,
        ascendant=ascendant, midheaven=midheaven,
        asc_sign=ZODIAC_SIGNS[asc_idx][0],
        mc_sign=ZODIAC_SIGNS[mc_idx][0],
        is_day_chart=is_day,
        chart_ruler=chart_ruler,
        chart_ruler_dignity=chart_ruler_dignity,
        lot_of_fortune=lot_of_fortune,
        arabic_parts=arabic_parts,
        fixed_star_conjunctions=fixed_star_conjunctions,
        sidereal_mode=sidereal,
        ayanamsa=ayanamsa,
    )


# ============================================================
# 向後相容 shim (Backward-compat shim for render_western_chart)
# ============================================================
#
# Streamlit 渲染程式碼已搬至 ui/handlers/tab_western/render.py。
# 為避免破壞既有 caller（``from astro.western.western import
# render_western_chart``），本檔仍 re-export 該名稱並以 lazy 方式
# 轉發到新位置。該函式只會在 streamlit 已啟動的環境下被呼叫,
# 不會在 compute 流程中觸碰 streamlit。
# ============================================================


def render_western_chart(chart, after_chart_hook=None, gender=None):
    """[deprecated] 渲染西洋占星排盤; 已搬至 ui/handlers/tab_western/render.py"""
    from ui.handlers.tab_western.render import render_streamlit as _render
    return _render(chart, after_chart_hook=after_chart_hook, gender=gender)
