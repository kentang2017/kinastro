# astro/lao/data/constants.py
"""
老撾占星術 (ໄທຣາສາດລາວ) 基礎常數表
嚴格對應書中 ວັນ・ເດືອນ・ປີ・ສີກາດ 章節
"""

# ==================== 1. 星期 (ວັນ) ====================
LAO_WEEKDAYS = {
    0: "ວັນອາທິດ",      # Sunday
    1: "ວັນຈັນ",        # Monday
    2: "ວັນອັງຄານ",      # Tuesday
    3: "ວັນພຸດ",         # Wednesday
    4: "ວັນພະຫັດ",       # Thursday
    5: "ວັນສຸກ",         # Friday
    6: "ວັນສົບ",         # Saturday
}

LAO_WEEKDAYS_SHORT = {
    0: "ອາ.", 1: "ຈ.", 2: "ອ.", 3: "ພ.", 4: "ພຫ.", 5: "ສຸ.", 6: "ສົບ."
}

# ==================== 2. 月份 (ເດືອນ) ====================
LAO_MONTHS = {
    1: "ເດືອນມັງກອນ",      # January
    2: "ເດືອນກຸມພາ",       # February
    3: "ເດືອນມີນາ",        # March
    4: "ເດືອນເມສາ",        # April
    5: "ເດືອນພຶດສະພາ",     # May
    6: "ເດືອນມິຖຸນາ",      # June
    7: "ເດືອນກໍລະກົດ",     # July
    8: "ເດືອນສິງຫາ",       # August
    9: "ເດືອນກັນຍາ",       # September
    10: "ເດືອນຕຸລາ",       # October
    11: "ເດືອນພະຈິກ",      # November
    12: "ເດືອນທັນວາ",      # December
}

# ==================== 3. 季節 (ລະດູ) ====================
LAO_SEASONS = {
    1: "ລະດູໜາວ",    # 冷季 (11-2月)
    2: "ລະດູຝົນ",     # 雨季 (5-10月)
    3: "ລະດູແຫ້ງ",    # 旱季 (3-4月)
}

# ==================== 4. 特殊年份規則 (ປີອະທິກະ...) ====================
SPECIAL_YEAR_CYCLES = {
    "ອະທິກະສຸຣະທິບ": {          # Adhikasurathib
        "cycle": 11,
        "offset": 0,
        "description": "ປີເພີ່ມສຸຣະທິບ (11 ປີມີ 1 ປີ)"
    },
    "ອະທິກະມາດ": {              # Adhikamat
        "cycle": 7,
        "offset": 2,
        "description": "ປີເພີ່ມມາດ (7 ປີມີ 1 ປີ)"
    },
    "ອະທິກະອານ": {               # Adhikawan
        "cycle": 19,
        "offset": 5,
        "description": "ປີເພີ່ມອານ (19 ປີມີ 1 ປີ)"
    },
}

BUDDHIST_ERA_OFFSET = 543   # ພ.ສ. = ค.ศ. + 543 (老撾/泰國佛曆)

# ==================== 5. 色嘎週期 (ສີກາດ) ====================
SIKARAT_CYCLE = [
    # 書中第36頁完整色嘎表（簡化為常用值，可後續擴充）
    "ສີກາດລາວ", "ສີກາດຝຣັ່ງ", "ສີກາດຈູລະ", "ສີກາດມະຫາ"
]

SIKARAT_NAMES = {
    0: "ສີກາດລາວ",
    1: "ສີກາດຝຣັ່ງ",
    2: "ສີກາດຈູລະ",
    3: "ສີກາດມະຫາ",
}

# ==================== 6. 其他核心常數 ====================
LAO_CALENDAR_RULES = {
    "default_era": "ພ.ສ.",           # 佛曆
    "gregorian_offset": -543,
    "days_in_month": [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    "leap_month_rule": "ອະທິກະມາດ",   # 閏月規則
}

# ==================== 7. 符號與顯示 ====================
LAO_ASTRO_EMOJIS = {
    "sun": "☀️",
    "moon": "🌕",
    "planet": "🪐",
    "wheel": "🌀",
    "good": "✅",
    "bad": "❌",
}

# ==================== 工具函數 ====================
def get_weekday_name(day: int, short: bool = False) -> str:
    """取得老撾星期名稱"""
    if short:
        return LAO_WEEKDAYS_SHORT.get(day % 7, "未知")
    return LAO_WEEKDAYS.get(day % 7, "未知")

def get_month_name(month: int) -> str:
    """取得老撾月份名稱"""
    return LAO_MONTHS.get(month, f"ເດືອນ{month}")

def is_special_year(year: int) -> dict:
    """判斷是否為特殊年份"""
    results = {}
    for name, rule in SPECIAL_YEAR_CYCLES.items():
        if (year - rule["offset"]) % rule["cycle"] == 0:
            results[name] = rule
    return results


# 讓 from .constants import * 可以正常運作
__all__ = [
    "LAO_WEEKDAYS", "LAO_WEEKDAYS_SHORT",
    "LAO_MONTHS", "LAO_SEASONS",
    "SPECIAL_YEAR_CYCLES", "BUDDHIST_ERA_OFFSET",
    "SIKARAT_CYCLE", "SIKARAT_NAMES",
    "LAO_CALENDAR_RULES", "LAO_ASTRO_EMOJIS",
    "get_weekday_name", "get_month_name", "is_special_year",
]
