"""
納迪占星 Nadi Amsha (D150) 計算模組
Nadi Amsha (D150) Calculation Module for Vedic Astrology (Jyotish)

概述 (Overview)
--------------
Nadi Amsha，又稱 D150 或 Nadi Varga，是 Vedic 占星中精度最高的 Varga（分割盤）之一。
每個 Nadi 覆蓋黃道弧度僅 12 分鐘（12'），使其成為精確預測（Phala）的重要工具。
本模組以《Deva Keralam》（又稱《Chandra Kala Nadi》）傳統定義的 150 個 Nadi 名稱為依據，
嚴格遵循古法排列規則。

⚠️ Ayanamsa 警告 (Ayanamsa Warning)
------------------------------------
Nadi Amsha 計算必須基於 Sidereal Zodiac（恆星黃道），且需正確配置 Ayanamsa。
建議使用 Lahiri Ayanamsa（印度政府標準）。若使用 Tropical 黃道或錯誤的 Ayanamsa，
計算結果將與傳統 Nadi 占星一致性相差甚遠，結果無效。
（Warning: Nadi Amsha must be computed from Sidereal longitudes with proper Ayanamsa,
preferably Lahiri. Results are invalid for Tropical/unsupported Ayanamsa.）

古法排列規則 (Ancient Ordering Rules — per Deva Keralam)
-----------------------------------------------------
- 活動星座 Movable / Chara  (Mesha, Karka, Tula, Makara — 牡羊、巨蟹、天秤、摩羯)：
  Nadi 按 1 → 150 順序排列。
- 固定星座 Fixed  / Sthira  (Vrishabha, Simha, Vrischika, Kumbha — 金牛、獅子、天蠍、水瓶)：
  Nadi 按 150 → 1 逆序排列。
- 雙重星座 Dual   / Dwiswabhava (Mithuna, Kanya, Dhanu, Meena — 雙子、處女、射手、雙魚)：
  Nadi 從第 76 個名稱開始排列（76 → 150，接著 1 → 75）。

精度設計 (Precision Design)
---------------------------
每個 Nadi 覆蓋 0.2° (12')。由於行星經度精度需求，本模組使用 epsilon = 1e-9 做邊界保護，
確保剛好落在 Nadi 邊界的行星不因浮點誤差被歸入相鄰 Nadi，與 Jagannatha Hora 等專業
占星軟件保持一致。
"""

from dataclasses import dataclass
from typing import Literal

# ============================================================
# 常量 (Constants)
# ============================================================

# 每個 Nadi 覆蓋的黃道弧度 (12 arc-minutes = 0.2°)
NADI_ARC_DEGREES: float = 12.0 / 60.0  # 0.2°

# 邊界保護 epsilon (prevents floating-point misassignment at Nadi boundaries)
EPSILON: float = 1e-9

