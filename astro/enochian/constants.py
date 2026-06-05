"""
astro/enochian/constants.py — Enochian Astrology 對應資料表

資料來源 / Sources:
  - John Dee & Edward Kelley: Liber Loagaeth, 48 Calls/Keys (1582–1587)
  - Israel Regardie: The Golden Dawn (Llewellyn, 1971)
  - Lon Milo DuQuette: Enochian Vision Magick (Weiser, 2008)
  - Stephen Skinner: The Complete Magician's Tables (Golden Hoard, 2007)
  - Aaron Leitch: Secrets of the Magickal Grimoires (Llewellyn, 2005)

模組提供以下資料表：
  AETHYRS          — 30 個以太層 (名稱、守護天使、元素、行星、關鍵字)
  WATCHTOWERS      — 4 個守望塔 (名稱、方向、元素、行星統治、天使)
  ENOCHIAN_PLANETS — 行星 → Enochian 對應 (天使、守望塔、Aethyr 索引)
  SIGN_ENOCHIAN    — 黃道星座 → Enochian 對應
  HOUSE_ENOCHIAN   — 宮位 → Enochian 對應
  SIGILLUM_DATA    — Sigillum Dei Aemeth 圓形圖資料
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================================================
# 資料類別 (Data Classes)
# ============================================================

@dataclass
class AethyrData:
    """30 個以太層之一的完整資料 / Data for one of the 30 Aethyrs."""
    number: int            # 1 (最高) → 30 (最低) / 1=highest, 30=lowest
    name: str              # Enochian 名稱 (大寫) / Enochian name
    name_zh: str           # 中文名稱
    governors: List[str]   # 三位守護天使名稱 / Three Governor Angel names
    element: str           # 主元素 (Fire/Water/Air/Earth/Spirit)
    element_zh: str        # 元素中文
    planet: str            # 對應行星 (如 "Saturn", "Venus")
    planet_zh: str         # 行星中文
    keywords_en: List[str] # 英文關鍵字
    keywords_zh: List[str] # 中文關鍵字
    ritual_direction: str  # 儀式方向 (North/South/East/West)
    meditation_en: str     # 冥想建議 (英)
    meditation_zh: str     # 冥想建議 (中)
    level: str             # 靈性層次 (Celestial/Mental/Astral/Physical)
    level_zh: str          # 層次中文


@dataclass
class WatchtowerData:
    """四個守望塔之一 / One of the Four Watchtowers (Great Tablets)."""
    name: str              # 英文名稱
    name_zh: str           # 中文名稱
    direction: str         # 方向 (East/West/North/South)
    direction_zh: str      # 方向中文
    element: str           # 對應元素
    element_zh: str        # 元素中文
    ruling_planet: str     # 主宰行星
    planet_zh: str         # 行星中文
    kerub_angel: str       # 守護克魯賓天使
    king_angel: str        # 四王天使名稱
    senior_angels: List[str]  # 六位資深天使
    sub_angles: List[str]  # 四個副角
    color: str             # 對應顏色 (hex)
    zodiac_signs: List[str]   # 對應黃道星座
    keywords_en: List[str]
    keywords_zh: List[str]
    ritual_purpose_en: str
    ritual_purpose_zh: str


@dataclass
class EnochianAngel:
    """Enochian 天使資料 / Enochian Angel descriptor."""
    name: str              # Enochian 名稱
    name_zh: str           # 中文音譯
    rank: str              # 天使等級 (Governor/Senior/King/Archangel)
    rank_zh: str
    aethyr_number: Optional[int]   # 所屬以太層 (如無則 None)
    watchtower: Optional[str]      # 所屬守望塔 (East/West/North/South/None)
    element: str
    planet: str
    attributes_en: List[str]
    attributes_zh: List[str]
    invocation_key: str    # 召喚關鍵詞


# ============================================================
# 30 個以太層 (The 30 Aethyrs / Aires)
# ============================================================
# 依照 Dee-Kelley 原始系統：LIL (30) 為最低/最外層，TEX (1) 為最低層物質界
# DuQuette 現代應用：30=最高精神層，1=最接近地球物質層
# ============================================================

AETHYRS: List[AethyrData] = [
    AethyrData(
        number=30, name="LIL", name_zh="利勒",
        governors=["OZAAY", "CALVAZAS", "LEXARPH"],
        element="Spirit", element_zh="靈質",
        planet="Saturn", planet_zh="土星",
        keywords_en=["Unity", "Void", "Pure Being", "The Limitless Light"],
        keywords_zh=["合一", "虛空", "純粹存在", "無限之光"],
        ritual_direction="Above",
        meditation_en="Meditate on the dissolution of all boundaries and the unity of existence.",
        meditation_zh="冥想一切界限的消融以及存在的合一。",
        level="Celestial", level_zh="天界",
    ),
    AethyrData(
        number=29, name="RII", name_zh="里依",
        governors=["DOANZIN", "LEXARPH", "COMANAN"],
        element="Fire", element_zh="火",
        planet="Sun", planet_zh="太陽",
        keywords_en=["Divine Will", "Pure Fire", "Initiation", "Sacred Power"],
        keywords_zh=["神聖意志", "純粹火焰", "啟蒙", "神聖力量"],
        ritual_direction="South",
        meditation_en="Contemplate the pure solar fire of divine will working through you.",
        meditation_zh="沈思神聖意志的純粹太陽火焰通過你運作。",
        level="Celestial", level_zh="天界",
    ),
    AethyrData(
        number=28, name="BAG", name_zh="巴格",
        governors=["TAPAMAL", "GEDOONS", "AMBRIOL"],
        element="Water", element_zh="水",
        planet="Moon", planet_zh="月亮",
        keywords_en=["Compassion", "Mystery", "Lunar Currents", "Reflection"],
        keywords_zh=["慈悲", "神秘", "月亮流動", "反思"],
        ritual_direction="West",
        meditation_en="Reflect on the deep waters of compassion and the lunar mysteries.",
        meditation_zh="反思慈悲的深水和月亮神秘。",
        level="Celestial", level_zh="天界",
    ),
    AethyrData(
        number=27, name="ZAA", name_zh="查阿",
        governors=["SAMAPHA", "VIROOLI", "ANDISPI"],
        element="Air", element_zh="風",
        planet="Mercury", planet_zh="水星",
        keywords_en=["Communication", "Mind", "Messenger", "Divine Word"],
        keywords_zh=["溝通", "心智", "信使", "神聖之言"],
        ritual_direction="East",
        meditation_en="Open yourself to the divine messages carried on the winds of the mind.",
        meditation_zh="向承載心智之風的神聖訊息敞開自己。",
        level="Celestial", level_zh="天界",
    ),
    AethyrData(
        number=26, name="DES", name_zh="德斯",
        governors=["POPHAND", "NIGRANA", "PАЗНИТА"],
        element="Earth", element_zh="土",
        planet="Venus", planet_zh="金星",
        keywords_en=["Beauty", "Foundation", "Form", "Material Manifestation"],
        keywords_zh=["美麗", "基礎", "形式", "物質顯現"],
        ritual_direction="North",
        meditation_en="Contemplate the beauty of physical manifestation as a reflection of higher beauty.",
        meditation_zh="思考物質顯現之美作為更高美麗的反映。",
        level="Mental", level_zh="心智界",
    ),
    AethyrData(
        number=25, name="VTI", name_zh="烏提",
        governors=["MIRCIND", "ODRAXTI", "GENADOL"],
        element="Fire", element_zh="火",
        planet="Mars", planet_zh="火星",
        keywords_en=["Courage", "Transformation", "Combat", "Sacred War"],
        keywords_zh=["勇氣", "轉化", "戰鬥", "神聖之戰"],
        ritual_direction="South",
        meditation_en="Channel the martial fire of transformation to overcome inner obstacles.",
        meditation_zh="引導轉化的戰神之火來克服內在障礙。",
        level="Mental", level_zh="心智界",
    ),
    AethyrData(
        number=24, name="NIA", name_zh="尼亞",
        governors=["POCISNI", "OXLOPAR", "VASTRIM"],
        element="Water", element_zh="水",
        planet="Jupiter", planet_zh="木星",
        keywords_en=["Expansion", "Wisdom", "Grace", "Higher Mind"],
        keywords_zh=["擴展", "智慧", "恩典", "更高心智"],
        ritual_direction="West",
        meditation_en="Allow Jupiterian grace and wisdom to expand your consciousness.",
        meditation_zh="讓木星的恩典與智慧擴展你的意識。",
        level="Mental", level_zh="心智界",
    ),
    AethyrData(
        number=23, name="TOR", name_zh="托爾",
        governors=["RONOAMB", "ONIZIMP", "ZAXANIN"],
        element="Air", element_zh="風",
        planet="Saturn", planet_zh="土星",
        keywords_en=["Karma", "Restriction", "Testing", "Discipline"],
        keywords_zh=["業力", "限制", "試煉", "紀律"],
        ritual_direction="East",
        meditation_en="Accept Saturnian discipline as the teacher of spiritual mastery.",
        meditation_zh="接受土星紀律作為靈性掌握的教師。",
        level="Mental", level_zh="心智界",
    ),
    AethyrData(
        number=22, name="LIN", name_zh="林",
        governors=["OZIDAIA", "CALZIRG", "RONOAMB"],
        element="Earth", element_zh="土",
        planet="Sun", planet_zh="太陽",
        keywords_en=["Solar Consciousness", "Identity", "Light Bearer", "Self"],
        keywords_zh=["太陽意識", "身份認同", "光的承載者", "自我"],
        ritual_direction="North",
        meditation_en="Illuminate the core of your solar identity and your role as a light bearer.",
        meditation_zh="照亮你太陽身份的核心以及你作為光的承載者的角色。",
        level="Mental", level_zh="心智界",
    ),
    AethyrData(
        number=21, name="ASP", name_zh="阿斯普",
        governors=["TORZOXI", "ABAIOND", "OMAGRAP"],
        element="Fire", element_zh="火",
        planet="Moon", planet_zh="月亮",
        keywords_en=["Astral Reflection", "Instinct", "Dreamwork", "Unconscious"],
        keywords_zh=["星光反映", "本能", "夢境工作", "潛意識"],
        ritual_direction="South",
        meditation_en="Dive into the lunar astral waters to illuminate your unconscious patterns.",
        meditation_zh="潛入月亮星光水域以照亮你的潛意識模式。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=20, name="KHR", name_zh="柯爾",
        governors=["ZILDRON", "PARZIBA", "TOTOCAN"],
        element="Water", element_zh="水",
        planet="Mercury", planet_zh="水星",
        keywords_en=["Crossroads", "Choices", "Messages", "Threshold"],
        keywords_zh=["十字路口", "選擇", "訊息", "門檻"],
        ritual_direction="West",
        meditation_en="Stand at the crossroads of Mercury and receive clarity for your path.",
        meditation_zh="站在水星的十字路口，為你的道路獲得清晰。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=19, name="POP", name_zh="波普",
        governors=["TORZOXI", "ABAIOND", "OMAGRAP"],
        element="Air", element_zh="風",
        planet="Venus", planet_zh="金星",
        keywords_en=["Love", "Harmony", "Artistic Vision", "Beauty"],
        keywords_zh=["愛", "和諧", "藝術視野", "美麗"],
        ritual_direction="East",
        meditation_en="Open your heart to Venusian love as the cosmic harmonizing force.",
        meditation_zh="敞開你的心靈接受金星之愛作為宇宙和諧力量。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=18, name="ZEN", name_zh="辰",
        governors=["NABAOMI", "ZAFASAI", "YALPAMB"],
        element="Earth", element_zh="土",
        planet="Mars", planet_zh="火星",
        keywords_en=["Willpower", "Anchoring", "Earthly Power", "Manifestation"],
        keywords_zh=["意志力", "錨定", "地球力量", "顯化"],
        ritual_direction="North",
        meditation_en="Ground the martial will into practical earthly manifestation.",
        meditation_zh="將戰神意志錨定到實際的地球顯化中。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=17, name="TAN", name_zh="坦",
        governors=["SIGMORF", "AYDROPT", "TOANTOM"],
        element="Fire", element_zh="火",
        planet="Jupiter", planet_zh="木星",
        keywords_en=["Blessing", "Expansion", "Spiritual Law", "Abundance"],
        keywords_zh=["祝福", "擴展", "靈性法則", "豐盛"],
        ritual_direction="South",
        meditation_en="Receive Jupiterian blessings and align with the laws of spiritual abundance.",
        meditation_zh="接受木星祝福，與靈性豐盛的法則對齊。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=16, name="LEA", name_zh="萊阿",
        governors=["OXIAYAL", "PABNIXP", "POCISNI"],
        element="Water", element_zh="水",
        planet="Saturn", planet_zh="土星",
        keywords_en=["Fate", "Karma", "Time", "Reaping"],
        keywords_zh=["命運", "業力", "時間", "收穫"],
        ritual_direction="West",
        meditation_en="Accept the Saturnian harvest of your actions as the teacher of wisdom.",
        meditation_zh="接受你行動的土星收穫作為智慧的教師。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=15, name="OXO", name_zh="歐索",
        governors=["TAPAMAL", "GEDOONS", "AMBRIOL"],
        element="Air", element_zh="風",
        planet="Sun", planet_zh="太陽",
        keywords_en=["Radiance", "Centre", "Authority", "Solar Throne"],
        keywords_zh=["光輝", "中心", "權威", "太陽寶座"],
        ritual_direction="East",
        meditation_en="Claim your solar authority at the throne of your higher self.",
        meditation_zh="在你更高自我的寶座上宣稱你的太陽權威。",
        level="Astral", level_zh="星光界",
    ),
    AethyrData(
        number=14, name="UTA", name_zh="烏塔",
        governors=["LANGUND", "OCHIAP", "SFRGSD"],
        element="Earth", element_zh="土",
        planet="Moon", planet_zh="月亮",
        keywords_en=["Grounding", "Lunar Earth", "Sacred Ground", "Stability"],
        keywords_zh=["接地", "月亮地球", "神聖土地", "穩定"],
        ritual_direction="North",
        meditation_en="Ground yourself in the sacred earth while honoring lunar cycles.",
        meditation_zh="在神聖土地上接地，同時尊重月亮週期。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=13, name="ZIM", name_zh="辛",
        governors=["GEBABAL", "ASPIAO", "ZAMFRES"],
        element="Fire", element_zh="火",
        planet="Mercury", planet_zh="水星",
        keywords_en=["Quick Mind", "Agility", "Trade", "Intellect"],
        keywords_zh=["敏銳心智", "靈活", "貿易", "智力"],
        ritual_direction="South",
        meditation_en="Quicken your Mercurial intellect to navigate the crossroads ahead.",
        meditation_zh="激活你的水星智力以在前方的十字路口導航。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=12, name="LOE", name_zh="洛伊",
        governors=["TAPAMAL", "GEDOONS", "AMBRIOL"],
        element="Water", element_zh="水",
        planet="Venus", planet_zh="金星",
        keywords_en=["Sacred Love", "Devotion", "Healing", "Artistic Power"],
        keywords_zh=["神聖愛", "奉獻", "療癒", "藝術力量"],
        ritual_direction="West",
        meditation_en="Surrender to sacred love as the healing and harmonizing force in your life.",
        meditation_zh="臣服於神聖愛作為你生命中的療癒與和諧力量。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=11, name="IKH", name_zh="依克",
        governors=["LABNIXP", "FOCISNI", "OXLOPAR"],
        element="Air", element_zh="風",
        planet="Mars", planet_zh="火星",
        keywords_en=["Conflict", "Purification", "Sacred Battle", "Courage"],
        keywords_zh=["衝突", "淨化", "神聖戰役", "勇氣"],
        ritual_direction="East",
        meditation_en="Embrace martial courage to purify what no longer serves your highest path.",
        meditation_zh="擁抱戰神勇氣來淨化不再服務你最高道路的事物。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=10, name="ZAX", name_zh="扎克斯",
        governors=["LEXARPH", "COMANAN", "TABITOM"],
        element="Earth", element_zh="土",
        planet="Jupiter", planet_zh="木星",
        keywords_en=["Abyss", "Choronzon", "Dissolution", "Crossing the Abyss"],
        keywords_zh=["深淵", "克羅農宗", "消融", "越過深淵"],
        ritual_direction="North",
        meditation_en="Face the abyss of ego dissolution with Jupiterian grace and divine trust.",
        meditation_zh="以木星恩典和神聖信任面對自我消融的深淵。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=9, name="ZIP", name_zh="辛普",
        governors=["ODDIORG", "CRALPIR", "DOANZIN"],
        element="Fire", element_zh="火",
        planet="Saturn", planet_zh="土星",
        keywords_en=["Severity", "Justice", "Cosmic Law", "Threshold Keeper"],
        keywords_zh=["嚴格", "正義", "宇宙法則", "門檻守護者"],
        ritual_direction="South",
        meditation_en="Honor the stern justice of Saturn as the guardian of cosmic order.",
        meditation_zh="尊重土星的嚴格正義作為宇宙秩序的守護者。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=8, name="ZID", name_zh="辛德",
        governors=["ZAMFRES", "TODNAON", "PRISTAC"],
        element="Water", element_zh="水",
        planet="Sun", planet_zh="太陽",
        keywords_en=["Solar Mysteries", "Secret Fire", "Inner Sun", "Hidden Light"],
        keywords_zh=["太陽神秘", "秘密火焰", "內在太陽", "隱藏之光"],
        ritual_direction="West",
        meditation_en="Discover the hidden solar fire burning at the core of your being.",
        meditation_zh="發現在你存在核心燃燒的隱藏太陽火焰。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=7, name="DEO", name_zh="德歐",
        governors=["DOANZIN", "LEXARPH", "COMANAN"],
        element="Air", element_zh="風",
        planet="Moon", planet_zh="月亮",
        keywords_en=["Lunar Wisdom", "Reflection", "Cycles", "Inner Vision"],
        keywords_zh=["月亮智慧", "反思", "週期", "內在視野"],
        ritual_direction="East",
        meditation_en="Align with the Lunar cycles to receive the wisdom of rhythmic change.",
        meditation_zh="與月亮週期對齊以接受節奏變化的智慧。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=6, name="MAZ", name_zh="馬辛",
        governors=["SAMAPHA", "VIROOLI", "ANDISPI"],
        element="Earth", element_zh="土",
        planet="Mercury", planet_zh="水星",
        keywords_en=["Practical Wisdom", "Earthly Mind", "Craft", "Skill"],
        keywords_zh=["實用智慧", "地球心智", "工藝", "技能"],
        ritual_direction="North",
        meditation_en="Apply Mercurial wisdom to master the practical arts of earthly life.",
        meditation_zh="應用水星智慧來掌握地球生活的實用藝術。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=5, name="LIT", name_zh="利特",
        governors=["TOANTOM", "VIXPALG", "OOANAMB"],
        element="Fire", element_zh="火",
        planet="Venus", planet_zh="金星",
        keywords_en=["Sacred Heart", "Burning Love", "Passion", "Higher Desire"],
        keywords_zh=["神聖心靈", "燃燒的愛", "激情", "更高渴望"],
        ritual_direction="South",
        meditation_en="Ignite the sacred fire of Venusian love that transforms all desire.",
        meditation_zh="點燃轉化一切渴望的金星神聖愛之火。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=4, name="PAZ", name_zh="帕辛",
        governors=["TOTOCAN", "CHIRZPA", "TOANTOM"],
        element="Water", element_zh="水",
        planet="Mars", planet_zh="火星",
        keywords_en=["Martial Waters", "Emotional Courage", "Depth", "Inner Warrior"],
        keywords_zh=["戰神水域", "情感勇氣", "深度", "內在戰士"],
        ritual_direction="West",
        meditation_en="Discover the warrior of compassion dwelling in the depths of your heart.",
        meditation_zh="發現棲居在你心靈深處的慈悲戰士。",
        level="Physical", level_zh="物質界",
    ),
    AethyrData(
        number=3, name="ZOM", name_zh="佐姆",
        governors=["SIGMORF", "AYDROPT", "TOANTOM"],
        element="Air", element_zh="風",
        planet="Jupiter", planet_zh="木星",
        keywords_en=["High Wisdom", "Cosmic Mind", "Divine Teacher", "Expansion"],
        keywords_zh=["高等智慧", "宇宙心智", "神聖導師", "擴展"],
        ritual_direction="East",
        meditation_en="Receive the high Jupiterian wisdom flowing through the cosmic mind.",
        meditation_zh="接受流經宇宙心智的高等木星智慧。",
        level="Celestial", level_zh="天界",
    ),
    AethyrData(
        number=2, name="ARN", name_zh="阿農",
        governors=["PARAOAN", "DOANZIN", "LEXARPH"],
        element="Earth", element_zh="土",
        planet="Saturn", planet_zh="土星",
        keywords_en=["Final Initiation", "Divine Order", "Completion", "Ultimate Form"],
        keywords_zh=["最終啟蒙", "神聖秩序", "完成", "終極形式"],
        ritual_direction="North",
        meditation_en="Complete the final Saturnian initiation and find divine order within all form.",
        meditation_zh="完成最終的土星啟蒙，在所有形式中找到神聖秩序。",
        level="Celestial", level_zh="天界",
    ),
    AethyrData(
        number=1, name="LIL", name_zh="利勒（頂層）",
        governors=["OCCODON", "PASCOMB", "VALGARS"],
        element="Spirit", element_zh="靈質",
        planet="Sun", planet_zh="太陽",
        keywords_en=["Crown", "Unity with All", "Completion", "Return to Source"],
        keywords_zh=["王冠", "與萬物合一", "完成", "回歸源頭"],
        ritual_direction="Above",
        meditation_en="Rest in the crown of pure being — the LIL of perfect solar unity.",
        meditation_zh="安息在純粹存在的王冠中——完美太陽合一的LIL。",
        level="Celestial", level_zh="天界",
    ),
]

# 建立索引 / Build lookup by Aethyr number
AETHYR_BY_NUMBER: Dict[int, AethyrData] = {a.number: a for a in AETHYRS}
AETHYR_BY_NAME: Dict[str, AethyrData] = {a.name: a for a in AETHYRS}


# ============================================================
# 四個守望塔 (The Four Watchtowers / Great Tablets)
# ============================================================

WATCHTOWERS: Dict[str, WatchtowerData] = {
    "East": WatchtowerData(
        name="Tablet of the East (Air)",
        name_zh="東方守望塔（風元素）",
        direction="East", direction_zh="東",
        element="Air", element_zh="風",
        ruling_planet="Mercury", planet_zh="水星",
        kerub_angel="BATAIVAH",
        king_angel="BATAIVAH",
        senior_angels=["HABIORO", "AAOXAIF", "HTMORDA", "AHAOZPI", "AVTOTAR", "HIPOTGA"],
        sub_angles=["AIR of AIR", "WATER of AIR", "EARTH of AIR", "FIRE of AIR"],
        color="#87CEEB",  # Sky blue
        zodiac_signs=["Gemini", "Libra", "Aquarius"],
        keywords_en=["Mind", "Communication", "Swift Change", "Intellect", "Study"],
        keywords_zh=["心智", "溝通", "迅速變化", "智識", "學習"],
        ritual_purpose_en="For works of intellect, communication, travel, divination, and learning.",
        ritual_purpose_zh="用於智識、溝通、旅行、占卜和學習之工作。",
    ),
    "West": WatchtowerData(
        name="Tablet of the West (Water)",
        name_zh="西方守望塔（水元素）",
        direction="West", direction_zh="西",
        element="Water", element_zh="水",
        ruling_planet="Moon", planet_zh="月亮",
        kerub_angel="RAAGIOSL",
        king_angel="RAAGIOSL",
        senior_angels=["LSRAHPM", "SAIINOV", "LAVACON", "SLGAIOL", "LIGDISA", "SONIZNT"],
        sub_angles=["AIR of WATER", "WATER of WATER", "EARTH of WATER", "FIRE of WATER"],
        color="#4169E1",  # Royal blue
        zodiac_signs=["Cancer", "Scorpio", "Pisces"],
        keywords_en=["Emotion", "Intuition", "Healing", "Dreams", "Compassion"],
        keywords_zh=["情感", "直覺", "療癒", "夢境", "慈悲"],
        ritual_purpose_en="For works of healing, love, dreams, emotional purification, and psychic work.",
        ritual_purpose_zh="用於療癒、愛情、夢境、情感淨化和靈性工作。",
    ),
    "North": WatchtowerData(
        name="Tablet of the North (Earth)",
        name_zh="北方守望塔（土元素）",
        direction="North", direction_zh="北",
        element="Earth", element_zh="土",
        ruling_planet="Saturn", planet_zh="土星",
        kerub_angel="ICZHIHAL",
        king_angel="ICZHIHAL",
        senior_angels=["ACZINOR", "LZINOPO", "ALHCTGA", "AHMLICV", "LIIANSA", "LAOAXRP"],
        sub_angles=["AIR of EARTH", "WATER of EARTH", "EARTH of EARTH", "FIRE of EARTH"],
        color="#8B4513",  # Earth brown
        zodiac_signs=["Taurus", "Virgo", "Capricorn"],
        keywords_en=["Manifestation", "Stability", "Material World", "Grounding", "Endurance"],
        keywords_zh=["顯化", "穩定", "物質世界", "接地", "持久"],
        ritual_purpose_en="For works of material manifestation, stability, prosperity, and earth connection.",
        ritual_purpose_zh="用於物質顯化、穩定、繁榮和大地連結之工作。",
    ),
    "South": WatchtowerData(
        name="Tablet of the South (Fire)",
        name_zh="南方守望塔（火元素）",
        direction="South", direction_zh="南",
        element="Fire", element_zh="火",
        ruling_planet="Sun", planet_zh="太陽",
        kerub_angel="OHOOOHAATAN",
        king_angel="EDLPRNAA",
        senior_angels=["AAETPIO", "ADOEOET", "ALOAISM", "ABOAPRZ", "ABNALOT", "ARINNAP"],
        sub_angles=["AIR of FIRE", "WATER of FIRE", "EARTH of FIRE", "FIRE of FIRE"],
        color="#FF4500",  # Fire red-orange
        zodiac_signs=["Aries", "Leo", "Sagittarius"],
        keywords_en=["Will", "Transformation", "Purification", "Divine Fire", "Leadership"],
        keywords_zh=["意志", "轉化", "淨化", "神聖火焰", "領導力"],
        ritual_purpose_en="For works of will, courage, transformation, leadership, and sacred fire.",
        ritual_purpose_zh="用於意志、勇氣、轉化、領導力和神聖火焰之工作。",
    ),
}


# ============================================================
# 行星 → Enochian 對應 (Planet → Enochian Correspondences)
# ============================================================
# 依據 Golden Dawn / DuQuette 的現代 Enochian 對應
# Based on Golden Dawn / DuQuette modern Enochian correspondences

ENOCHIAN_PLANETS: Dict[str, Dict] = {
    "Sun": {
        "angel": "Michael",
        "angel_zh": "米迦勒",
        "watchtower": "South",
        "aethyr_range": (1, 5),        # 最高層 Aethyrs
        "element": "Fire",
        "element_zh": "火",
        "keywords_en": ["Solar Will", "Leadership", "Divine Authority", "Light"],
        "keywords_zh": ["太陽意志", "領導力", "神聖權威", "光"],
        "ritual_direction": "South",
        "call_number": 1,              # Enochian Call/Key number
        "color": "#FF8C00",
    },
    "Moon": {
        "angel": "GABRIEL",
        "angel_zh": "加百列",
        "watchtower": "West",
        "aethyr_range": (6, 10),
        "element": "Water",
        "element_zh": "水",
        "keywords_en": ["Lunar Cycles", "Reflection", "Astral Travel", "Intuition"],
        "keywords_zh": ["月亮週期", "反思", "星光旅行", "直覺"],
        "ritual_direction": "West",
        "call_number": 2,
        "color": "#C0C0C0",
    },
    "Mercury": {
        "angel": "RAPHAEL",
        "angel_zh": "拉斐爾",
        "watchtower": "East",
        "aethyr_range": (11, 15),
        "element": "Air",
        "element_zh": "風",
        "keywords_en": ["Messenger", "Mind", "Communication", "Divination"],
        "keywords_zh": ["信使", "心智", "溝通", "占卜"],
        "ritual_direction": "East",
        "call_number": 3,
        "color": "#4169E1",
    },
    "Venus": {
        "angel": "HANIEL",
        "angel_zh": "哈尼爾",
        "watchtower": "East",
        "aethyr_range": (16, 20),
        "element": "Air",
        "element_zh": "風",
        "keywords_en": ["Love", "Beauty", "Harmony", "Sacred Art"],
        "keywords_zh": ["愛", "美麗", "和諧", "神聖藝術"],
        "ritual_direction": "East",
        "call_number": 4,
        "color": "#FF69B4",
    },
    "Mars": {
        "angel": "CAMAEL",
        "angel_zh": "卡麥爾",
        "watchtower": "South",
        "aethyr_range": (21, 24),
        "element": "Fire",
        "element_zh": "火",
        "keywords_en": ["Courage", "Transformation", "Sacred War", "Will"],
        "keywords_zh": ["勇氣", "轉化", "神聖之戰", "意志"],
        "ritual_direction": "South",
        "call_number": 5,
        "color": "#DC143C",
    },
    "Jupiter": {
        "angel": "TZADKIEL",
        "angel_zh": "察基爾",
        "watchtower": "West",
        "aethyr_range": (25, 27),
        "element": "Water",
        "element_zh": "水",
        "keywords_en": ["Wisdom", "Expansion", "Grace", "Abundance"],
        "keywords_zh": ["智慧", "擴展", "恩典", "豐盛"],
        "ritual_direction": "West",
        "call_number": 6,
        "color": "#228B22",
    },
    "Saturn": {
        "angel": "TZAPHKIEL",
        "angel_zh": "察法基爾",
        "watchtower": "North",
        "aethyr_range": (28, 30),
        "element": "Earth",
        "element_zh": "土",
        "keywords_en": ["Karma", "Time", "Restriction", "Final Teaching"],
        "keywords_zh": ["業力", "時間", "限制", "最終教導"],
        "ritual_direction": "North",
        "call_number": 7,
        "color": "#8B4513",
    },
    "Uranus": {
        "angel": "URIEL",
        "angel_zh": "烏利爾",
        "watchtower": "North",
        "aethyr_range": (1, 10),      # 橫跨高層 Aethyrs
        "element": "Earth",
        "element_zh": "土",
        "keywords_en": ["Awakening", "Revolution", "Higher Octave of Mercury", "Liberation"],
        "keywords_zh": ["覺醒", "革命", "水星高階振動", "解放"],
        "ritual_direction": "North",
        "call_number": 8,
        "color": "#00CED1",
    },
    "Neptune": {
        "angel": "ASARIEL",
        "angel_zh": "阿薩利爾",
        "watchtower": "West",
        "aethyr_range": (28, 30),
        "element": "Water",
        "element_zh": "水",
        "keywords_en": ["Dissolution", "Mysticism", "Higher Octave of Venus", "Transcendence"],
        "keywords_zh": ["消融", "神秘主義", "金星高階振動", "超越"],
        "ritual_direction": "West",
        "call_number": 9,
        "color": "#7B68EE",
    },
    "Pluto": {
        "angel": "AZRAEL",
        "angel_zh": "阿茲拉爾",
        "watchtower": "South",
        "aethyr_range": (10, 15),
        "element": "Fire",
        "element_zh": "火",
        "keywords_en": ["Death/Rebirth", "Transformation", "Higher Octave of Mars", "Deep Power"],
        "keywords_zh": ["死亡/重生", "轉化", "火星高階振動", "深層力量"],
        "ritual_direction": "South",
        "call_number": 10,
        "color": "#800080",
    },
}


# ============================================================
# 黃道星座 → Enochian 對應
# ============================================================

SIGN_ENOCHIAN: Dict[str, Dict] = {
    "Aries":       {"watchtower": "South", "element": "Fire",  "aethyr": 29, "call": 3,  "angel": "CAMAEL",   "angel_zh": "卡麥爾",   "keyword_zh": "火焰意志"},
    "Taurus":      {"watchtower": "North", "element": "Earth", "aethyr": 26, "call": 4,  "angel": "HANIEL",   "angel_zh": "哈尼爾",   "keyword_zh": "穩固美麗"},
    "Gemini":      {"watchtower": "East",  "element": "Air",   "aethyr": 27, "call": 5,  "angel": "RAPHAEL",  "angel_zh": "拉斐爾",   "keyword_zh": "雙重心智"},
    "Cancer":      {"watchtower": "West",  "element": "Water", "aethyr": 28, "call": 6,  "angel": "GABRIEL",  "angel_zh": "加百列",   "keyword_zh": "月亮直覺"},
    "Leo":         {"watchtower": "South", "element": "Fire",  "aethyr": 22, "call": 7,  "angel": "MICHAEL",  "angel_zh": "米迦勒",   "keyword_zh": "太陽光芒"},
    "Virgo":       {"watchtower": "North", "element": "Earth", "aethyr": 18, "call": 8,  "angel": "RAPHAEL",  "angel_zh": "拉斐爾",   "keyword_zh": "完美服務"},
    "Libra":       {"watchtower": "East",  "element": "Air",   "aethyr": 19, "call": 9,  "angel": "HANIEL",   "angel_zh": "哈尼爾",   "keyword_zh": "神聖平衡"},
    "Scorpio":     {"watchtower": "West",  "element": "Water", "aethyr": 21, "call": 10, "angel": "AZRAEL",   "angel_zh": "阿茲拉爾", "keyword_zh": "深淵轉化"},
    "Sagittarius": {"watchtower": "South", "element": "Fire",  "aethyr": 17, "call": 11, "angel": "TZADKIEL", "angel_zh": "察基爾",   "keyword_zh": "光明求索"},
    "Capricorn":   {"watchtower": "North", "element": "Earth", "aethyr": 16, "call": 12, "angel": "TZAPHKIEL","angel_zh": "察法基爾", "keyword_zh": "業力攀登"},
    "Aquarius":    {"watchtower": "East",  "element": "Air",   "aethyr": 15, "call": 13, "angel": "URIEL",    "angel_zh": "烏利爾",   "keyword_zh": "革命覺醒"},
    "Pisces":      {"watchtower": "West",  "element": "Water", "aethyr": 12, "call": 14, "angel": "ASARIEL",  "angel_zh": "阿薩利爾", "keyword_zh": "神秘消融"},
}


# ============================================================
# 宮位 → Enochian 對應 (House → Enochian)
# ============================================================

HOUSE_ENOCHIAN: Dict[int, Dict] = {
    1:  {"aethyr": 30, "watchtower": "East",  "theme_en": "Self & Awakening",     "theme_zh": "自我與覺醒",   "call": 1},
    2:  {"aethyr": 26, "watchtower": "North", "theme_en": "Material Resources",   "theme_zh": "物質資源",     "call": 2},
    3:  {"aethyr": 27, "watchtower": "East",  "theme_en": "Communication",        "theme_zh": "溝通",         "call": 3},
    4:  {"aethyr": 28, "watchtower": "West",  "theme_en": "Ancestral Roots",      "theme_zh": "祖先根基",     "call": 4},
    5:  {"aethyr": 29, "watchtower": "South", "theme_en": "Creative Fire",        "theme_zh": "創造之火",     "call": 5},
    6:  {"aethyr": 18, "watchtower": "North", "theme_en": "Purification & Service","theme_zh": "淨化與服務",  "call": 6},
    7:  {"aethyr": 19, "watchtower": "East",  "theme_en": "Partnership",          "theme_zh": "夥伴關係",     "call": 7},
    8:  {"aethyr": 10, "watchtower": "West",  "theme_en": "The Abyss & Rebirth",  "theme_zh": "深淵與重生",   "call": 8},
    9:  {"aethyr": 17, "watchtower": "South", "theme_en": "Higher Wisdom",        "theme_zh": "更高智慧",     "call": 9},
    10: {"aethyr": 22, "watchtower": "South", "theme_en": "Solar Authority",      "theme_zh": "太陽權威",     "call": 10},
    11: {"aethyr": 15, "watchtower": "East",  "theme_en": "Community Vision",     "theme_zh": "社群願景",     "call": 11},
    12: {"aethyr": 12, "watchtower": "West",  "theme_en": "Hidden Mysteries",     "theme_zh": "隱藏神秘",     "call": 12},
}


# ============================================================
# Sigillum Dei Aemeth — 神之印資料
# 用於繪製神聖幾何圖形
# ============================================================

SIGILLUM_DEI_AEMETH = {
    "name": "Sigillum Dei Aemeth",
    "name_zh": "神之印",
    "description_en": "The Seal of Truth (God) — a complex magical talisman described in John Dee's angelic journals. Contains concentric circles, a heptagram (7-pointed star), pentagram (5-pointed star), and the names of God and angels arranged in geometric patterns.",
    "description_zh": "神之印（Sigillum Dei Aemeth）——一個複雜的魔法護符，記載於約翰·迪伊的天使日誌中。包含同心圓、七芒星、五芒星以及按幾何圖案排列的神名和天使名。",
    # 外圈七個天使名稱 / 7 Angels on outer ring (Heptarchical)
    "seven_angels": ["MICHAEL", "GABRIEL", "RAPHAEL", "URIEL", "HANIEL", "TZADKIEL", "TZAPHKIEL"],
    "seven_angels_zh": ["米迦勒", "加百列", "拉斐爾", "烏利爾", "哈尼爾", "察基爾", "察法基爾"],
    # 七個行星對應 / Corresponding planets
    "seven_planets": ["Sun", "Moon", "Mercury", "Uranus/Venus", "Venus/Haniel", "Jupiter", "Saturn"],
    # 內部五芒星字母 / Letters on inner pentagram
    "pentagram_letters": ["B", "O", "L", "A", "N"],
    # 中心神名 / Central divine name
    "center_name": "AGLA",
    "center_zh": "阿格拉（神聖之名）",
    # 神聖七角形邊長的 Enochian 字母
    "heptagram_letters": ["IL", "DEL", "EL", "TOTH", "GEAL", "THAA", "YALD"],
    # 顏色 / Colors
    "ring_colors": ["#FFD700", "#C0C0C0", "#4169E1", "#DC143C", "#FF69B4", "#228B22", "#8B4513"],
}


# ============================================================
# Enochian 元素對應表
# ============================================================

ELEMENT_TABLE: Dict[str, Dict] = {
    "Fire": {
        "zh": "火",
        "watchtower": "South",
        "direction": "South",
        "direction_zh": "南",
        "planets": ["Sun", "Mars"],
        "signs": ["Aries", "Leo", "Sagittarius"],
        "angel": "MICHAEL",
        "angel_zh": "米迦勒",
        "color": "#FF4500",
        "qualities_en": ["Will", "Transformation", "Leadership", "Purification"],
        "qualities_zh": ["意志", "轉化", "領導力", "淨化"],
    },
    "Water": {
        "zh": "水",
        "watchtower": "West",
        "direction": "West",
        "direction_zh": "西",
        "planets": ["Moon", "Jupiter", "Neptune"],
        "signs": ["Cancer", "Scorpio", "Pisces"],
        "angel": "GABRIEL",
        "angel_zh": "加百列",
        "color": "#4169E1",
        "qualities_en": ["Emotion", "Intuition", "Compassion", "Healing"],
        "qualities_zh": ["情感", "直覺", "慈悲", "療癒"],
    },
    "Air": {
        "zh": "風",
        "watchtower": "East",
        "direction": "East",
        "direction_zh": "東",
        "planets": ["Mercury", "Venus", "Uranus"],
        "signs": ["Gemini", "Libra", "Aquarius"],
        "angel": "RAPHAEL",
        "angel_zh": "拉斐爾",
        "color": "#87CEEB",
        "qualities_en": ["Intellect", "Communication", "Movement", "Vision"],
        "qualities_zh": ["智識", "溝通", "運動", "視野"],
    },
    "Earth": {
        "zh": "土",
        "watchtower": "North",
        "direction": "North",
        "direction_zh": "北",
        "planets": ["Saturn", "Venus"],
        "signs": ["Taurus", "Virgo", "Capricorn"],
        "angel": "URIEL",
        "angel_zh": "烏利爾",
        "color": "#8B4513",
        "qualities_en": ["Manifestation", "Stability", "Material World", "Grounding"],
        "qualities_zh": ["顯化", "穩定", "物質世界", "接地"],
    },
}


# ============================================================
# 儀式建議模板 / Ritual Recommendation Templates
# ============================================================

RITUAL_TEMPLATES = {
    "south_fire": {
        "en": "Face South. Light a red or orange candle. Vibrate MICHAEL and call upon the fire angels of the Southern Watchtower. Your natal {planet} in {sign} activates the {aethyr_name} Aethyr.",
        "zh": "面向南方。點燃紅色或橙色蠟燭。振動唱誦 MICHAEL，召喚南方守望塔的火焰天使。你命盤中的{planet}在{sign}激活了{aethyr_name}以太層。",
    },
    "west_water": {
        "en": "Face West. Use a bowl of water. Vibrate GABRIEL and connect with the water angels of the Western Watchtower. Your natal {planet} in {sign} connects to the {aethyr_name} Aethyr.",
        "zh": "面向西方。使用一碗水。振動唱誦 GABRIEL，與西方守望塔的水之天使連結。你命盤中的{planet}在{sign}連結到{aethyr_name}以太層。",
    },
    "east_air": {
        "en": "Face East. Burn incense. Vibrate RAPHAEL and open to the air angels of the Eastern Watchtower. Your natal {planet} in {sign} attunes to the {aethyr_name} Aethyr.",
        "zh": "面向東方。燃燒香料。振動唱誦 RAPHAEL，向東方守望塔的風之天使敞開。你命盤中的{planet}在{sign}共鳴{aethyr_name}以太層。",
    },
    "north_earth": {
        "en": "Face North. Hold a stone or soil. Vibrate URIEL and ground into the earth angels of the Northern Watchtower. Your natal {planet} in {sign} grounds into the {aethyr_name} Aethyr.",
        "zh": "面向北方。握住石頭或土壤。振動唱誦 URIEL，接地於北方守望塔的大地天使。你命盤中的{planet}在{sign}扎根於{aethyr_name}以太層。",
    },
}

# 30 Aethyr Calls 開頭模板（第 1、2 Call 為特殊；3-18 為普通形式）
# The opening of the Enochian Call for visiting an Aethyr
AETHYR_CALL_TEMPLATE = {
    "en": "I call upon thee, O mighty {aethyr_name}, the {number}{suffix} Aethyr! By the authority of the Eternal One, and through the governors {gov1}, {gov2}, and {gov3}, I seek vision and wisdom!",
    "zh": "我呼喚你，強大的{aethyr_name}，第{number}以太層！以永恆者的權威，通過守護者{gov1}、{gov2}和{gov3}，我尋求願景與智慧！",
}
