"""
阿拉伯占星排盤模組 (Arabic Astrology Chart Module)

阿拉伯占星以中世紀伊斯蘭黃金時代天文學家的成果為基礎，其最具代表性的技法
為「阿拉伯點」(Arabic Parts / Lots)——透過上升點與行星經度的加減運算推導
出各生活主題的敏感度數。本模組同時提供日夜盤判斷、行星廟旺落陷（Essential
Dignities）以及回歸黃道（Tropical Zodiac）Placidus 宮位制排盤。
"""

import swisseph as swe
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

# Planets used in Arabic astrology (tropical, same IDs as Western)
ARABIC_PLANETS = {
    "Sun ☉ (太陽)": swe.SUN,
    "Moon ☽ (月亮)": swe.MOON,
    "Mercury ☿ (水星)": swe.MERCURY,
    "Venus ♀ (金星)": swe.VENUS,
    "Mars ♂ (火星)": swe.MARS,
    "Jupiter ♃ (木星)": swe.JUPITER,
    "Saturn ♄ (土星)": swe.SATURN,
}

# 12 Zodiac signs (tropical)
# (English name, glyph, Chinese name, element, Arabic name)
ZODIAC_SIGNS = [
    ("Aries", "♈", "白羊座", "Fire 火", "الحمل (Al-Ḥamal)"),
    ("Taurus", "♉", "金牛座", "Earth 土", "الثور (Al-Thawr)"),
    ("Gemini", "♊", "雙子座", "Air 風", "الجوزاء (Al-Jawzāʾ)"),
    ("Cancer", "♋", "巨蟹座", "Water 水", "السرطان (Al-Saraṭān)"),
    ("Leo", "♌", "獅子座", "Fire 火", "الأسد (Al-Asad)"),
    ("Virgo", "♍", "處女座", "Earth 土", "السنبلة (Al-Sunbula)"),
    ("Libra", "♎", "天秤座", "Air 風", "الميزان (Al-Mīzān)"),
    ("Scorpio", "♏", "天蠍座", "Water 水", "العقرب (Al-ʿAqrab)"),
    ("Sagittarius", "♐", "射手座", "Fire 火", "القوس (Al-Qaws)"),
    ("Capricorn", "♑", "摩羯座", "Earth 土", "الجدي (Al-Jady)"),
    ("Aquarius", "♒", "水瓶座", "Air 風", "الدلو (Al-Dalw)"),
    ("Pisces", "♓", "雙魚座", "Water 水", "الحوت (Al-Ḥūt)"),
]

# Essential Dignities – Domicile & Exaltation
# sign_index -> { "domicile": planet(s), "exaltation": planet or None }
ESSENTIAL_DIGNITIES = {
    0:  {"domicile": "Mars ♂",    "exaltation": "Sun ☉"},       # Aries
    1:  {"domicile": "Venus ♀",   "exaltation": "Moon ☽"},      # Taurus
    2:  {"domicile": "Mercury ☿", "exaltation": None},           # Gemini
    3:  {"domicile": "Moon ☽",    "exaltation": "Jupiter ♃"},    # Cancer
    4:  {"domicile": "Sun ☉",     "exaltation": None},           # Leo
    5:  {"domicile": "Mercury ☿", "exaltation": "Mercury ☿"},    # Virgo
    6:  {"domicile": "Venus ♀",   "exaltation": "Saturn ♄"},     # Libra
    7:  {"domicile": "Mars ♂",    "exaltation": None},           # Scorpio
    8:  {"domicile": "Jupiter ♃", "exaltation": None},           # Sagittarius
    9:  {"domicile": "Saturn ♄",  "exaltation": "Mars ♂"},       # Capricorn
    10: {"domicile": "Saturn ♄",  "exaltation": None},           # Aquarius
    11: {"domicile": "Jupiter ♃", "exaltation": "Venus ♀"},      # Pisces
}

