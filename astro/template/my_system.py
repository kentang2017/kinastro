"""
astro/template/my_system.py — 新占星體系模板 (New Astrology System Template) — 2026 版

【現代流程】
1. 在 astro/<slug>/ 建立 package（推薦 calculator.py + renderer.py 分離）。
2. 計算層 **絕對不可 import streamlit**（純函式 + 可序列化輸出）。
3. 在 astro/system_registry.py 宣告 System(...)。
4. （推薦）在 ui/system_handlers/ 建立 build_<slug>_handler.py 回傳 SystemHandler。
5. 由 EXECUTION_REGISTRY 統一驅動（app.py 仍保留 legacy fallback 相容）。
6. 使用 i18n.t() + chart_theme 確保一致體驗。
7. 加入測試 + 更新 wiki/。

參考良好範例：andean/、maya/、bintang_duabelas/、jawa_weton/。
舊式單檔模板已過時，優先採用 package + handler 模式。
"""

from dataclasses import dataclass, field
from typing import List

# 計算層永遠不 import streamlit！
# 渲染層才允許（見下方 render 函式內 lazy import 示範）。


# ============================================================
# 資料模型 (Data Models)
# ============================================================

@dataclass
class MyPlanet:
    """行星 / 星體資料。"""
    name: str = ""
    name_cn: str = ""
    longitude: float = 0.0
    sign: str = ""
    sign_degree: float = 0.0
    retrograde: bool = False
    house: int = 0


@dataclass
class MySystemChart:
    """排盤結果資料類。

    所有體系共用的基本欄位放在前面，
    體系特有的欄位放在後面。
    """
    # ── 共用欄位 (Common fields) ──
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""
    julian_day: float = 0.0
    planets: List[MyPlanet] = field(default_factory=list)

    # ── 體系特有欄位 (System-specific fields) ──
    # my_special_field: str = ""
    # my_houses: list = field(default_factory=list)


# ============================================================
# 核心計算 (Core Computation) — 必須純淨
# ============================================================

def compute_my_system_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> MySystemChart:
    """核心計算函式（純函式）。

    2026 最佳實踐：
    - 絕對不依賴 Streamlit、session_state 或任何 UI。
    - 回傳可 JSON 序列化的 dataclass（供 API + handler 快取）。
    - 由 ui/system_handlers/ 中的 handler 負責 @st.cache_data 包裝。
    - 建議繼承或組合 astro.systems.base.BaseChart。

    測試時可直接 import 呼叫，無需 Streamlit 環境。
    """
    chart = MySystemChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )

    # TODO: 在此實作計算邏輯（使用 pyswisseph、sxtwl 等）
    # 範例：
    #   import swisseph as swe
    #   decimal_hour = hour + minute / 60.0 - timezone
    #   jd = swe.julday(year, month, day, decimal_hour)
    #   chart.julian_day = jd

    return chart


# ============================================================
# Streamlit 渲染 (UI Rendering) — 僅此處允許 Streamlit
# ============================================================

def render_my_system_chart(chart: MySystemChart) -> None:
    """Streamlit 渲染函式。

    2026 推薦：函式內部 lazy import streamlit，避免計算路徑污染。
    強烈建議使用：
      - astro.i18n.t()
      - astro.chart_theme (svg_header, colors, apply_chart_theme)
    """
    import streamlit as st  # lazy import，保持計算層乾淨

    st.subheader("我的占星體系（範例）")

    # ── 基本資料 ──
    st.info(
        f"📅 {chart.year}-{chart.month:02d}-{chart.day:02d} "
        f"{chart.hour:02d}:{chart.minute:02d} "
        f"(UTC{chart.timezone:+.1f})"
    )

    # ── 行星表格 ──
    if chart.planets:
        st.dataframe(
            [
                {
                    "Name": f"{p.name} ({p.name_cn})",
                    "Sign": p.sign,
                    "Degree": f"{p.sign_degree:.2f}°",
                    "R": "R" if p.retrograde else "",
                }
                for p in chart.planets
            ],
            width="stretch",
        )

    # ── 匯出按鈕 (可選，使用共享工具) ──
    # from astro.export import render_download_buttons
    # render_download_buttons(my_chart_to_dict(chart), key_prefix="my_system")

    # 真實專案中請盡量重用 frontend/ 既有元件或 ui/components/result_shell。
