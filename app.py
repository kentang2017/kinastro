"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、紫微斗數、西洋占星、印度占星（Jyotish）、宿曜道、泰國占星、
卡巴拉占星、阿拉伯占星（含 Picatrix 星體魔法、太陽知識大全 Shams al-Maʻārif）、
瑪雅占星、緬甸占星（Mahabote）、古埃及十度區間（Decans）、
納迪占星（Nadi Jyotish）、蒙古祖爾海（Zurkhai）十三種體系，
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
    render_bazi,
    render_shensha,
    render_dasha,
    render_transit_comparison,
)
from astro.shensha import compute_shensha
from astro.qizheng_dasha import compute_dasha
from astro.qizheng_transit import compute_transit, compute_transit_now
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
    compute_moon_longitude,
)
from astro.shams_maarif import render_shams_browse, render_shams_chart

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
tab_chinese, tab_ziwei, tab_western, tab_indian, tab_sukkayodo, tab_thai, tab_kabbalistic, tab_arabic, tab_maya, tab_mahabote, tab_decans, tab_nadi, tab_zurkhai = st.tabs(
    [t("tab_chinese"), t("tab_ziwei"), t("tab_western"), t("tab_indian"),
     t("tab_sukkayodo"), t("tab_thai"), t("tab_kabbalistic"), t("tab_arabic"), t("tab_maya"),
     t("tab_mahabote"), t("tab_decans"), t("tab_nadi"), t("tab_zurkhai")]
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

        # 子 tabs for the Chinese chart
        _ch_tab_natal, _ch_tab_shensha, _ch_tab_dasha, _ch_tab_transit = st.tabs([
            t("ch_subtab_natal"),
            t("ch_subtab_shensha"),
            t("ch_subtab_dasha"),
            t("ch_subtab_transit"),
        ])

        with _ch_tab_natal:
            render_chart_info(chart)
            st.divider()

            # 計算流時盤 for overlay
            _transit_now = compute_transit_now(timezone=input_tz)

            # 選擇是否顯示流時對盤
            _show_transit_overlay = st.checkbox(
                t("show_transit_overlay"), value=False,
            )
            _transit_for_ring = _transit_now if _show_transit_overlay else None

            render_mansion_ring(chart, transit=_transit_for_ring)
            st.divider()
            render_bazi(chart)
            st.divider()
            render_planet_table(chart)
            st.divider()
            render_house_table(chart)
            st.divider()
            render_aspect_summary(chart)

        with _ch_tab_shensha:
            _shensha = compute_shensha(
                year=chart.year,
                solar_month=chart.solar_month,
                julian_day=chart.julian_day,
                hour_branch=chart.hour_branch,
            )
            render_shensha(chart, _shensha)

        with _ch_tab_dasha:
            from datetime import datetime as _dt
            _current_year = _dt.now().year
            _dasha = compute_dasha(
                birth_year=chart.year,
                ming_gong_branch=chart.ming_gong_branch,
                gender=gender,
                houses=chart.houses,
                current_year=_current_year,
            )
            render_dasha(chart, _dasha)

        with _ch_tab_transit:
            st.subheader(t("transit_header"))
            _t_col1, _t_col2, _t_col3 = st.columns(3)
            with _t_col1:
                _t_date = st.date_input(
                    t("transit_date"),
                    value=datetime.now().date(),
                    key="transit_date_input",
                )
            with _t_col2:
                _t_time = st.time_input(
                    t("transit_time"),
                    value=datetime.now().time(),
                    key="transit_time_input",
                )
            with _t_col3:
                _t_tz = st.number_input(
                    t("transit_tz"),
                    value=input_tz,
                    format="%.1f",
                    min_value=-12.0, max_value=14.0, step=0.5,
                    key="transit_tz_input",
                )

            _transit_custom = compute_transit(
                year=_t_date.year, month=_t_date.month, day=_t_date.day,
                hour=_t_time.hour, minute=_t_time.minute,
                timezone=_t_tz,
            )
            render_transit_comparison(chart, _transit_custom)

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
        arabic_subtab_chart, arabic_subtab_picatrix, arabic_subtab_shams = st.tabs([
            t("arabic_subtab_chart"),
            t("arabic_subtab_picatrix"),
            t("arabic_subtab_shams"),
        ])

        with arabic_subtab_chart:
            with st.spinner(t("spinner_arabic")):
                a_chart = compute_arabic_chart(**_params)
            render_arabic_chart(a_chart)

        # --- Picatrix 星體魔法 ---
        with arabic_subtab_picatrix:
            st.subheader(t("picatrix_subheader"))
            st.caption(t("picatrix_source"))

            _birth_moon_lon: float | None = compute_moon_longitude(
                year=birth_date.year,
                month=birth_date.month,
                day=birth_date.day,
                hour=birth_time.hour,
                minute=birth_time.minute,
                timezone=input_tz,
            )

            ptab_browse, ptab_mansions, ptab_hours, ptab_talisman = st.tabs([
                t("picatrix_subtab_browse"),
                t("picatrix_subtab_mansion"),
                t("picatrix_subtab_hours"),
                t("picatrix_subtab_talisman"),
            ])

            with ptab_browse:
                render_picatrix_browse()

            with ptab_mansions:
                st.info(f"🌙 使用出生月亮黃經 (Birth Moon Longitude)：{_birth_moon_lon:.2f}°")
                render_mansion_lookup(moon_lon=_birth_moon_lon)

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

        # --- 太陽知識大全 (Shams al-Maʻārif) ---
        with arabic_subtab_shams:
            st.subheader(t("shams_subheader"))
            st.caption(t("shams_source"))

            _shams_planets = {
                p.name.split("(")[0].strip().split()[-1]: p.longitude
                for p in a_chart.planets
            }
            _shams_sun_idx: int | None = None
            for p in a_chart.planets:
                if "Sun" in p.name:
                    _shams_sun_idx = int(p.longitude / 30.0)
                    break
            render_shams_chart(chart_planets=_shams_planets,
                               birth_sign_idx=_shams_sun_idx)

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
        arabic_subtab_chart, arabic_subtab_picatrix, arabic_subtab_shams = st.tabs([
            t("arabic_subtab_chart"),
            t("arabic_subtab_picatrix"),
            t("arabic_subtab_shams"),
        ])

        with arabic_subtab_chart:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_arabic"))

        with arabic_subtab_picatrix:
            st.subheader(t("picatrix_subheader"))
            st.caption(t("picatrix_source"))

            ptab_browse, ptab_mansions, ptab_hours, ptab_talisman = st.tabs([
                t("picatrix_subtab_browse"),
                t("picatrix_subtab_mansion"),
                t("picatrix_subtab_hours"),
                t("picatrix_subtab_talisman"),
            ])

            with ptab_browse:
                render_picatrix_browse()

            with ptab_mansions:
                render_mansion_lookup(moon_lon=None)

            with ptab_hours:
                render_planetary_hours_tool(
                    timezone=input_tz,
                    latitude=input_lat,
                    longitude=input_lon,
                )

            with ptab_talisman:
                render_talisman_generator()

        with arabic_subtab_shams:
            st.subheader(t("shams_subheader"))
            st.caption(t("shams_source"))
            st.markdown(t("desc_shams"))
            render_shams_browse()
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
