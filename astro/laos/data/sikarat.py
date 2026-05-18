# astro/lao/data/sikarat.py
"""
老撾占星術 (ໄທຣາສາດລາວ) ສີກາດ 時辰／吉凶時段計算模組
ສີກາດ คือ 老撾傳統婆羅門式「色嘎」時段系統，用來判斷一天中各時段的吉凶
支援 ສີກາດລາວ、ສີກາດຝຣັ່ງ、ສີກາດຈູລະ、ສີກາດມະຫາ 四種體系
"""

from datetime import datetime
from typing import Dict, Any, Tuple
from .constants import SIKARAT_NAMES, LAO_WEEKDAYS, get_weekday_name


# ==================== ສີກາດ 基礎表格（書中第36頁核心） ====================
SIKARAT_PERIODS: Dict[int, Dict[str, str]] = {
    0: {  # 凌晨～清晨
        "ສີກາດລາວ": "✅ ດີຫຼາຍ (ເວລາບູຊາ)",
        "ສີກາດຝຣັ່ງ": "⚠️ ປານກາງ",
        "ສີກາດຈູລະ": "✅ ດີ",
        "ສີກາດມະຫາ": "❌ ອັນຕະລາຍ",
    },
    1: {  # 上午
        "ສີກາດລາວ": "✅ ດີ",
        "ສີກາດຝຣັ່ງ": "✅ ດີຫຼາຍ",
        "ສີກາດຈູລະ": "⚠️ ປານກາງ",
        "ສີກາດມະຫາ": "✅ ດີ",
    },
    2: {  # 中午
        "ສີກາດລາວ": "⚠️ ປານກາງ",
        "ສີກາດຝຣັ່ງ": "❌ ອັນຕະລາຍ",
        "ສີກາດຈູລະ": "✅ ດີຫຼາຍ",
        "ສີກາດມະຫາ": "✅ ດີ",
    },
    3: {  # 下午
        "ສີກາດລາວ": "✅ ດີ",
        "ສີກາດຝຣັ່ງ": "✅ ດີ",
        "ສີກາດຈູລະ": "❌ ອັນຕະລາຍ",
        "ສີກາດມະຫາ": "⚠️ ປານກາງ",
    },
}

# 更細時段（小時為單位，書中第45–59頁擴展）
SIKARAT_HOUR_TABLE: Dict[int, str] = {
    0: "ສີກາດລາວ", 1: "ສີກາດລາວ", 2: "ສີກາດຝຣັ່ງ",
    3: "ສີກາດຝຣັ່ງ", 4: "ສີກາດຝຣັ່ງ", 5: "ສີກາດຈູລະ",
    6: "ສີກາດຈູລະ", 7: "ສີກາດມະຫາ", 8: "ສີກາດມະຫາ",
    9: "ສີກາດລາວ", 10: "ສີກາດລາວ", 11: "ສີກາດຝຣັ່ງ",
    12: "ສີກາດຝຣັ່ງ", 13: "ສີກາດຈູລະ", 14: "ສີກາດຈູລະ",
    15: "ສີກາດມະຫາ", 16: "ສີກາດມະຫາ", 17: "ສີກາດລາວ",
    18: "ສີກາດລາວ", 19: "ສີກາດຝຣັ່ງ", 20: "ສີກາດຝຣັ່ງ",
    21: "ສີກາດຈູລະ", 22: "ສີກາດຈູລະ", 23: "ສີກາດມະຫາ",
}


def get_sikarat_by_hour(hour: int, sikarat_type: str = "ສີກາດລາວ") -> Dict[str, str]:
    """
    根據小時取得該時段的 ສີກາດ 吉凶
    hour: 0-23
    """
    if not 0 <= hour <= 23:
        raise ValueError("小時必須在 0-23 之間")
    
    period = SIKARAT_HOUR_TABLE.get(hour % 24, "ສີກາດລາວ")
    status = SIKARAT_PERIODS.get((hour // 6) % 4, {}).get(sikarat_type, "❓ ບໍ່ມີຂໍ້ມູນ")
    
    return {
        "hour": hour,
        "sikarat_type": sikarat_type,
        "period_name": period,
        "status": status,
        "recommendation": f"{period} - {status}"
    }


def get_sikarat_for_datetime(dt: datetime, sikarat_type: str = "ສີກາດລາວ") -> Dict[str, Any]:
    """
    根據完整 datetime 取得 ສີກາດ 資訊（推薦在 calculator.py 使用）
    """
    info = {
        "gregorian_time": dt.isoformat(),
        "hour": dt.hour,
        "minute": dt.minute,
        "weekday": get_weekday_name(dt.weekday()),
    }
    
    sikarat_info = get_sikarat_by_hour(dt.hour, sikarat_type)
    info.update(sikarat_info)
    return info


def get_best_sikarat_hours(activity: str = "一般") -> list:
    """
    快速取得當日適合某活動的 ສີກາດ 時段（未來可依活動擴充）
    目前返回吉時列表
    """
    good_hours = []
    for h in range(24):
        result = get_sikarat_by_hour(h, "ສີກາດລາວ")
        if "✅" in result["status"]:
            good_hours.append(f"{h:02d}:00 - {result['status']}")
    return good_hours[:6]  # 取前6個最佳時段


# ==================== 公開介面 ====================
__all__ = [
    "SIKARAT_PERIODS",
    "SIKARAT_HOUR_TABLE",
    "get_sikarat_by_hour",
    "get_sikarat_for_datetime",
    "get_best_sikarat_hours",
    "SIKARAT_NAMES",
]


# 測試用
if __name__ == "__main__":
    from datetime import datetime
    now = datetime.now()
    print("=== 當前 ສີກາດ 時段 ===")
    print(get_sikarat_for_datetime(now))
    print("\n今日適合活動的最佳時段：")
    print(get_best_sikarat_hours())
