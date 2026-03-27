"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、西洋占星、印度占星（Jyotish）、泰國占星四種體系，
使用 pyswisseph 進行天文計算，以 Streamlit 提供互動式排盤介面。
"""

import streamlit as st
from datetime import datetime, date, time

from astro.calculator import compute_chart
from astro.chart_renderer import (
    render_chart_info,
    render_planet_table,
    render_house_table,
    render_chart_grid,
    render_aspect_summary,
)
from astro.western import compute_western_chart, render_western_chart
from astro.indian import compute_vedic_chart, render_vedic_chart
from astro.thai import compute_thai_chart, render_thai_chart

# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="堅占星 Kin Astro",
    page_icon="⭐",
    layout="wide",
)

st.title("⭐ 堅占星 Kin Astro")
st.markdown(
    "多體系占星排盤系統 — "
    "支援七政四餘（中國）、西洋占星、印度占星（Jyotish）、泰國占星。"
)

# ============================================================
# 預設城市資料
# ============================================================
CITY_PRESETS = {
    "自訂": (0.0, 0.0, 0.0),
    "北京": (39.9042, 116.4074, 8.0),
    "上海": (31.2304, 121.4737, 8.0),
    "香港": (22.3193, 114.1694, 8.0),
    "台北": (25.0330, 121.5654, 8.0),
    "東京": (35.6762, 139.6503, 9.0),
    "首爾": (37.5665, 126.9780, 9.0),
    "新加坡": (1.3521, 103.8198, 8.0),
    "倫敦": (51.5074, -0.1278, 0.0),
    "紐約": (40.7128, -74.0060, -5.0),
}

# ============================================================
# 側邊欄 - 輸入排盤資料
# ============================================================
with st.sidebar:
    st.header("📝 排盤資料")

    # 日期時間輸入
    st.subheader("日期與時間")
    birth_date = st.date_input(
        "出生日期",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )
    birth_time = st.time_input("出生時間", value=time(12, 0))

    # 地點輸入
    st.subheader("出生地點")
    city = st.selectbox("預設城市", options=list(CITY_PRESETS.keys()))

    if city != "自訂":
        preset_lat, preset_lon, preset_tz = CITY_PRESETS[city]
        input_lat = st.number_input(
            "緯度", value=preset_lat, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            "經度", value=preset_lon, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            "時區 (UTC)", value=preset_tz, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = city
    else:
        input_lat = st.number_input(
            "緯度", value=39.9042, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            "經度", value=116.4074, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            "時區 (UTC)", value=8.0, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = "自訂地點"

    # 排盤按鈕
    calculate = st.button("🔮 開始排盤", use_container_width=True, type="primary")

# ============================================================
# 主區域 - 排盤結果（使用 Tabs 切換不同占星體系）
# ============================================================
tab_chinese, tab_western, tab_indian, tab_thai = st.tabs(
    ["🀄 七政四餘（中國）", "🌍 西洋占星", "🙏 印度占星", "🐘 泰國占星"]
)

if calculate:
    _params = dict(
        year=birth_date.year, month=birth_date.month, day=birth_date.day,
        hour=birth_time.hour, minute=birth_time.minute,
        timezone=input_tz, latitude=input_lat, longitude=input_lon,
        location_name=location_name,
    )

    # --- 七政四餘（中國） ---
    with tab_chinese:
        with st.spinner("正在計算七政四餘位置..."):
            chart = compute_chart(**_params)
        render_chart_info(chart)
        st.divider()
        render_chart_grid(chart)
        st.divider()
        render_planet_table(chart)
        st.divider()
        render_house_table(chart)
        st.divider()
        render_aspect_summary(chart)

    # --- 西洋占星 ---
    with tab_western:
        with st.spinner("正在計算西洋占星排盤..."):
            w_chart = compute_western_chart(**_params)
        render_western_chart(w_chart)

    # --- 印度占星 ---
    with tab_indian:
        with st.spinner("正在計算印度占星排盤..."):
            v_chart = compute_vedic_chart(**_params)
        render_vedic_chart(v_chart)

    # --- 泰國占星 ---
    with tab_thai:
        with st.spinner("正在計算泰國占星排盤..."):
            t_chart = compute_thai_chart(**_params)
        render_thai_chart(t_chart)

else:
    with tab_chinese:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是七政四餘？

            **七政四餘**是中國傳統占星術的核心體系：

            - **七政（日月五星）**：太陽、太陰（月亮）、水星、金星、火星、木星、土星
            - **四餘（虛星）**：羅睺（北交點）、計都（南交點）、月孛（平均遠地點）、紫氣

            本系統使用 **pyswisseph**（瑞士星曆表）進行精確的天文計算，
            提供星曜的黃經位置、所在星次、二十八宿對應、十二宮位分布等資訊。
            """
        )
    with tab_western:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是西洋占星？

            **西洋占星**使用回歸黃道（Tropical Zodiac）計算行星位置：

            - **行星**：太陽、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星
            - **十二星座**：白羊座至雙魚座
            - **宮位制**：Placidus 等分宮制
            - **相位**：合、沖、刑、三合、六合等
            """
        )
    with tab_indian:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是印度占星 (Jyotish)？

            **印度占星**使用恆星黃道（Sidereal Zodiac）搭配 Lahiri 歲差：

            - **九曜 (Navagraha)**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
            - **十二星座 (Rashi)**：Mesha 至 Meena
            - **二十七宿 (Nakshatra)**：Ashwini 至 Revati，每宿分四足 (Pada)
            - **南印度式方盤 (South Indian Chart)**
            """
        )
    with tab_thai:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是泰國占星？

            **泰國占星**以印度 Jyotish 為基礎，融合泰國傳統文化：

            - **九曜**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
            - **十二星座 (ราศี)**：使用泰語命名的恆星黃道星座
            - **日主星 (ดาวประจำวัน)**：根據出生星期判定守護星
            - **泰式方盤 (ผังดวงชาตา)**
            """
        )
