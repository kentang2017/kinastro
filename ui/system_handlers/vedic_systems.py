"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t
from core.cached_computations import (
    compute_ashtakavarga_cached,
    compute_bphs_cached,
    compute_varga_cached,
    compute_vimshottari_cached,
    compute_yogas_cached,
    compute_yogini_cached,
    get_or_compute_chart,
    _birth_sig,
)

_LEGACY_NAMES = ('VARGA_INFO', 'VARGA_KEYS', 'auto_cn', 'compute_jaimini_chart', 'compute_lal_kitab_chart', 'compute_nadi_chart', 'compute_vedic_chart', 'get_dasha_reading', 'get_lang', 'get_yogini_reading', 'render_jaimini_chart', 'render_jaimini_dasha', 'render_lal_kitab_1952_page', 'render_nadi_chart', 'render_single_varga', 'render_sukkayodo_chart', 'render_vedic_chart', 'render_vedic_financial_tab')

def _bind_legacy() -> None:
    from core import legacy_bridge as _legacy_bridge

    for _name in _LEGACY_NAMES:
        if hasattr(_legacy_bridge, _name):
            globals()[_name] = getattr(_legacy_bridge, _name)

def _render_ai_button(system_key: str, chart_obj, page_content: str = "", **_kwargs) -> None:
    set_ai_context(system_key, chart_obj, page_content)

