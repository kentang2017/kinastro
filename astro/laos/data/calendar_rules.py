# astro/lao/data/calendar_rules.py
"""
老撾占星術 (ໄທຣາສາດລາວ) 曆法轉換規則模組
負責 ວັນ・ເດືອນ・ປີ・ສີກາດ 的完整轉換與資訊提取
"""

from datetime import date
from typing import Dict, Any, Optional
from .constants import (
    LAO_WEEKDAYS,
    LAO_MONTHS,
    get_weekday_name,
    get_month_name,
    BUDDHIST_ERA_OFFSET,
    LAO_CALENDAR_RULES,
    LAO_SEASONS,
)
from .special_years import (
    get_lao_year_from_gregorian,
    analyze_special_year,
)


def gregorian_to_lao(greg_date: date) -> Dict[str, Any]:
    """
    將西曆日期轉換為老撾傳統日期資訊（核心函數）
    """
    lao_year = get_lao_year_from_gregorian(greg_date.year)
    month = greg_date.month
    day = greg_date.day
    weekday_num = greg_date.weekday()

    # 季節判斷（書中第1章）
    if month in [11, 12, 1, 2]:
        season = LAO_SEASONS[1]  # ລະດູໜາວ
    elif month in [5, 6, 7, 8, 9, 10]:
        season = LAO_SEASONS[2]  # ລະດູຝົນ
    else:
        season = LAO_SEASONS[3]  # ລະດູແຫ້ງ

    special_info = analyze_special_year(lao_year, era="lao")

    return {
        "gregorian_date": greg_date.isoformat(),
        "lao_year": lao_year,
        "lao_year_display": f"ພ.ສ. {lao_year}",
        "lao_month": month,
        "lao_month_name": get_month_name(month),
        "lao_day": day,
        "weekday_num": weekday_num,
        "weekday_lao": get_weekday_name(weekday_num),
        "weekday_lao_short": get_weekday_name(weekday_num, short=True),
        "season": season,
        "is_special_year": special_info["is_special"],
        "special_types": special_info["special_types"],
        "full_lao_date": f"{day} {get_month_name(month)} ພ.ສ. {lao_year}",
        "full_lao_date_with_weekday": f"{get_weekday_name(weekday_num)} {day} {get_month_name(month)} ພ.ສ. {lao_year}",
    }


def lao_to_gregorian(lao_year: int, lao_month: int, lao_day: int) -> Optional[date]:
    """
    老撾佛曆日期轉西曆日期（簡化版，實際使用時可再精準調整）
    """
    try:
        greg_year = lao_year - BUDDHIST_ERA_OFFSET
        return date(greg_year, lao_month, lao_day)
    except ValueError:
        return None


def get_lao_date_info(greg_date: date) -> Dict[str, Any]:
    """
    取得老撾日期的完整占星資訊（推薦在 calculator.py 中呼叫）
    包含 ວັນ、ເດືອນ、ປີ、季節、特殊年份等
    """
    base_info = gregorian_to_lao(greg_date)

    # 未來可在此擴充 ສີກາດ、ປະຕິທິນ 吉凶 等（已預留介面）
    return {
        **base_info,
        "calendar_type": "ໄທຣາສາດລາວ",
        "era": LAO_CALENDAR_RULES["default_era"],
    }


def is_valid_lao_date(lao_year: int, lao_month: int, lao_day: int) -> bool:
    """驗證老撾日期是否合法"""
    if not (1 <= lao_month <= 12):
        return False
    if not (1 <= lao_day <= 31):
        return False
    try:
        greg_date = lao_to_gregorian(lao_year, lao_month, lao_day)
        return greg_date is not None
    except:
        return False


# ==================== 測試與開發用 ====================
if __name__ == "__main__":
    today = date.today()
    info = get_lao_date_info(today)
    print("=== 今日老撾占星日期資訊 ===")
    for k, v in info.items():
        if not isinstance(v, dict):
            print(f"{k}: {v}")
    print("\n特殊年份:", info["special_types"])
