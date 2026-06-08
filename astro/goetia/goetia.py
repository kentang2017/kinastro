"""
astro/goetia/goetia.py — Goetia / Solomonic Astrology 計算引擎

本模組將出生盤與所羅門魔法傳統（72 柱魔神系統）結合：
  - 依出生盤行星位置、宮位、元素平衡推薦最相關的魔神
  - 計算未來 30 天內適合召喚的選時窗口（Electional Astrology）
  - 生成個人化路徑摘要、儀式建議與召喚語

設計原則：
  - compute_goetia_chart() 為純函式（無 Streamlit 依賴）
  - 繼承西方出生盤行星計算（使用 pyswisseph），不重複計算
  - 依照 CONTRIBUTING.md：compute_* 不依賴 Streamlit

參考資料 / References:
  - S.L. MacGregor Mathers & Aleister Crowley: The Goetia (1904)
  - Joseph H. Peterson: The Lesser Key of Solomon (Ibis Press, 2001)
  - Stephen Skinner & David Rankine: The Goetia of Dr Rudd (Golden Hoard, 2007)
  - Lon Milo DuQuette: The Key to Solomon's Key (CCC Publishing, 2006)
"""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    SIGNS_EN,
    SIGNS_ZH,
    SIGN_INDEX,
    SIGN_PLANET,
    SIGN_ELEMENT,
    SIGN_ZH,
    ELEMENT_SIGNS,
    ELEMENT_ZH,
    PLANET_ZH,
    PLANET_COLORS,
    RANK_ZH,
    DIRECTION_ELEMENT,
    DIRECTION_ZH,
    DemonData,
    DemonRecommendation,
    ElectionalWindow,
    GoetiaPlanetPoint,
    GoetiaChart,
)
from .data import load_demons
from .interpretations import (
    build_path_summary,
    build_working_purpose,
    build_ritual_steps,
    build_banishing_steps,
    build_safety_overview,
    build_demon_recommendation_reason,
)

# ============================================================
# SWE 行星 ID / Swiss Ephemeris Planet IDs
# ============================================================

_SWE_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

# 行星權重（用於計算最強行星）/ Planet weights for dominant planet
_PLANET_WEIGHTS = {
    "Sun":     3.0,
    "Moon":    2.5,
    "Mercury": 1.5,
    "Venus":   1.5,
    "Mars":    2.0,
    "Jupiter": 1.5,
    "Saturn":  1.5,
}

# 廟旺表 / Dignities for strength calculation
_DOMICILE: Dict[str, List[str]] = {
    "Sun":     ["Leo"],
    "Moon":    ["Cancer"],
    "Mercury": ["Gemini", "Virgo"],
    "Venus":   ["Taurus", "Libra"],
    "Mars":    ["Aries", "Scorpio"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn":  ["Capricorn", "Aquarius"],
}

_EXALTATION: Dict[str, str] = {
    "Sun":     "Aries",
    "Moon":    "Taurus",
    "Mercury": "Virgo",
    "Venus":   "Pisces",
    "Mars":    "Capricorn",
    "Jupiter": "Cancer",
    "Saturn":  "Libra",
}

# 星期幾 (weekday) 對照
_WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_WEEKDAYS_ZH = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]

# 行星 → 最佳星期（0=Mon … 6=Sun）
_PLANET_WEEKDAY: Dict[str, int] = {
    "Moon":    0,  # Monday
    "Mars":    1,  # Tuesday
    "Mercury": 2,  # Wednesday
    "Jupiter": 3,  # Thursday
    "Venus":   4,  # Friday
    "Saturn":  5,  # Saturday
    "Sun":     6,  # Sunday
}

# 行星 → 黃道小時序（Chaldean order for planetary hours）
_CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]


# ============================================================
# 輔助函式 / Helper Functions
# ============================================================

def _get_sign(longitude: float) -> Tuple[str, str, float]:
    """從黃道經度取得星座名稱、中文名稱、星座內度數。"""
    idx = int(longitude / 30) % 12
    deg = longitude % 30
    return SIGNS_EN[idx], SIGNS_ZH[idx], deg


def _get_julian_day(
    year: int, month: int, day: int,
    hour: float, minute: float, timezone: float,
) -> float:
    """計算儒略日 / Compute Julian Day Number."""
    ut_hour = hour + minute / 60.0 - timezone
    return swe.julday(year, month, day, ut_hour)