def _render_bphs_result(bphs_result):
    """Render BPHS interpretation result in Streamlit."""
    import pandas as pd

    # ── 1. 行星品位 (Dignity) ──
    st.markdown(t("bphs_section_dignity"))
    st.caption(t("bphs_caption_dignity"))
    _dignity_rows = []
    for d in bphs_result.dignities:
        status_icon = ""
        if d.uccha:
            status_icon = "⬆️"
        elif d.neecha:
            status_icon = "⬇️"
        elif d.moola_trikona:
            status_icon = "🔺"
        elif d.own_sign:
            status_icon = "🏠"
        _dignity_rows.append({
            "": status_icon,
            t("bphs_col_planet"): f"{auto_cn(d.planet_zh)} ({d.planet})",
            t("bphs_col_sign"): f"{auto_cn(d.rashi_zh)} ({d.rashi_en})",
            t("bphs_col_dignity"): auto_cn(d.status_zh),
        })
    if _dignity_rows:
        st.dataframe(pd.DataFrame(_dignity_rows), hide_index=True, width='stretch')

    st.divider()

    # ── 2. 行星友敵關係 (Graha Maitri) ──
    st.markdown(t("bphs_section_maitri"))
    st.caption(t("bphs_caption_maitri"))
    _maitri_rows = []
    for m in bphs_result.graha_maitri:
        _maitri_rows.append({
            t("bphs_col_planet"): f"{auto_cn(m.planet_zh)} ({m.planet})",
            t("bphs_col_friends"): auto_cn(m.friends_zh),
            t("bphs_col_neutral"): auto_cn(m.neutral_zh),
            t("bphs_col_enemies"): auto_cn(m.enemies_zh),
        })
    if _maitri_rows:
        st.dataframe(pd.DataFrame(_maitri_rows), hide_index=True, width='stretch')

    st.divider()

    # ── 3. 行星阿瓦斯塔 (Graha Avastha) ──
    st.markdown(t("bphs_section_avastha"))
    st.caption(t("bphs_caption_avastha"))
    _strength_icon_map = {"強": "💪", "中": "⚖️", "弱": "⚠️"}
    for av in bphs_result.avasthas:
        _av_strength = auto_cn(av.strength)
        strength_icon = _strength_icon_map.get(av.strength, "❓")
        with st.expander(f"{strength_icon} {auto_cn(av.planet_zh)} ({av.planet}) — {auto_cn(av.avastha_name)} [{_av_strength}]"):
            st.markdown(f"**{t('bphs_label_avastha')}:** {auto_cn(av.avastha_name)}")
            st.markdown(f"**{t('bphs_label_strength')}:** {_av_strength}")
            st.markdown(f"**{t('bphs_label_effect')}:** {auto_cn(av.reading_zh)}")

    st.divider()

    # ── 4. 王者瑜伽 (Raja Yoga) ──
    st.markdown(t("bphs_section_raja"))
    st.caption(t("bphs_caption_raja"))
    for ry in bphs_result.raja_yogas:
        icon = "✅" if ry.is_present else "⬜"
        with st.expander(f"{icon} {auto_cn(ry.name)}"):
            st.markdown(f"**{t('bphs_label_description')}:** {auto_cn(ry.description_zh)}")
            st.markdown(f"**{t('bphs_label_judgment')}:** {auto_cn(ry.reason_zh)}")

    st.divider()

    # ── 5. 宮位果報 (Bhava Phala) ──
    st.markdown(t("bphs_section_bhava"))
    st.caption(t("bphs_caption_bhava"))
    for br in bphs_result.bhava_readings:
        _house_label = t("bphs_label_house_num").format(n=br.bhava)
        label_parts = [f"{_house_label} {auto_cn(br.bhava_zh)}"]
        if br.signification:
            label_parts.append(f"— {br.signification}")
        label = " ".join(label_parts)
        with st.expander(label):
            _lord_in = t("bphs_label_lord_in_house").format(n=br.lord_house)
            st.markdown(f"**{t('bphs_label_house_lord')}:** {auto_cn(br.lord_zh)} ({br.lord_key}) — {_lord_in}")
            if br.lord_placement_zh:
                st.info(f"{t('bphs_label_lord_reading')}：{auto_cn(br.lord_placement_zh)}")
            if br.planets_in_bhava:
                st.markdown(t("bphs_label_planets_in"))
                for pk, pk_zh, reading, level in br.planets_in_bhava:
                    level_str = f" [{auto_cn(level)}]" if level else ""
                    st.markdown(f"- **{auto_cn(pk_zh)}** ({pk}){level_str}：{auto_cn(reading)}")
            if br.special_yogas:
                st.markdown(t("bphs_label_special_yogas"))
                for sy in br.special_yogas:
                    st.markdown(f"- **{auto_cn(sy.get('name', ''))}**：{auto_cn(sy.get('zh', ''))}")
            if br.note_zh:
                st.caption(f"💡 {auto_cn(br.note_zh)}")

    st.divider()

    # ── 6. 16分盤簡表 (Shodasa Varga Reference) ──
    st.markdown(t("bphs_section_varga"))
    st.caption(t("bphs_caption_varga"))
    _varga_rows = []
    for key, val in bphs_result.varga_info.get("vargas", {}).items():
        _varga_rows.append({
            t("bphs_col_varga_chart"): key,
            t("bphs_col_varga_name"): auto_cn(val.get("zh", "")),
            t("bphs_col_varga_division"): val.get("division", ""),
            t("bphs_col_varga_use"): auto_cn(val.get("use", "")),
            t("bphs_col_varga_judgment"): auto_cn(val.get("judgment", "")),
        })
    if _varga_rows:
        st.dataframe(pd.DataFrame(_varga_rows), hide_index=True, width='stretch')
    note = bphs_result.varga_info.get("general_note_zh", "")
    if note:
        st.caption(f"💡 {auto_cn(note)}")


