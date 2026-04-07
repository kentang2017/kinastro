"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、西洋占星、印度占星（Jyotish）、泰國占星、卡巴拉占星五種體系，
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
from astro.sukkayodo import render_sukkayodo_chart
from astro.thai import (
    compute_thai_chart, render_thai_chart,
    calculate_thai_nine_grid, render_nine_grid,
)
from astro.kabbalistic import compute_kabbalistic_chart, render_kabbalistic_chart
from astro.arabic import compute_arabic_chart, render_arabic_chart
from astro.maya import compute_maya_chart, render_maya_chart
from astro.ziwei import compute_ziwei_chart, render_ziwei_chart

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
    "支援七政四餘（中國）、紫微斗數、西洋占星、印度占星（Jyotish）、宿曜道、泰國占星、"
    "卡巴拉占星、阿拉伯占星、瑪雅占星。"
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
tab_chinese, tab_ziwei, tab_western, tab_indian, tab_sukkayodo, tab_thai, tab_kabbalistic, tab_arabic, tab_maya = st.tabs(
    ["🀄 七政四餘（中國）", "🌟 紫微斗數", "🌍 西洋占星", "🙏 印度占星",
     "🈳 宿曜道", "🐘 泰國占星", "✡ 卡巴拉占星", "☪ 阿拉伯占星", "🏺 瑪雅占星"]
)