def _compute_planet_positions(jd: float) -> Dict[str, Tuple[float, bool]]:
    """計算所有行星位置和逆行狀態。"""
    positions: Dict[str, Tuple[float, bool]] = {}
    for planet_name, swe_id in _SWE_IDS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, swe_id, flags)
        lon = result[0]
        speed = result[3]
        positions[planet_name] = (lon, speed < 0)
    return positions


def _compute_houses(
    jd: float, lat: float, lon: float,
) -> Tuple[List[float], float, float]:
    """計算 Placidus 宮位，返回 (宮首列表[12], ASC, MC)。"""
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    house_cusps = list(cusps[:12])
    if len(house_cusps) != 12:
        raise ValueError(f"Expected 12 house cusps from swe.houses(), got {len(house_cusps)}")
    return house_cusps, ascmc[0], ascmc[1]


def _get_house(longitude: float, cusps: List[float]) -> int:
    """判斷給定黃道經度落在哪個宮位（1–12）。"""
    for i in range(12):
        start = cusps[i] % 360
        end = cusps[(i + 1) % 12] % 360
        lon = longitude % 360
        if start <= end:
            if start <= lon < end:
                return i + 1
        else:  # 跨越 0° 點
            if lon >= start or lon < end:
                return i + 1
    return 1


def _planet_strength(planet: str, sign: str, house: int, is_retrograde: bool) -> float:
    """計算行星在命盤中的強度分數。"""
    score = _PLANET_WEIGHTS.get(planet, 1.0)

    # 廟宮加分
    if sign in _DOMICILE.get(planet, []):
        score += 1.5
    # 旺位加分
    if sign == _EXALTATION.get(planet, ""):
        score += 1.0
    # 角宮加分（1, 4, 7, 10）
    if house in (1, 4, 7, 10):
        score += 1.0
    # 逆行扣分
    if is_retrograde:
        score -= 0.3

    return max(0.1, score)


def _load_demon_objects() -> List[DemonData]:
    """從 JSON 資料庫載入 DemonData 物件列表。"""
    raw = load_demons()
    demons: List[DemonData] = []
    for d in raw:
        demons.append(DemonData(
            number=d["number"],
            name=d["name"],
            name_zh=d["name_zh"],
            rank=d["rank"],
            rank_zh=d.get("rank_zh", RANK_ZH.get(d["rank"], d["rank"])),
            planet=d["planet"],
            planet_zh=d.get("planet_zh", PLANET_ZH.get(d["planet"], d["planet"])),
            element=d["element"],
            element_zh=d.get("element_zh", ELEMENT_ZH.get(d["element"], d["element"])),
            zodiac_sign=d["zodiac_sign"],
            sign_zh=d.get("sign_zh", SIGN_ZH.get(d["zodiac_sign"], d["zodiac_sign"])),
            direction=d["direction"],
            direction_zh=d.get("direction_zh", DIRECTION_ZH.get(d["direction"], d["direction"])),
            legion_count=d.get("legion_count", 0),
            powers_en=d.get("powers_en", []),
            powers_zh=d.get("powers_zh", []),
            appearance_en=d.get("appearance_en", ""),
            appearance_zh=d.get("appearance_zh", ""),
            sigil_description=d.get("sigil_description", ""),
            keywords_en=d.get("keywords_en", []),
            keywords_zh=d.get("keywords_zh", []),
            house_affinity=d.get("house_affinity", []),
            invocation_en=d.get("invocation_en", ""),
            invocation_zh=d.get("invocation_zh", ""),
            safety_note_en=d.get("safety_note_en", ""),
            safety_note_zh=d.get("safety_note_zh", ""),
        ))
    return demons


# ============================================================
# 核心推薦邏輯 / Core Recommendation Logic
# ============================================================