def render_tab_indian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_indian"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_indian")):
                v_chart = get_or_compute_chart(
                    "tab_indian",
                    _p,
                    {"location_name": _p.get("location_name", "")},
                )

            _v_tab_rashi, _v_tab_dasha, _v_tab_ashtaka, _v_tab_yogas, _v_tab_bphs, _v_tab_varga, _v_tab_financial = st.tabs([
                t("vedic_subtab_rashi"),
                t("vedic_subtab_dasha"),
                t("vedic_subtab_ashtaka"),
                t("vedic_subtab_yogas"),
                t("vedic_subtab_bphs"),
                t("vedic_subtab_varga"),
                t("vedic_subtab_financial"),
            ])

            with _v_tab_rashi:
                render_vedic_chart(v_chart, after_chart_hook=lambda: _render_ai_button("tab_indian", v_chart, btn_key="vedic"))

            with _v_tab_dasha:
                st.subheader(t("vedic_subtab_dasha"))
                moon_p = next((p for p in v_chart.planets if "Chandra" in p.name or "Moon" in p.name), None)
                if moon_p:
                    vim = compute_vimshottari_cached(moon_p.longitude, v_chart.julian_day)
                    st.info(f"Moon Nakshatra: **{vim.moon_nakshatra}** | Lord: **{vim.moon_nakshatra_lord}** | Balance: {vim.balance_years:.2f} yrs")
                    for md in vim.mahadasha_periods:
                        _dasha_reading = get_dasha_reading(md.lord, get_lang())
                        with st.expander(f"**{md.lord}** ({md.lord_cn}) — {md.start_date} to {md.end_date} ({md.years:.1f} yrs)"):
                            if _dasha_reading:
                                st.markdown(f"📖 {_dasha_reading}")
                            if md.sub_periods:
                                st.dataframe([{"Lord": s.lord, "CN": s.lord_cn,
                                              "Start": s.start_date, "End": s.end_date,
                                              "Years": f"{s.years:.2f}"}
                                             for s in md.sub_periods],
                                             width="stretch")
                    st.divider()
                    st.markdown("##### Yogini Dasha (36-year cycle)")
                    yog = compute_yogini_cached(moon_p.longitude, v_chart.julian_day)
                    st.dataframe([{"Yogini": p.lord, "CN": p.lord_cn,
                                  "Start": p.start_date, "End": p.end_date,
                                  "Years": f"{p.years:.2f}"}
                                 for p in yog.periods], width="stretch")
                    # Yogini reading for current period
                    if yog.periods:
                        _yog_reading = get_yogini_reading(yog.periods[0].lord, get_lang())
                        if _yog_reading:
                            st.info(f"📖 Current: {_yog_reading}")
                else:
                    st.warning("Moon position not found.")
                _render_ai_button("tab_indian", v_chart, btn_key="vedic_dasha")

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
                    av = compute_ashtakavarga_cached(tuple(sorted(p_lons.items())), asc_lon)
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
                    st.dataframe(pd.DataFrame(rows), width="stretch")
                else:
                    st.warning("Insufficient planet data for Ashtakavarga.")
                _render_ai_button("tab_indian", v_chart, btn_key="vedic_ashtaka")

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
                yogas = compute_yogas_cached(tuple(sorted(p_lons_y.items())), asc_lon_y)
                for yg in yogas:
                    icon = "✅" if yg.is_present else "⬜"
                    with st.expander(f"{icon} {yg.name} ({auto_cn(yg.name_cn)}) — {yg.strength}"):
                        _yg_text = yg.description_cn if get_lang() in ("zh", "zh_cn") else yg.description
                        st.write(auto_cn(_yg_text))
                _render_ai_button("tab_indian", v_chart, btn_key="vedic_yogas")

            with _v_tab_bphs:
                st.subheader("📜 " + t("vedic_subtab_bphs"))
                bphs_result = compute_bphs_cached(_birth_sig(_p), _p.get("location_name", ""))
                _render_bphs_result(bphs_result)
                _render_ai_button("tab_indian", v_chart, btn_key="vedic_bphs")

            with _v_tab_varga:
                st.subheader("📊 " + t("vedic_subtab_varga"))
                st.caption(t("bphs_caption_varga_tab"))
                _varga_tab_labels = [f"{k} {VARGA_INFO[k]['zh']}" for k in VARGA_KEYS]
                _varga_tabs = st.tabs(_varga_tab_labels)
                for _vi, _vk in enumerate(VARGA_KEYS):
                    with _varga_tabs[_vi]:
                        _vc = compute_varga_cached(_vk, _birth_sig(_p), _p.get("location_name", ""))
                        render_single_varga(_vc)
                _render_ai_button("tab_indian", v_chart, btn_key="vedic_varga")

            with _v_tab_financial:
                render_vedic_financial_tab(input_tz=float(_p.get("timezone", 8.0)))

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_indian"))


