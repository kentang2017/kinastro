"""Thai Duang Chata (ดวงชะตา) phase-1 core calculation.

This module is intentionally Streamlit-free and focuses on pure computation:
- 9 graha (Sun..Saturn + Rahu/Ketu) sidereal positions via pyswisseph
- Thai-style fortune number (生肖數字 + month + day, subtract 10 repeatedly)
- 12 Bhavas with selectable house system (whole sign / thai_traditional / placidus)
- Simple annual trend marker

Note:
This file is created under ``astro/thai/`` as stage-1 groundwork.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Literal, Optional

import swisseph as swe

HouseSystem = Literal["whole_sign", "thai_traditional", "placidus"]


THAI_GRAHA_IDS: Dict[str, int] = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
}

PLANET_SYMBOLS: Dict[str, str] = {
    "sun": "☉",
    "moon": "☽",
    "mars": "♂",
    "mercury": "☿",
    "jupiter": "♃",
    "venus": "♀",
    "saturn": "♄",
    "rahu": "☊",
    "ketu": "☋",
}

PLANET_COLORS: Dict[str, str] = {
    "sun": "#ff9f1c",
    "moon": "#d8e2f2",
    "mars": "#ef476f",
    "mercury": "#5fa8d3",
    "jupiter": "#ffd166",
    "venus": "#ff7eb6",
    "saturn": "#8d6a9f",
    "rahu": "#9b5de5",
    "ketu": "#4361ee",
}

SIGNS = [
    {"en": "Aries", "zh": "白羊", "th": "เมษ", "glyph": "♈", "ruler": "mars"},
    {"en": "Taurus", "zh": "金牛", "th": "พฤษภ", "glyph": "♉", "ruler": "venus"},
    {"en": "Gemini", "zh": "雙子", "th": "เมถุน", "glyph": "♊", "ruler": "mercury"},
    {"en": "Cancer", "zh": "巨蟹", "th": "กรกฎ", "glyph": "♋", "ruler": "moon"},
    {"en": "Leo", "zh": "獅子", "th": "สิงห์", "glyph": "♌", "ruler": "sun"},
    {"en": "Virgo", "zh": "處女", "th": "กันย์", "glyph": "♍", "ruler": "mercury"},
    {"en": "Libra", "zh": "天秤", "th": "ตุลย์", "glyph": "♎", "ruler": "venus"},
    {"en": "Scorpio", "zh": "天蠍", "th": "พิจิก", "glyph": "♏", "ruler": "mars"},
    {"en": "Sagittarius", "zh": "射手", "th": "ธนู", "glyph": "♐", "ruler": "jupiter"},
    {"en": "Capricorn", "zh": "摩羯", "th": "มกร", "glyph": "♑", "ruler": "saturn"},
    {"en": "Aquarius", "zh": "水瓶", "th": "กุมภ์", "glyph": "♒", "ruler": "saturn"},
    {"en": "Pisces", "zh": "雙魚", "th": "มีน", "glyph": "♓", "ruler": "jupiter"},
]

THAI_ZODIAC_ANIMALS = [
    {"number": 1, "en": "Rat", "zh": "鼠", "th": "ชวด"},
    {"number": 2, "en": "Ox", "zh": "牛", "th": "ฉลู"},
    {"number": 3, "en": "Tiger", "zh": "虎", "th": "ขาล"},
    {"number": 4, "en": "Rabbit", "zh": "兔", "th": "เถาะ"},
    {"number": 5, "en": "Dragon", "zh": "龍", "th": "มะโรง"},
    {"number": 6, "en": "Snake", "zh": "蛇", "th": "มะเส็ง"},
    {"number": 7, "en": "Horse", "zh": "馬", "th": "มะเมีย"},
    {"number": 8, "en": "Goat", "zh": "羊", "th": "มะแม"},
    {"number": 9, "en": "Monkey", "zh": "猴", "th": "วอก"},
    {"number": 10, "en": "Rooster", "zh": "雞", "th": "ระกา"},
    {"number": 11, "en": "Dog", "zh": "狗", "th": "จอ"},
    {"number": 12, "en": "Pig", "zh": "豬", "th": "กุน"},
]

BHAVA_MEANINGS = {
    1: {"en": "Self & vitality", "zh": "自我與體能", "th": "ตัวตนและพลังชีวิต"},
    2: {"en": "Wealth & speech", "zh": "財富與口才", "th": "ทรัพย์สินและวาจา"},
    3: {"en": "Courage & skills", "zh": "勇氣與技能", "th": "ความกล้าและทักษะ"},
    4: {"en": "Home & roots", "zh": "家庭與根基", "th": "บ้านและรากฐาน"},
    5: {"en": "Creativity & children", "zh": "創造與子女", "th": "ความคิดสร้างสรรค์และบุตร"},
    6: {"en": "Service & obstacles", "zh": "服務與挑戰", "th": "งานรับใช้และอุปสรรค"},
    7: {"en": "Partnership", "zh": "伴侶與合作", "th": "คู่ครองและหุ้นส่วน"},
    8: {"en": "Transformation", "zh": "轉化與業力", "th": "การเปลี่ยนแปลงและกรรม"},
    9: {"en": "Dharma & learning", "zh": "信念與學問", "th": "ศรัทธาและการศึกษา"},
    10: {"en": "Career & status", "zh": "事業與名望", "th": "การงานและชื่อเสียง"},
    11: {"en": "Gains & network", "zh": "收穫與人脈", "th": "ผลประโยชน์และเครือข่าย"},
    12: {"en": "Retreat & liberation", "zh": "隱退與解脫", "th": "การปล่อยวางและหลุดพ้น"},
}


# Registry update sample for next-stage integration.
REGISTRY_UPDATE_EXAMPLE: Dict[str, Any] = {
    "id": "tab_thai_duang_chata",
    "name_zh": "泰國 Duang Chata",
    "name_en": "Thai Duang Chata",
    "category": "cat_asian",
    "icon": "🇹🇭",
    "tab_key": "tab_thai_duang_chata",
    "desc_key": "desc_thai_duang_chata",
    "spinner_key": "spinner_thai_duang_chata",
    "hint_key": "sys_hint_thai_duang_chata",
    "tags": ["thai", "duang_chata", "southeast_asia", "navagraha"],
    "maturity": "beta",
    "origin_culture": "Thai",
    "tradition_period": "Traditional Thai Horasastra",
    "ai_persona_key": "info_thai_duang_chata_prompt",
}


@dataclass
class DuangPlanet:
    key: str
    symbol: str
    longitude: float
    latitude: float
    speed: float
    sign_index: int
    sign_degree: float
    house: int
    retrograde: bool


@dataclass
class DuangBhava:
    number: int
    cusp: float
    sign_index: int
    ruler: str
    meaning: Dict[str, str]
    planets: List[str] = field(default_factory=list)


@dataclass
class DuangAnnualTrend:
    target_year: int
    age: int
    activated_house: int
    activated_sign_index: int
    activated_ruler: str
    fortune_cycle_number: int
    note: Dict[str, str]


@dataclass
class DuangChataChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day_ut: float
    ayanamsa: float
    house_system: HouseSystem
    ascendant: float
    planets: List[DuangPlanet]
    houses: List[DuangBhava]
    zodiac_year_number: int
    zodiac_year_animal: Dict[str, str]
    fortune_number: int
    annual_trend: DuangAnnualTrend


def _init_swe() -> None:
    try:
        from astro.swe_init import init_swe

        init_swe()
    except Exception:
        swe.set_ephe_path("")


def _norm(deg: float) -> float:
    return deg % 360.0


def _sign_index(lon: float) -> int:
    return int(_norm(lon) // 30)


def _sign_degree(lon: float) -> float:
    return _norm(lon) % 30.0


def _compute_fortune_number(year: int, month: int, day: int) -> tuple[int, Dict[str, str]]:
    animal = THAI_ZODIAC_ANIMALS[(year - 4) % 12]
    total = int(animal["number"]) + int(month) + int(day)
    total = ((total - 1) % 9) + 1
    return total, animal


def _whole_sign_cusps(ascendant: float) -> List[float]:
    asc_sign = _sign_index(ascendant)
    return [((asc_sign + i) % 12) * 30.0 for i in range(12)]


def _thai_equal_cusps(ascendant: float) -> List[float]:
    return [_norm(ascendant + i * 30.0) for i in range(12)]


def _planet_house_by_cusps(lon: float, cusps: List[float]) -> int:
    lon = _norm(lon)
    for i in range(12):
        start = _norm(cusps[i])
        end = _norm(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def _planet_house_whole_sign(lon: float, ascendant: float) -> int:
    return ((_sign_index(lon) - _sign_index(ascendant)) % 12) + 1


def _build_annual_trend(
    *,
    birth_year: int,
    target_year: int,
    fortune_number: int,
    houses: List[DuangBhava],
) -> DuangAnnualTrend:
    age = max(0, target_year - birth_year)
    activated_house = (age % 12) + 1
    active = houses[activated_house - 1]
    cycle = ((fortune_number + target_year) % 9) or 9
    note = {
        "en": (
            f"Year focus on House {activated_house} ({BHAVA_MEANINGS[activated_house]['en']}). "
            f"Fortune cycle number {cycle} emphasizes practical pacing and consistency."
        ),
        "zh": (
            f"今年重點在第 {activated_house} 宮（{BHAVA_MEANINGS[activated_house]['zh']}），"
            f"命數循環 {cycle} 建議採取務實、穩定節奏。"
        ),
        "th": (
            f"ปีนี้เน้นภพที่ {activated_house} ({BHAVA_MEANINGS[activated_house]['th']}) "
            f"เลขวัฏจักร {cycle} เน้นความสม่ำเสมอและการวางแผนเชิงปฏิบัติ"
        ),
    }
    return DuangAnnualTrend(
        target_year=target_year,
        age=age,
        activated_house=activated_house,
        activated_sign_index=active.sign_index,
        activated_ruler=active.ruler,
        fortune_cycle_number=cycle,
        note=note,
    )


def compute_duang_chata(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    house_system: HouseSystem = "whole_sign",
    target_year: Optional[int] = None,
) -> DuangChataChart:
    """Compute phase-1 Thai Duang Chata core chart."""
    _init_swe()
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour_ut = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, decimal_hour_ut)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # We call houses_ex with whole sign for stable sidereal ASC extraction.
    _, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    ascendant = _norm(ascmc[0])

    if house_system == "whole_sign":
        cusps = _whole_sign_cusps(ascendant)
    elif house_system == "thai_traditional":
        cusps = _thai_equal_cusps(ascendant)
    elif house_system == "placidus":
        placidus_cusps, _ = swe.houses_ex(jd_ut, latitude, longitude, b"P", swe.FLG_SIDEREAL)
        cusps = [_norm(placidus_cusps[i]) for i in range(12)]
    else:
        raise ValueError(f"Unsupported house_system: {house_system}")

    planets: List[DuangPlanet] = []

    for key, pid in THAI_GRAHA_IDS.items():
        result, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        lon = _norm(result[0])
        lat = result[1]
        speed = result[3]
        house = (
            _planet_house_whole_sign(lon, ascendant)
            if house_system == "whole_sign"
            else _planet_house_by_cusps(lon, cusps)
        )
        planets.append(
            DuangPlanet(
                key=key,
                symbol=PLANET_SYMBOLS[key],
                longitude=lon,
                latitude=lat,
                speed=speed,
                sign_index=_sign_index(lon),
                sign_degree=_sign_degree(lon),
                house=house,
                retrograde=speed < 0,
            )
        )

    rahu_raw, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _norm(rahu_raw[0])
    ketu_lon = _norm(rahu_lon + 180.0)

    for key, lon, lat in (
        ("rahu", rahu_lon, rahu_raw[1]),
        ("ketu", ketu_lon, -rahu_raw[1]),
    ):
        house = (
            _planet_house_whole_sign(lon, ascendant)
            if house_system == "whole_sign"
            else _planet_house_by_cusps(lon, cusps)
        )
        planets.append(
            DuangPlanet(
                key=key,
                symbol=PLANET_SYMBOLS[key],
                longitude=lon,
                latitude=lat,
                speed=rahu_raw[3],
                sign_index=_sign_index(lon),
                sign_degree=_sign_degree(lon),
                house=house,
                retrograde=True,
            )
        )

    houses: List[DuangBhava] = []
    for i in range(12):
        sign_idx = _sign_index(cusps[i])
        houses.append(
            DuangBhava(
                number=i + 1,
                cusp=_norm(cusps[i]),
                sign_index=sign_idx,
                ruler=SIGNS[sign_idx]["ruler"],
                meaning=BHAVA_MEANINGS[i + 1],
                planets=[],
            )
        )

    for p in planets:
        houses[p.house - 1].planets.append(p.key)

    fortune_number, animal = _compute_fortune_number(year, month, day)
    trend = _build_annual_trend(
        birth_year=year,
        target_year=target_year or date.today().year,
        fortune_number=fortune_number,
        houses=houses,
    )

    return DuangChataChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        julian_day_ut=jd_ut,
        ayanamsa=ayanamsa,
        house_system=house_system,
        ascendant=ascendant,
        planets=planets,
        houses=houses,
        zodiac_year_number=animal["number"],
        zodiac_year_animal=animal,
        fortune_number=fortune_number,
        annual_trend=trend,
    )


def chart_to_dict(chart: DuangChataChart) -> Dict[str, Any]:
    """Lightweight serializer for API/AI prompt usage."""
    return {
        "birth": {
            "year": chart.year,
            "month": chart.month,
            "day": chart.day,
            "hour": chart.hour,
            "minute": chart.minute,
            "timezone": chart.timezone,
            "latitude": chart.latitude,
            "longitude": chart.longitude,
            "location_name": chart.location_name,
        },
        "meta": {
            "julian_day_ut": chart.julian_day_ut,
            "ayanamsa": chart.ayanamsa,
            "house_system": chart.house_system,
            "ascendant": chart.ascendant,
        },
        "zodiac_year_number": chart.zodiac_year_number,
        "zodiac_year_animal": chart.zodiac_year_animal,
        "fortune_number": chart.fortune_number,
        "planets": [
            {
                "key": p.key,
                "symbol": p.symbol,
                "longitude": p.longitude,
                "latitude": p.latitude,
                "sign_index": p.sign_index,
                "sign_degree": p.sign_degree,
                "house": p.house,
                "retrograde": p.retrograde,
            }
            for p in chart.planets
        ],
        "houses": [
            {
                "number": h.number,
                "cusp": h.cusp,
                "sign_index": h.sign_index,
                "ruler": h.ruler,
                "meaning": h.meaning,
                "planets": h.planets,
            }
            for h in chart.houses
        ],
        "annual_trend": {
            "target_year": chart.annual_trend.target_year,
            "age": chart.annual_trend.age,
            "activated_house": chart.annual_trend.activated_house,
            "activated_sign_index": chart.annual_trend.activated_sign_index,
            "activated_ruler": chart.annual_trend.activated_ruler,
            "fortune_cycle_number": chart.annual_trend.fortune_cycle_number,
            "note": chart.annual_trend.note,
        },
    }