# Arabic Parts definitions
# Each entry: (Arabic name, Chinese name, English name,
#              day_formula: (A, B), night_formula: (A, B))
# Formula: Part = ASC + A - B  (day) / Part = ASC + A - B (night)
# A and B are planet keys referencing ARABIC_PLANETS or special values
ARABIC_PARTS = [
    ("سهم السعادة",  "幸運點",  "Part of Fortune",
     ("Moon ☽ (月亮)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Moon ☽ (月亮)")),
    ("سهم الروح",    "精神點",  "Part of Spirit",
     ("Sun ☉ (太陽)", "Moon ☽ (月亮)"),
     ("Moon ☽ (月亮)", "Sun ☉ (太陽)")),
    ("سهم الحب",     "愛情點",  "Part of Love (Eros)",
     ("Venus ♀ (金星)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Venus ♀ (金星)")),
    ("سهم الشجاعة",  "勇氣點",  "Part of Courage",
     ("Mars ♂ (火星)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Mars ♂ (火星)")),
    ("سهم النصر",    "勝利點",  "Part of Victory",
     ("Jupiter ♃ (木星)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Jupiter ♃ (木星)")),
    ("سهم القهر",    "宿命點",  "Part of Fate (Nemesis)",
     ("Saturn ♄ (土星)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Saturn ♄ (土星)")),
    ("سهم التجارة",  "商業點",  "Part of Commerce",
     ("Mercury ☿ (水星)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Mercury ☿ (水星)")),
    ("سهم الأم",     "母親點",  "Part of Mother",
     ("Moon ☽ (月亮)", "Venus ♀ (金星)"),
     ("Venus ♀ (金星)", "Moon ☽ (月亮)")),
    ("سهم الأب",     "父親點",  "Part of Father",
     ("Saturn ♄ (土星)", "Sun ☉ (太陽)"),
     ("Sun ☉ (太陽)", "Saturn ♄ (土星)")),
    ("سهم الإخوة",   "兄弟點",  "Part of Brethren",
     ("Jupiter ♃ (木星)", "Saturn ♄ (土星)"),
     ("Saturn ♄ (土星)", "Jupiter ♃ (木星)")),
    ("سهم الأولاد",  "子女點",  "Part of Children",
     ("Jupiter ♃ (木星)", "Moon ☽ (月亮)"),
     ("Moon ☽ (月亮)", "Jupiter ♃ (木星)")),
    ("سهم المرض",    "疾病點",  "Part of Sickness",
     ("Mars ♂ (火星)", "Saturn ♄ (土星)"),
     ("Saturn ♄ (土星)", "Mars ♂ (火星)")),
    ("سهم الزواج",   "婚姻點",  "Part of Marriage",
     ("Venus ♀ (金星)", "Saturn ♄ (土星)"),
     ("Saturn ♄ (土星)", "Venus ♀ (金星)")),
    ("سهم العبيد",   "奴僕點",  "Part of Servants",
     ("Mercury ☿ (水星)", "Moon ☽ (月亮)"),
     ("Moon ☽ (月亮)", "Mercury ☿ (水星)")),
    ("سهم السفر",    "旅行點",  "Part of Travel",
     ("Saturn ♄ (土星)", "Moon ☽ (月亮)"),
     ("Moon ☽ (月亮)", "Saturn ♄ (土星)")),
]

PLANET_COLORS = {
    "Sun ☉ (太陽)": "#FFD700",
    "Moon ☽ (月亮)": "#C0C0C0",
    "Mercury ☿ (水星)": "#FFA500",
    "Venus ♀ (金星)": "#228B22",
    "Mars ♂ (火星)": "#DC143C",
    "Jupiter ♃ (木星)": "#4169E1",
    "Saturn ♄ (土星)": "#000080",
    "North Node ☊ (北交點)": "#556B2F",
}