def render_tab_vastu() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_vastu"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_vastu")):
                _vastu_vchart = compute_vedic_chart(**_p)
            from frontend.vastu_renderer import render_vastu_tab
            render_vastu_tab(
                v_chart=_vastu_vchart,
                after_chart_hook=lambda: _render_ai_button("tab_vastu", _vastu_vchart, btn_key="vastu"),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_vastu_prompt"))
        st.markdown(t("desc_vastu"))


def render_tab_lal_kitab() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_lal_kitab"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_lal_kitab")):
                _lk_chart = compute_lal_kitab_chart(**_p)
            _lk_lang = st.session_state.get("lang", "zh")
            render_lal_kitab_1952_page(
                _lk_chart,
                lang=_lk_lang,
                after_chart_hook=lambda: _render_ai_button("tab_lal_kitab", _lk_chart, btn_key="lal_kitab"),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_lal_kitab"))


def render_tab_sukkayodo() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_sukkayodo"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_indian")):
                _v_chart_sukka = compute_vedic_chart(**_p)
            render_sukkayodo_chart(_v_chart_sukka, after_chart_hook=lambda: _render_ai_button("tab_sukkayodo", _v_chart_sukka, btn_key="sukkayodo"))
            st.subheader(t("sukkayodo_subheader"))
            st.info(t("sukkayodo_info"))
            st.markdown(t("desc_sukkayodo"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_sukkayodo"))


def render_tab_kp() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_kp"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_kp") if hasattr(t, "spinner_kp") else "計算 KP 星盤..."):
                from astro.kp import compute_kp_chart, render_kp_chart
            
                kp_chart = compute_kp_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    latitude=_p.get("latitude", 0.0), longitude=_p.get("longitude", 0.0),
                    timezone=_p.get("timezone", 0.0),
                    language=get_lang()
                )
        
            # KP Astrology main layout
            st.header(t("kp_title"))
            st.caption(t("kp_subtitle"))
        
            # KP vs Vedic note
            st.info(t("kp_placidus_note"))
        
            # Render KP chart (tables + SVG chart)
            render_kp_chart(kp_chart, language=get_lang())
        
            # AI Analysis button
            _render_ai_button("tab_kp", kp_chart, btn_key="kp")
        
        except ImportError as _ie:
            st.error("KP Astrology module not available.")
            st.exception(_ie)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_kp") if hasattr(t, "desc_kp") else "🔮 **KP Astrology (Krishnamurti Paddhati)** — 印度現代占星大師 K.S. Krishnamurti 創立的精確預測系統，使用宿度主星 (Sub Lord) 和時辰主星 (Ruling Planets) 判斷事件發生時機。")


def render_tab_nadi() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_nadi"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_nadi")):
                nadi_chart = compute_nadi_chart(**_p)
            render_nadi_chart(nadi_chart, after_chart_hook=lambda: _render_ai_button("tab_nadi", nadi_chart, btn_key="nadi"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_nadi"))


def render_tab_jaimini() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_jaimini"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    if _p0:
        birth_date = date(_p0["year"], _p0["month"], _p0["day"])
        birth_time = time_cls(_p0["hour"], _p0["minute"])
        input_tz = _p0.get("timezone", 8.0)
        input_lat = _p0.get("latitude", 25.033)
        input_lon = _p0.get("longitude", 121.565)
        location_name = _p0.get("location_name", "")
    else:
        birth_date = None
        birth_time = None
        input_tz = 8.0
        input_lat = 25.033
        input_lon = 121.565
        location_name = ""
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_jaimini")):
                jm_chart = compute_jaimini_chart(**_p)

            _jm_tab_chart, _jm_tab_dasha = st.tabs([
                t("jaimini_subtab_chart"),
                t("jaimini_subtab_dasha"),
            ])

            with _jm_tab_chart:
                render_jaimini_chart(jm_chart, after_chart_hook=lambda: _render_ai_button("tab_jaimini", jm_chart, btn_key="jaimini"))

            with _jm_tab_dasha:
                render_jaimini_dasha(jm_chart)
                _render_ai_button("tab_jaimini", jm_chart, btn_key="jaimini_dasha")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_jaimini"))