def _score_demon(
    demon: DemonData,
    planet_points: List[GoetiaPlanetPoint],
    dominant_element: str,
    strongest_planet: str,
    asc_sign: str,
) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    """
    計算魔神與命盤的匹配分數及推薦理由。

    Returns:
        (score, reasons_en, reasons_zh, connections_en, connections_zh)
    """
    score = 0.0
    reasons_en: List[str] = []
    reasons_zh: List[str] = []
    connections_en: List[str] = []
    connections_zh: List[str] = []

    for pp in planet_points:
        # 行星匹配（最高權重）
        if demon.planet == pp.planet_name:
            planet_score = _PLANET_WEIGHTS.get(pp.planet_name, 1.0)
            if pp.sign in _DOMICILE.get(pp.planet_name, []):
                planet_score *= 1.5
            score += planet_score
            r_en, r_zh, c_en, c_zh = build_demon_recommendation_reason(
                demon.name, demon.name_zh,
                demon.planet, demon.planet_zh,
                demon.element, demon.element_zh,
                pp.planet_name, pp.planet_zh,
                pp.sign, pp.sign_zh, pp.house,
                "planet_match",
            )
            reasons_en.extend(r_en); reasons_zh.extend(r_zh)
            connections_en.extend(c_en); connections_zh.extend(c_zh)

        # 星座匹配
        if demon.zodiac_sign == pp.sign:
            score += 1.5
            r_en, r_zh, c_en, c_zh = build_demon_recommendation_reason(
                demon.name, demon.name_zh,
                demon.planet, demon.planet_zh,
                demon.element, demon.element_zh,
                pp.planet_name, pp.planet_zh,
                pp.sign, pp.sign_zh, pp.house,
                "sign_match",
            )
            reasons_en.extend(r_en); reasons_zh.extend(r_zh)
            connections_en.extend(c_en); connections_zh.extend(c_zh)

        # 宮位親和性匹配
        if pp.house in demon.house_affinity:
            score += 0.8
            r_en, r_zh, c_en, c_zh = build_demon_recommendation_reason(
                demon.name, demon.name_zh,
                demon.planet, demon.planet_zh,
                demon.element, demon.element_zh,
                pp.planet_name, pp.planet_zh,
                pp.sign, pp.sign_zh, pp.house,
                "house_match",
            )
            reasons_en.extend(r_en); reasons_zh.extend(r_zh)
            connections_en.extend(c_en); connections_zh.extend(c_zh)

    # 元素匹配（命盤主元素）
    if demon.element == dominant_element:
        score += 1.2
        reasons_en.append(
            f"{demon.name}'s {demon.element} nature matches your dominant natal element."
        )
        reasons_zh.append(
            f"{demon.name_zh}的{demon.element_zh}本質與你命盤的主導元素相符。"
        )

    # 最強行星匹配
    if demon.planet == strongest_planet:
        score += 1.0

    # 上升星座匹配
    if demon.zodiac_sign == asc_sign:
        score += 0.8
        reasons_en.append(
            f"{demon.name} rules {demon.zodiac_sign}, which is your rising sign — "
            f"a direct link to your identity and outward expression."
        )
        reasons_zh.append(
            f"{demon.name_zh}統治{demon.sign_zh}，即你的上升星座——"
            f"與你的身份和外在表現有直接聯繫。"
        )

    # 去重（保持順序）
    unique_reasons_en = list(dict.fromkeys(reasons_en))
    unique_reasons_zh = list(dict.fromkeys(reasons_zh))

    return score, unique_reasons_en[:3], unique_reasons_zh[:3], connections_en[:3], connections_zh[:3]


def _score_label(score: float) -> str:
    """將數字分數轉換為等級描述（中文）。"""
    if score >= 8.0:
        return "極強共鳴"
    elif score >= 5.0:
        return "強烈共鳴"
    elif score >= 3.0:
        return "中度共鳴"
    elif score >= 1.5:
        return "輕度共鳴"
    else:
        return "一般對應"


def _build_recommendations(
    demons: List[DemonData],
    planet_points: List[GoetiaPlanetPoint],
    dominant_element: str,
    strongest_planet: str,
    asc_sign: str,
    top_n: int = 5,
) -> List[DemonRecommendation]:
    """評分所有 72 柱魔神並返回前 top_n 名推薦。"""
    scored: List[Tuple[float, DemonData, List, List, List, List]] = []

    for demon in demons:
        score, r_en, r_zh, c_en, c_zh = _score_demon(
            demon, planet_points, dominant_element, strongest_planet, asc_sign
        )
        scored.append((score, demon, r_en, r_zh, c_en, c_zh))

    # 按分數降序排列
    scored.sort(key=lambda x: x[0], reverse=True)

    recommendations: List[DemonRecommendation] = []
    for score, demon, r_en, r_zh, c_en, c_zh in scored[:top_n]:
        # 標準化分數到 0–1
        normalized = min(1.0, score / 12.0)
        best_purpose_en = ", ".join(demon.powers_en[:2]) if demon.powers_en else "general working"
        best_purpose_zh = "、".join(demon.powers_zh[:2]) if demon.powers_zh else "通用工作"

        recommendations.append(DemonRecommendation(
            demon=demon,
            score=normalized,
            score_zh=_score_label(score),
            reasons_en=r_en or [f"{demon.name} aligns with your natal {demon.planet} energy."],
            reasons_zh=r_zh or [f"{demon.name_zh}與你命盤的{demon.planet_zh}能量相符。"],
            natal_connections=c_en or [f"Planetary resonance through {demon.planet}."],
            natal_connections_zh=c_zh or [f"透過{demon.planet_zh}的行星共鳴。"],
            best_purpose_en=best_purpose_en,
            best_purpose_zh=best_purpose_zh,
        ))

    return recommendations


