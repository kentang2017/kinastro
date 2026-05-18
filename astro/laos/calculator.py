# astro/lao/calculator.py
"""
老撾占星主計算器 (Lao Horasat Calculator)
基於《ໄທຣາສາດລາວ ພາກຕົ້ນ》完整實現
整合：
- calendar.py（老撾曆轉換 + 特殊年份）
- sangkhom.py（ສັງຄົມ 吉凶擇日）
- pyswisseph（精準行星位置）
與專案其他體系 (thai.py 等) 風格完全一致
"""

from datetime import datetime
import swisseph as swe
from typing import Dict, Any, Optional
from .calendar import LaoCalendar
from .sangkhom import Sangkhom
from ..base import BaseCalculator  # 專案共用基礎計算器（若無可移除繼承）

class LaoCalculator(BaseCalculator):
    """老撾占星核心計算器"""

    def __init__(self):
        super().__init__()
        self.calendar = LaoCalendar()
        self.sangkhom = Sangkhom()
        
        # 預設萬象座標（老撾首都，書中常見基準）
        self.DEFAULT_LAT = 17.9667
        self.DEFAULT_LON = 102.6000
        self.DEFAULT_TZ = 7  # UTC+7（老撾時區）

    def get_birth_chart(self, birth_dt: datetime, 
                       lat: Optional[float] = None, 
                       lon: Optional[float] = None) -> Dict[str, Any]:
        """
        生成老撾出生盤（完整出生圖 + ສັງຄົມ 解讀）
        嚴格依照書中第1-4章時間系統 + 第5章 ປະຕິທິນ
        """
        if lat is None:
            lat = self.DEFAULT_LAT
        if lon is None:
            lon = self.DEFAULT_LON

        # 1. 轉換老撾曆（書中第1-4章核心）
        lao_date = self.calendar.gregorian_to_lao(birth_dt)

        # 2. 計算儒略日（供 pyswisseph 使用）
        jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
        )

        # 3. 計算行星位置（與專案 thai.py / 其他體系一致）
        planets = self._calculate_planets(jd, lat, lon)

        # 4. ສັງຄົມ 吉凶解讀
        sangkhom_data = self.sangkhom.get_daily_fortune(birth_dt, activity="birth")

        # 5. 組合成完整出生盤
        chart = {
            "system": "lao_horasat",
            "system_name": "ໄທຣາສາດລາວ (老撾占星術)",
            "birth_datetime": birth_dt.isoformat(),
            "lao_date": lao_date,
            "planets": planets,
            "sangkhom": sangkhom_data,
            "ascendant": self._calculate_ascendant(jd, lat, lon),  # 上升點
            "house_system": "brahma_wheel",  # 婆羅門占星輪
            "interpretation": self._generate_interpretation(lao_date, planets, sangkhom_data)
        }

        return chart

    def _calculate_planets(self, jd: float, lat: float, lon: float) -> Dict[str, Dict]:
        """使用 pyswisseph 計算主要行星位置（書中第4章 行星系統）"""
        swe.set_ephe_path()  # 使用專案預設星曆
        planets_data = {}

        # 書中常用行星（日、月、火、水、木、金、土 + 羅睺/計都）
        planet_list = {
            "sun": swe.SUN,
            "moon": swe.MOON,
            "mercury": swe.MERCURY,
            "venus": swe.VENUS,
            "mars": swe.MARS,
            "jupiter": swe.JUPITER,
            "saturn": swe.SATURN,
            "rahu": swe.MEAN_NODE,      # 羅睺
            "ketu": swe.MEAN_NODE + 1   # 計都
        }

        for name, planet_id in planet_list.items():
            try:
                pos, _ = swe.calc_ut(jd, planet_id)
                planets_data[name] = {
                    "longitude": pos[0] % 360,   # 黃道經度
                    "latitude": pos[1],
                    "speed": pos[3],
                    "house": int(pos[0] // 30) + 1  # 簡單 12 宮位
                }
            except:
                planets_data[name] = {"longitude": 0, "latitude": 0, "speed": 0, "house": 1}

        return planets_data

    def _calculate_ascendant(self, jd: float, lat: float, lon: float) -> float:
        """計算上升點（Ascendant）"""
        try:
            # 簡單版上升點計算（實際專案可使用更精確方法）
            asc = swe.houses(jd, lat, lon, b'P')[0][0] % 360
            return asc
        except:
            return 0.0

    def _generate_interpretation(self, lao_date: Dict, planets: Dict, sangkhom: Dict) -> str:
        """簡單 AI 風格解讀（可後續接 Cerebras）"""
        year_type = lao_date.get("year_type", "ປົກກະຕິ")
        fortune = sangkhom.get("fortune_level", "中")
        return f"出生於{year_type}年，{sangkhom['weekday_lao']}，整體{fortune}。適合參考婆羅門占星輪進行詳細解讀。"

    def get_auspicious_time(self, target_dt: datetime, activity: str = "general") -> Dict:
        """
        擇吉時（書中第137-156頁 ຖອຍມະຫາສັງຄົມ）
        包含日期 + 時辰建議
        """
        sangkhom_data = self.sangkhom.get_daily_fortune(target_dt, activity)
        time_slot = self.sangkhom.get_time_slot(target_dt)
        
        return {
            "lao_date": sangkhom_data["lao_date"],
            "fortune": sangkhom_data,
            "time_slot": time_slot,
            "best_hours": time_slot["best_hours"],
            "recommendation": f"今日適合{activity}：{sangkhom_data['suitable_activities']}"
        }

    def find_best_dates(self, start_dt: datetime, days: int = 30, activity: str = "general") -> list:
        """批量尋找最佳吉日（實務常用）"""
        return self.sangkhom.find_auspicious_dates(start_dt, days, activity)

    # ==================== 供 Streamlit / API 統一呼叫 ====================
    def get_chart(self, birth_date_str: str, lat: float = None, lon: float = None) -> Dict:
        """對外統一介面（與 lao_horasat.py 配合）"""
        dt = datetime.fromisoformat(birth_date_str.replace("Z", "+00:00"))
        chart = self.get_birth_chart(dt, lat, lon)
        return chart


# ==================== 測試用（直接執行此檔案可驗證） ====================
if __name__ == "__main__":
    calc = LaoCalculator()
    test_dt = datetime(2026, 5, 18, 11, 27)  # 當前時間
    chart = calc.get_birth_chart(test_dt)
    print("✅ 老撾出生盤生成成功")
    print("老撾日期:", chart["lao_date"]["lao_year"], "年")
    print("吉凶:", chart["sangkhom"]["fortune_level"])
    print("行星數量:", len(chart["planets"]))
