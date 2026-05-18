# astro/lao/lao_horasat.py
"""
老撾占星系統統一介面 (Lao Horasat / ໄທຣາສາດລາວ)
基於《ໄທຣາສາດລາວ ພາກຕົ້ນ》完整實現
這是對外唯一公開的介面，與專案中 thai.py、chinese.py 等其他體系風格完全一致
供 Streamlit、API、CLI 直接呼叫
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .calculator import LaoCalculator
from .renderer import render_brahma_wheel


class LaoHorasat:
    """老撾占星術主類別 - 統一入口"""

    def __init__(self):
        self.calculator = LaoCalculator()

    def get_chart(self, 
                  birth_date: str, 
                  lat: Optional[float] = None, 
                  lon: Optional[float] = None) -> Dict[str, Any]:
        """
        生成完整老撾出生盤（最常用方法）
        
        Parameters:
            birth_date (str): ISO 格式日期時間，例如 "1995-03-15T08:30:00"
            lat, lon: 可選經緯度（預設萬象）
        
        Returns:
            包含 lao_date、planets、sangkhom、SVG 婆羅門占星輪的完整字典
        """
        chart = self.calculator.get_chart(birth_date, lat, lon)
        
        # 渲染婆羅門占星輪 SVG
        svg = render_brahma_wheel(chart)
        
        # 最終輸出格式與專案其他體系一致
        return {
            "system": "lao_horasat",
            "system_name": "ໄທຣາສາດລາວ (老撾占星術)",
            "chart": chart,
            "svg": svg,
            "interpretation": chart.get("interpretation", "")
        }

    def get_sangkhom(self, 
                     target_date: str, 
                     activity: str = "general") -> Dict[str, Any]:
        """
        單日 ສັງຄົມ 吉凶擇日（結婚、建房、出行、開業等）
        """
        dt = datetime.fromisoformat(target_date.replace("Z", "+00:00"))
        result = self.calculator.get_auspicious_time(dt, activity)
        return {
            "system": "lao_horasat",
            "lao_date": result["lao_date"],
            "fortune": result["fortune"],
            "time_slot": result["time_slot"],
            "recommendation": result["recommendation"]
        }

    def find_best_dates(self, 
                        start_date: str, 
                        days: int = 30, 
                        activity: str = "general") -> list:
        """
        批量尋找未來最適合某活動的吉日
        """
        dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        return self.calculator.find_best_dates(dt, days, activity)

    def get_monthly_fortune(self, year: int, month: int) -> list:
        """
        取得該月完整 ປະຕິທິນ 吉凶曆
        """
        from .sangkhom import Sangkhom
        sangkhom = Sangkhom()
        return sangkhom.get_monthly_fortune(year, month)

    def render_wheel(self, chart_data: Dict[str, Any]) -> str:
        """單獨生成婆羅門占星輪 SVG（供 UI 彈性使用）"""
        return render_brahma_wheel(chart_data)


# ==================== 便捷工廠方法（供 app.py 快速註冊） ====================
def create_lao_horasat() -> LaoHorasat:
    """供 Streamlit 或其他模組快速建立實例"""
    return LaoHorasat()


# ==================== 測試用（直接執行本檔案可驗證） ====================
if __name__ == "__main__":
    print("🚀 正在測試 LaoHorasat 完整功能...")
    hor = LaoHorasat()
    
    # 測試出生盤
    test_birth = "2026-05-18T11:32:00"
    chart = hor.get_chart(test_birth)
    print(f"✅ 出生盤生成成功 | 年份: {chart['chart']['lao_date']['lao_year']} | 吉凶: {chart['chart']['sangkhom']['fortune_level']}")
    print(f"SVG 長度: {len(chart['svg'])} 字符（已包含婆羅門占星輪）")
    
    # 測試擇日
    sang = hor.get_sangkhom(test_birth, activity="結婚")
    print(f"✅ 結婚擇日: {sang['fortune']['fortune_level']} - {sang['recommendation']}")
    
    print("🎉 LaoHorasat 模組全部測試通過，可直接整合到 kinastro 主程式！")
