"""
astro/enochian/enochian.py — Enochian Astrology 計算引擎

本模組將標準 natal chart（出生盤）對應到 Enochian 魔法系統：
  - 行星位置 → Enochian 天使、守望塔、以太層（Aethyr）
  - 宮位 → Enochian 主題與對應天使
  - 黃道星座 → Watchtower 與元素歸屬
  - 計算個人守護天使（Patron Angel）
  - 識別「需要工作」的 Aethyr 層級
  - 生成儀式建議與魔法對應

設計原則：
  - compute_enochian_chart() 為純函式（無 Streamlit 依賴）
  - 繼承西方出生盤計算（使用 pyswisseph），不重複計算行星位置
  - 依照 CONTRIBUTING.md：compute_* 不依賴 Streamlit

參考資料 / References:
  - Lon Milo DuQuette: Enochian Vision Magick (Weiser, 2008)
  - Stephen Skinner: The Complete Magician's Tables (Golden Hoard, 2007)
  - Aaron Leitch: Secrets of the Magickal Grimoires (Llewellyn, 2005)
  - Israel Regardie: The Golden Dawn (Llewellyn, 1971)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import swisseph as swe
from astro.western.western import WesternChart, compute_western_chart

from .data import (
    load_angel_tables,
    load_sigillum_rules,
    load_watchtower_aethyr_rules,
)
from .interpretations import (
    build_invocation,
    build_magical_purpose,
    build_spiritual_path,
)

from .constants import (
    AETHYRS,
    AETHYR_BY_NUMBER,
    AETHYR_BY_NAME,
    WATCHTOWERS,
    ENOCHIAN_PLANETS,
    SIGN_ENOCHIAN,
    HOUSE_ENOCHIAN,
    ELEMENT_TABLE,
    RITUAL_TEMPLATES,
    SIGILLUM_DEI_AEMETH,
    AethyrData,
    WatchtowerData,
)

# ============================================================
# SWE 行星 ID
# ============================================================

_SWE_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
}

# ============================================================
# 黃道星座名稱列表（0=Aries … 11=Pisces）
# ============================================================

_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_SIGNS_ZH = [
    "白羊座", "金牛座", "雙子座", "巨蟹座",
    "獅子座", "處女座", "天秤座", "天蠍座",
    "射手座", "摩羯座", "水瓶座", "雙魚座",
]

PLANET_ZH_MAP: Dict[str, str] = {
    "Sun": "太陽",
    "Moon": "月亮",
    "Mercury": "水星",
    "Venus": "金星",
    "Mars": "火星",
    "Jupiter": "木星",
    "Saturn": "土星",
    "Uranus": "天王星",
    "Neptune": "海王星",
    "Pluto": "冥王星",
}

# ============================================================
# 資料類別 (Data Classes)
# ============================================================

@dataclass
class EnochianPlanetPoint:
    """命盤中一個行星的 Enochian 對應 / Enochian mapping for one natal planet."""
    planet_name: str          # 行星英文名 (e.g. "Sun")
    planet_zh: str            # 行星中文名 (e.g. "太陽")
    longitude: float          # 黃道經度 0–360°
    sign: str                 # 黃道星座 (e.g. "Aries")
    sign_zh: str              # 星座中文
    sign_degree: float        # 星座內度數 0–30
    house: int                # 宮位 1–12
    is_retrograde: bool       # 是否逆行

    # Enochian 對應 / Enochian correspondences
    enochian_angel: str       # 對應天使名稱
    angel_zh: str             # 天使中文音譯
    watchtower: str           # 守望塔方向 (East/West/North/South)
    watchtower_zh: str        # 守望塔中文
    aethyr: AethyrData        # 主要對應以太層
    element: str              # 元素
    element_zh: str           # 元素中文
    call_number: int          # 對應 Enochian Call 編號
    planet_color: str         # 顯示顏色

    # 解讀 / Interpretation
    keywords_en: List[str]
    keywords_zh: List[str]
    ritual_direction: str     # 儀式方向
    interpretation_zh: str    # 中文解讀
    interpretation_en: str    # 英文解讀


@dataclass
class EnochianHousePoint:
    """一個宮位的 Enochian 對應 / Enochian mapping for one natal house."""
    house_number: int
    cusp_longitude: float
    sign: str
    sign_zh: str
    watchtower: str
    watchtower_zh: str
    aethyr: AethyrData
    theme_en: str
    theme_zh: str
    call_number: int
    active_planets: List[str]   # 在此宮位中的行星名稱


@dataclass
class PatronAngel:
    """個人守護天使 / Personal Patron/Matron Angel."""
    name: str
    name_zh: str
    type: str                   # "Patron" (男性) 或 "Matron" (女性)
    determined_by: str          # 根據哪個行星/宮位確定
    determined_zh: str
    watchtower: str
    watchtower_zh: str
    primary_aethyr: AethyrData
    attributes_en: List[str]
    attributes_zh: List[str]
    invocation_en: str
    invocation_zh: str
    source_role: str = ""


@dataclass
class SigillumNode:
    """Personalized Sigillum Dei Aemeth node mapping."""
    node_index: int
    planet: str
    angel: str
    is_activated: bool


@dataclass
class AethyrReading:
    """一個以太層的完整解讀 / Full reading for one Aethyr."""
    aethyr: AethyrData
    relevance_score: float      # 相關性評分 0–1（根據命盤計算）
    activating_planets: List[str]  # 激活此 Aethyr 的行星
    key_themes_en: List[str]
    key_themes_zh: List[str]
    work_needed_en: str         # 建議的工作或冥想
    work_needed_zh: str
    ritual_suggestion_en: str
    ritual_suggestion_zh: str


@dataclass
class EnochianChart:
    """完整的 Enochian 占星命盤 / Complete Enochian Astrology chart."""
    # 出生資料 / Birth data
    year: int
    month: int
    day: int
    hour: float
    minute: float
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # 行星 Enochian 對應 / Planet mappings
    planet_points: List[EnochianPlanetPoint]

    # 宮位 Enochian 對應 / House mappings
    house_points: List[EnochianHousePoint]

    # 守護天使 / Patron Angels
    patron_angel: PatronAngel       # 主守護天使（由太陽決定）
    matron_angel: PatronAngel       # 守護女神天使（由月亮決定）
    asc_angel: PatronAngel          # 上升點天使（由 ASC 決定）
    chart_ruler_angel: PatronAngel  # 命主星守護天使（動態）
    strongest_planet_angel: PatronAngel  # 最強行星守護天使（動態）
    guardian_angel_cards: List[PatronAngel]

    # Watchtower 強度分析 / Watchtower strength analysis
    watchtower_scores: Dict[str, float]   # 方向 → 強度分數
    dominant_watchtower: str              # 最強守望塔
    dominant_watchtower_zh: str

    # 元素平衡 / Elemental balance
    element_scores: Dict[str, float]      # 元素 → 強度分數
    dominant_element: str
    dominant_element_zh: str

    # 重要 Aethyr / Key Aethyrs to work with
    primary_aethyr: AethyrData            # 最重要的以太層
    secondary_aethyrs: List[AethyrData]   # 次要以太層（前 3 個）
    aethyr_readings: List[AethyrReading]  # 前 5 個 Aethyr 的完整解讀

    # 上升點 / Ascendant
    ascendant_longitude: float
    ascendant_sign: str
    ascendant_sign_zh: str

    # 中天 / Midheaven
    midheaven_longitude: float
    midheaven_sign: str
    midheaven_sign_zh: str

    # Sigillum Dei Aemeth 個人化 / Personalized Sigillum data
    sigillum_active_angels: List[str]     # 激活的天使名稱
    sigillum_personal_number: int         # 個人對應的 Sigillum 號碼（1–7）
    sigillum_nodes: List[SigillumNode]

    # 綜合解讀 / Overall interpretation
    overall_path_en: str
    overall_path_zh: str
    magical_purpose_en: str
    magical_purpose_zh: str
    invocation_en: str
    invocation_zh: str

    # 與西方占星的對照 / Western astrology comparison
    western_cross_reference: Dict[str, str]


# ============================================================
# 輔助函式 (Helper Functions)
# ============================================================

def _get_sign(longitude: float) -> Tuple[str, str, float]:
    """從黃道經度取得星座名稱、中文名稱和星座內度數。"""
    sign_idx = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    return _SIGNS[sign_idx], _SIGNS_ZH[sign_idx], degree_in_sign


def _get_julian_day(year: int, month: int, day: int, hour: float,
                    minute: float, timezone: float) -> float:
    """計算儒略日。"""
    ut_hour = hour + minute / 60.0 - timezone
    return swe.julday(year, month, day, ut_hour)


def _compute_planet_positions(jd: float) -> Dict[str, Tuple[float, bool]]:
    """計算所有行星的黃道經度和逆行狀態。回傳 {planet_name: (longitude, is_retrograde)}。"""
    positions: Dict[str, Tuple[float, bool]] = {}
    for planet_name, swe_id in _SWE_IDS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, swe_id, flags)
        lon = result[0]
        speed = result[3]
        is_retrograde = speed < 0
        positions[planet_name] = (lon, is_retrograde)
    return positions


def _compute_houses(jd: float, lat: float, lon: float) -> Tuple[List[float], float, float]:
    """計算 Placidus 宮位。回傳 (house_cusps[12], asc_lon, mc_lon)。"""
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    # cusps[0] = 1st house cusp, cusps[11] = 12th house cusp
    asc = ascmc[0]
    mc = ascmc[1]
    return list(cusps), asc, mc


def _get_house_for_longitude(longitude: float, house_cusps: List[float]) -> int:
    """根據黃道經度判斷所在宮位（1–12）。"""
    for i in range(12):
        cusp_start = house_cusps[i]
        cusp_end = house_cusps[(i + 1) % 12]
        # 跨越 0° 的情況
        if cusp_start > cusp_end:
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1
        else:
            if cusp_start <= longitude < cusp_end:
                return i + 1
    return 1  # 默認第一宮


def _score_watchtowers(planet_points: List[EnochianPlanetPoint]) -> Dict[str, float]:
    """計算四個守望塔的強度分數（基於行星在其對應守望塔中的數量和重要性）。"""
    scores = {"East": 0.0, "West": 0.0, "North": 0.0, "South": 0.0}
    # 行星重要性權重
    weights = {
        "Sun": 3.0, "Moon": 2.5, "Ascendant": 2.0,
        "Mercury": 1.5, "Venus": 1.5, "Mars": 1.5,
        "Jupiter": 1.2, "Saturn": 1.2,
        "Uranus": 1.0, "Neptune": 1.0, "Pluto": 1.0,
    }
    for point in planet_points:
        w = weights.get(point.planet_name, 1.0)
        scores[point.watchtower] = scores.get(point.watchtower, 0.0) + w
    # 正規化
    total = sum(scores.values()) or 1.0
    return {k: round(v / total, 3) for k, v in scores.items()}


def _score_elements(planet_points: List[EnochianPlanetPoint]) -> Dict[str, float]:
    """計算四元素平衡分數。"""
    scores = {"Fire": 0.0, "Water": 0.0, "Air": 0.0, "Earth": 0.0}
    weights = {
        "Sun": 3.0, "Moon": 2.5,
        "Mercury": 1.5, "Venus": 1.5, "Mars": 1.5,
        "Jupiter": 1.2, "Saturn": 1.2,
        "Uranus": 1.0, "Neptune": 1.0, "Pluto": 1.0,
    }
    for point in planet_points:
        w = weights.get(point.planet_name, 1.0)
        scores[point.element] = scores.get(point.element, 0.0) + w
    total = sum(scores.values()) or 1.0
    return {k: round(v / total, 3) for k, v in scores.items()}


def _find_primary_aethyr(planet_points: List[EnochianPlanetPoint],
                         ascendant_sign: str) -> AethyrData:
    """根據太陽、月亮、上升點決定最重要的 Aethyr。"""
    # 以太陽的 Aethyr 為主
    for point in planet_points:
        if point.planet_name == "Sun":
            return point.aethyr
    # 備選：月亮
    for point in planet_points:
        if point.planet_name == "Moon":
            return point.aethyr
    # 最後備選：ASC 星座
    sign_data = SIGN_ENOCHIAN.get(ascendant_sign, {})
    aethyr_num = sign_data.get("aethyr", 30)
    return AETHYR_BY_NUMBER.get(aethyr_num, AETHYRS[0])


def _compute_aethyr_relevance(aethyr: AethyrData,
                               planet_points: List[EnochianPlanetPoint]) -> float:
    """計算一個 Aethyr 對命盤的相關性分數（0–1）。"""
    score = 0.0
    weights = {"Sun": 0.25, "Moon": 0.20, "Mercury": 0.10,
               "Venus": 0.10, "Mars": 0.10, "Jupiter": 0.08,
               "Saturn": 0.08, "Uranus": 0.03, "Neptune": 0.03, "Pluto": 0.03}
    for point in planet_points:
        if point.aethyr.number == aethyr.number:
            score += weights.get(point.planet_name, 0.02)
        # 相鄰 Aethyr 加分
        elif abs(point.aethyr.number - aethyr.number) <= 2:
            score += weights.get(point.planet_name, 0.02) * 0.3
        # 同元素加分
        if point.element == aethyr.element:
            score += weights.get(point.planet_name, 0.02) * 0.2
    return min(score, 1.0)


def _build_aethyr_readings(planet_points: List[EnochianPlanetPoint],
                            top_n: int = 5) -> List[AethyrReading]:
    """為最相關的 Aethyrs 生成完整解讀。"""
    # 計算所有 Aethyr 的相關性分數
    scored = []
    for aethyr in AETHYRS:
        score = _compute_aethyr_relevance(aethyr, planet_points)
        activating = [
            p.planet_name for p in planet_points
            if p.aethyr.number == aethyr.number
        ]
        scored.append((score, aethyr, activating))
    # 按分數排序
    scored.sort(key=lambda x: x[0], reverse=True)

    readings = []
    for score, aethyr, activating_planets in scored[:top_n]:
        ritual_dir = aethyr.ritual_direction.lower().replace("above", "south")
        template_key = f"{ritual_dir}_{aethyr.element.lower()}"
        template = RITUAL_TEMPLATES.get(template_key, RITUAL_TEMPLATES["south_fire"])

        planet_str = ", ".join(activating_planets) if activating_planets else "your natal chart"
        planet_str_zh = "、".join(activating_planets) if activating_planets else "你的命盤"

        ritual_en = template["en"].format(
            planet=planet_str, sign="your chart",
            aethyr_name=aethyr.name
        )
        ritual_zh = template["zh"].format(
            planet=planet_str_zh, sign="你的命盤",
            aethyr_name=aethyr.name_zh
        )

        reading = AethyrReading(
            aethyr=aethyr,
            relevance_score=round(score, 3),
            activating_planets=activating_planets,
            key_themes_en=aethyr.keywords_en[:3],
            key_themes_zh=aethyr.keywords_zh[:3],
            work_needed_en=aethyr.meditation_en,
            work_needed_zh=aethyr.meditation_zh,
            ritual_suggestion_en=ritual_en,
            ritual_suggestion_zh=ritual_zh,
        )
        readings.append(reading)
    return readings


def _build_patron_angel(planet_name: str, planet_point: Optional[EnochianPlanetPoint],
                        angel_type: str, sign: str, source_role: str = "") -> PatronAngel:
    """建立守護天使物件。"""
    if planet_point:
        watchtower = planet_point.watchtower
        watchtower_zh = planet_point.watchtower_zh
        primary_aethyr = planet_point.aethyr
        angel_name = planet_point.enochian_angel
        angel_name_zh = planet_point.angel_zh
    else:
        sign_data = SIGN_ENOCHIAN.get(sign, {})
        watchtower = sign_data.get("watchtower", "East")
        watchtower_zh = WATCHTOWERS[watchtower].direction_zh
        aethyr_num = sign_data.get("aethyr", 30)
        primary_aethyr = AETHYR_BY_NUMBER.get(aethyr_num, AETHYRS[0])
        angel_name = sign_data.get("angel", "RAPHAEL")
        angel_name_zh = sign_data.get("angel_zh", "拉斐爾")

    planet_data = ENOCHIAN_PLANETS.get(planet_name, {})
    attributes_en = planet_data.get("keywords_en", ["Guidance", "Protection"])
    attributes_zh = planet_data.get("keywords_zh", ["引導", "保護"])

    invocation_en = (
        f"I call upon thee, {angel_name}, my {angel_type} Angel! "
        f"By the power of the {watchtower}ern Watchtower and the "
        f"{primary_aethyr.name} Aethyr, guide and protect me on my path."
    )
    invocation_zh = (
        f"我呼喚你，{angel_name_zh}，我的守護天使！"
        f"以{watchtower_zh}方守望塔的力量和{primary_aethyr.name_zh}以太層的庇護，"
        f"在我的道路上引導和保護我。"
    )

    return PatronAngel(
        name=angel_name,
        name_zh=angel_name_zh,
        type=angel_type,
        determined_by=planet_name,
        determined_zh={"Sun": "太陽", "Moon": "月亮", "Ascendant": "上升點"}.get(planet_name, planet_name),
        watchtower=watchtower,
        watchtower_zh=watchtower_zh,
        primary_aethyr=primary_aethyr,
        attributes_en=attributes_en,
        attributes_zh=attributes_zh,
        invocation_en=invocation_en,
        invocation_zh=invocation_zh,
        source_role=source_role,
    )


def _build_overall_path(dominant_watchtower: str, dominant_element: str,
                        primary_aethyr: AethyrData, patron: PatronAngel) -> Tuple[str, str]:
    """生成整體靈性路徑解讀。"""
    wt = WATCHTOWERS.get(dominant_watchtower)
    el = ELEMENT_TABLE.get(dominant_element, {})

    en = (
        f"Your Enochian natal chart reveals a strong {dominant_element} emphasis "
        f"({wt.name if wt else dominant_watchtower + ' Watchtower'}), "
        f"with your primary spiritual work centered in the {primary_aethyr.name} Aethyr "
        f"({primary_aethyr.level} level). "
        f"Your Patron Angel {patron.name} guides your path of "
        f"{', '.join(patron.attributes_en[:2])}. "
        f"Your magical work this lifetime focuses on: {', '.join(primary_aethyr.keywords_en[:3])}."
    )
    zh = (
        f"你的伊諾克命盤顯示強烈的{el.get('zh', dominant_element)}元素傾向"
        f"（{wt.name_zh if wt else dominant_watchtower + '守望塔'}），"
        f"你的主要靈性工作集中在{primary_aethyr.name_zh}以太層"
        f"（{primary_aethyr.level_zh}層級）。"
        f"你的守護天使{patron.name_zh}引導你在{' 、'.join(patron.attributes_zh[:2])}的道路上前行。"
        f"你今生的魔法工作聚焦於：{' 、'.join(primary_aethyr.keywords_zh[:3])}。"
    )
    return en, zh


def _build_magical_purpose(planet_points: List[EnochianPlanetPoint],
                            watchtower_scores: Dict[str, float]) -> Tuple[str, str]:
    """生成魔法目的描述。"""
    dominant_dir = max(watchtower_scores, key=watchtower_scores.get)
    wt = WATCHTOWERS.get(dominant_dir)

    en = (
        f"Your primary magical purpose is aligned with the {dominant_dir}ern Watchtower ({wt.element if wt else ''} element). "
        f"{wt.ritual_purpose_en if wt else 'Work with elemental forces for transformation.'}"
    )
    zh = (
        f"你的主要魔法目的與{wt.direction_zh if wt else dominant_dir}方守望塔（{wt.element_zh if wt else ''}元素）對齊。"
        f"{wt.ritual_purpose_zh if wt else '與元素力量合作進行轉化。'}"
    )
    return en, zh


def _build_western_cross_reference(planet_points: List[EnochianPlanetPoint]) -> Dict[str, str]:
    """建立 Enochian 與西方占星的對照說明。"""
    cross_ref = {}
    for point in planet_points:
        cross_ref[point.planet_name] = (
            f"{point.planet_name} in {point.sign} → "
            f"{point.enochian_angel} ({point.watchtower} WT, "
            f"{point.aethyr.name} Aethyr, {point.element})"
        )
    return cross_ref


def _normalize_western_planet_name(name: str) -> str:
    """Extract plain planet name from Western labels (e.g. 'Sun ☉' -> 'Sun')."""
    return name.split()[0].strip()


def _compute_strongest_planet(western_chart: WesternChart) -> str:
    """Score planets by angularity, luminary priority, dignity, and retrograde state."""
    rules = load_watchtower_aethyr_rules().get("watchtower_weights", {})
    angular_bonus = float(rules.get("angular_house_bonus", 0.4))
    luminary_bonus = float(rules.get("luminary_bonus", 0.3))
    scores: Dict[str, float] = {}
    for planet in western_chart.planets:
        p_name = _normalize_western_planet_name(planet.name)
        score = 1.0
        if planet.house in (1, 4, 7, 10):
            score += angular_bonus
        if p_name in {"Sun", "Moon"}:
            score += luminary_bonus
        dignity = str(getattr(planet, "essential_dignity", "")).lower()
        if "domicile" in dignity:
            score += 0.5
        elif "exalt" in dignity:
            score += 0.35
        elif "detriment" in dignity or "fall" in dignity:
            score -= 0.3
        if getattr(planet, "retrograde", False):
            score -= 0.2
        scores[p_name] = max(scores.get(p_name, 0.0), score)
    return max(scores, key=scores.get) if scores else "Sun"


def _build_sigillum_nodes(
    sigillum_active_angels: List[str],
    fallback_planet_angels: Dict[str, str],
) -> List[SigillumNode]:
    rules = load_sigillum_rules()
    nodes: List[SigillumNode] = []
    active_set = set(sigillum_active_angels)
    for node in rules.get("heptagram_nodes", []):
        planet = node.get("planet", "Sun")
        angel = fallback_planet_angels.get(planet, node.get("default_angel", "MICHAEL"))
        nodes.append(
            SigillumNode(
                node_index=int(node.get("index", 1)),
                planet=planet,
                angel=angel,
                is_activated=angel in active_set,
            )
        )
    return nodes


def _build_dynamic_activation_angels(
    chart_ruler_planet: str,
    strongest_planet: str,
    asc_angel_name: str,
) -> List[str]:
    angel_tables = load_angel_tables()
    activation = angel_tables.get("sigillum_activation_angels", {})
    angels: List[str] = [asc_angel_name]
    for planet in ("Sun", "Moon", chart_ruler_planet, strongest_planet):
        for row in activation.get(planet, []):
            angel = row.get("angel")
            if angel:
                angels.append(angel)
    if len(angels) < 3:
        for row in activation.get("default", []):
            angel = row.get("angel")
            if angel:
                angels.append(angel)
    deduped: List[str] = []
    for angel in angels:
        if angel and angel not in deduped:
            deduped.append(angel)
    sigillum_rules = load_sigillum_rules()
    max_items = int(sigillum_rules.get("activation_window", {}).get("max_highlight_angels", 7))
    return deduped[:max_items]


# ============================================================
# 主計算函式 (Main Computation Function)
# ============================================================

def compute_enochian_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> EnochianChart:
    """
    計算完整的 Enochian 占星命盤。

    此函式為純函式（pure function），無任何 Streamlit 依賴，
    可安全用於 API 端點和測試。

    Args:
        year, month, day: 出生年月日
        hour, minute: 出生時間（24小時制）
        timezone: 時區偏移（UTC+N，如台灣為 8.0）
        latitude, longitude: 出生地緯度、經度
        location_name: 地點名稱（可選）

    Returns:
        EnochianChart: 完整的 Enochian 分析結果
    """
    # 1-3. 重用西方命盤計算（共享 pyswisseph 結果）
    western_chart = compute_western_chart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )
    jd = float(western_chart.julian_day)
    house_cusps = [float(h.cusp) for h in western_chart.houses]
    asc_lon = float(western_chart.ascendant)
    mc_lon = float(western_chart.midheaven)

    # 4. 取得上升點與中天星座
    asc_sign, asc_sign_zh, _ = _get_sign(asc_lon)
    mc_sign, mc_sign_zh, _ = _get_sign(mc_lon)

    # 5. 建立行星 Enochian 對應
    planet_points: List[EnochianPlanetPoint] = []
    western_planets = {
        _normalize_western_planet_name(p.name): p
        for p in western_chart.planets
    }

    for planet_name in _SWE_IDS:
        west_planet = western_planets.get(planet_name)
        if west_planet is None:
            continue
        lon = float(west_planet.longitude)
        is_retro = bool(getattr(west_planet, "retrograde", False))
        sign, sign_zh, sign_degree = _get_sign(lon)
        house = int(getattr(west_planet, "house", _get_house_for_longitude(lon, house_cusps)))

        # Enochian 對應
        planet_data = ENOCHIAN_PLANETS.get(planet_name, {})
        sign_data = SIGN_ENOCHIAN.get(sign, {})

        # 天使：優先用行星對應，其次用星座對應
        angel_name = planet_data.get("angel", sign_data.get("angel", "RAPHAEL"))
        angel_zh = planet_data.get("angel_zh", sign_data.get("angel_zh", "拉斐爾"))

        # 守望塔：行星對應
        watchtower_dir = planet_data.get("watchtower", sign_data.get("watchtower", "East"))
        wt = WATCHTOWERS.get(watchtower_dir)
        watchtower_zh = wt.direction_zh if wt else watchtower_dir

        # Aethyr：優先使用星座對應 Aethyr（若在行星範圍內），否則用行星範圍中心
        aethyr_range = planet_data.get("aethyr_range", (16, 20))
        sign_aethyr_num = sign_data.get("aethyr", aethyr_range[0])
        if aethyr_range[0] <= sign_aethyr_num <= aethyr_range[1]:
            aethyr_num = sign_aethyr_num
        else:
            aethyr_num = (aethyr_range[0] + aethyr_range[1]) // 2
        aethyr = AETHYR_BY_NUMBER.get(aethyr_num, AETHYRS[0])

        element = planet_data.get("element", sign_data.get("element", "Air"))
        element_zh = planet_data.get("element_zh", sign_data.get("element_zh", "風"))
        call_number = planet_data.get("call_number", sign_data.get("call", 3))
        color = planet_data.get("color", "#4169E1")

        # 關鍵字
        keywords_en = planet_data.get("keywords_en", aethyr.keywords_en[:2])
        keywords_zh = planet_data.get("keywords_zh", aethyr.keywords_zh[:2])

        # 儀式方向
        ritual_dir = planet_data.get("ritual_direction", wt.direction if wt else "East")

        # 個人化解讀
        interp_zh = (
            f"你的{PLANET_ZH_MAP.get(planet_name, planet_name)}位於{sign_zh}（宮位{house}），"
            f"對應{element_zh}元素守望塔（{watchtower_zh}方）和{aethyr.name_zh}以太層。"
            f"守護天使{angel_zh}帶來：{' 、'.join(keywords_zh[:2])}。"
        )
        interp_en = (
            f"Your {planet_name} in {sign} (House {house}) corresponds to the "
            f"{element} Watchtower ({watchtower_dir}) and the {aethyr.name} Aethyr. "
            f"Angel {angel_name} brings: {', '.join(keywords_en[:2])}."
        )

        point = EnochianPlanetPoint(
            planet_name=planet_name,
            planet_zh=PLANET_ZH_MAP.get(planet_name, planet_name),
            longitude=lon,
            sign=sign,
            sign_zh=sign_zh,
            sign_degree=sign_degree,
            house=house,
            is_retrograde=is_retro,
            enochian_angel=angel_name,
            angel_zh=angel_zh,
            watchtower=watchtower_dir,
            watchtower_zh=watchtower_zh,
            aethyr=aethyr,
            element=element,
            element_zh=element_zh,
            call_number=call_number,
            planet_color=color,
            keywords_en=keywords_en,
            keywords_zh=keywords_zh,
            ritual_direction=ritual_dir,
            interpretation_zh=interp_zh,
            interpretation_en=interp_en,
        )
        planet_points.append(point)

    # 6. 建立宮位 Enochian 對應
    house_points: List[EnochianHousePoint] = []
    for i, cusp in enumerate(house_cusps):
        h_num = i + 1
        h_sign, h_sign_zh, _ = _get_sign(cusp)
        h_data = HOUSE_ENOCHIAN.get(h_num, {"aethyr": 15, "watchtower": "East", "theme_en": "", "theme_zh": "", "call": 1})
        h_aethyr_num = h_data.get("aethyr", 15)
        h_aethyr = AETHYR_BY_NUMBER.get(h_aethyr_num, AETHYRS[0])
        h_wt_dir = h_data.get("watchtower", "East")
        h_wt = WATCHTOWERS.get(h_wt_dir)
        h_wt_zh = h_wt.direction_zh if h_wt else h_wt_dir

        # 找出在此宮位中的行星
        active_planets = [p.planet_name for p in planet_points if p.house == h_num]

        house_points.append(EnochianHousePoint(
            house_number=h_num,
            cusp_longitude=cusp,
            sign=h_sign,
            sign_zh=h_sign_zh,
            watchtower=h_wt_dir,
            watchtower_zh=h_wt_zh,
            aethyr=h_aethyr,
            theme_en=h_data.get("theme_en", ""),
            theme_zh=h_data.get("theme_zh", ""),
            call_number=h_data.get("call", 1),
            active_planets=active_planets,
        ))

    # 7. 計算守望塔強度和元素平衡
    watchtower_scores = _score_watchtowers(planet_points)
    element_scores = _score_elements(planet_points)

    dominant_watchtower = max(watchtower_scores, key=watchtower_scores.get)
    dominant_wt_obj = WATCHTOWERS.get(dominant_watchtower)
    dominant_watchtower_zh = dominant_wt_obj.direction_zh + "方" if dominant_wt_obj else dominant_watchtower

    dominant_element = max(element_scores, key=element_scores.get)
    el_data = ELEMENT_TABLE.get(dominant_element, {})
    dominant_element_zh = el_data.get("zh", dominant_element)

    # 8. 確定主要以太層
    primary_aethyr = _find_primary_aethyr(planet_points, asc_sign)
    secondary_aethyrs_set = set()
    secondary_aethyrs: List[AethyrData] = []
    for pt in planet_points:
        if pt.aethyr.number != primary_aethyr.number and pt.aethyr.number not in secondary_aethyrs_set:
            secondary_aethyrs_set.add(pt.aethyr.number)
            secondary_aethyrs.append(pt.aethyr)
            if len(secondary_aethyrs) >= 3:
                break

    # 9. 生成 Aethyr 解讀
    aethyr_readings = _build_aethyr_readings(planet_points, top_n=5)

    # 10. 守護天使（動態）
    sun_point = next((p for p in planet_points if p.planet_name == "Sun"), None)
    moon_point = next((p for p in planet_points if p.planet_name == "Moon"), None)

    patron_angel = _build_patron_angel("Sun", sun_point, "Patron", asc_sign, source_role="Patron")
    matron_angel = _build_patron_angel("Moon", moon_point, "Matron", asc_sign, source_role="Matron")

    # 上升點天使：用上升點星座對應
    asc_sign_data = SIGN_ENOCHIAN.get(asc_sign, {})
    asc_angel_name = asc_sign_data.get("angel", "RAPHAEL")
    asc_angel_zh = asc_sign_data.get("angel_zh", "拉斐爾")
    asc_wt = asc_sign_data.get("watchtower", "East")
    asc_wt_obj = WATCHTOWERS.get(asc_wt)
    asc_aethyr_num = asc_sign_data.get("aethyr", 30)
    asc_aethyr = AETHYR_BY_NUMBER.get(asc_aethyr_num, AETHYRS[0])
    asc_angel = PatronAngel(
        name=asc_angel_name,
        name_zh=asc_angel_zh,
        type="Ascendant",
        determined_by="Ascendant",
        determined_zh="上升點",
        watchtower=asc_wt,
        watchtower_zh=asc_wt_obj.direction_zh if asc_wt_obj else asc_wt,
        primary_aethyr=asc_aethyr,
        attributes_en=["Guidance", "New Beginnings", "Soul Expression"],
        attributes_zh=["引導", "新的開始", "靈魂表達"],
        invocation_en=f"I call upon {asc_angel_name}, guardian of my Ascendant, to guide my soul's expression.",
        invocation_zh=f"我呼喚{asc_angel_zh}，我上升點的守護天使，引導我靈魂的表達。",
        source_role="Ascendant",
    )

    chart_ruler_raw = _normalize_western_planet_name(getattr(western_chart, "chart_ruler", "Sun"))
    chart_ruler_planet = chart_ruler_raw if chart_ruler_raw in _SWE_IDS else "Sun"
    strongest_planet = _compute_strongest_planet(western_chart)
    chart_ruler_point = next((p for p in planet_points if p.planet_name == chart_ruler_planet), sun_point)
    strongest_planet_point = next((p for p in planet_points if p.planet_name == strongest_planet), sun_point)

    chart_ruler_angel = _build_patron_angel(
        chart_ruler_planet,
        chart_ruler_point,
        "ChartRuler",
        asc_sign,
        source_role="ChartRuler",
    )
    strongest_planet_angel = _build_patron_angel(
        strongest_planet,
        strongest_planet_point,
        "StrongestPlanet",
        asc_sign,
        source_role="StrongestPlanet",
    )

    guardian_angel_cards = [
        patron_angel,
        matron_angel,
        asc_angel,
        chart_ruler_angel,
        strongest_planet_angel,
    ]

    # 11. Sigillum 個人化資料（上升 + 命主星 + 最強行星激活）
    sun_sign = sun_point.sign if sun_point else asc_sign
    sigillum_idx = 0
    for i, sign in enumerate(_SIGNS):
        if sign == sun_sign:
            sigillum_idx = i % 7
            break
    sigillum_angels = _build_dynamic_activation_angels(
        chart_ruler_planet=chart_ruler_planet,
        strongest_planet=strongest_planet,
        asc_angel_name=asc_angel.name,
    )
    sigillum_personal_number = sigillum_idx + 1
    fallback_planet_angels = {p.planet_name: p.enochian_angel for p in planet_points}
    sigillum_nodes = _build_sigillum_nodes(
        sigillum_active_angels=sigillum_angels,
        fallback_planet_angels=fallback_planet_angels,
    )

    # 12. 整體解讀
    overall_en, overall_zh = build_spiritual_path(
        dominant_watchtower=dominant_watchtower,
        dominant_watchtower_zh=dominant_watchtower_zh,
        dominant_element=dominant_element,
        dominant_element_zh=dominant_element_zh,
        primary_aethyr_name=primary_aethyr.name,
        primary_aethyr_name_zh=primary_aethyr.name_zh,
        guardian_angels=sigillum_angels,
    )
    magical_en, magical_zh = build_magical_purpose(
        dominant_watchtower=dominant_watchtower,
        dominant_watchtower_zh=dominant_watchtower_zh,
        watchtower_purpose_en=dominant_wt_obj.ritual_purpose_en if dominant_wt_obj else "",
        watchtower_purpose_zh=dominant_wt_obj.ritual_purpose_zh if dominant_wt_obj else "",
        strongest_planet=strongest_planet,
    )
    angel_tables = load_angel_tables()
    invoc = build_invocation(
        invocation_template_en=angel_tables.get("invocation_templates", {}).get(
            "en",
            "By the Names of {angel_names}, through the {watchtower} Watchtower and Aethyr {aethyr}, I align with my divine path.",
        ),
        invocation_template_zh=angel_tables.get("invocation_templates", {}).get(
            "zh",
            "奉 {angel_names} 之名，透過{watchtower}方守望塔與 {aethyr} 以太層，我與神聖道路對齊。",
        ),
        angel_names=sigillum_angels,
        watchtower=dominant_watchtower,
        watchtower_zh=dominant_watchtower_zh,
        aethyr_name=primary_aethyr.name,
        aethyr_name_zh=primary_aethyr.name_zh,
    )

    # 13. 西方占星對照
    cross_ref = _build_western_cross_reference(planet_points)

    return EnochianChart(
        year=year, month=month, day=day,
        hour=float(hour), minute=float(minute),
        timezone=float(timezone),
        latitude=float(latitude), longitude=float(longitude),
        location_name=location_name,
        planet_points=planet_points,
        house_points=house_points,
        patron_angel=patron_angel,
        matron_angel=matron_angel,
        asc_angel=asc_angel,
        chart_ruler_angel=chart_ruler_angel,
        strongest_planet_angel=strongest_planet_angel,
        guardian_angel_cards=guardian_angel_cards,
        watchtower_scores=watchtower_scores,
        dominant_watchtower=dominant_watchtower,
        dominant_watchtower_zh=dominant_watchtower_zh,
        element_scores=element_scores,
        dominant_element=dominant_element,
        dominant_element_zh=dominant_element_zh,
        primary_aethyr=primary_aethyr,
        secondary_aethyrs=secondary_aethyrs,
        aethyr_readings=aethyr_readings,
        ascendant_longitude=asc_lon,
        ascendant_sign=asc_sign,
        ascendant_sign_zh=asc_sign_zh,
        midheaven_longitude=mc_lon,
        midheaven_sign=mc_sign,
        midheaven_sign_zh=mc_sign_zh,
        sigillum_active_angels=sigillum_angels,
        sigillum_personal_number=sigillum_personal_number,
        sigillum_nodes=sigillum_nodes,
        overall_path_en=overall_en,
        overall_path_zh=overall_zh,
        magical_purpose_en=magical_en,
        magical_purpose_zh=magical_zh,
        western_cross_reference=cross_ref,
        invocation_en=invoc["en"],
        invocation_zh=invoc["zh"],
    )