if calculate:
    _params = dict(
        year=birth_date.year, month=birth_date.month, day=birth_date.day,
        hour=birth_time.hour, minute=birth_time.minute,
        timezone=input_tz, latitude=input_lat, longitude=input_lon,
        location_name=location_name,
    )

    # 印度占星/宿曜道共用的排盤（提前計算一次）
    with st.spinner("正在計算印度占星排盤..."):
        v_chart = compute_vedic_chart(**_params)

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

    # --- 紫微斗數 ---
    with tab_ziwei:
        with st.spinner("正在計算紫微斗數命盤..."):
            zw_chart = compute_ziwei_chart(**_params)
        render_ziwei_chart(zw_chart)

    # --- 西洋占星 ---
    with tab_western:
        sidereal_mode = st.checkbox(
            "🌟 使用恆星黃道 (Sidereal Zodiac / Lahiri Ayanamsa)",
            value=False,
            help="恆星黃道以實際星座位置計算，含歲差修正（印度占星用同一體系）"
        )
        with st.spinner("正在計算西洋占星排盤..."):
            w_params = dict(**_params, sidereal=sidereal_mode)
            w_chart = compute_western_chart(**w_params)
        render_western_chart(w_chart)

    # --- 印度占星 ---
    with tab_indian:
        render_vedic_chart(v_chart)

    # --- 宿曜道 ---
    with tab_sukkayodo:
        st.subheader("🈳 日本宿曜道 (Yojōdō)")
        st.info("宿曜道建基於印度占星排盤，請至「🙏 印度占星」分頁查看完整印度占星排盤。")
        st.markdown(
            """
            ### 什麼是宿曜道？

            **宿曜道**由空海大師於 9 世紀自印度傳入日本，是融合佛密與道教的占星體系：

            - **二十八宿 (Nakshatra)**：比印度 Jyotish 多出 **Abhijit（牛宿）**，共 28 宿
            - **六曜 (Rokuyō)**：先勝・友引・先負・仏滅・大安・赤口，由 **Moon 所在宿** 決定
            - **宿曜道方盤**：以 Moon 為中心，二十八宿沿圓環排列

            宿曜道可用於擇日、占卜日常生活中各類事務的吉凶。
            """
        )
        render_sukkayodo_chart(v_chart)

    # --- 泰國占星 ---
    with tab_thai:
        with st.spinner("正在計算泰國占星排盤..."):
            t_chart = compute_thai_chart(**_params)
        thai_tab_chart, thai_tab_numerology = st.tabs(
            ["🐘 ผังดวงชาตา (占星排盤)", "🔢 ตาราง 9 ช่อง (9宮格數字學)"]
        )
        with thai_tab_chart:
            render_thai_chart(t_chart)
        with thai_tab_numerology:
            nine_grid_result = calculate_thai_nine_grid(
                birth_date.day, birth_date.month, birth_date.year
            )
            render_nine_grid(nine_grid_result)

    # --- 卡巴拉占星 ---
    with tab_kabbalistic:
        with st.spinner("正在計算卡巴拉占星排盤..."):
            k_chart = compute_kabbalistic_chart(**_params)
        render_kabbalistic_chart(k_chart)

    # --- 阿拉伯占星 ---
    with tab_arabic:
        with st.spinner("正在計算阿拉伯占星排盤..."):
            a_chart = compute_arabic_chart(**_params)
        render_arabic_chart(a_chart)

    # --- 瑪雅占星 ---
    with tab_maya:
        with st.spinner("正在計算瑪雅占星排盤..."):
            m_chart = compute_maya_chart(**_params)
        render_maya_chart(m_chart)

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
    with tab_ziwei:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是紫微斗數？

            **紫微斗數**是中國傳統命理學最重要的排盤體系之一，相傳由五代末宋初的
            **陳希夷**（陳摶）整理創立：

            - **十四主星**：紫微（帝王星）、天機、太陽、武曲、天同、廉貞（紫微六系）；
              天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍（天府八系）
            - **十二宮位**：命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、
              遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮
            - **五行局**：由命宮天干決定，分水二、木三、金四、土五、火六局，
              影響紫微星安星方式
            - **農曆排盤**：以農曆生辰（年、月、日、時辰）為基礎
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
            - **七曜管宿**：每顆曜主管 3 個 Nakshatra，構成 27 宿體系

            | 曜 | 主宿 |
            |:--:|:-----|
            | Sun | Krittika、Uttara Phalguni、Uttara Ashadha |
            | Moon | Rohini、Hasta、Shravana |
            | Mars | Mrigashira、Chitra、Dhanishta |
            | Mercury | Ashlesha、Jyeshtha、Revati |
            | Jupiter | Punarvasu、Vishakha、Purva Bhadrapada |
            | Venus | Bharani、Purva Phalguni、Purva Ashadha |
            | Saturn | Pushya、Anuradha、Uttara Bhadrapada |
            | Rahu | Ardra、Swati、Shatabhisha |
            | Ketu | Ashwini、Magha、Mula |
            """
        )
    with tab_sukkayodo:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是宿曜道？

            **宿曜道**由空海大師於 9 世紀自印度傳入日本，是融合佛密與道教的占星體系：

            - **二十八宿 (Nakshatra)**：比印度 Jyotish 多出 **Abhijit（牛宿）**，共 28 宿
            - **六曜 (Rokuyō)**：先勝・友引・先負・仏滅・大安・赤口，由 **Moon 所在宿** 決定
            - **宿曜道方盤**：以 Moon 為中心，二十八宿沿圓環排列
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
    with tab_kabbalistic:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是卡巴拉占星？

            **卡巴拉占星**結合猶太神祕主義（Kabbalah）與占星術：

            - **生命之樹 (Tree of Life)**：十個質點（Sephiroth）對應不同行星
            - **希伯來字母**：22 個字母分別對應黃道星座與行星
            - **塔羅對應**：每個星座對應一張塔羅大牌
            - **回歸黃道 (Tropical Zodiac)**：使用西洋占星的回歸黃道系統
            """
        )
    with tab_arabic:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是阿拉伯占星？

            **阿拉伯占星**源自中世紀伊斯蘭黃金時代，融合希臘與波斯天文傳統：

            - **阿拉伯點 (Arabic Parts / Lots)**：透過上升點與行星經度加減運算，
              推導出幸運點、精神點、愛情點等各生活主題的敏感度數
            - **日夜盤 (Sect)**：根據太陽位置區分日盤與夜盤，影響阿拉伯點公式
            - **行星廟旺落陷 (Essential Dignities)**：入廟、入旺、落陷、入弱
            - **回歸黃道 (Tropical Zodiac)**：使用 Placidus 宮位制
            """
        )
    with tab_maya:
        st.info("👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。")
        st.markdown(
            """
            ### 什麼是瑪雅占星？

            **瑪雅占星**源自瓜地馬拉瑪雅文明的天文與曆法傳統：

            - **Long Count（長紀年）**：以 B'ak'tun、Ka'tun、Tu'n、Winal、K'in 計算天數
            - **Tzolkin（神聖曆）**：260 天循環，13 數字 × 20 神明名
            - **Haab（民用曆）**：365 天，18 月 × 20 日 + 5 Wayeb 無日
            - **Calendar Round**：Tzolkin × Haab 同步循環，約 52 年一輪
            - **行星疊加**：結合西方占星行星位置對應 Tzolkin 能量
            """
        )