# ============================================================
# 選時占星 / Electional Astrology
# ============================================================

def _quality_label(score: float) -> Tuple[str, str]:
    """品質分數 → (英文標籤, 中文標籤)。"""
    if score >= 0.7:
        return "Excellent", "極佳"
    elif score >= 0.4:
        return "Good", "良好"
    else:
        return "Fair", "普通"


def _compute_electional_windows(
    demon: DemonData,
    year: int,
    month: int,
    day: int,
    timezone: float,
    days_ahead: int = 30,
) -> List[ElectionalWindow]:
    """
    計算未來 days_ahead 天內適合召喚特定魔神的時間窗口。

    策略：
    - 優先選擇魔神統治行星對應的星期幾
    - 選擇該行星廟旺的時段（使用粗略當日行星計算）
    - 每天最多保留一個窗口，總計最多 10 個
    """
    planet = demon.planet
    planet_zh = demon.planet_zh
    best_weekday = _PLANET_WEEKDAY.get(planet, 6)  # 預設週日（太陽）

    # 計算起始儒略日
    jd_start = swe.julday(year, month, day, -timezone)

    windows: List[ElectionalWindow] = []
    current_jd = jd_start

    for day_offset in range(days_ahead):
        jd = current_jd + day_offset

        # 取得日期對應的星期幾
        # 儒略日 0 對應 Monday（在 proleptic Gregorian 中）
        greg = swe.jdut1_to_utc(jd, 1)  # type: ignore[attr-defined]
        # swe.jdut1_to_utc 返回 (year, month, day, hour, minute, second)
        import datetime
        dt = datetime.date(int(greg[0]), int(greg[1]), int(greg[2]))
        weekday = dt.weekday()  # 0=Monday

        # 計算行星在當天的位置
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd + 0.5, _SWE_IDS.get(planet, swe.SUN), flags)
        planet_lon = result[0]
        planet_sign = SIGNS_EN[int(planet_lon / 30) % 12]
        planet_speed = result[3]
        is_retrograde = planet_speed < 0

        # 計算品質分數
        quality_score = 0.5  # 基礎分
        if weekday == best_weekday:
            quality_score += 0.3
        if planet_sign in _DOMICILE.get(planet, []):
            quality_score += 0.3
        elif planet_sign == _EXALTATION.get(planet, ""):
            quality_score += 0.2
        if is_retrograde:
            quality_score -= 0.2

        quality_score = max(0.05, min(1.0, quality_score))

        # 確定最佳時段（魔法時：以天亮時間為基準，粗略取凌晨 23:00–01:00 或正午）
        if weekday == best_weekday:
            hour_start, hour_end = 22, 24
        else:
            hour_start, hour_end = 12, 14  # 日間次佳

        quality_en, quality_zh = _quality_label(quality_score)

        # 儀式準備建議
        ritual_prep_en = (
            f"Prepare {demon.name}'s sigil, {_planet_incense(planet)}, "
            f"and {_planet_color(planet)}-colored candles. "
            f"The {planet} current is currently in {planet_sign} — "
            f"{'avoid as retrograde' if is_retrograde else 'favorable for working'}."
        )
        ritual_prep_zh = (
            f"準備{demon.name_zh}的印記、{_planet_incense_zh(planet)}以及{_planet_color_zh(planet)}蠟燭。"
            f"{planet_zh}目前位於{SIGN_ZH.get(planet_sign, planet_sign)}——"
            f"{'逆行期間避免工作' if is_retrograde else '適合進行工作'}。"
        )

        # 日期描述
        reason_en = (
            f"{_WEEKDAYS_EN[weekday]} — {planet} is in {planet_sign}"
            f"{' (retrograde)' if is_retrograde else ''}. "
            f"Quality: {quality_en}."
        )
        reason_zh = (
            f"{_WEEKDAYS_ZH[weekday]} — {planet_zh}位於{SIGN_ZH.get(planet_sign, planet_sign)}"
            f"{'（逆行）' if is_retrograde else ''}。"
            f"品質：{quality_zh}。"
        )

        windows.append(ElectionalWindow(
            demon_name=demon.name,
            demon_name_zh=demon.name_zh,
            year=int(greg[0]),
            month=int(greg[1]),
            day=int(greg[2]),
            hour_start=hour_start,
            # hour_end is capped at 23 because the window may cross midnight
            # (e.g., hour_start=22 + 2-hour window = 24); 23 is the last valid hour
            hour_end=min(hour_end, 23),
            timezone=timezone,
            planet=planet,
            planet_zh=planet_zh,
            quality=quality_en,
            quality_zh=quality_zh,
            quality_score=quality_score,
            reason_en=reason_en,
            reason_zh=reason_zh,
            ritual_preparation_en=ritual_prep_en,
            ritual_preparation_zh=ritual_prep_zh,
            day_of_week=_WEEKDAYS_EN[weekday],
            day_of_week_zh=_WEEKDAYS_ZH[weekday],
        ))

        if len(windows) >= 10:
            break

    # 按品質排序，最多返回 10 個
    windows.sort(key=lambda w: w.quality_score, reverse=True)
    return windows[:10]