# 150 個 Nadi 名稱 — 依《Deva Keralam》(Chandra Kala Nadi) 傳統
# 索引 0 對應第 1 個 Nadi（Vasudha），索引 149 對應第 150 個 Nadi（Parameshwari）
NADI_NAMES: tuple[str, ...] = (
    # 1–15: 五大元素與護法神 (Panchabhutas and Guardians)
    "Vasudha",        "Vaishnavi",      "Brahmi",         "Kaumari",
    "Maheshwari",     "Chamundi",       "Varahee",        "Narasimhi",
    "Lakshmi",        "Saraswati",      "Gauri",          "Durgaa",
    "Indrani",        "Varahi",         "Tripura",
    # 16–30: 吉祥與力量 (Auspicious and Shakti aspects)
    "Bhadra",         "Sharada",        "Mahakali",       "Shree",
    "Mangala",        "Pingala",        "Dhanya",         "Bhramari",
    "Bala",           "Bala Tripura",   "Nila",           "Ghana",
    "Dhana",          "Siddha",         "Riddhi",
    # 31–45: 七大仙人 (Saptarishis and Sages)
    "Vibhava",        "Vardhini",       "Narada",         "Vishwamitra",
    "Jamadagni",      "Bharadwaja",     "Vasishtha",      "Kashyapa",
    "Atri",           "Kratu",          "Pulaha",         "Pulastya",
    "Marichi",        "Angirasa",       "Devala",
    # 46–60: 賢者傳承 (Rishi lineage and Vidyas)
    "Chyavana",       "Galava",         "Shaunaka",       "Agastya",
    "Dadhichi",       "Vamadeva",       "Vararuchi",      "Kaushika",
    "Jaimini",        "Shankhapada",    "Mudgala",        "Vishoka",
    "Vyaghrapada",    "Upamanyu",       "Dhanvantari",
    # 61–75: 七曜與四尖 (Grahas and Angular points)
    "Durvasa",        "Surya",          "Chandra",        "Mangal",
    "Budha",          "Guru",           "Shukra",         "Shani",
    "Rahu",           "Ketu",           "Lagna",          "Hora",
    "Drekkana",       "Navamsha",       "Dwadashamsha",
    # 76–90: 高階分割盤 (Higher Vargas)
    "Shodashamsha",   "Vimshamsha",     "Chaturvimshamsha","Saptavimshamsha",
    "Trimshamsha",    "Khavedamsha",    "Akshavedamsha",  "Shastiamsha",
    "Vargottama",     "Pushkara",       "Argala",         "Ashtakavarga",
    "Shadbala",       "Vimshottari",    "Ashtottari",
    # 91–105: 占星命運週期 (Dasha systems and cycles)
    "Yogini",         "Kalachakra",     "Narayana",       "Shula",
    "Pinda",          "Nisarga",        "Brahma",         "Shiva",
    "Vishnu",         "Harihara",       "Brahmananda",    "Shivananda",
    "Vishnvananda",   "Sachidananda",   "Chidananda",
    # 106–120: 至福境界 (States of Ananda and Bliss)
    "Paramananda",    "Nandana",        "Harshana",       "Shobhana",
    "Subhaga",        "Sadhya",         "Shubha",         "Shukla",
    "Aindra",         "Vaishnava",      "Shaiva",         "Saura",
    "Ganesha",        "Nairrtya",       "Vayu",
    # 121–135: 天神、夜叉與靈界 (Celestial beings and spirit realms)
    "Kubera",         "Yaksha",         "Rakshasa",       "Deva",
    "Asura",          "Manusha",        "Preta",          "Paishacha",
    "Naga",           "Gandharva",      "Kinnara",        "Vidyadhara",
    "Chariti",        "Maharshi",       "Pitru",
    # 136–150: 梵天至上 (Brahmic and Supreme aspects)
    "Brahma Swarupa", "Vishnu Swarupa", "Rudra",          "Ishwara",
    "Sadashiva",      "Akula",          "Kula",           "Ananda",
    "Chit",           "Sat",            "Turiya",         "Turiyatita",
    "Nirvana",        "Moksha",         "Parameshwari",
)

assert len(NADI_NAMES) == 150, (
    f"NADI_NAMES must contain exactly 150 entries; found {len(NADI_NAMES)}"
)

# 星座性質分類 (Sign Modality classification by Rashi index 0–11)
# 0=Mesha(♈), 1=Vrishabha(♉), 2=Mithuna(♊), 3=Karka(♋),
# 4=Simha(♌),  5=Kanya(♍),    6=Tula(♎),    7=Vrischika(♏),
# 8=Dhanu(♐),  9=Makara(♑),  10=Kumbha(♒), 11=Meena(♓)
Modality = Literal["Movable", "Fixed", "Dual"]

_MOVABLE_INDICES: frozenset[int] = frozenset({0, 3, 6, 9})   # Chara
_FIXED_INDICES:   frozenset[int] = frozenset({1, 4, 7, 10})  # Sthira
_DUAL_INDICES:    frozenset[int] = frozenset({2, 5, 8, 11})  # Dwiswabhava


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass(frozen=True)
class NadiAmshaResult:
    """
    Nadi Amsha (D150) 計算結果 (Result of Nadi Amsha calculation)

    Attributes
    ----------
    nadi_index : int
        1-based Nadi index (1–150).  1 = Vasudha, 150 = Parameshwari.
    nadi_name : str
        Nadi name from the Deva Keralam tradition.
    modality : str
        Sign modality: 'Movable', 'Fixed', or 'Dual'.
    sign_degree : float
        Input degree within the sign (0° ≤ sign_degree < 30°).
    """
    nadi_index: int
    nadi_name: str
    modality: str
    sign_degree: float


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def get_sign_modality(sign_index: int) -> Modality:
    """
    根據星座索引 (0–11) 自動返回其性質 (Modality)。
    Determine the modality of a Rashi from its zero-based index.

    Parameters
    ----------
    sign_index : int
        Zero-based Rashi index (0 = Mesha/Aries … 11 = Meena/Pisces).

    Returns
    -------
    str
        'Movable' (Chara), 'Fixed' (Sthira), or 'Dual' (Dwiswabhava).

    Raises
    ------
    ValueError
        If sign_index is not in the range 0–11.
    """
    if not (0 <= sign_index <= 11):
        raise ValueError(
            f"sign_index must be in range 0–11; got {sign_index!r}"
        )
    if sign_index in _MOVABLE_INDICES:
        return "Movable"
    if sign_index in _FIXED_INDICES:
        return "Fixed"
    return "Dual"


