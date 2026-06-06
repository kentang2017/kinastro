"""
astro/goetia/constants.py — Goetia / Solomonic Astrology 對應資料與資料類別

資料來源 / Sources:
  - S.L. MacGregor Mathers & Aleister Crowley: The Goetia — The Lesser Key of Solomon (1904)
  - Joseph H. Peterson: The Lesser Key of Solomon — Lemegeton Clavicula Salomonis (Ibis Press, 2001)
  - Stephen Skinner & David Rankine: The Goetia of Dr Rudd (Golden Hoard, 2007)
  - Israel Regardie: The Golden Dawn (Llewellyn, 1971)
  - Lon Milo DuQuette: The Key to Solomon's Key (CCC Publishing, 2006)

模組提供以下資料：
  DemonData        — 單一魔神的完整資料類別
  GoetiaChart      — 個人化 Goetia 命盤結果類別
  DemonRecommendation — 推薦魔神結果類別
  ElectionalWindow — 選時窗口類別
  PLANET_GOETIA    — 行星 → Goetia 對應
  SIGN_PLANET      — 星座 → 統治行星
  ELEMENT_SIGNS    — 元素 → 星座列表
  RANK_PLANET      — 魔神等級 → 典型行星
  DIRECTION_MAP    — 方向 → 元素對應
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================================================
# 黃道星座 / Zodiac Signs
# ============================================================

SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGNS_ZH = [
    "白羊座", "金牛座", "雙子座", "巨蟹座",
    "獅子座", "處女座", "天秤座", "天蠍座",
    "射手座", "摩羯座", "水瓶座", "雙魚座",
]

# 星座索引 (0=Aries)
SIGN_INDEX: Dict[str, int] = {s: i for i, s in enumerate(SIGNS_EN)}

# ============================================================
# 星座 → 統治行星（傳統）/ Sign → Ruling Planet (traditional)
# ============================================================

SIGN_PLANET: Dict[str, str] = {
    "Aries":       "Mars",
    "Taurus":      "Venus",
    "Gemini":      "Mercury",
    "Cancer":      "Moon",
    "Leo":         "Sun",
    "Virgo":       "Mercury",
    "Libra":       "Venus",
    "Scorpio":     "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn":   "Saturn",
    "Aquarius":    "Saturn",
    "Pisces":      "Jupiter",
}

# 星座中文名稱
SIGN_ZH: Dict[str, str] = dict(zip(SIGNS_EN, SIGNS_ZH))

# ============================================================
# 元素 → 星座列表 / Element → Signs
# ============================================================

ELEMENT_SIGNS: Dict[str, List[str]] = {
    "Fire":  ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air":   ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"],
}

# 星座 → 元素
SIGN_ELEMENT: Dict[str, str] = {}
for _elem, _signs in ELEMENT_SIGNS.items():
    for _s in _signs:
        SIGN_ELEMENT[_s] = _elem

# 元素中文
ELEMENT_ZH: Dict[str, str] = {
    "Fire":  "火",
    "Earth": "土",
    "Air":   "風",
    "Water": "水",
}

# 元素顏色（用於視覺化）
ELEMENT_COLORS: Dict[str, str] = {
    "Fire":  "#FF4500",
    "Earth": "#8B6914",
    "Air":   "#87CEEB",
    "Water": "#4169E1",
}

# ============================================================
# 行星中文 / Planet Chinese Names
# ============================================================

PLANET_ZH: Dict[str, str] = {
    "Sun":     "太陽",
    "Moon":    "月亮",
    "Mercury": "水星",
    "Venus":   "金星",
    "Mars":    "火星",
    "Jupiter": "木星",
    "Saturn":  "土星",
    "Uranus":  "天王星",
    "Neptune": "海王星",
    "Pluto":   "冥王星",
}

# 行星顏色
PLANET_COLORS: Dict[str, str] = {
    "Sun":     "#FFD700",
    "Moon":    "#C0C0C0",
    "Mercury": "#B8B8FF",
    "Venus":   "#FF69B4",
    "Mars":    "#FF4500",
    "Jupiter": "#FF8C00",
    "Saturn":  "#808080",
    "Uranus":  "#40E0D0",
    "Neptune": "#4169E1",
    "Pluto":   "#8B008B",
}

# ============================================================
# 魔神等級 → 典型統治行星 / Demon Rank → Typical Ruling Planet
# ============================================================

RANK_PLANET: Dict[str, str] = {
    "King":      "Sun",
    "Duke":      "Venus",
    "Prince":    "Jupiter",
    "Marquis":   "Moon",
    "President": "Mercury",
    "Count":     "Saturn",
    "Earl":      "Saturn",
    "Knight":    "Saturn",
}

RANK_ZH: Dict[str, str] = {
    "King":      "王",
    "Duke":      "公爵",
    "Prince":    "王子",
    "Marquis":   "侯爵",
    "President": "總裁",
    "Count":     "伯爵",
    "Earl":      "伯爵",
    "Knight":    "騎士",
}

# ============================================================
# 方向 → 元素對應 / Direction → Element
# ============================================================

DIRECTION_ELEMENT: Dict[str, str] = {
    "East":  "Air",
    "South": "Fire",
    "West":  "Water",
    "North": "Earth",
}

DIRECTION_ZH: Dict[str, str] = {
    "East":  "東",
    "South": "南",
    "West":  "西",
    "North": "北",
}

# ============================================================
# 行星 → Goetia 力量領域 / Planet → Goetia Power Domain
# ============================================================

PLANET_GOETIA: Dict[str, dict] = {
    "Sun": {
        "domain_en": "Authority, visibility, leadership, wealth, solar magic",
        "domain_zh": "權威、曝光、領導、財富、太陽魔法",
        "best_day": "Sunday",
        "best_day_zh": "週日",
        "hour_planet": "Sun",
        "color": "#FFD700",
        "metal": "Gold",
        "metal_zh": "金",
        "incense": "Frankincense",
        "incense_zh": "乳香",
    },
    "Moon": {
        "domain_en": "Dreams, intuition, water, travel, divination, hidden things",
        "domain_zh": "夢境、直覺、水元素、旅行、占卜、隱秘之事",
        "best_day": "Monday",
        "best_day_zh": "週一",
        "hour_planet": "Moon",
        "color": "#C0C0C0",
        "metal": "Silver",
        "metal_zh": "銀",
        "incense": "Jasmine",
        "incense_zh": "茉莉",
    },
    "Mercury": {
        "domain_en": "Communication, knowledge, trade, language, cunning, binding",
        "domain_zh": "溝通、知識、貿易、語言、謀略、束縛",
        "best_day": "Wednesday",
        "best_day_zh": "週三",
        "hour_planet": "Mercury",
        "color": "#B8B8FF",
        "metal": "Quicksilver",
        "metal_zh": "水銀",
        "incense": "Storax",
        "incense_zh": "蘇合香",
    },
    "Venus": {
        "domain_en": "Love, beauty, arts, pleasure, relationships, desire",
        "domain_zh": "愛情、美麗、藝術、享樂、關係、慾望",
        "best_day": "Friday",
        "best_day_zh": "週五",
        "hour_planet": "Venus",
        "color": "#FF69B4",
        "metal": "Copper",
        "metal_zh": "銅",
        "incense": "Rose",
        "incense_zh": "玫瑰",
    },
    "Mars": {
        "domain_en": "War, conflict, courage, strength, destruction, protection",
        "domain_zh": "戰爭、衝突、勇氣、力量、毀滅、保護",
        "best_day": "Tuesday",
        "best_day_zh": "週二",
        "hour_planet": "Mars",
        "color": "#FF4500",
        "metal": "Iron",
        "metal_zh": "鐵",
        "incense": "Dragon's Blood",
        "incense_zh": "龍血脂",
    },
    "Jupiter": {
        "domain_en": "Wisdom, fortune, philosophy, spirituality, expansion",
        "domain_zh": "智慧、財運、哲學、靈性、擴展",
        "best_day": "Thursday",
        "best_day_zh": "週四",
        "hour_planet": "Jupiter",
        "color": "#FF8C00",
        "metal": "Tin",
        "metal_zh": "錫",
        "incense": "Cedar",
        "incense_zh": "雪松",
    },
    "Saturn": {
        "domain_en": "Binding, time, death, secrets, agriculture, restriction",
        "domain_zh": "束縛、時間、死亡、秘密、農業、限制",
        "best_day": "Saturday",
        "best_day_zh": "週六",
        "hour_planet": "Saturn",
        "color": "#808080",
        "metal": "Lead",
        "metal_zh": "鉛",
        "incense": "Myrrh",
        "incense_zh": "沒藥",
    },
}

# ============================================================
# 資料類別 / Data Classes
# ============================================================

@dataclass
class DemonData:
    """72 柱魔神之一的完整資料 / Complete data for one of the 72 Goetia demons."""
    number: int                 # 所羅門魔神編號 1–72
    name: str                   # 英文名稱 (e.g. "Bael")
    name_zh: str                # 中文音譯 (e.g. "巴耶爾")
    rank: str                   # 等級 (King/Duke/Prince/Marquis/President/Count/Earl/Knight)
    rank_zh: str                # 等級中文
    planet: str                 # 統治行星 (e.g. "Sun")
    planet_zh: str              # 行星中文
    element: str                # 元素 (Fire/Earth/Air/Water)
    element_zh: str             # 元素中文
    zodiac_sign: str            # 對應星座 (e.g. "Aries")
    sign_zh: str                # 星座中文
    direction: str              # 儀式方向 (East/West/North/South)
    direction_zh: str           # 方向中文
    legion_count: int           # 統領軍團數量
    powers_en: List[str]        # 主要力量/能力（英文）
    powers_zh: List[str]        # 主要力量/能力（中文）
    appearance_en: str          # 外貌描述（英文）
    appearance_zh: str          # 外貌描述（中文）
    sigil_description: str      # 印記描述（英文）
    keywords_en: List[str]      # 關鍵字（英文）
    keywords_zh: List[str]      # 關鍵字（中文）
    house_affinity: List[int]   # 對應宮位親和性（1–12）
    invocation_en: str          # 召喚語（英文）
    invocation_zh: str          # 召喚語（中文）
    safety_note_en: str         # 安全提示（英文）
    safety_note_zh: str         # 安全提示（中文）


@dataclass
class DemonRecommendation:
    """個人化魔神推薦結果 / Personalized demon recommendation result."""
    demon: DemonData
    score: float                      # 匹配分數 0.0–1.0
    score_zh: str                     # 分數等級描述（中文）
    reasons_en: List[str]             # 推薦原因（英文）
    reasons_zh: List[str]             # 推薦原因（中文）
    natal_connections: List[str]      # 命盤連結說明（英文）
    natal_connections_zh: List[str]   # 命盤連結說明（中文）
    best_purpose_en: str              # 最適合的目的（英文）
    best_purpose_zh: str              # 最適合的目的（中文）


@dataclass
class ElectionalWindow:
    """選時窗口 / Electional timing window."""
    demon_name: str
    demon_name_zh: str
    year: int
    month: int
    day: int
    hour_start: int               # 開始小時 (0–23, UTC+timezone)
    hour_end: int                 # 結束小時 (0–23, UTC+timezone)
    timezone: float
    planet: str                   # 統治行星
    planet_zh: str
    quality: str                  # 時機品質 ("Excellent"/"Good"/"Fair")
    quality_zh: str               # 時機品質（中文）
    quality_score: float          # 品質分數 0–1
    reason_en: str                # 選時理由（英文）
    reason_zh: str                # 選時理由（中文）
    ritual_preparation_en: str    # 儀式準備（英文）
    ritual_preparation_zh: str    # 儀式準備（中文）
    day_of_week: str              # 星期幾（英文）
    day_of_week_zh: str           # 星期幾（中文）


@dataclass
class GoetiaPlanetPoint:
    """命盤中一個行星的 Goetia 對應 / Goetia mapping for one natal planet."""
    planet_name: str          # 行星英文名
    planet_zh: str            # 行星中文名
    longitude: float          # 黃道經度 0–360°
    sign: str                 # 黃道星座
    sign_zh: str              # 星座中文
    sign_degree: float        # 星座內度數 0–30
    house: int                # 宮位 1–12
    is_retrograde: bool       # 是否逆行
    element: str              # 元素
    element_zh: str           # 元素中文
    associated_demons: List[str]  # 與此行星位置相關的魔神名稱（前 3 名）


@dataclass
class GoetiaChart:
    """完整的個人化 Goetia 命盤 / Complete personalized Goetia chart."""
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

    # 行星對應 / Planet correspondences
    planet_points: List[GoetiaPlanetPoint]

    # 上升點 / Ascendant
    ascendant_longitude: float
    ascendant_sign: str
    ascendant_sign_zh: str

    # 中天 / Midheaven
    midheaven_longitude: float
    midheaven_sign: str
    midheaven_sign_zh: str

    # 元素平衡 / Elemental balance
    element_scores: Dict[str, float]
    dominant_element: str
    dominant_element_zh: str

    # 最強行星 / Strongest planet
    strongest_planet: str
    strongest_planet_zh: str

    # 個人化推薦魔神 / Personalized demon recommendations
    recommendations: List[DemonRecommendation]  # 前 5 名推薦

    # 選時窗口（未來 30 天）/ Electional windows (next 30 days)
    electional_windows: List[ElectionalWindow]  # 最多 10 個窗口

    # 整體 Goetia 路徑 / Overall Goetia path
    primary_demon: DemonData          # 最主要推薦魔神
    primary_demon_score: float        # 主要魔神匹配分數

    # 綜合解讀 / Overall interpretation
    path_summary_en: str
    path_summary_zh: str
    working_purpose_en: str
    working_purpose_zh: str
    safety_overview_en: str
    safety_overview_zh: str

    # 儀式建議 / Ritual suggestion
    ritual_steps_en: List[str]
    ritual_steps_zh: List[str]
    primary_invocation_en: str
    primary_invocation_zh: str
    banishing_steps_en: List[str]
    banishing_steps_zh: List[str]

    # 72 柱完整列表（用於 UI 展示）
    all_demons: List[DemonData] = field(default_factory=list)
