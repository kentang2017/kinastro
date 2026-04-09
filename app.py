"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、紫微斗數、西洋占星、印度占星（Jyotish）、宿曜道、泰國占星、
卡巴拉占星、阿拉伯占星、瑪雅占星、緬甸占星（Mahabote）、古埃及十度區間（Decans）、
納迪占星（Nadi Jyotish）、蒙古祖爾海（Zurkhai）、Picatrix 星體魔法十四種體系，
使用 pyswisseph 進行天文計算，以 Streamlit 提供互動式排盤介面。
"""

import streamlit as st
from datetime import datetime, date, time

from astro.i18n import TRANSLATIONS, get_lang
from astro.calculator import compute_chart
from astro.chart_renderer import (
    render_chart_info,
    render_planet_table,
    render_house_table,
    render_aspect_summary,
    render_mansion_ring,
)
from astro.western import compute_western_chart, render_western_chart
from astro.indian import compute_vedic_chart, render_vedic_chart
from astro.sukkayodo import render_sukkayodo_chart
from astro.thai import (
    compute_thai_chart, render_thai_chart,
    calculate_thai_nine_grid, render_nine_grid,
    calculate_nine_palace_divination, render_nine_palace_divination,
)
from astro.kabbalistic import compute_kabbalistic_chart, render_kabbalistic_chart
from astro.arabic import compute_arabic_chart, render_arabic_chart
from astro.maya import compute_maya_chart, render_maya_chart
from astro.ziwei import compute_ziwei_chart, render_ziwei_chart
from astro.mahabote import compute_mahabote_chart, render_mahabote_chart
from astro.decans import compute_decan_chart, render_decan_chart, render_decan_browse
from astro.nadi import compute_nadi_chart, render_nadi_chart
from astro.zurkhai import compute_zurkhai_chart, render_zurkhai_chart
from astro.picatrix_mansions import (
    render_mansion_lookup,
    render_planetary_hours_tool,
    render_talisman_generator,
    render_picatrix_browse,
    get_mansion_index,
)

# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="堅占星 Kin Astro",
    page_icon="⭐",
    layout="wide",
)

# ── Initialise language from the persisted radio widget value ────────────────
# When the user clicks the language radio, Streamlit reruns the script with the
# new "_lang_radio" value already in session_state.  We read it here — before
# rendering the title — so that *all* content on the page uses the correct
# language in the same rerun.
if "_lang_radio" in st.session_state:
    st.session_state["lang"] = (
        "en" if st.session_state["_lang_radio"] == "English" else "zh"
    )
elif "lang" not in st.session_state:
    st.session_state["lang"] = "zh"


def t(key: str) -> str:
    """Return the translated string for *key* in the current UI language."""
    lang = st.session_state.get("lang", "zh")
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("zh", key))


st.title(t("app_title"))
st.markdown(t("app_subtitle"))

# ============================================================
# 預設城市資料
# ============================================================
# Internal keys are Chinese; CITY_NAMES_EN maps them to English display names.
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
    "仰光": (16.8661, 96.1951, 6.5),
    "烏蘭巴托": (47.9077, 106.8832, 8.0),
}

CITY_NAMES_EN = {
    "自訂": "Custom",
    "北京": "Beijing",
    "上海": "Shanghai",
    "香港": "Hong Kong",
    "台北": "Taipei",
    "東京": "Tokyo",
    "首爾": "Seoul",
    "新加坡": "Singapore",
    "倫敦": "London",
    "紐約": "New York",
    "仰光": "Yangon",
    "烏蘭巴托": "Ulaanbaatar",
}

# ============================================================
# 側邊欄 - 輸入排盤資料
# ============================================================
with st.sidebar:
    # ── Language switcher (top of sidebar) ──────────────────
    st.radio(
        "🌐 Language / 語言",
        options=["繁體中文", "English"],
        index=0 if st.session_state.get("lang", "zh") == "zh" else 1,
        key="_lang_radio",
        horizontal=True,
    )
    st.divider()

    st.header(t("sidebar_header"))

    # 日期時間輸入
    st.subheader(t("date_time"))
    birth_date = st.date_input(
        t("birth_date"),
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )
    birth_time = st.time_input(t("birth_time"), value=time(12, 0))

    # 地點輸入
    st.subheader(t("birth_location"))
    _city_format = (
        (lambda c: CITY_NAMES_EN.get(c, c))
        if st.session_state.get("lang") == "en"
        else (lambda c: c)
    )
    city = st.selectbox(
        t("city_preset"),
        options=list(CITY_PRESETS.keys()),
        format_func=_city_format,
    )

    if city != "自訂":
        preset_lat, preset_lon, preset_tz = CITY_PRESETS[city]
        input_lat = st.number_input(
            t("latitude"), value=preset_lat, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            t("longitude"), value=preset_lon, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            t("timezone"), value=preset_tz, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = CITY_NAMES_EN[city] if st.session_state.get("lang") == "en" else city
    else:
        input_lat = st.number_input(
            t("latitude"), value=39.9042, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            t("longitude"), value=116.4074, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            t("timezone"), value=8.0, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = t("custom_location")

    # 排盤按鈕
    calculate = st.button(t("calculate_btn"), use_container_width=True, type="primary")

    # 性別（用於七政四餘宮位方向）
    st.subheader(t("gender_header"))
    _male_label = t("male")
    _female_label = t("female")
    gender_choice = st.radio(
        t("gender_label"),
        options=[_male_label, _female_label],
        index=0,
        horizontal=True,
    )
    gender = "male" if gender_choice == _male_label else "female"

# ============================================================
# 主區域 - 排盤結果（使用 Tabs 切換不同占星體系）
# ============================================================
tab_chinese, tab_ziwei, tab_western, tab_indian, tab_sukkayodo, tab_thai, tab_kabbalistic, tab_arabic, tab_maya, tab_mahabote, tab_decans, tab_nadi, tab_zurkhai, tab_picatrix = st.tabs(
    [t("tab_chinese"), t("tab_ziwei"), t("tab_western"), t("tab_indian"),
     t("tab_sukkayodo"), t("tab_thai"), t("tab_kabbalistic"), t("tab_arabic"), t("tab_maya"),
     t("tab_mahabote"), t("tab_decans"), t("tab_nadi"), t("tab_zurkhai"),
     t("tab_picatrix")]
)

if calculate:
    _params = dict(
        year=birth_date.year, month=birth_date.month, day=birth_date.day,
        hour=birth_time.hour, minute=birth_time.minute,
        timezone=input_tz, latitude=input_lat, longitude=input_lon,
        location_name=location_name,
    )

    # 印度占星/宿曜道共用的排盤（提前計算一次）
    with st.spinner(t("spinner_indian")):
        v_chart = compute_vedic_chart(**_params)

    # --- 七政四餘（中國） ---
    with tab_chinese:
        with st.spinner(t("spinner_chinese")):
            chart = compute_chart(**_params, gender=gender)
        render_chart_info(chart)
        st.divider()
        render_mansion_ring(chart)
        st.divider()
        render_planet_table(chart)
        st.divider()
        render_house_table(chart)
        st.divider()
        render_aspect_summary(chart)

    # --- 紫微斗數 ---
    with tab_ziwei:
        with st.spinner(t("spinner_ziwei")):
            zw_chart = compute_ziwei_chart(**_params)
        render_ziwei_chart(zw_chart)

    # --- 西洋占星 ---
    with tab_western:
        sidereal_mode = st.checkbox(
            t("sidereal_label"),
            value=False,
            help=t("sidereal_help"),
        )
        with st.spinner(t("spinner_western")):
            w_params = dict(**_params, sidereal=sidereal_mode)
            w_chart = compute_western_chart(**w_params)
        render_western_chart(w_chart)

    # --- 印度占星 ---
    with tab_indian:
        render_vedic_chart(v_chart)

    # --- 宿曜道 ---
    with tab_sukkayodo:
        st.subheader(t("sukkayodo_subheader"))
        st.info(t("sukkayodo_info"))
        st.markdown(t("desc_sukkayodo"))
        render_sukkayodo_chart(v_chart)

    # --- 泰國占星 ---
    with tab_thai:
        with st.spinner(t("spinner_thai")):
            t_chart = compute_thai_chart(**_params)
        thai_tab_chart, thai_tab_nine = st.tabs(
            [t("thai_subtab_chart"), t("thai_subtab_nine")]
        )
        with thai_tab_chart:
            render_thai_chart(t_chart)
        with thai_tab_nine:
            nine_grid_result = calculate_thai_nine_grid(
                birth_date.day, birth_date.month, birth_date.year
            )
            render_nine_grid(nine_grid_result)
            st.markdown("---")
            divination_result = calculate_nine_palace_divination(t_chart)
            render_nine_palace_divination(divination_result)

    # --- 卡巴拉占星 ---
    with tab_kabbalistic:
        with st.spinner(t("spinner_kabbalistic")):
            k_chart = compute_kabbalistic_chart(**_params)
        render_kabbalistic_chart(k_chart)

    # --- 阿拉伯占星 ---
    with tab_arabic:
        with st.spinner(t("spinner_arabic")):
            a_chart = compute_arabic_chart(**_params)
        render_arabic_chart(a_chart)

    # --- 瑪雅占星 ---
    with tab_maya:
        with st.spinner(t("spinner_maya")):
            m_chart = compute_maya_chart(**_params)
        render_maya_chart(m_chart)

    # --- 緬甸占星 (Mahabote) ---
    with tab_mahabote:
        with st.spinner(t("spinner_mahabote")):
            mb_chart = compute_mahabote_chart(**_params)
        render_mahabote_chart(mb_chart)

    # --- 古埃及十度區間 (Decans) ---
    with tab_decans:
        with st.spinner(t("spinner_decans")):
            dc_chart = compute_decan_chart(**_params)
        render_decan_chart(dc_chart)

    # --- 納迪占星 (Nadi Jyotish) ---
    with tab_nadi:
        with st.spinner(t("spinner_nadi")):
            nadi_chart = compute_nadi_chart(**_params)
        render_nadi_chart(nadi_chart)

    # --- 蒙古祖爾海 (Zurkhai) ---
    with tab_zurkhai:
        with st.spinner(t("spinner_zurkhai")):
            zk_chart = compute_zurkhai_chart(**_params)
        render_zurkhai_chart(zk_chart)

    # --- Picatrix 星體魔法 ---
    with tab_picatrix:
        st.subheader(t("picatrix_subheader"))
        st.info(t("picatrix_source"))
        # Get Moon longitude from birth chart parameters
        import swisseph as _swe
        _decimal_hour = birth_time.hour + birth_time.minute / 60.0 - input_tz
        _jd = _swe.julday(
            birth_date.year, birth_date.month, birth_date.day, _decimal_hour
        )
        _moon_result, _ = _swe.calc_ut(_jd, _swe.MOON)
        moon_lon = float(_moon_result[0]) % 360.0

        ptab_mansions, ptab_hours, ptab_talisman, ptab_browse = st.tabs(
            [t("picatrix_subtab_mansion"), t("picatrix_subtab_hours"),
             t("picatrix_subtab_talisman"), t("picatrix_subtab_browse")]
        )
        with ptab_mansions:
            render_mansion_lookup(moon_lon=moon_lon)
        with ptab_hours:
            render_planetary_hours_tool(
                year=birth_date.year,
                month=birth_date.month,
                day=birth_date.day,
                timezone=input_tz,
                latitude=input_lat,
                longitude=input_lon,
            )
        with ptab_talisman:
            render_talisman_generator()
        with ptab_browse:
            render_picatrix_browse()

else:
    with tab_chinese:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_chinese"))
    with tab_ziwei:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_ziwei"))
    with tab_western:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_western"))
    with tab_indian:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_indian"))
    with tab_sukkayodo:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_sukkayodo"))
    with tab_thai:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_thai"))
    with tab_kabbalistic:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_kabbalistic"))
    with tab_arabic:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_arabic"))
    with tab_maya:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_maya"))
    with tab_mahabote:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_mahabote"))
    with tab_decans:
        st.info(t("info_decans_prompt"))
        render_decan_browse()
    with tab_nadi:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_nadi"))
    with tab_zurkhai:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_zurkhai"))
    with tab_picatrix:
        st.info(t("info_picatrix_prompt"))
        st.markdown(t("desc_picatrix"))
        render_picatrix_browse()
        st.divider()
        st.subheader(t("picatrix_talisman_subheader"))
        render_talisman_generator()
