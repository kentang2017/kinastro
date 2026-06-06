"""
astro/goetia/interpretations.py — Goetia 個人化解讀與儀式建議生成器

提供以下功能：
  - build_path_summary()       — 生成個人化 Goetia 路徑摘要
  - build_working_purpose()    — 生成魔法工作目的建議
  - build_ritual_steps()       — 生成儀式步驟
  - build_invocation()         — 組裝召喚語
  - build_banishing_steps()    — 生成遣返步驟
  - build_safety_overview()    — 安全概述

設計原則：
  - 所有函式均為純函式（無 Streamlit 依賴）
  - 輸出均為中英雙語 Tuple[str, str]
  - 遵循 CONTRIBUTING.md：compute_* 函式不依賴 Streamlit
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# ============================================================
# 召喚儀式標準步驟 / Standard Ritual Steps
# ============================================================

_STANDARD_RITUAL_STEPS_EN = [
    "Purify yourself with a ritual bath; fast for 3 hours before the working",
    "Set up a clean, quiet space; mark out the protective Triangle of Art to the East",
    "Draw or place the Magic Circle around your working area (9 feet diameter)",
    "Light candles of the demon's planetary color; burn the appropriate incense",
    "Write the demon's name and sigil on virgin parchment or paper",
    "Recite the Lesser Banishing Ritual of the Pentagram (LBRP) to cleanse the space",
    "Read the Preliminary Invocation (Bornless Ritual) to establish authority",
    "Call the demon three times using the specific Goetic conjuration",
    "State your request clearly, respectfully, and with firm will",
    "Give the demon a task with a reasonable deadline",
    "Formally thank and license the spirit to depart with the License to Depart",
    "Close the ceremony with the LBRP; record everything in your magical journal",
]

_STANDARD_RITUAL_STEPS_ZH = [
    "以儀式浴淨化自身；在工作前禁食三小時",
    "準備乾淨安靜的空間；在東方標示保護性的「藝術三角陣」",
    "在工作區域周圍繪製魔法圓（直徑約 2.7 米）",
    "點燃魔神對應行星顏色的蠟燭；燃燒對應薰香",
    "在原始羊皮紙或紙上寫下魔神名字與印記",
    "誦讀五芒星小驅邪儀式（LBRP）以淨化空間",
    "誦讀前置召喚（無名儀式）以建立施法者的權威",
    "使用特定的格提亞召喚語三次呼喚魔神",
    "清晰、尊重且堅定地陳述你的請求",
    "給予魔神一個具有合理期限的任務",
    "正式感謝魔神並宣讀「許可離去文」，允許其返回",
    "以 LBRP 結束儀式；將一切記錄於魔法日誌中",
]

# ============================================================
# 遣返步驟 / Banishing Steps
# ============================================================

_BANISHING_STEPS_EN = [
    "When the working is complete, firmly state: 'I thank you [DEMON NAME] for your presence and service. By the authority granted to me, I now release and license you to depart in peace, causing no harm to any person or creature.'",
    "Read the License to Depart three times clearly",
    "Close the Triangle of Art with a banishing gesture (trace a banishing Earth pentagram over it)",
    "Perform the Lesser Banishing Ritual of the Pentagram (LBRP) in full",
    "Extinguish the candles in reverse order of lighting",
    "Dispose of any remaining ritual materials appropriately (burn or bury)",
    "Ground yourself: eat food, drink water, and walk barefoot on the earth if possible",
    "Record the complete experience in your magical journal within 24 hours",
]

_BANISHING_STEPS_ZH = [
    "工作完成後，堅定地宣告：「我感謝您【魔神名稱】的到來與服務。憑借賦予我的權威，我現在釋放並許可您和平離去，不得傷害任何人或生物。」",
    "清晰地誦讀「許可離去文」三次",
    "以驅邪手勢關閉藝術三角陣（在其上方描繪驅邪大地五芒星）",
    "完整執行五芒星小驅邪儀式（LBRP）",
    "依點燃的相反順序熄滅蠟燭",
    "適當處置剩餘的儀式材料（燃燒或掩埋）",
    "接地氣：進食、飲水，如有可能則赤腳踩在大地上",
    "在 24 小時內將完整體驗記錄於魔法日誌中",
]

# ============================================================
# 安全概述模板 / Safety Overview Templates
# ============================================================

_SAFETY_TEMPLATE_EN = (
    "Goetia working requires genuine magical authority, not just curiosity. "
    "Never attempt to contact {demon_name} without full protective preparations. "
    "The {element} nature of this spirit means {safety_element_note}. "
    "Always maintain complete control of the working space, and never break the magic circle "
    "while the spirit is present. If you feel overwhelmed, immediately perform the LBRP and "
    "close the working. Work with {demon_name} only for legitimate, ethical purposes aligned "
    "with {powers_summary}."
)

_SAFETY_TEMPLATE_ZH = (
    "格提亞工作需要真正的魔法權威，而非單純的好奇心。"
    "切勿在沒有完整保護準備的情況下嘗試接觸{demon_name}。"
    "此靈體的{element}本質意味著{safety_element_note}。"
    "始終保持對工作空間的完全控制，當靈體在場時切勿打破魔法圓。"
    "若感到不堪重負，立即執行 LBRP 並關閉工作。"
    "僅為符合{powers_summary}的合法、道德目的與{demon_name}合作。"
)

_SAFETY_ELEMENT_NOTES_EN = {
    "Fire":  "it may act with sudden, passionate intensity — stay grounded",
    "Earth": "it may move slowly but is persistent and thorough",
    "Air":   "it communicates in subtle ways — pay attention to signs and dreams",
    "Water": "it can influence emotions and dreams powerfully",
}

_SAFETY_ELEMENT_NOTES_ZH = {
    "Fire":  "它可能以突然而熱烈的強度行動——保持腳踏實地",
    "Earth": "它可能行動緩慢但持續而徹底",
    "Air":   "它以微妙的方式溝通——留意符號與夢境",
    "Water": "它能強力影響情緒與夢境",
}

# ============================================================
# 路徑摘要模板 / Path Summary Templates
# ============================================================

_PATH_TEMPLATES_EN = {
    "Fire": (
        "Your natal chart shows a strong {element} emphasis, resonating with the fiery, "
        "dynamic spirits of the Goetia. With {planet} dominant and the Ascendant in {asc_sign}, "
        "you carry natural authority for Solomonic work. Your primary spirit {demon_name} aligns "
        "with your solar current — approach this path with will, courage, and discipline."
    ),
    "Earth": (
        "Your chart reveals a grounded {element} temperament, naturally suited to the Goetia's "
        "practical, material workings. With {planet} strong and {asc_sign} rising, you have the "
        "patience and persistence needed for Solomonic practice. {demon_name} embodies the "
        "earthy wisdom at the heart of your magical path."
    ),
    "Air": (
        "Your natal {element} dominance speaks to the intellectual and communicative currents "
        "of the Goetia. With {planet} as your strongest planet and {asc_sign} on the Ascendant, "
        "you are well suited to work with spirits of knowledge and language. {demon_name} is "
        "your primary Goetic ally in this mercurial path."
    ),
    "Water": (
        "Your deeply {element}-aspected chart resonates with the lunar, intuitive spirits of "
        "the Goetia. With {planet} at the forefront and {asc_sign} rising, your natural "
        "psychic sensitivity makes this a powerful path. {demon_name} connects with your "
        "emotional depth and visionary capacity."
    ),
}

_PATH_TEMPLATES_ZH = {
    "Fire": (
        "你的命盤顯示出強烈的{element}元素傾向，與格提亞中炽熱、動態的靈體產生共鳴。"
        "以{planet}為最強行星，{asc_sign}上升，你天生具有進行所羅門工作的權威。"
        "你的主要靈體{demon_name}與你的太陽流相契合——以意志、勇氣與自律踏上這條道路。"
    ),
    "Earth": (
        "你的命盤揭示了一種腳踏實地的{element}氣質，天然適合格提亞的實際、物質性工作。"
        "以{planet}強勢，{asc_sign}上升，你擁有所羅門修行所需的耐心與毅力。"
        "{demon_name}體現了你魔法道路核心的大地智慧。"
    ),
    "Air": (
        "你命盤的{element}主導反映了格提亞中智識與溝通的流。"
        "以{planet}為最強行星，{asc_sign}在上升點，你非常適合與知識和語言的靈體合作。"
        "{demon_name}是你在這條水星之道上的主要格提亞盟友。"
    ),
    "Water": (
        "你命盤的深度{element}特質與格提亞中月亮、直覺性的靈體產生共鳴。"
        "以{planet}居首，{asc_sign}上升，你天然的靈覺敏感性使這成為一條強力的道路。"
        "{demon_name}與你的情感深度和先見能力相連接。"
    ),
}

# ============================================================
# 工作目的模板 / Working Purpose Templates
# ============================================================

_PURPOSE_TEMPLATES_EN = {
    "Sun":     "Your solar current calls you toward workings of authority, visibility, and self-mastery. {demon_name} can assist with leadership, recognition, and accessing your inherent power.",
    "Moon":    "Your lunar nature draws you toward workings of intuition, dreams, and emotional healing. {demon_name} opens pathways to hidden knowledge and psychic development.",
    "Mercury": "Your mercurial path focuses on communication, knowledge, and cunning intelligence. {demon_name} excels at teaching, binding agreements, and revealing what is concealed.",
    "Venus":   "Your Venusian current resonates with love, beauty, and harmonious relations. {demon_name} works best for matters of the heart, artistic inspiration, and social grace.",
    "Mars":    "Your martial energy calls for workings of strength, protection, and decisive action. {demon_name} is your ally in overcoming obstacles and defeating adversaries.",
    "Jupiter": "Your Jovian nature seeks wisdom, fortune, and spiritual expansion. {demon_name} can open doors to higher knowledge, material abundance, and philosophical insight.",
    "Saturn":  "Your Saturnine path embraces discipline, hidden knowledge, and long-term transformation. {demon_name} specializes in binding, revealing secrets, and mastering time.",
}

_PURPOSE_TEMPLATES_ZH = {
    "Sun":     "你的太陽流召喚你走向權威、曝光與自我掌控的工作。{demon_name}可在領導力、認可度以及接觸你與生俱來的力量方面提供協助。",
    "Moon":    "你的月亮本質吸引你走向直覺、夢境與情感療癒的工作。{demon_name}開啟通往隱秘知識與靈覺發展的道路。",
    "Mercury": "你的水星之路聚焦於溝通、知識與機敏智慧。{demon_name}在教授、約束協議與揭示隱秘事物方面表現出色。",
    "Venus":   "你的金星流與愛情、美麗和和諧關係產生共鳴。{demon_name}最適合心靈事務、藝術靈感與社交優雅。",
    "Mars":    "你的火星能量呼喚力量、保護與果斷行動的工作。{demon_name}是你克服障礙與擊敗對手的盟友。",
    "Jupiter": "你的木星本質追求智慧、財富與靈性擴展。{demon_name}可為你開啟通往更高知識、物質豐盛與哲學洞見的門戶。",
    "Saturn":  "你的土星道路擁抱紀律、隱秘知識與長期轉化。{demon_name}專精於束縛、揭示秘密與掌控時間。",
}

# ============================================================
# 公開介面函式 / Public API Functions
# ============================================================

def build_path_summary(
    dominant_element: str,
    dominant_element_zh: str,
    strongest_planet: str,
    strongest_planet_zh: str,
    ascendant_sign: str,
    ascendant_sign_zh: str,
    primary_demon_name: str,
    primary_demon_name_zh: str,
) -> Tuple[str, str]:
    """
    建立個人化 Goetia 路徑摘要。

    Returns:
        (en_text, zh_text)
    """
    template_en = _PATH_TEMPLATES_EN.get(dominant_element, _PATH_TEMPLATES_EN["Fire"])
    template_zh = _PATH_TEMPLATES_ZH.get(dominant_element, _PATH_TEMPLATES_ZH["Fire"])

    en = template_en.format(
        element=dominant_element,
        planet=strongest_planet,
        asc_sign=ascendant_sign,
        demon_name=primary_demon_name,
    )
    zh = template_zh.format(
        element=dominant_element_zh,
        planet=strongest_planet_zh,
        asc_sign=ascendant_sign_zh,
        demon_name=primary_demon_name_zh,
    )
    return en, zh


def build_working_purpose(
    strongest_planet: str,
    strongest_planet_zh: str,
    primary_demon_name: str,
    primary_demon_name_zh: str,
) -> Tuple[str, str]:
    """建立魔法工作目的建議。"""
    template_en = _PURPOSE_TEMPLATES_EN.get(strongest_planet, _PURPOSE_TEMPLATES_EN["Sun"])
    template_zh = _PURPOSE_TEMPLATES_ZH.get(strongest_planet, _PURPOSE_TEMPLATES_ZH["Sun"])
    en = template_en.format(demon_name=primary_demon_name)
    zh = template_zh.format(demon_name=primary_demon_name_zh)
    return en, zh


def build_ritual_steps() -> Tuple[List[str], List[str]]:
    """回傳標準儀式步驟（英文列表, 中文列表）。"""
    return list(_STANDARD_RITUAL_STEPS_EN), list(_STANDARD_RITUAL_STEPS_ZH)


def build_banishing_steps() -> Tuple[List[str], List[str]]:
    """回傳遣返步驟（英文列表, 中文列表）。"""
    return list(_BANISHING_STEPS_EN), list(_BANISHING_STEPS_ZH)


def build_safety_overview(
    demon_name: str,
    demon_name_zh: str,
    element: str,
    element_zh: str,
    powers_summary: str,
    powers_summary_zh: str,
) -> Tuple[str, str]:
    """建立安全概述文字。"""
    element_note_en = _SAFETY_ELEMENT_NOTES_EN.get(element, "it may act in unexpected ways")
    element_note_zh = _SAFETY_ELEMENT_NOTES_ZH.get(element, "它可能以意想不到的方式行動")

    en = _SAFETY_TEMPLATE_EN.format(
        demon_name=demon_name,
        element=element,
        safety_element_note=element_note_en,
        powers_summary=powers_summary,
    )
    zh = _SAFETY_TEMPLATE_ZH.format(
        demon_name=demon_name_zh,
        element=element_zh,
        safety_element_note=element_note_zh,
        powers_summary=powers_summary_zh,
    )
    return en, zh


def build_demon_recommendation_reason(
    demon_name: str,
    demon_name_zh: str,
    planet: str,
    planet_zh: str,
    element: str,
    element_zh: str,
    natal_planet: str,
    natal_planet_zh: str,
    natal_sign: str,
    natal_sign_zh: str,
    natal_house: int,
    connection_type: str,  # "planet_match", "sign_match", "element_match", "house_match"
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    建立魔神推薦理由。

    Returns:
        (reasons_en, reasons_zh, connections_en, connections_zh)
    """
    reasons_en: List[str] = []
    reasons_zh: List[str] = []
    connections_en: List[str] = []
    connections_zh: List[str] = []

    if connection_type == "planet_match":
        reasons_en.append(
            f"{demon_name} is ruled by {planet}, which is your dominant natal planet."
        )
        reasons_zh.append(
            f"{demon_name_zh}由{planet_zh}統治，而{planet_zh}是你命盤中的主導行星。"
        )
        connections_en.append(
            f"Your natal {natal_planet} in {natal_sign} (House {natal_house}) "
            f"directly activates {demon_name}'s {planet} current."
        )
        connections_zh.append(
            f"你命盤中{natal_sign_zh}的{natal_planet_zh}（第{natal_house}宮）"
            f"直接激活了{demon_name_zh}的{planet_zh}流。"
        )

    elif connection_type == "sign_match":
        reasons_en.append(
            f"{demon_name} corresponds to {natal_sign}, which hosts your natal {natal_planet}."
        )
        reasons_zh.append(
            f"{demon_name_zh}對應{natal_sign_zh}，你的{natal_planet_zh}就落於此座。"
        )
        connections_en.append(
            f"Your {natal_planet} in {natal_sign} creates a strong zodiacal link "
            f"to {demon_name}'s sphere of influence."
        )
        connections_zh.append(
            f"你{natal_sign_zh}的{natal_planet_zh}與{demon_name_zh}的影響領域形成強烈的黃道連結。"
        )

    elif connection_type == "element_match":
        reasons_en.append(
            f"{demon_name} embodies {element} energy, which is your dominant natal element."
        )
        reasons_zh.append(
            f"{demon_name_zh}體現{element_zh}能量，這也是你命盤的主導元素。"
        )
        connections_en.append(
            f"Your elemental emphasis on {element} (via {natal_planet} in {natal_sign}) "
            f"resonates naturally with {demon_name}'s nature."
        )
        connections_zh.append(
            f"你對{element_zh}元素的強調（透過{natal_sign_zh}的{natal_planet_zh}）"
            f"與{demon_name_zh}的本質自然共鳴。"
        )

    elif connection_type == "house_match":
        reasons_en.append(
            f"{demon_name}'s powers resonate strongly with your {natal_house}th house themes."
        )
        reasons_zh.append(
            f"{demon_name_zh}的力量與你第{natal_house}宮的主題產生強烈共鳴。"
        )
        connections_en.append(
            f"Your natal {natal_planet} in House {natal_house} ({natal_sign}) "
            f"aligns with {demon_name}'s {element} working domain."
        )
        connections_zh.append(
            f"你第{natal_house}宮的{natal_planet_zh}（{natal_sign_zh}）"
            f"與{demon_name_zh}的{element_zh}工作領域一致。"
        )

    return reasons_en, reasons_zh, connections_en, connections_zh
