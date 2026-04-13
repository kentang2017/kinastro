"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、紫微斗數、西洋占星、印度占星（Jyotish）、宿曜道、泰國占星、
卡巴拉占星、阿拉伯占星（含 Picatrix 星體魔法、太陽知識大全 Shams al-Maʻārif）、
瑪雅占星、緬甸占星（Mahabote）、古埃及十度區間（Decans）、
納迪占星（Nadi Jyotish）、蒙古祖爾海（Zurkhai）、希臘占星（Hellenistic）
共十四種體系 + 跨體系比較，使用 pyswisseph 進行天文計算。
"""

import streamlit as st
from datetime import datetime, date, time

from astro.i18n import TRANSLATIONS, get_lang
from astro.chart_theme import MOBILE_CSS
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
    render_zhangguo,
)
from astro.shensha import compute_shensha
from astro.qizheng_dasha import compute_dasha
from astro.qizheng_transit import compute_transit, compute_transit_now
from astro.zhangguo import compute_zhangguo
from astro.qizheng_electional import render_electional_tool
from astro.western import compute_western_chart, render_western_chart
from astro.western_transit import compute_western_transits
from astro.western_return import compute_solar_return
from astro.western_synastry import compute_synastry
from astro.indian import compute_vedic_chart, render_vedic_chart
from astro.vedic_dasha import compute_vimshottari, compute_yogini
from astro.ashtakavarga import compute_ashtakavarga
from astro.vedic_yogas import compute_yogas
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
from astro.hellenistic import compute_hellenistic_chart, render_hellenistic_chart, build_greek_horoscope_svg
from astro.cross_compare import compute_cross_comparison, render_cross_comparison
from astro.fixed_stars import compute_fixed_star_positions, find_conjunctions
from astro.asteroids import compute_asteroids
from astro.export import render_download_buttons, western_chart_to_dict, vedic_chart_to_dict, chinese_chart_to_dict
from astro.session_store import render_chart_manager, save_chart
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

# ── Mobile-responsive CSS ──────────────────────────────────────
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

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
    calculate = st.button(t("calculate_btn"), width='stretch', type="primary")

    # 排盤儲存管理
    st.divider()
    render_chart_manager()

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
tab_chinese, tab_ziwei, tab_western, tab_indian, tab_sukkayodo, tab_thai, tab_kabbalistic, tab_arabic, tab_maya, tab_mahabote, tab_decans, tab_nadi, tab_zurkhai, tab_hellenistic, tab_cross_compare = st.tabs(
    [t("tab_chinese"), t("tab_ziwei"), t("tab_western"), t("tab_indian"),
     t("tab_sukkayodo"), t("tab_thai"), t("tab_kabbalistic"), t("tab_arabic"), t("tab_maya"),
     t("tab_mahabote"), t("tab_decans"), t("tab_nadi"), t("tab_zurkhai"),
     t("tab_hellenistic"), t("tab_cross_compare")]
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
        _ch_tab_natal, _ch_tab_shensha, _ch_tab_dasha, _ch_tab_transit, _ch_tab_zhangguo, _ch_tab_elect = st.tabs([
            t("ch_subtab_natal"),
            t("ch_subtab_shensha"),
            t("ch_subtab_dasha"),
            t("ch_subtab_transit"),
            t("ch_subtab_zhangguo"),
            t("ch_subtab_electional"),
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
                timezone=chart.timezone,
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

        with _ch_tab_zhangguo:
            _zhangguo = compute_zhangguo(
                planets=chart.planets,
                houses=chart.houses,
                gender=gender,
            )
            render_zhangguo(chart, _zhangguo)

        with _ch_tab_elect:
            render_electional_tool(timezone=input_tz)

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

        _w_tab_natal, _w_tab_transit, _w_tab_return, _w_tab_synastry = st.tabs([
            t("western_subtab_natal"),
            t("western_subtab_transit"),
            t("western_subtab_return"),
            t("western_subtab_synastry"),
        ])

        with _w_tab_natal:
            render_western_chart(w_chart)
            # Fixed stars & asteroids checkboxes
            _show_stars = st.checkbox(t("show_fixed_stars"), value=False, key="w_stars")
            _show_asteroids = st.checkbox(t("show_asteroids"), value=False, key="w_asteroids")
            if _show_stars:
                stars = compute_fixed_star_positions(w_chart.julian_day)
                p_lons = {p.name: p.longitude for p in w_chart.planets}
                conjs = find_conjunctions(stars, p_lons)
                if conjs:
                    st.markdown("#### ⭐ Fixed Star Conjunctions / 恆星合相")
                    st.dataframe([{"Star": c.star_name, "Planet": c.planet_name,
                                   "Orb": f"{c.orb:.2f}°", "Nature": c.nature,
                                   "Meaning": c.meaning_cn}
                                  for c in conjs], use_container_width=True)
                else:
                    st.info("No fixed star conjunctions within orb.")
            if _show_asteroids:
                asts = compute_asteroids(w_chart.julian_day)
                if asts:
                    st.markdown("#### ☄️ Asteroids / 小行星")
                    st.dataframe([{"Name": f"{a.name} {a.symbol} ({a.name_cn})",
                                   "Sign": a.sign, "Degree": f"{a.sign_degree:.2f}°",
                                   "R": "R" if a.retrograde else "",
                                   "Meaning": a.meaning_cn}
                                  for a in asts], use_container_width=True)
            # Export
            render_download_buttons(western_chart_to_dict(w_chart), key_prefix="western")

        with _w_tab_transit:
            st.subheader(t("western_subtab_transit"))
            _wt_col1, _wt_col2 = st.columns(2)
            with _wt_col1:
                _wt_date = st.date_input(t("transit_target_date"),
                                         value=datetime.now().date(),
                                         key="wt_date")
            with _wt_col2:
                _wt_time = st.time_input("Time", value=datetime.now().time(),
                                         key="wt_time")
            w_transits = compute_western_transits(
                w_chart, _wt_date.year, _wt_date.month, _wt_date.day,
                _wt_time.hour, _wt_time.minute, input_tz,
            )
            if w_transits.aspects_to_natal:
                st.dataframe([{"Transit": a.transit_planet, "Natal": a.natal_planet,
                               "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                               "Applying": "→" if a.is_applying else "←"}
                              for a in w_transits.aspects_to_natal[:20]],
                             use_container_width=True)
            else:
                st.info("No transit aspects found.")

        with _w_tab_return:
            st.subheader(t("western_subtab_return"))
            _return_year = st.number_input(t("return_year_label"),
                                           value=datetime.now().year,
                                           min_value=1900, max_value=2100,
                                           key="return_year")
            sun_planet = next((p for p in w_chart.planets if p.name.startswith("Sun")), None)
            if sun_planet:
                sr = compute_solar_return(
                    sun_planet.longitude, _return_year,
                    input_lat, input_lon, input_tz, location_name,
                )
                st.success(f"Solar Return: **{sr.return_date}**")
                render_western_chart(sr.return_chart)
            else:
                st.warning("Sun position not found in natal chart.")

        with _w_tab_synastry:
            st.subheader(t("synastry_header"))
            st.markdown(t("synastry_person_b"))
            _s_col1, _s_col2, _s_col3 = st.columns(3)
            with _s_col1:
                _s_date = st.date_input("Date B", value=date(1990, 6, 15), key="syn_date")
            with _s_col2:
                _s_time = st.time_input("Time B", value=time(12, 0), key="syn_time")
            with _s_col3:
                _s_tz = st.number_input("TZ B", value=input_tz, key="syn_tz",
                                        min_value=-12.0, max_value=14.0, step=0.5)
            if st.button("Calculate Synastry / 計算合盤", key="syn_btn"):
                w_b = compute_western_chart(
                    year=_s_date.year, month=_s_date.month, day=_s_date.day,
                    hour=_s_time.hour, minute=_s_time.minute,
                    timezone=_s_tz, latitude=input_lat, longitude=input_lon,
                    location_name=location_name,
                )
                syn = compute_synastry(w_chart, w_b, "Person A", "Person B")
                st.metric("Harmony Score", f"{syn.harmony_summary:.3f}")
                st.info(syn.summary_cn if get_lang() == "zh" else syn.summary_en)
                if syn.element_compatibility:
                    st.write(f"🔮 {syn.element_compatibility}")
                if syn.inter_aspects:
                    st.dataframe([{"A": a.planet_a, "B": a.planet_b,
                                   "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                   "Score": f"{a.harmony_score:+.3f}"}
                                  for a in syn.inter_aspects[:20]],
                                 use_container_width=True)

    # --- 印度占星 ---
    with tab_indian:
        _v_tab_rashi, _v_tab_dasha, _v_tab_ashtaka, _v_tab_yogas = st.tabs([
            t("vedic_subtab_rashi"),
            t("vedic_subtab_dasha"),
            t("vedic_subtab_ashtaka"),
            t("vedic_subtab_yogas"),
        ])

        with _v_tab_rashi:
            render_vedic_chart(v_chart)
            render_download_buttons(vedic_chart_to_dict(v_chart), key_prefix="vedic")

        with _v_tab_dasha:
            st.subheader(t("vedic_subtab_dasha"))
            moon_p = next((p for p in v_chart.planets if "Chandra" in p.name or "Moon" in p.name), None)
            if moon_p:
                vim = compute_vimshottari(moon_p.longitude, v_chart.julian_day)
                st.info(f"Moon Nakshatra: **{vim.moon_nakshatra}** | Lord: **{vim.moon_nakshatra_lord}** | Balance: {vim.balance_years:.2f} yrs")
                for md in vim.mahadasha_periods:
                    with st.expander(f"**{md.lord}** ({md.lord_cn}) — {md.start_date} to {md.end_date} ({md.years:.1f} yrs)"):
                        if md.sub_periods:
                            st.dataframe([{"Lord": s.lord, "CN": s.lord_cn,
                                          "Start": s.start_date, "End": s.end_date,
                                          "Years": f"{s.years:.2f}"}
                                         for s in md.sub_periods],
                                         use_container_width=True)
                st.divider()
                st.markdown("##### Yogini Dasha (36-year cycle)")
                yog = compute_yogini(moon_p.longitude, v_chart.julian_day)
                st.dataframe([{"Yogini": p.lord, "CN": p.lord_cn,
                              "Start": p.start_date, "End": p.end_date,
                              "Years": f"{p.years:.2f}"}
                             for p in yog.periods], use_container_width=True)
            else:
                st.warning("Moon position not found.")

        with _v_tab_ashtaka:
            st.subheader(t("vedic_subtab_ashtaka"))
            p_lons = {}
            for p in v_chart.planets:
                key = p.name.split("(")[0].strip().split()[0]
                _MAP = {"Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
                        "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn"}
                canonical = _MAP.get(key, key)
                p_lons[canonical] = p.longitude
            asc_lon = getattr(v_chart, 'ascendant', 0.0) if hasattr(v_chart, 'ascendant') else 0.0
            if len(p_lons) >= 7:
                av = compute_ashtakavarga(p_lons, asc_lon)
                st.info(f"Sarvashtakavarga Total: **{av.sarva_total}**")
                import pandas as pd
                signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                         "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
                rows = []
                for bav in av.bav:
                    row = {"Planet": f"{bav.planet} ({bav.planet_cn})"}
                    for i, s in enumerate(signs):
                        row[s] = bav.bindus[i]
                    row["Total"] = bav.total
                    rows.append(row)
                sarva_row = {"Planet": "SARVA"}
                for i, s in enumerate(signs):
                    sarva_row[s] = av.sarva[i]
                sarva_row["Total"] = av.sarva_total
                rows.append(sarva_row)
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.warning("Insufficient planet data for Ashtakavarga.")

        with _v_tab_yogas:
            st.subheader(t("vedic_subtab_yogas"))
            p_lons_y = {}
            for p in v_chart.planets:
                key = p.name.split("(")[0].strip().split()[0]
                _MAP2 = {"Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
                         "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus",
                         "Shani": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu"}
                canonical = _MAP2.get(key, key)
                p_lons_y[canonical] = p.longitude
            asc_lon_y = getattr(v_chart, 'ascendant', 0.0) if hasattr(v_chart, 'ascendant') else 0.0
            yogas = compute_yogas(p_lons_y, asc_lon_y)
            for yg in yogas:
                icon = "✅" if yg.is_present else "⬜"
                with st.expander(f"{icon} {yg.name} ({yg.name_cn}) — {yg.strength}"):
                    st.write(yg.description_cn if get_lang() == "zh" else yg.description)

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

    # --- 希臘占星 (Hellenistic) ---
    with tab_hellenistic:
        st.markdown(t("desc_hellenistic"))
        with st.spinner(t("spinner_hellenistic")):
            _hellen_chart = compute_hellenistic_chart(
                w_chart,
                birth_year=birth_date.year,
                current_year=datetime.now().year,
            )
        _h_tab_chart, _h_tab_natal, _h_tab_prof, _h_tab_zr, _h_tab_lots = st.tabs([
            t("hellen_subtab_chart"),
            t("hellen_subtab_natal"),
            t("hellen_subtab_profections"),
            t("hellen_subtab_zr"),
            t("hellen_subtab_lots"),
        ])
        with _h_tab_chart:
            _greek_svg = build_greek_horoscope_svg(
                _hellen_chart,
                year=birth_date.year,
                month=birth_date.month,
                day=birth_date.day,
                hour=birth_time.hour,
                minute=birth_time.minute,
                tz=tz_offset,
                location=location_name,
            )
            st.markdown(_greek_svg, unsafe_allow_html=True)
            st.caption(
                '<p style="text-align:center; color:#888; font-size:11px;">'
                'Greek Horoscope (θέμα) — Square chart form after L 497 · '
                'Whole-sign houses · ASC at left, MC at top'
                '</p>',
                unsafe_allow_html=True,
            )
        with _h_tab_natal:
            render_hellenistic_chart(_hellen_chart)
        with _h_tab_prof:
            if _hellen_chart.profection:
                pf = _hellen_chart.profection
                st.subheader("Annual Profections / 年限推進")
                st.metric("Age", pf.current_age)
                st.metric("Profected Sign", f"{pf.profected_sign} ({pf.profected_sign_cn})")
                st.metric("Time Lord", f"{pf.time_lord} ({pf.time_lord_cn})")
                st.info(f"House from Ascendant: {pf.house_from_asc}")
        with _h_tab_zr:
            if _hellen_chart.zodiacal_releasing:
                st.subheader("Zodiacal Releasing (L1) / 黃道釋放")
                st.dataframe([{"Sign": p.sign, "CN": p.sign_cn,
                               "Ruler": p.ruler, "Years": p.years,
                               "Start": p.start_date, "End": p.end_date}
                              for p in _hellen_chart.zodiacal_releasing],
                             use_container_width=True)
        with _h_tab_lots:
            if _hellen_chart.lots:
                st.subheader("Greek Lots / 希臘點")
                st.dataframe([{"Name": f"{l.name} ({l.name_cn})",
                               "Sign": l.sign, "Degree": f"{l.sign_degree:.2f}°",
                               "House": l.house, "Formula": l.formula_en,
                               "Meaning": l.meaning_cn}
                              for l in _hellen_chart.lots],
                             use_container_width=True)

    # --- 跨體系比較 (Cross-System Comparison) ---
    with tab_cross_compare:
        st.markdown(t("desc_cross_compare"))
        with st.spinner(t("spinner_cross_compare")):
            _cross = compute_cross_comparison(chart, w_chart, v_chart)
        render_cross_comparison(_cross)

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
    with tab_hellenistic:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_hellenistic"))
    with tab_cross_compare:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_cross_compare"))
