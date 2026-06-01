"""
Decanic Astrology 計算模組 (Decanic Astrology Computation Module)

基於古埃及三十六十度區間 (36 Decans) 系統，結合迦勒底行星序 (Chaldean Order)、
三分主星 (Triplicity Rulers)、金色黎明塔羅對應 (Golden Dawn Tarot Correspondences)
以及本質尊貴 (Essential Dignities) 技法，提供出生圖 Decan 分析的純計算結果。

This module is **compute-only**: it does not import or call Streamlit, so it can
be used in headless contexts (FastAPI, tests, scripts).

Sources: Neugebauer & Parker "Egyptian Astronomical Texts",
         Dendera zodiac ceiling, Ptolemy "Tetrabiblos",
         Golden Dawn tradition.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

import swisseph as swe

from .decans_data import (
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