def _planet_incense(planet: str) -> str:
    incenses = {
        "Sun": "Frankincense", "Moon": "Jasmine", "Mercury": "Storax",
        "Venus": "Rose", "Mars": "Dragon's Blood",
        "Jupiter": "Cedar", "Saturn": "Myrrh",
    }
    return incenses.get(planet, "Frankincense")


def _planet_incense_zh(planet: str) -> str:
    incenses = {
        "Sun": "乳香", "Moon": "茉莉", "Mercury": "蘇合香",
        "Venus": "玫瑰", "Mars": "龍血脂",
        "Jupiter": "雪松", "Saturn": "沒藥",
    }
    return incenses.get(planet, "乳香")


def _planet_color(planet: str) -> str:
    colors = {
        "Sun": "gold", "Moon": "silver/white", "Mercury": "violet",
        "Venus": "green/pink", "Mars": "red",
        "Jupiter": "blue/purple", "Saturn": "black/dark brown",
    }
    return colors.get(planet, "white")


def _planet_color_zh(planet: str) -> str:
    colors = {
        "Sun": "金色", "Moon": "銀色/白色", "Mercury": "紫色",
        "Venus": "綠色/粉紅", "Mars": "紅色",
        "Jupiter": "藍色/紫色", "Saturn": "黑色/深棕",
    }
    return colors.get(planet, "白色")


# ============================================================
# 主計算函式 / Main Computation Function
# ============================================================

