"""
Ancient Egyptian Civil Calendar & Astronomical Calculations
古埃及民用曆法與天文計算模組

Implements:
- Egyptian civil calendar (三季曆法): 3 seasons × 4 months × 30 days + 5 epagomenal days
- Night hours (夜間十二時): 12 decan-ruled hours of darkness
- Diagonal star table (對角星表): 12×36 decan-to-hour mapping
- Heliacal rising approximations for each decan
- Visibility / invisibility cycles (Duat period)
- Sothic cycle reference data (天狼星週期)
- Modern star identifications (Neugebauer & Parker)
- Ramesside transit star clocks (拉美西斯過境星鐘)

Pure computation module — no Streamlit dependency.

Sources:
    Neugebauer & Parker, "Egyptian Astronomical Texts" (EAT) I–III.
    R. A. Parker, "The Calendars of Ancient Egypt" (1950).
    Marshall Clagett, "Ancient Egyptian Science, Vol. II" (1995).
    Censorinus, "De Die Natali" (238 CE).
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Optional

from astro.decans_data import DECANS_DATA

# ============================================================
# Constants
# ============================================================

# Gregorian date of the Egyptian New Year (Wepet Renpet) for our
# reference frame.  Historically this corresponded to the heliacal
# rising of Sirius at Memphis (~30°N), Julian July 19.
# In the proleptic Gregorian calendar for the modern era this is
# approximately July 20.  We use July 20 as our fixed anchor.
_EGYPTIAN_NEW_YEAR_MONTH = 7
_EGYPTIAN_NEW_YEAR_DAY = 20

# Non-leap reference year used to keep the civil year exactly 365 days.
_REFERENCE_YEAR = 2023

# Sothic cycle length
SOTHIC_CYCLE_YEARS = 1461  # Egyptian civil years (= 1460 Julian years)

# Sirius heliacal rising for latitude ~30°N (Memphis / Cairo)
SIRIUS_HELIACAL_RISING_LATITUDE_30N: tuple[int, int] = (7, 19)

# ============================================================
# Season & Month Data
# ============================================================

_SEASONS: list[dict] = [
    {
        "name_en": "Akhet",
        "name_cn": "泛濫季",
        "meaning_en": "Inundation",
        "emoji": "🌊",
        "months": (1, 4),
    },
    {
        "name_en": "Peret",
        "name_cn": "生長季",
        "meaning_en": "Growth",
        "emoji": "🌱",
        "months": (5, 8),
    },
    {
        "name_en": "Shemu",
        "name_cn": "收穫季",
        "meaning_en": "Harvest",
        "emoji": "🌾",
        "months": (9, 12),
    },
]

_MONTH_NAMES_EN: list[str] = [
    "Thoth", "Phaophi", "Athyr", "Choiak",       # Akhet
    "Tybi", "Mechir", "Phamenoth", "Pharmuthi",   # Peret
    "Pachons", "Payni", "Epiphi", "Mesore",        # Shemu
]

_MONTH_NAMES_CN: list[str] = [
    "透特月", "帕奧斐月", "阿提爾月", "科伊阿克月",
    "提比月", "墨契爾月", "法梅諾特月", "法爾穆提月",
    "帕孔斯月", "帕伊尼月", "伊皮斐月", "梅索雷月",
]

# ============================================================
# Epagomenal Days Data (五日節)
# ============================================================

_EPAGOMENAL_DEITIES: list[dict] = [
    {
        "deity_en": "Osiris",
        "deity_cn": "歐西里斯",
        "story_en": (
            "Osiris, Lord of the Dead, was the first king of Egypt and "
            "bringer of civilisation. Murdered by his brother Set and "
            "resurrected by Isis, he became eternal ruler of the Duat, "
            "embodying the promise of rebirth for all."
        ),
        "story_cn": (
            "歐西里斯，亡者之主，是埃及的第一位國王與文明的帶來者。"
            "他被兄弟塞特殺害，由伊西斯復活後，成為冥界的永恆統治者，"
            "象徵著一切生命重生的承諾。"
        ),
    },
    {
        "deity_en": "Horus the Elder",
        "deity_cn": "老荷魯斯",
        "story_en": (
            "Horus the Elder is the great sky god whose eyes are the Sun "
            "and Moon. As protector of Egypt, he maintains cosmic order "
            "and was invoked as guardian at the boundaries of the year."
        ),
        "story_cn": (
            "老荷魯斯是偉大的天空之神，雙眼即太陽與月亮。"
            "作為埃及的守護者，他維護宇宙秩序，"
            "在年末之際被召喚為歲界的守衛。"
        ),
    },
    {
        "deity_en": "Set",
        "deity_cn": "塞特",
        "story_en": (
            "Set, god of chaos, storms and the desert, represents the "
            "necessary force of disruption. His birth on the third "
            "epagomenal day was considered inauspicious, yet his strength "
            "defended Ra's solar barque against the serpent Apophis each night."
        ),
        "story_cn": (
            "塞特，混沌、風暴與沙漠之神，代表必要的破壞力量。"
            "他在五日節第三天的誕生被視為不吉，"
            "然而他的力量每夜保護拉的太陽船抵禦巨蛇阿波菲斯。"
        ),
    },
    {
        "deity_en": "Isis",
        "deity_cn": "伊西斯",
        "story_en": (
            "Isis, Great Mother and goddess of magic and wisdom, "
            "reassembled the body of Osiris and conceived Horus. "
            "Her mastery of heka (magic) made her the most powerful "
            "of all deities, protector of the living and the dead."
        ),
        "story_cn": (
            "伊西斯，偉大的母親與魔法智慧女神，"
            "重組了歐西里斯的遺體並孕育了荷魯斯。"
            "她對赫卡（魔法）的精通使她成為最強大的神祇，"
            "守護生者與亡者。"
        ),
    },
    {
        "deity_en": "Nephthys",
        "deity_cn": "奈芙蒂斯",
        "story_en": (
            "Nephthys, guardian of the dead and protector of the canopic "
            "jars, stood vigil at the funerary bier alongside Isis. "
            "She guided souls through the darkness of the Duat toward "
            "their final judgement before Osiris."
        ),
        "story_cn": (
            "奈芙蒂斯，亡者的守護者與卡諾卜罐的保護者，"
            "與伊西斯一同在靈柩旁守夜。"
            "她引導靈魂穿越冥界的黑暗，走向歐西里斯面前的終審。"
        ),
    },
]

# ============================================================
# Night Hour Names
# ============================================================

_NIGHT_HOUR_NAMES_EN: list[str] = [
    "First Hour of Night",
    "Second Hour of Night",
    "Third Hour of Night",
    "Fourth Hour of Night",
    "Fifth Hour of Night",
    "Sixth Hour of Night",
    "Seventh Hour of Night",
    "Eighth Hour of Night",
    "Ninth Hour of Night",
    "Tenth Hour of Night",
    "Eleventh Hour of Night",
    "Twelfth Hour of Night",
]

_NIGHT_HOUR_NAMES_CN: list[str] = [
    "夜之第一時",
    "夜之第二時",
    "夜之第三時",
    "夜之第四時",
    "夜之第五時",
    "夜之第六時",
    "夜之第七時",
    "夜之第八時",
    "夜之第九時",
    "夜之第十時",
    "夜之第十一時",
    "夜之第十二時",
]

# ============================================================
# Modern Star Identifications (Neugebauer & Parker)
# ============================================================

MODERN_STAR_IDS: dict[int, dict] = {
    0:  {"star_en": "α Trianguli area", "star_cn": "三角座α區域",
         "constellation_en": "Triangulum", "constellation_cn": "三角座",
         "certainty": "uncertain"},
    1:  {"star_en": "uncertain, near Triangulum", "star_cn": "不確定，三角座附近",
         "constellation_en": "Triangulum", "constellation_cn": "三角座",
         "certainty": "uncertain"},
    2:  {"star_en": "Pleiades area", "star_cn": "昴宿星團區域",
         "constellation_en": "Taurus", "constellation_cn": "金牛座",
         "certainty": "probable"},
    3:  {"star_en": "Hyades area", "star_cn": "畢宿星團區域",
         "constellation_en": "Taurus", "constellation_cn": "金牛座",
         "certainty": "probable"},
    4:  {"star_en": "near α Tauri (Aldebaran)", "star_cn": "畢宿五（金牛座α）附近",
         "constellation_en": "Taurus", "constellation_cn": "金牛座",
         "certainty": "probable"},
    5:  {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Taurus-Orion", "constellation_cn": "金牛-獵戶座",
         "certainty": "uncertain"},
    6:  {"star_en": "uncertain, Orion area", "star_cn": "不確定，獵戶座區域",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "uncertain"},
    7:  {"star_en": "near δ Orionis", "star_cn": "參宿一（獵戶座δ）附近",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "probable"},
    8:  {"star_en": "near ε Orionis", "star_cn": "參宿二（獵戶座ε）附近",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "probable"},
    9:  {"star_en": "near α Centauri or α Columbae",
         "star_cn": "南門二或天鴿座α附近",
         "constellation_en": "Centaurus or Columba",
         "constellation_cn": "半人馬座或天鴿座",
         "certainty": "debated"},
    10: {"star_en": "uncertain, near Canis Major", "star_cn": "不確定，大犬座附近",
         "constellation_en": "Canis Major", "constellation_cn": "大犬座",
         "certainty": "uncertain"},
    11: {"star_en": "uncertain, Puppis area", "star_cn": "不確定，船尾座區域",
         "constellation_en": "Puppis", "constellation_cn": "船尾座",
         "certainty": "uncertain"},
    12: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Puppis-Vela", "constellation_cn": "船尾-船帆座",
         "certainty": "uncertain"},
    13: {"star_en": "near α Cancri", "star_cn": "巨蟹座α附近",
         "constellation_en": "Cancer", "constellation_cn": "巨蟹座",
         "certainty": "uncertain"},
    14: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Cancer-Leo", "constellation_cn": "巨蟹-獅子座",
         "certainty": "uncertain"},
    15: {"star_en": "uncertain, near Leo", "star_cn": "不確定，獅子座附近",
         "constellation_en": "Leo", "constellation_cn": "獅子座",
         "certainty": "uncertain"},
    16: {"star_en": "uncertain, near Leo", "star_cn": "不確定，獅子座附近",
         "constellation_en": "Leo", "constellation_cn": "獅子座",
         "certainty": "uncertain"},
    17: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Leo-Virgo", "constellation_cn": "獅子-處女座",
         "certainty": "uncertain"},
    18: {"star_en": "uncertain, near Virgo", "star_cn": "不確定，處女座附近",
         "constellation_en": "Virgo", "constellation_cn": "處女座",
         "certainty": "uncertain"},
    19: {"star_en": "near Spica (α Virginis)", "star_cn": "角宿一（處女座α）附近",
         "constellation_en": "Virgo", "constellation_cn": "處女座",
         "certainty": "probable"},
    20: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Virgo-Libra", "constellation_cn": "處女-天秤座",
         "certainty": "uncertain"},
    21: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Libra-Scorpius", "constellation_cn": "天秤-天蠍座",
         "certainty": "uncertain"},
    22: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Scorpius", "constellation_cn": "天蠍座",
         "certainty": "uncertain"},
    23: {"star_en": "near Antares (α Scorpii)", "star_cn": "心宿二（天蠍座α）附近",
         "constellation_en": "Scorpius", "constellation_cn": "天蠍座",
         "certainty": "probable"},
    24: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Sagittarius", "constellation_cn": "射手座",
         "certainty": "uncertain"},
    25: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Sagittarius", "constellation_cn": "射手座",
         "certainty": "uncertain"},
    26: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Sagittarius-Capricornus",
         "constellation_cn": "射手-摩羯座",
         "certainty": "uncertain"},
    27: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Capricornus-Aquarius",
         "constellation_cn": "摩羯-水瓶座",
         "certainty": "uncertain"},
    28: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Aquarius", "constellation_cn": "水瓶座",
         "certainty": "uncertain"},
    29: {"star_en": "uncertain", "star_cn": "不確定",
         "constellation_en": "Aquarius-Pisces", "constellation_cn": "水瓶-雙魚座",
         "certainty": "uncertain"},
    30: {"star_en": "near α or κ Orionis (Upper Arm of Orion)",
         "star_cn": "參宿四或獵戶座κ附近（獵戶上臂）",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "probable"},
    31: {"star_en": "near β Orionis (Rigel, Lower Arm of Orion)",
         "star_cn": "參宿七（獵戶座β，獵戶下臂）附近",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "probable"},
    32: {"star_en": "near Orion's Belt area", "star_cn": "獵戶腰帶區域附近",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "probable"},
    33: {"star_en": "near Procyon (α Canis Minoris)",
         "star_cn": "南河三（小犬座α）附近",
         "constellation_en": "Canis Minor", "constellation_cn": "小犬座",
         "certainty": "probable"},
    34: {"star_en": "Orion (constellation as a whole)",
         "star_cn": "獵戶座（整體星座）",
         "constellation_en": "Orion", "constellation_cn": "獵戶座",
         "certainty": "confirmed"},
    35: {"star_en": "near Sirius (α Canis Majoris)",
         "star_cn": "天狼星（大犬座α）附近",
         "constellation_en": "Canis Major", "constellation_cn": "大犬座",
         "certainty": "confirmed"},
}

# ============================================================
# 1. Egyptian Civil Calendar  (三季曆法)
# ============================================================


def _egyptian_new_year(year: int) -> date:
    """Return the Gregorian date of the Egyptian New Year for *year*."""
    return date(year, _EGYPTIAN_NEW_YEAR_MONTH, _EGYPTIAN_NEW_YEAR_DAY)


def gregorian_to_egyptian(month: int, day: int) -> dict:
    """Convert a Gregorian month/day to the Egyptian civil calendar.

    The conversion is independent of the Gregorian year because the
    Egyptian civil year is always 365 days and we anchor it to a fixed
    Gregorian start date (July 20).

    Parameters
    ----------
    month : int
        Gregorian month (1-12).
    day : int
        Gregorian day of month.

    Returns
    -------
    dict
        Egyptian calendar information including season, month, decade,
        day-of-year, and epagomenal-day details when applicable.
    """
    # Use a non-leap reference year so the civil year is exactly 365 days.
    ref_year = _REFERENCE_YEAR
    target = date(ref_year, month, day)
    new_year = _egyptian_new_year(ref_year)

    # Handle dates before July 20 → they belong to the previous Egyptian year
    if target < new_year:
        new_year = _egyptian_new_year(ref_year - 1)

    day_of_year: int = (target - new_year).days + 1  # 1-based

    # Epagomenal days (五日節): days 361-365
    if day_of_year > 360:
        epag_day = day_of_year - 360  # 1-5
        deity_info = _EPAGOMENAL_DEITIES[epag_day - 1]
        return {
            "season_en": "Epagomenal Days",
            "season_cn": "五日節",
            "season_emoji": "🎭",
            "month_number": None,
            "month_name_en": "Epagomenal",
            "month_name_cn": "五日節",
            "day_in_month": None,
            "decade": None,
            "day_of_year": day_of_year,
            "is_epagomenal": True,
            "epagomenal_day": epag_day,
            "epagomenal_deity_en": deity_info["deity_en"],
            "epagomenal_deity_cn": deity_info["deity_cn"],
            "epagomenal_story_en": deity_info["story_en"],
            "epagomenal_story_cn": deity_info["story_cn"],
        }

    # Regular month days
    month_index = (day_of_year - 1) // 30          # 0-11
    day_in_month = (day_of_year - 1) % 30 + 1      # 1-30
    month_number = month_index + 1                  # 1-12
    decade = (day_in_month - 1) // 10 + 1           # 1-3

    season_index = month_index // 4                 # 0-2
    season = _SEASONS[season_index]

    return {
        "season_en": season["name_en"],
        "season_cn": season["name_cn"],
        "season_emoji": season["emoji"],
        "month_number": month_number,
        "month_name_en": _MONTH_NAMES_EN[month_index],
        "month_name_cn": _MONTH_NAMES_CN[month_index],
        "day_in_month": day_in_month,
        "decade": decade,
        "day_of_year": day_of_year,
        "is_epagomenal": False,
        "epagomenal_day": None,
        "epagomenal_deity_en": None,
        "epagomenal_deity_cn": None,
        "epagomenal_story_en": None,
        "epagomenal_story_cn": None,
    }


# ============================================================
# 2. Night Hours  (夜間十二時)
# ============================================================


def get_night_hours(decan_index: int) -> list[dict]:
    """Return the 12 decan-ruled night hours for a given decade.

    The decan whose heliacal rising has just occurred rules the first
    hour of night.  Each subsequent hour is ruled by the next decan in
    the 36-decan sequence.

    Parameters
    ----------
    decan_index : int
        Index (0-35) of the decan whose heliacal rising marks the
        current 10-day period (decade).

    Returns
    -------
    list[dict]
        Twelve dicts, one per night hour, each containing:
        ``hour``, ``decan_index``, ``decan_name``,
        ``hour_name_en``, ``hour_name_cn``.
    """
    hours: list[dict] = []
    for h in range(12):
        d_idx = (decan_index + h) % 36
        hours.append({
            "hour": h + 1,
            "decan_index": d_idx,
            "decan_name": DECANS_DATA[d_idx]["egyptian_name"],
            "hour_name_en": _NIGHT_HOUR_NAMES_EN[h],
            "hour_name_cn": _NIGHT_HOUR_NAMES_CN[h],
        })
    return hours


# ============================================================
# 3. Diagonal Star Table  (對角星表)
# ============================================================


def build_diagonal_star_table() -> list[list[int]]:
    """Build a 12×36 diagonal star table.

    ``table[h][d]`` gives the decan index (0-35) of the star that
    rules night hour *h* (0-11, where 0 = first hour) during decade
    *d* (0-35).

    The characteristic diagonal shift arises because each decade a new
    decan has its heliacal rising, pushing the sequence forward by one
    position.

    Formula::

        table[h][d] = (d - (11 - h)) % 36

    Returns
    -------
    list[list[int]]
        12 rows (hours) × 36 columns (decades).
    """
    table: list[list[int]] = []
    for h in range(12):
        row: list[int] = []
        for d in range(36):
            row.append((d - (11 - h)) % 36)
        table.append(row)
    return table


# ============================================================
# 4. Heliacal Rising Dates
# ============================================================

# Reference anchor: decan 35 (Tepy-a-Sapet / "Forepart of Sothis")
# rises around July 19 (Julian) ≈ July 19 Gregorian for antiquity.
# Decan 0 rises ~10 days later (July 29).  Each subsequent decan adds
# another 10 days.
_DECAN_0_RISING = date(2000, 7, 29)  # arbitrary year, only month/day matter


def get_heliacal_rising_approx(decan_index: int) -> tuple[int, int]:
    """Return the approximate heliacal rising date for a decan.

    Parameters
    ----------
    decan_index : int
        Decan index (0-35).

    Returns
    -------
    tuple[int, int]
        ``(month, day)`` of the approximate Gregorian heliacal rising.
    """
    rising_date = _DECAN_0_RISING + timedelta(days=10 * decan_index)
    # Wrap around the year boundary if needed
    if rising_date.year != _DECAN_0_RISING.year:
        rising_date = rising_date.replace(year=_DECAN_0_RISING.year)
    return (rising_date.month, rising_date.day)


# ============================================================
# 5. Visibility Cycle
# ============================================================


def _add_days_to_month_day(month: int, day: int, days: int) -> tuple[int, int]:
    """Add *days* to a (month, day) using a non-leap reference year."""
    ref = date(2023, month, day) + timedelta(days=days)
    return (ref.month, ref.day)


def get_visibility_cycle(decan_index: int) -> dict:
    """Return the approximate visibility cycle for a decan star.

    The Egyptian model associates ~270 days of visibility with ~70 days
    of invisibility (the "Duat period"), which mirrors the 70-day
    mummification ritual.  Remaining days account for transitional
    phases near the horizons.

    Parameters
    ----------
    decan_index : int
        Decan index (0-35).

    Returns
    -------
    dict
        Visibility cycle data including rising/setting dates and
        cultural significance of the Duat period.
    """
    rising = get_heliacal_rising_approx(decan_index)
    visible_end = _add_days_to_month_day(rising[0], rising[1], 270)
    invisible_start = _add_days_to_month_day(visible_end[0], visible_end[1], 1)
    invisible_end = _add_days_to_month_day(rising[0], rising[1], -1)

    return {
        "heliacal_rising": rising,
        "visible_start": rising,
        "visible_end": visible_end,
        "invisible_start": invisible_start,
        "invisible_end": invisible_end,
        "visible_days": 270,
        "invisible_days": 70,
        "duat_meaning_en": (
            "The star descends into the Duat (underworld) for 70 days, "
            "mirroring the mummification period"
        ),
        "duat_meaning_cn": "此星降入冥界（杜阿特）70天，映射木乃伊化的過程",
        "rebirth_meaning_en": (
            "The heliacal rising marks the star's rebirth from the Duat, "
            "symbolising renewal"
        ),
        "rebirth_meaning_cn": "偕日升標誌著此星從冥界重生，象徵更新",
    }


# ============================================================
# 6. Sothic Cycle  (天狼星週期)
# ============================================================


def get_sothic_info() -> dict:
    """Return educational information about the Sothic cycle.

    Returns
    -------
    dict
        Descriptive data about the 1461-year Sothic cycle, its
        significance, and historically recorded Sothic risings.
    """
    return {
        "cycle_years": SOTHIC_CYCLE_YEARS,
        "description_en": (
            "The Sothic cycle is the period of approximately 1461 Egyptian "
            "civil years (1460 Julian years) required for the heliacal "
            "rising of Sirius to return to the same day of the Egyptian "
            "civil calendar. Because the civil year of 365 days lacks a "
            "leap-day correction, it drifts by one day every four years "
            "relative to the astronomical (Julian) year of 365.25 days."
        ),
        "description_cn": (
            "天狼星週期是指天狼星偕日升回到埃及民用曆同一天所需的約1461個"
            "埃及民用年（1460個儒略年）。由於民用年365天缺乏閏日校正，"
            "相對於365.25天的天文（儒略）年，每四年漂移一天。"
        ),
        "significance_en": (
            "The Sothic cycle is the cornerstone of Egyptian chronology. "
            "Ancient records of Sirius's heliacal rising on specific civil "
            "calendar dates allow modern scholars to anchor Egyptian "
            "historical events to absolute dates."
        ),
        "significance_cn": (
            "天狼星週期是埃及年代學的基石。古代關於天狼星在特定民用曆日期"
            "偕日升的記錄，使現代學者能夠將埃及歷史事件錨定為絕對日期。"
        ),
        "known_cycles": [
            {
                "year_bce": 2781,
                "description_en": (
                    "Probable start of a Sothic cycle; inferred from later "
                    "records and back-calculation."
                ),
                "description_cn": "一個天狼星週期的可能起點；由後期記錄反推。",
            },
            {
                "year_bce": 1321,
                "description_en": (
                    "Approximate Sothic rising alignment during the reign "
                    "of Ramesses I (19th Dynasty). The Ebers Papyrus "
                    "records a Sothic rising in regnal year 9 of "
                    "Amenhotep I, often dated near this cycle."
                ),
                "description_cn": (
                    "拉美西斯一世（第十九王朝）統治期間天狼星週期的大致"
                    "對齊。埃伯斯紙莎草記錄了阿蒙霍特普一世在位第九年的"
                    "天狼星偕日升，通常被追溯到此週期附近。"
                ),
            },
            {
                "year_ce": 139,
                "description_en": (
                    "Recorded by the Roman author Censorinus in his work "
                    "'De Die Natali' (238 CE). He notes that Sirius rose "
                    "heliacally on 1 Thoth in 139 CE, providing the most "
                    "reliable fixed point for the Sothic cycle."
                ),
                "description_cn": (
                    "由羅馬作家凱恩索里努斯在其著作《論生日》（公元238年）"
                    "中記錄。他指出天狼星在公元139年透特月一日偕日升，"
                    "提供了天狼星週期最可靠的固定參考點。"
                ),
            },
        ],
    }


# ============================================================
# 7. Modern Star Identifications
# ============================================================
# Exposed as the module-level constant ``MODERN_STAR_IDS`` (above).


# ============================================================
# 8. Ramesside Transit Star Clocks  (拉美西斯過境星鐘)
# ============================================================


def build_transit_star_table() -> dict:
    """Return data about the Ramesside-era transit star clocks.

    The Ramesside star clocks (found in royal tombs of the 20th Dynasty)
    replaced the older diagonal star tables.  Instead of heliacal
    risings, they tracked stars as they crossed (transited) the
    observer's meridian, using a seated human figure as the alignment
    reference.

    Returns
    -------
    dict
        Educational text, date range, methodology, differences from
        diagonal star tables, and a simplified sample table.
    """
    description_en = (
        "The Ramesside transit star clocks are a series of astronomical "
        "tables found on the ceilings of royal tombs from the 20th Dynasty "
        "(c. 1150-1069 BCE). They represent a significant evolution from "
        "the earlier diagonal star tables, using meridian transit "
        "observations rather than heliacal risings to mark the hours of "
        "the night."
    )
    description_cn = (
        "拉美西斯過境星鐘是一系列天文表，發現於第二十王朝（約公元前1150-1069年）"
        "皇家陵墓的天花板上。它們代表了對早期對角星表的重大改進，"
        "使用子午線過境觀測而非偕日升來標記夜間時辰。"
    )

    method_en = (
        "An observer sat facing a colleague who was aligned with the "
        "north-south meridian. The observer noted which stars passed over "
        "specific body positions of the seated figure — directly above "
        "the head, over the left or right ear, or over the left or right "
        "shoulder. Each transit marked a specific hour of the night. "
        "Thirteen body positions were used as reference points."
    )
    method_cn = (
        "觀測者面對一位與南北子午線對齊的同伴坐下。觀測者記錄哪些星星"
        "經過坐像的特定身體部位——正頭頂、左耳或右耳上方、左肩或右肩上方。"
        "每次過境標記夜間的一個特定時辰。共使用十三個身體部位作為參考點。"
    )

    differences_en = (
        "Unlike the diagonal star tables which tracked heliacal risings "
        "(first dawn appearances), the transit clocks observed stars "
        "crossing the meridian throughout the night. This method was more "
        "accurate and less affected by atmospheric conditions near the "
        "horizon. The transit clocks also used a different set of stars "
        "and divided the night into 13 intervals rather than 12."
    )
    differences_cn = (
        "與追蹤偕日升（黎明首次出現）的對角星表不同，過境星鐘觀測整夜"
        "星星穿越子午線的時刻。這種方法更準確，受地平線附近大氣條件的"
        "影響較小。過境星鐘還使用了不同的恆星組合，並將夜晚分為13個"
        "時段而非12個。"
    )

    # Simplified sample table: 13 body positions × 24 half-month periods.
    # Values are placeholder decan indices showing the general diagonal
    # pattern that characterises these clocks.
    sample_table: list[list[int]] = []
    for pos in range(13):
        row: list[int] = []
        for period in range(24):
            row.append((period + pos) % 36)
        sample_table.append(row)

    return {
        "description_en": description_en,
        "description_cn": description_cn,
        "method_en": method_en,
        "method_cn": method_cn,
        "date_range_en": "c. 1150-1069 BCE (20th Dynasty)",
        "date_range_cn": "約公元前1150-1069年（第二十王朝）",
        "differences_en": differences_en,
        "differences_cn": differences_cn,
        "sample_table": sample_table,
    }
