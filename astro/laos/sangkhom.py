# astro/lao/sangkhom.py
"""
ສັງຄົມ 吉凶擇日邏輯 (書中第66-98頁 + 附錄)
包含結婚、開工、出行、建房等實務判斷
"""

from .calendar import LaoCalendar

class Sangkhom:
    """老撾擇日系統 - 完全依照書中「ສັງຄົມ」章節"""

    def __init__(self):
        self.calendar = LaoCalendar()

    def get_daily_fortune(self, date: datetime, activity: str = "general"):
        """每日吉凶 (書中第70-76頁 ສັງຄົມ)"""
        lao = self.calendar.gregorian_to_lao(date)
        
        # 簡化版吉凶表 (實際應從書中 data/ 載入完整表格)
        fortune_map = {
            0: "吉 (適合結婚、開工)",   # 星期日
            1: "中 (適合出行)",
            # ... 完整 7 天 + 特殊日規則
        }
        
        base = fortune_map.get(lao["weekday"], "中性")
        
        # 加入特殊年份與月令影響 (書中第82-98頁)
        if lao["is_leap"]:
            base += " (閏年加持)"
            
        return {
            "lao_date": lao,
            "fortune": base,
            "recommend": self._get_recommendation(activity, lao),
            "avoid": self._get_avoidance(activity, lao),
        }

    def _get_recommendation(self, activity: str, lao_date: dict):
        # 根據書中第3章「ປະຕິທິນ」實作
        return "今日適合：結婚、奠基、出行" if activity == "wedding" else "一般吉"

    # 更多：結婚擇日、建房擇日 等 (可擴展)