def get_nadi_amsha(sign_degree: float, modality: Modality) -> NadiAmshaResult:
    """
    計算行星的 Nadi Amsha (D150)。
    Compute the Nadi Amsha (D150) for a planet positioned within a sign.

    ⚠️ 確保輸入的 sign_degree 來自恆星黃道（Sidereal）並已套用正確 Ayanamsa（建議 Lahiri）。
       The sign_degree MUST be derived from a Sidereal longitude with a valid Ayanamsa
       (Lahiri recommended).  Tropical longitudes will produce invalid results.

    每個 Nadi 覆蓋精確的 12 分弧（0.2°），共 150 個 Nadi 填滿一個 30° 星座。
    Each Nadi spans exactly 12 arc-minutes (0.2°); 150 Nadis fill one 30° Rashi.

    排列規則 (Ordering per Deva Keralam)
    ------------------------------------
    - Movable (Chara)      : Nadi 1 → 150  (順序 / ascending)
    - Fixed   (Sthira)     : Nadi 150 → 1  (逆序 / descending)
    - Dual    (Dwiswabhava): Nadi 76 → 150, then 1 → 75  (雙向 / split)

    Parameters
    ----------
    sign_degree : float
        Planet's degree within the Rashi, in the range [0°, 30°).
        （行星於星座內的精確度數，範圍 0° ≤ sign_degree < 30°）
    modality : str
        Sign modality: 'Movable', 'Fixed', or 'Dual'.

    Returns
    -------
    NadiAmshaResult
        Dataclass containing nadi_index (1-based), nadi_name, modality,
        and the input sign_degree.

    Raises
    ------
    ValueError
        If sign_degree is outside [0, 30) or modality is unrecognised.
    """
    # ── 輸入驗證 (Input validation) ──────────────────────────
    if not (0.0 <= sign_degree < 30.0):
        raise ValueError(
            f"sign_degree must be in [0, 30); got {sign_degree!r}"
        )
    if modality not in ("Movable", "Fixed", "Dual"):
        raise ValueError(
            f"modality must be 'Movable', 'Fixed', or 'Dual'; got {modality!r}"
        )

    # ── 核心計算 (Core calculation) ──────────────────────────
    # 使用 epsilon 防止邊界浮點誤差（對應 Jagannatha Hora 的處理方式）
    # Apply epsilon guard before integer truncation to avoid float boundary errors.
    raw_index = int((sign_degree + EPSILON) / NADI_ARC_DEGREES)

    # 夾緊至合法範圍 0–149（保護上界邊緣）
    # Clamp to valid range [0, 149] to guard against rounding at exactly 30°.
    raw_index = max(0, min(raw_index, 149))

    # ── 按性質映射 Nadi 序號 (Modality-based Nadi index mapping) ──
    if modality == "Movable":
        # 順序 1–150：raw_index 直接映射
        # Ascending order: raw_index 0 → Nadi 1, raw_index 149 → Nadi 150
        nadi_1based = raw_index + 1

    elif modality == "Fixed":
        # 逆序 150–1：raw_index 0 → Nadi 150, raw_index 149 → Nadi 1
        # Descending order: first arc-segment maps to Nadi 150
        nadi_1based = 150 - raw_index

    else:  # Dual
        # 從第 76 個 Nadi 開始：76 → 150，接著 1 → 75
        # Starts at Nadi 76: raw_index 0 → Nadi 76, raw_index 74 → Nadi 150,
        #                     raw_index 75 → Nadi 1,  raw_index 149 → Nadi 75
        nadi_1based = ((raw_index + 75) % 150) + 1

    return NadiAmshaResult(
        nadi_index=nadi_1based,
        nadi_name=NADI_NAMES[nadi_1based - 1],
        modality=modality,
        sign_degree=sign_degree,
    )


def get_nadi_amsha_by_sign_index(
    sign_degree: float,
    sign_index: int,
) -> NadiAmshaResult:
    """
    便利函數：直接傳入星座索引 (0–11) 自動識別性質後計算 Nadi Amsha。
    Convenience wrapper: auto-detect modality from sign_index then compute.

    Parameters
    ----------
    sign_degree : float
        Planet's degree within the Rashi, [0°, 30°).
    sign_index : int
        Zero-based Rashi index (0 = Mesha … 11 = Meena).

    Returns
    -------
    NadiAmshaResult
    """
    modality = get_sign_modality(sign_index)
    return get_nadi_amsha(sign_degree, modality)
