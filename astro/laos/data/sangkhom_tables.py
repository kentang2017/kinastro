# astro/lao/data/sangkhom_tables.py
"""
老撾占星術 (ໄທຣາສາດລາວ) ສັງຄົມ 吉凶擇日表格模組
包含結婚、建房、出行、開業、祭祀等常見 ສັງຄົມ 宜忌表
"""

from typing import Dict, Any, List, Optional
from datetime import date
from .constants import LAO_WEEKDAYS, get_weekday_name, LAO_MONTHS, get_month_name
from .calendar_rules import get_lao_date_info


# ==================== 核心 ສັງຄົມ 宜忌大表 ====================
# 格式：活動類型 → 星期/日期條件 → 吉凶 + 解說
SANGKHOM_TABLES: Dict[str, Dict[str, Dict[str, str]]] = {
    "ການແຕ່ງງານ": {  # 結婚
        "0": {"status": "✅ ດີ", "note": "ວັນອາທິດ - ເໝາະສົມທີ່ສຸດ"},   # Sunday
        "1": {"status": "✅ ດີ", "note": "ວັນຈັນ - ໄດ້ຮັບຄວາມສຸກ"},
        "2": {"status": "⚠️ ປານກາງ", "note": "ວັນອັງຄານ - ຕ້ອງລະມັດລະວັງ"},
        "3": {"status": "❌ ອາດເປັນອຸບັດເຫດ", "note": "ວັນພຸດ - ບໍ່ແນະນຳ"},
        "4": {"status": "✅ ດີຫຼາຍ", "note": "ວັນພະຫັດ - ມີໂຊກລາບ"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ຄວາມຮັກອົບອຸ່ນ"},
        "6": {"status": "⚠️ ປານກາງ", "note": "ວັນສົບ - ຕ້ອງເບິ່ງເວລາເພີ່ມ"},
    },

    "ການສ້າງເຮືອນ": {  # 建房 / 動土
        "0": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນອາທິດ - ບໍ່ເໝາະ"},
        "1": {"status": "✅ ດີຫຼາຍ", "note": "ວັນຈັນ - ມີຄວາມສະຖິດສະຖຽນ"},
        "2": {"status": "⚠️ ປານກາງ", "note": "ວັນອັງຄານ - ຕ້ອງຫຼົດຮູບ"},
        "3": {"status": "✅ ດີ", "note": "ວັນພຸດ - ເໝາະສົມ"},
        "4": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນພະຫັດ - ບໍ່ແນະນຳ"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ໄດ້ຮັບຄວາມອຸ່ນອົບ"},
        "6": {"status": "✅ ດີຫຼາຍ", "note": "ວັນສົບ - ມີໂຊກລາບ"},
    },

    "ການເດີນທາງ": {  # 出行
        "0": {"status": "✅ ດີ", "note": "ວັນອາທິດ - ປອດໄພ"},
        "1": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນຈັນ - ງ່າຍຕິດຂັດ"},
        "2": {"status": "✅ ດີ", "note": "ວັນອັງຄານ - ສຳເລັດຕາມຄວາມປາຖະໜາ"},
        "3": {"status": "⚠️ ປານກາງ", "note": "ວັນພຸດ - ຕ້ອງລະມັດລະວັງ"},
        "4": {"status": "✅ ດີຫຼາຍ", "note": "ວັນພະຫັດ - ໄດ້ຮັບການຊ່ວຍເຫຼືອ"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ກັບມາໄດ້ຢ່າງປອດໄພ"},
        "6": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນສົບ - ງ່າຍເກີດອຸບັດເຫດ"},
    },

    "ການເປີດກິຈະການ": {  # 開業
        "0": {"status": "✅ ດີ", "note": "ວັນອາທິດ - ມີກຳໄລ"},
        "1": {"status": "⚠️ ປານກາງ", "note": "ວັນຈັນ - ຕ້ອງເບິ່ງເວລາ"},
        "2": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນອັງຄານ - ງ່າຍຂາດທຶນ"},
        "3": {"status": "✅ ດີຫຼາຍ", "note": "ວັນພຸດ - ບໍລິສັດເຕີບໂຕ"},
        "4": {"status": "✅ ດີ", "note": "ວັນພະຫັດ - ມີຄູ່ຮ່ວມງານ"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ລູກຄ້າອົບອຸ່ນ"},
        "6": {"status": "⚠️ ປານກາງ", "note": "ວັນສົບ - ຕ້ອງລະມັດລະວັງ"},
    },

    "ການບູຊາບູຊາ": {  # 祭祀 / 做功德
        "0": {"status": "✅ ດີຫຼາຍ", "note": "ວັນອາທິດ - ຜົນບຸນໃຫຍ່"},
        "1": {"status": "✅ ດີ", "note": "ວັນຈັນ - ເໝາະສົມ"},
        "2": {"status": "✅ ດີ", "note": "ວັນອັງຄານ - ໄດ້ຮັບການປົກປ້ອງ"},
        "3": {"status": "✅ ດີ", "note": "ວັນພຸດ - ຜົນບຸນເຕັມ"},
        "4": {"status": "✅ ດີ", "note": "ວັນພະຫັດ - ເປັນສິ່ງດີ"},
        "5": {"status": "✅ ດີຫຼາຍ", "note": "ວັນສຸກ - ບຸນໃຫຍ່"},
        "6": {"status": "✅ ດີ", "note": "ວັນສົບ - ເໝາະສົມ"},
    },
}

# ==================== 額外補充表格（月份 / 特殊日）================
SANGKHOM_MONTH_RULES: Dict[int, Dict[str, str]] = {
    1: {"status": "✅ ດີ", "note": "ເດືອນມັງກອນ - ເໝາະກັບການເລີ່ມຕົ້ນ"},
    3: {"status": "⚠️ ປານກາງ", "note": "ເດືອນມີນາ - ຕ້ອງລະມັດລະວັງ"},
    5: {"status": "✅ ດີຫຼາຍ", "note": "ເດືອນພຶດສະພາ - ມີໂຊກລາບ"},
    7: {"status": "❌ ອັນຕະລາຍ", "note": "ເດືອນກໍລະກົດ - ງ່າຍເກີດບັນຫາ"},
    # ... 可繼續補充其餘月份
}


def get_sangkhom_for_date(activity: str, greg_date: date) -> Dict[str, Any]:
    """
    根據活動類型與日期，查詢 ສັງຄົມ 吉凶建議
    """
    info = get_lao_date_info(greg_date)
    weekday_num = info["weekday_num"]
    
    activity_table = SANGKHOM_TABLES.get(activity, {})
    weekday_result = activity_table.get(str(weekday_num), {
        "status": "❓ ບໍ່ມີຂໍ້ມູນ",
        "note": "ບໍ່ພົບຂໍ້ມູນ ສັງຄົມ ສຳລັບກິດຈະກຳນີ້"
    })
    
    month_result = SANGKHOM_MONTH_RULES.get(info["lao_month"], {"status": "✅ ດີ", "note": "ເດືອນທົ່ວໄປ"})
    
    return {
        "activity": activity,
        "gregorian_date": greg_date.isoformat(),
        "lao_date": info["full_lao_date_with_weekday"],
        "weekday": info["weekday_lao"],
        "status": weekday_result["status"],
        "note": weekday_result["note"],
        "month_note": month_result["note"],
        "recommendation": f"{weekday_result['status']} - {weekday_result['note']}",
        "overall": "✅ ແນະນຳ" if "✅" in weekday_result["status"] else "⚠️ ລະມັດລະວັງ",
    }


def get_sangkhom_recommendation(activity: str, greg_date: date) -> str:
    """快速取得單一行文字建議（供 UI 使用）"""
    result = get_sangkhom_for_date(activity, greg_date)
    return f"{result['activity']}：{result['recommendation']} ({result['lao_date']})"


# ==================== 所有支援的活動清單 ====================
SUPPORTED_SANGKHOM_ACTIVITIES: List[str] = list(SANGKHOM_TABLES.keys())


# 測試用
if __name__ == "__main__":
    from datetime import date
    test_date = date(2026, 5, 18)
    print(get_sangkhom_for_date("ການແຕ່ງງານ", test_date))
    print("\n支援活動：", SUPPORTED_SANGKHOM_ACTIVITIES)