# Classical aspects used in Arabic astrology
# (English name, Arabic name, Chinese name, angle, orb)
ASPECT_TYPES = [
    ("Conjunction", "اقتران", "合 (0°)", 0, 8),
    ("Opposition", "مقابلة", "沖 (180°)", 180, 8),
    ("Trine", "تثليث", "三合 (120°)", 120, 6),
    ("Square", "تربيع", "刑 (90°)", 90, 6),
    ("Sextile", "تسديس", "六合 (60°)", 60, 4),
]


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ArabicPlanet:
    """Arabic astrology planet position with essential dignities"""
    name: str
    longitude: float
    latitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    element: str
    sign_degree: float
    retrograde: bool
    arabic_sign: str
    dignity: str           # Essential dignity status
    house: int = 0


@dataclass
class ArabicPart:
    """An Arabic Part / Lot"""
    arabic_name: str
    chinese_name: str
    english_name: str
    longitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    house: int = 0


@dataclass
class ArabicHouse:
    """Arabic house data"""
    number: int
    cusp: float
    sign: str
    sign_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class ArabicAspect:
    """An aspect between two planets"""
    planet1: str
    planet2: str
    aspect_name: str
    arabic_name: str
    chinese_name: str
    angle: float
    orb: float


@dataclass
class ArabicChart:
    """Arabic astrology chart"""
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
    arabic_parts: list
    aspects: list
    ascendant: float
    midheaven: float
    asc_sign: str
    mc_sign: str
    is_day_chart: bool


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


def _get_dignity(planet_name, sign_idx):
    """Determine essential dignity of a planet in a given sign."""
    short_name = planet_name.split(" (")[0]
    dignities = ESSENTIAL_DIGNITIES[sign_idx]

    if dignities["domicile"] and short_name == dignities["domicile"].split(" (")[0]:
        return "入廟 (Domicile)"
    if dignities["exaltation"] and short_name == dignities["exaltation"].split(" (")[0]:
        return "入旺 (Exaltation)"

    # Detriment: opposite sign of domicile
    opp_idx = (sign_idx + 6) % 12
    opp_dig = ESSENTIAL_DIGNITIES[opp_idx]
    if opp_dig["domicile"] and short_name == opp_dig["domicile"].split(" (")[0]:
        return "落陷 (Detriment)"

    # Fall: opposite sign of exaltation
    if opp_dig["exaltation"] and short_name == opp_dig["exaltation"].split(" (")[0]:
        return "入弱 (Fall)"

    return "—"


def _is_day_chart(sun_lon, cusps):
    """Determine if this is a day chart (Sun above horizon)."""
    sun_house = _find_house(sun_lon, cusps)
    return sun_house >= 7


def _compute_aspects(planets):
    """Compute classical aspects between the 7 classical planets."""
    aspects = []
    classical = [p for p in planets if "North Node" not in p.name]
    for i in range(len(classical)):
        for j in range(i + 1, len(classical)):
            p1, p2 = classical[i], classical[j]
            diff = abs(p1.longitude - p2.longitude)
            if diff > 180:
                diff = 360 - diff
            for eng, ar, cn, angle, orb in ASPECT_TYPES:
                if abs(diff - angle) <= orb:
                    aspects.append(ArabicAspect(
                        planet1=p1.name,
                        planet2=p2.name,
                        aspect_name=eng,
                        arabic_name=ar,
                        chinese_name=cn,
                        angle=diff,
                        orb=round(abs(diff - angle), 2),
                    ))
                    break
    return aspects