def compute_goetia_chart(
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    electional_days: int = 30,
) -> GoetiaChart:
    """
    計算個人化 Goetia 命盤。

    Args:
        year, month, day: 出生日期
        hour, minute:     出生時間（本地時間）
        timezone:         UTC 偏移（如 +8.0）
        latitude:         出生地緯度
        longitude:        出生地經度
        location_name:    地名（純顯示用）
        electional_days:  計算選時的未來天數（預設 30）

    Returns:
        GoetiaChart — 完整的個人化 Goetia 命盤結果
    """
    # ── 1. 計算儒略日 ───────────────────────────────────────────
    jd = _get_julian_day(year, month, day, hour, minute, timezone)

    # ── 2. 計算行星位置 ─────────────────────────────────────────
    positions = _compute_planet_positions(jd)

    # ── 3. 計算宮位 ─────────────────────────────────────────────
    house_cusps, asc_lon, mc_lon = _compute_houses(jd, latitude, longitude)

    # ── 4. 建立 GoetiaPlanetPoint 列表 ──────────────────────────
    all_demons = _load_demon_objects()
    planet_points: List[GoetiaPlanetPoint] = []
    planet_strengths: Dict[str, float] = {}

    for planet_name, (lon, is_retro) in positions.items():
        sign, sign_zh, sign_deg = _get_sign(lon)
        house = _get_house(lon, house_cusps)
        element = SIGN_ELEMENT.get(sign, "Fire")
        element_zh = ELEMENT_ZH.get(element, element)
        strength = _planet_strength(planet_name, sign, house, is_retro)
        planet_strengths[planet_name] = strength

        # 找出與此行星最相關的魔神（前 3 名）
        related_demons = [
            d.name for d in all_demons
            if d.planet == planet_name
        ][:3]

        planet_points.append(GoetiaPlanetPoint(
            planet_name=planet_name,
            planet_zh=PLANET_ZH.get(planet_name, planet_name),
            longitude=lon,
            sign=sign,
            sign_zh=sign_zh,
            sign_degree=sign_deg,
            house=house,
            is_retrograde=is_retro,
            element=element,
            element_zh=element_zh,
            associated_demons=related_demons,
        ))

    # ── 5. 上升點 / 中天 ─────────────────────────────────────────
    asc_sign, asc_sign_zh, _ = _get_sign(asc_lon)
    mc_sign, mc_sign_zh, _ = _get_sign(mc_lon)

    # ── 6. 元素平衡 ─────────────────────────────────────────────
    element_scores: Dict[str, float] = {e: 0.0 for e in ("Fire", "Earth", "Air", "Water")}
    for pp in planet_points:
        element_scores[pp.element] = element_scores.get(pp.element, 0.0) + planet_strengths.get(pp.planet_name, 1.0)

    total_elem = sum(element_scores.values()) or 1.0
    element_scores = {k: v / total_elem for k, v in element_scores.items()}
    dominant_element = max(element_scores, key=element_scores.get)  # type: ignore[arg-type]
    dominant_element_zh = ELEMENT_ZH.get(dominant_element, dominant_element)

    # ── 7. 最強行星 ─────────────────────────────────────────────
    strongest_planet = max(planet_strengths, key=planet_strengths.get)  # type: ignore[arg-type]
    strongest_planet_zh = PLANET_ZH.get(strongest_planet, strongest_planet)

    # ── 8. 個人化魔神推薦 ───────────────────────────────────────
    recommendations = _build_recommendations(
        all_demons, planet_points,
        dominant_element, strongest_planet, asc_sign,
        top_n=5,
    )

    # ── 9. 主要魔神 ─────────────────────────────────────────────
    primary_demon = recommendations[0].demon if recommendations else all_demons[0]
    primary_score = recommendations[0].score if recommendations else 0.5

    # ── 10. 選時占星 ────────────────────────────────────────────
    electional_windows = _compute_electional_windows(
        primary_demon, year, month, day, timezone, days_ahead=electional_days
    )

    # ── 11. 生成解讀文字 ─────────────────────────────────────────
    path_en, path_zh = build_path_summary(
        dominant_element, dominant_element_zh,
        strongest_planet, strongest_planet_zh,
        asc_sign, asc_sign_zh,
        primary_demon.name, primary_demon.name_zh,
    )

    purpose_en, purpose_zh = build_working_purpose(
        strongest_planet, strongest_planet_zh,
        primary_demon.name, primary_demon.name_zh,
    )

    ritual_steps_en, ritual_steps_zh = build_ritual_steps()
    banishing_en, banishing_zh = build_banishing_steps()

    powers_summary_en = ", ".join(primary_demon.powers_en[:2]) if primary_demon.powers_en else "general working"
    powers_summary_zh = "、".join(primary_demon.powers_zh[:2]) if primary_demon.powers_zh else "通用工作"

    safety_en, safety_zh = build_safety_overview(
        primary_demon.name, primary_demon.name_zh,
        primary_demon.element, primary_demon.element_zh,
        powers_summary_en, powers_summary_zh,
    )

    return GoetiaChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        planet_points=planet_points,
        ascendant_longitude=asc_lon,
        ascendant_sign=asc_sign,
        ascendant_sign_zh=asc_sign_zh,
        midheaven_longitude=mc_lon,
        midheaven_sign=mc_sign,
        midheaven_sign_zh=mc_sign_zh,
        element_scores=element_scores,
        dominant_element=dominant_element,
        dominant_element_zh=dominant_element_zh,
        strongest_planet=strongest_planet,
        strongest_planet_zh=strongest_planet_zh,
        recommendations=recommendations,
        electional_windows=electional_windows,
        primary_demon=primary_demon,
        primary_demon_score=primary_score,
        path_summary_en=path_en,
        path_summary_zh=path_zh,
        working_purpose_en=purpose_en,
        working_purpose_zh=purpose_zh,
        safety_overview_en=safety_en,
        safety_overview_zh=safety_zh,
        ritual_steps_en=ritual_steps_en,
        ritual_steps_zh=ritual_steps_zh,
        primary_invocation_en=primary_demon.invocation_en,
        primary_invocation_zh=primary_demon.invocation_zh,
        banishing_steps_en=banishing_en,
        banishing_steps_zh=banishing_zh,
        all_demons=all_demons,
    )
