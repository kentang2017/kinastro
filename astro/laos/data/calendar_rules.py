"""
老撾占星術 (ໄທຣາສາດລາວ) 曆法轉換規則模組
Lao Calendar Rules Module

負責西曆 ↔ 老撾佛曆的轉換、星期、月份、季節、特殊年份等完整資訊提取
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
from .special_years import get_lao_year_from_gregorian, analyze_special_year


def gregorian_to_lao(greg_date: date) -> Dict[str, Any]:
    """
    將西曆日期轉換為老撾傳統日期資訊（核心函數）
    """
    lao_year = get_lao_year_from_gregorian(greg_date.year)
    month = greg_date.month
    day = greg_date.day
    weekday_num = greg_date.weekday()

    # 季節判斷（依據傳統老撾占星）
    if month in [11, 12, 1, 2]:
        season = LAO_SEASONS[1]  # ລະດູໜາວ - 冬季
        season_zh = "冬季"
    elif month in [5, 6, 7, 8, 9, 10]:
        season = LAO_SEASONS[2]  # ລະດູຝົນ - 雨季
        season_zh = "雨季"
    else:
        season = LAO_SEASONS[3]  # ລະດູແຫ້ງ - 旱季
        season_zh = "旱季"

    special_info = analyze_special_year(lao_year, era="lao")

    return {
        "gregorian_date": greg_date.isoformat(),
        "lao_year": lao_year,
        "lao_year_display": f"ພ.ສ. {lao_year}",
        "lao_year_display_zh": f"佛曆 {lao_year} 年",
        "lao_month": month,
        "lao_month_name": get_month_name(month),
        "lao_month_name_zh": LAO_MONTHS.get(month, {}).get("zh", ""),
        "lao_day": day,
        "weekday_num": weekday_num,
        "weekday_lao": get_weekday_name(weekday_num),
        "weekday_lao_short": get_weekday_name(weekday_num, short=True),
        "weekday_zh": LAO_WEEKDAYS[weekday_num]["zh"] if weekday_num in LAO_WEEKDAYS else "",
        "season": season,
        "season_zh": season_zh,
        "is_special_year": special_info.get("is_special", False),
        "special_types": special_info.get("special_types", []),
        "full_lao_date": f"{day} {get_month_name(month)} ພ.ສ. {lao_year}",
        "full_lao_date_zh": f"佛曆 {lao_year} 年 {get_month_name(month)} {day} 日",
        "full_lao_date_with_weekday": f"{get_weekday_name(weekday_num)} {day} {get_month_name(month)} ພ.ສ. {lao_year}",
        "full_lao_date_with_weekday_zh": f"{LAO_WEEKDAYS[weekday_num]['zh']} {get_month_name(month)} {day} 日 佛曆 {lao_year} 年",
    }


def lao_to_gregorian(lao_year: int, lao_month: int, lao_day: int) -> Optional[date]:
    """
    老撾佛曆日期轉西曆日期（簡化版）
    """
    try:
        greg_year = lao_year - BUDDHIST_ERA_OFFSET
        return date(greg_year, lao_month, lao_day)
    except ValueError:
        return None


def get_lao_date_info(greg_date: date) -> Dict[str, Any]:
    """
    取得老撾日期的完整占星資訊（推薦在 calculator.py 中呼叫）
    包含日期、星期、月份、季節、特殊年份等
    """
    base_info = gregorian_to_lao(greg_date)

    return {
        **base_info,
        "calendar_type": "ໄທຣາສາດລາວ",
        "calendar_type_zh": "老撾占星曆",
        "era": LAO_CALENDAR_RULES.get("default_era", "ພ.ສ."),
        "era_zh": "佛曆",
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
    except Exception:
        return False


def get_current_season(greg_date: date) -> Dict[str, str]:
    """單獨取得季節資訊"""
    month = greg_date.month
    if month in [11, 12, 1, 2]:
        return {"lao": LAO_SEASONS[1], "zh": "冬季"}
    elif month in [5, 6, 7, 8, 9, 10]:
        return {"lao": LAO_SEASONS[2], "zh": "雨季"}
    else:
        return {"lao": LAO_SEASONS[3], "zh": "旱季"}


# ==================== 測試與開發用 ====================
if __name__ == "__main__":
    today = date.today()
    info = get_lao_date_info(today)

    print("=== 今日老撾占星日期資訊 ===")
    print(f"西曆日期     : {info['gregorian_date']}")
    print(f"老撾佛曆     : {info['full_lao_date_with_weekday']}")
    print(f"中文顯示     : {info['full_lao_date_with_weekday_zh']}")
    print(f"季節         : {info['season']} ({info['season_zh']})")
    print(f"是否特殊年份 : {'是' if info['is_special_year'] else '否'}")
    if info['special_types']:
        print(f"特殊類型     : {info['special_types']}")

    print("\n=== 其他日期測試 ===")
    test_date = date(2026, 5, 20)
    print(get_lao_date_info(test_date)["full_lao_date_with_weekday_zh"])