def compute_arabic_chart(year, month, day, hour, minute, timezone,
                         latitude, longitude, location_name=""):
    """計算阿拉伯占星排盤 (Tropical Zodiac, Placidus Houses)"""
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    ascendant = ascmc[0]
    midheaven = ascmc[1]

    # Calculate planets
    planet_lons = {}  # store planet longitudes for Arabic Parts calculation
    planets = []
    for name, planet_id in ARABIC_PLANETS.items():
        result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]

        planet_lons[name] = lon

        planets.append(ArabicPlanet(
            name=name,
            longitude=lon,
            latitude=lat,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            element=sign_info[3],
            sign_degree=_sign_degree(lon),
            retrograde=speed < 0,
            arabic_sign=sign_info[4],
            dignity=_get_dignity(name, idx),
        ))

    # North Node (Rahu)
    rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = _normalize(rahu[0])
    idx = _sign_index(rahu_lon)
    sign_info = ZODIAC_SIGNS[idx]
    node_name = "North Node ☊ (北交點)"
    planet_lons[node_name] = rahu_lon
    planets.append(ArabicPlanet(
        name=node_name,
        longitude=rahu_lon,
        latitude=rahu[1],
        sign=sign_info[0],
        sign_glyph=sign_info[1],
        sign_chinese=sign_info[2],
        element=sign_info[3],
        sign_degree=_sign_degree(rahu_lon),
        retrograde=False,
        arabic_sign=sign_info[4],
        dignity="—",
    ))

    # Day / Night determination
    sun_lon = planet_lons["Sun ☉ (太陽)"]
    is_day = _is_day_chart(sun_lon, cusps)

    # Calculate Arabic Parts
    arabic_parts = []
    for part_def in ARABIC_PARTS:
        ar_name, cn_name, en_name, day_formula, night_formula = part_def
        formula = day_formula if is_day else night_formula
        a_lon = planet_lons[formula[0]]
        b_lon = planet_lons[formula[1]]
        part_lon = _normalize(ascendant + a_lon - b_lon)
        idx = _sign_index(part_lon)
        sign_info = ZODIAC_SIGNS[idx]
        arabic_parts.append(ArabicPart(
            arabic_name=ar_name,
            chinese_name=cn_name,
            english_name=en_name,
            longitude=part_lon,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(part_lon),
        ))

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        sign_info = ZODIAC_SIGNS[idx]
        houses.append(ArabicHouse(
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

    for part in arabic_parts:
        h = _find_house(part.longitude, cusps)
        part.house = h

    asc_idx = _sign_index(ascendant)
    mc_idx = _sign_index(midheaven)

    # Compute classical aspects
    aspects = _compute_aspects(planets)

    return ArabicChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        planets=planets, houses=houses, arabic_parts=arabic_parts,
        aspects=aspects,
        ascendant=ascendant, midheaven=midheaven,
        asc_sign=ZODIAC_SIGNS[asc_idx][0],
        mc_sign=ZODIAC_SIGNS[mc_idx][0],
        is_day_chart=is_day,
    )


# ============================================================
# Picatrix 擴充函數 (Picatrix Extension Functions)
# 資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
# ============================================================

def get_planetary_hours(
    year: int,
    month: int,
    day: int,
    timezone: float,
    latitude: float,
    longitude: float,
):
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    計算指定日期和地點的 24 行星時（12 日間時 + 12 夜間時）。

    整合阿拉伯占星的 Arabic Parts、Essential Dignities 與 Sect 概念。

    Args:
        year: 年
        month: 月
        day: 日
        timezone: 時區偏移（UTC+N）
        latitude: 緯度
        longitude: 經度

    Returns:
        PlanetaryHoursResult: 行星時計算結果
    """
    from astro.arabic.picatrix_mansions import get_planetary_hours as _get_hours
    return _get_hours(year, month, day, timezone, latitude, longitude)


def get_picatrix_talisman_recommendation(intent: str):
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    根據使用者意圖推薦 Picatrix 護符配方。

    整合現有的 Arabic Parts、Essential Dignities、Sect 技法。

    Args:
        intent: 意圖關鍵字（中英文均可），支援：
            "love"/"愛情", "wealth"/"財富", "health"/"治病",
            "travel"/"旅行", "protection"/"保護",
            "knowledge"/"知識", "power"/"權力", "agriculture"/"農業"

    Returns:
        TalismanRecommendation | None: 護符推薦，若意圖不識別則回傳 None
    """
    from astro.arabic.picatrix_mansions import get_picatrix_talisman_recommendation as _get_rec
    return _get_rec(intent)
