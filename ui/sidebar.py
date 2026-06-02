"""Sidebar rendering for KinAstro.

Provides ``render_sidebar()`` which renders the entire left sidebar
including city/location selection, the birth-data form, system selector,
advanced bodies settings, AI settings, and the contact section.

Also exports city preset helpers and constants used by the main app.
"""

from __future__ import annotations

import json
from datetime import date, time
from pathlib import Path
from typing import Any

import streamlit as st

from astro.ai_analysis import (
    CEREBRAS_MODEL_OPTIONS,
    CEREBRAS_MODEL_DESCRIPTIONS,
    OPENAI_MODEL_OPTIONS,
    OPENAI_MODEL_DESCRIPTIONS,
    DEFAULT_SYSTEM_PROMPT,
)
from ui.helpers import t, auto_cn
from ui.components.system_selector import render_system_selector
from ui.state import SessionKeys


# ============================================================
# 世界城市資料 (城市, 緯度, 經度, 時區)
# ============================================================
_CITY_DATA_DIR = Path(__file__).resolve().parent.parent / "tools" / "cities"
_CITY_WORLD_LIMIT = 3000
_CHINA_REGION_TZ = 8.0
_DEFAULT_LAT = 22.3193
_DEFAULT_LON = 114.1694
_DEFAULT_TZ = 8.0
_CITY_CUSTOM_LABEL = "自訂"
_PRIORITY_REGION_COUNTRIES = {"CN", "HK", "MO", "TW"}

STAR_CATALOG_ALL = -1


def _normalize_tz_from_lon(lon: float) -> float:
    tz = round((float(lon) / 15.0) * 2) / 2
    return max(-12.0, min(14.0, tz))


def _coerce_float_in_range(
    value: Any,
    *,
    default: float,
    min_value: float,
    max_value: float,
) -> float:
    try:
        _num = float(value)
    except (TypeError, ValueError):
        _num = default
    return max(min_value, min(max_value, _num))


def _safe_pop(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@st.cache_data(show_spinner=False)
def _build_city_presets() -> tuple[
    dict[str, tuple[float, float, float]],
    list[str],
]:
    city_presets: dict[str, tuple[float, float, float]] = {}

    def _add_city(city_name: str, lat: float, lon: float, tz: float) -> None:
        if city_name not in city_presets:
            city_presets[city_name] = (lat, lon, tz)

    china_file = _CITY_DATA_DIR / "china_cities.json"
    if china_file.exists():
        china_data = json.loads(china_file.read_text(encoding="utf-8"))

        def _collect_china_city(city_node: dict) -> None:
            city_name = (city_node.get("name") or "").strip()
            center = city_node.get("center") or {}
            if not city_name or "latitude" not in center or "longitude" not in center:
                return
            lat = float(center["latitude"])
            lon = float(center["longitude"])
            tz = _CHINA_REGION_TZ
            _add_city(city_name, lat, lon, tz)

        for province in china_data.get("districts", []) or []:
            province_name = province.get("name")
            province_center = province.get("center") or {}
            province_tz = _CHINA_REGION_TZ

            city_children = [
                c for c in (province.get("districts", []) or [])
                if c.get("level") == "city"
            ]
            if city_children:
                for city_node in city_children:
                    _collect_china_city(city_node)
            elif province_name and "latitude" in province_center and "longitude" in province_center:
                _add_city(
                    province_name,
                    float(province_center["latitude"]),
                    float(province_center["longitude"]),
                    province_tz,
                )

    world_file = _CITY_DATA_DIR / "cities.json"
    if world_file.exists():
        world_rows = json.loads(world_file.read_text(encoding="utf-8"))
        world_rows.sort(key=lambda r: _safe_pop(r.get("pop")), reverse=True)

        def _add_admin_alias(admin_name: str, country: str, lat: float, lon: float, tz: float) -> None:
            _admin = (admin_name or "").strip()
            if not _admin:
                return
            _label = f"{_admin} ({country})" if country else _admin
            _add_city(_label, lat, lon, tz)

        for idx, row in enumerate(world_rows):
            name = (row.get("name") or "").strip()
            country = (row.get("country") or "").strip()
            if not name or "lat" not in row or "lon" not in row:
                continue
            # Keep global options performant by capping low-population world rows,
            # while still loading full coverage for Greater China locales.
            if idx >= _CITY_WORLD_LIMIT and country not in _PRIORITY_REGION_COUNTRIES:
                continue

            city_label = f"{name} ({country})" if country else name
            lat = float(row["lat"])
            lon = float(row["lon"])
            tz = _CHINA_REGION_TZ if country in {"CN", "HK", "MO", "TW"} else _normalize_tz_from_lon(lon)
            _add_city(city_label, lat, lon, tz)
            _add_admin_alias(row.get("admin1") or "", country, lat, lon, tz)
            _add_admin_alias(row.get("admin2") or "", country, lat, lon, tz)

    city_presets[_CITY_CUSTOM_LABEL] = (0.0, 0.0, 0.0)
    city_options = sorted([c for c in city_presets if c != _CITY_CUSTOM_LABEL]) + [_CITY_CUSTOM_LABEL]
    return city_presets, city_options


CITY_PRESETS, CITY_OPTIONS = _build_city_presets()


def render_sidebar() -> None:
    """Render the full sidebar including birth form and system selector."""
    with st.sidebar:
        st.header(t("sidebar_header"))

        _dt_col, _now_col = st.columns([3, 1])
        _dt_col.subheader(t("date_time"))
        if _now_col.button(
            auto_cn("現時", "Now"),
            key="now_btn",
            width="stretch",
            help=auto_cn("填入現在的日期和時間", "Fill in the current date and time"),
        ):
            from datetime import datetime
            _now = datetime.now()
            st.session_state["birth_date_input"] = _now.date()
            st.session_state["birth_time_input"] = _now.time().replace(second=0, microsecond=0)
            st.rerun()

        if "birth_date_input" not in st.session_state:
            st.session_state["birth_date_input"] = date(1990, 1, 1)
        if "birth_time_input" not in st.session_state:
            st.session_state["birth_time_input"] = time(12, 0)
        if "_lat_input" not in st.session_state:
            st.session_state["_lat_input"] = _DEFAULT_LAT
        if "_lon_input" not in st.session_state:
            st.session_state["_lon_input"] = _DEFAULT_LON
        if "_tz_input" not in st.session_state:
            st.session_state["_tz_input"] = _DEFAULT_TZ

        st.subheader(t("birth_location"))
        city = st.selectbox(
            t("city_preset"),
            options=CITY_OPTIONS,
            key="city_sel",
        )

        _prev_city = st.session_state.get("_prev_city_sel")
        if _prev_city == _CITY_CUSTOM_LABEL and city != _CITY_CUSTOM_LABEL:
            st.session_state["_custom_lat"] = st.session_state.get("_lat_input", _DEFAULT_LAT)
            st.session_state["_custom_lon"] = st.session_state.get("_lon_input", _DEFAULT_LON)
            st.session_state["_custom_tz"] = st.session_state.get("_tz_input", _DEFAULT_TZ)
        st.session_state["_prev_city_sel"] = city

        with st.form("birth_data_form", border=False):
            birth_date = st.date_input(
                t("birth_date"),
                min_value=date(1, 1, 1),
                max_value=date(date.today().year, 12, 31),
                key="birth_date_input",
            )
            birth_time = st.time_input(
                t("birth_time"),
                key="birth_time_input",
            )

            _is_custom = city == _CITY_CUSTOM_LABEL
            if not _is_custom:
                _preset_lat, _preset_lon, _preset_tz = CITY_PRESETS.get(
                    city,
                    (_DEFAULT_LAT, _DEFAULT_LON, _DEFAULT_TZ),
                )
                st.session_state["_lat_input"] = _preset_lat
                st.session_state["_lon_input"] = _preset_lon
                st.session_state["_tz_input"] = _preset_tz
            else:
                _preset_lat = _coerce_float_in_range(
                    st.session_state.get("_custom_lat", _DEFAULT_LAT),
                    default=_DEFAULT_LAT,
                    min_value=-90.0,
                    max_value=90.0,
                )
                _preset_lon = _coerce_float_in_range(
                    st.session_state.get("_custom_lon", _DEFAULT_LON),
                    default=_DEFAULT_LON,
                    min_value=-180.0,
                    max_value=180.0,
                )
                _preset_tz = _coerce_float_in_range(
                    st.session_state.get("_custom_tz", _DEFAULT_TZ),
                    default=_DEFAULT_TZ,
                    min_value=-12.0,
                    max_value=14.0,
                )
                if _prev_city != _CITY_CUSTOM_LABEL:
                    st.session_state["_lat_input"] = _preset_lat
                    st.session_state["_lon_input"] = _preset_lon
                    st.session_state["_tz_input"] = _preset_tz

            if _is_custom and _prev_city == _CITY_CUSTOM_LABEL:
                st.session_state["_lat_input"] = _coerce_float_in_range(
                    st.session_state.get("_lat_input", _DEFAULT_LAT),
                    default=_DEFAULT_LAT,
                    min_value=-90.0,
                    max_value=90.0,
                )
                st.session_state["_lon_input"] = _coerce_float_in_range(
                    st.session_state.get("_lon_input", _DEFAULT_LON),
                    default=_DEFAULT_LON,
                    min_value=-180.0,
                    max_value=180.0,
                )
                st.session_state["_tz_input"] = _coerce_float_in_range(
                    st.session_state.get("_tz_input", _DEFAULT_TZ),
                    default=_DEFAULT_TZ,
                    min_value=-12.0,
                    max_value=14.0,
                )

            _coord_col1, _coord_col2 = st.columns(2)
            with _coord_col1:
                input_lat = st.number_input(
                    t("latitude"),
                    format="%.4f",
                    min_value=-90.0,
                    max_value=90.0,
                    disabled=not _is_custom,
                    key="_lat_input",
                )
            with _coord_col2:
                input_lon = st.number_input(
                    t("longitude"),
                    format="%.4f",
                    min_value=-180.0,
                    max_value=180.0,
                    disabled=not _is_custom,
                    key="_lon_input",
                )
            input_tz = st.number_input(
                t("timezone"),
                format="%.1f",
                min_value=-12.0,
                max_value=14.0,
                step=0.5,
                disabled=not _is_custom,
                key="_tz_input",
            )
            if _is_custom:
                if not (-90.0 <= input_lat <= 90.0) or not (-180.0 <= input_lon <= 180.0):
                    st.warning(t("form_validation_location"))

            if _is_custom:
                location_name = t("custom_location")
            else:
                location_name = city

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

            _form_submitted = st.form_submit_button(
                t("generate_chart_btn"),
                width="stretch",
                type="primary",
                key="_form_submit_button",  # Add explicit key for consistency
            )
            # Hidden checkbox to trigger form submission (helps with refresh issues)
            _form_submitted_flag = _form_submitted or st.session_state.get("_form_submitted_flag", False)
            st.session_state["_form_submitted_flag"] = _form_submitted_flag
            
            if _form_submitted_flag:
                if _is_custom:
                    st.session_state["_custom_lat"] = input_lat
                    st.session_state["_custom_lon"] = input_lon
                    st.session_state["_custom_tz"]  = input_tz
                st.session_state["_calc_success_flash"] = True
                st.session_state["_birth_confirmed"] = True
                st.session_state["_confirmed_params"] = dict(
                    year=birth_date.year, month=birth_date.month, day=birth_date.day,
                    hour=birth_time.hour, minute=birth_time.minute,
                    timezone=input_tz, latitude=input_lat, longitude=input_lon,
                    location_name=location_name,
                )
                st.session_state["_confirmed_gender"] = gender

        # ── Astrology system selector ────────────────────────────
        st.divider()
        st.markdown(
            f'<div class="sidebar-system-title">🌐 {t("sidebar_system_label")}</div>',
            unsafe_allow_html=True,
        )

        _cur_lang = st.session_state.get("lang", "zh")
        _search_placeholder = auto_cn("搜尋占星體系...") if _cur_lang in ("zh", "zh_cn") else "Search systems..."
        _system_search = st.text_input(
            "🔍",
            placeholder=_search_placeholder,
            key="_system_search",
            label_visibility="collapsed",
        )

        _selected_system = st.session_state.get(SessionKeys.SYSTEM_SELECT, None)
        _selected_system = render_system_selector(
            st_module=st,
            t=t,
            search_query=_system_search,
            current_system=_selected_system,
        )

        if st.button(
            t("tab_history"),
            key="_btn_history",
            width="stretch",
            type="secondary",
        ):
            st.session_state["_system_select"] = "tab_history"
            st.rerun()

        if st.button(
            t("tab_wiki"),
            key="_btn_wiki",
            width="stretch",
            type="secondary",
        ):
            st.session_state["_system_select"] = "tab_wiki"
            st.rerun()

        # ── Star particles toggle ────────────────────────────────
        st.divider()
        _particles_on = st.toggle(
            "✨ " + ("星空粒子背景" if _cur_lang in ("zh", "zh_cn") else "Star Particles"),
            value=st.session_state.get("_star_particles", True),
            key="_star_particles_toggle",
        )
        if _particles_on != st.session_state.get("_star_particles", True):
            st.session_state["_star_particles"] = _particles_on
            st.rerun()

        # ── Cross-system comparison toggle ───────────────────────
        _cross_system_on = st.toggle(
            t("enable_cross_system"),
            value=st.session_state.get("_cross_system_enabled", False),
            key="_cross_system_toggle",
            help=(
                "同時計算西洋、印度、七政四餘、紫微、希臘占星並進行 AI 交叉比對解讀"
                if _cur_lang in ("zh", "zh_cn") else
                "Compute Western, Vedic, Chinese, Zi Wei, and Hellenistic charts "
                "together for AI cross-system synthesis"
            ),
        )
        if _cross_system_on != st.session_state.get("_cross_system_enabled", False):
            st.session_state["_cross_system_enabled"] = _cross_system_on
            st.rerun()

        # ── Advanced Bodies settings ─────────────────────────────
        st.divider()
        with st.expander(t("adv_bodies_header"), expanded=False):
            _adv_ast = st.toggle(
                t("adv_asteroids_toggle"),
                value=st.session_state.get("_adv_asteroids", True),
                key="_adv_asteroids",
            )
            if _adv_ast:
                _group_options = {
                    t("adv_group_chiron_pholus"): "chiron_pholus",
                    t("adv_group_lilith"):        "lilith",
                    t("adv_group_main_belt"):     "main_belt",
                    t("adv_group_romance"):       "romance",
                    t("adv_group_centaurs"):      "centaurs",
                    t("adv_group_tnos"):          "tnos",
                    t("adv_group_dwarf_planets"): "dwarf_planets",
                }
                _selected_groups = st.multiselect(
                    t("adv_asteroids_groups"),
                    options=list(_group_options.keys()),
                    default=list(_group_options.keys())[:3],
                    key="_adv_ast_groups",
                )
                st.session_state["_adv_ast_group_keys"] = [
                    _group_options[g] for g in _selected_groups
                ]
                st.toggle(
                    t("adv_asteroids_helio"),
                    value=False,
                    key="_adv_helio",
                )
                st.toggle(
                    t("adv_asteroid_aspects_toggle"),
                    value=True,
                    key="_adv_ast_aspects",
                )

            _adv_stars = st.toggle(
                t("adv_stars_toggle"),
                value=st.session_state.get("_adv_fixed_stars", False),
                key="_adv_fixed_stars",
            )
            if _adv_stars:
                st.select_slider(
                    t("adv_stars_count"),
                    options=[10, 30, 50, STAR_CATALOG_ALL],
                    value=30,
                    key="_adv_stars_count",
                    format_func=lambda v: ("全部 / All" if v == STAR_CATALOG_ALL else str(v)),
                )

            st.toggle(
                t("adv_parans_toggle"),
                value=st.session_state.get("_adv_parans", False),
                key="_adv_parans",
                help=t("adv_parans_tooltip"),
            )

            st.toggle(
                t("adv_heliacal_toggle"),
                value=st.session_state.get("_adv_heliacal", False),
                key="_adv_heliacal",
                help=t("adv_heliacal_tooltip"),
            )

        # ── AI Analysis settings ─────────────────────────────────
        st.divider()
        with st.expander(t("ai_settings_header"), expanded=False):

            def _fmt_provider(x):
                if x == "cerebras":
                    return t("ai_provider_cerebras")
                if x == "openai":
                    return t("ai_provider_openai")
                return t("ai_provider_custom")

            _ai_provider = st.radio(
                t("ai_provider_label"),
                options=["cerebras", "openai", "custom"],
                format_func=_fmt_provider,
                key="_ai_provider",
                horizontal=True,
            )

            if _ai_provider == "openai":
                st.selectbox(
                    t("ai_model_label"),
                    options=OPENAI_MODEL_OPTIONS,
                    index=0,
                    key="_ai_model_select",
                    help="\n".join(f"• {k}: {v}" for k, v in OPENAI_MODEL_DESCRIPTIONS.items()),
                )
                st.text_input(
                    t("ai_openai_key_label"),
                    type="password",
                    key="_ai_openai_key",
                    help=t("ai_openai_key_help"),
                    placeholder="sk-...",
                )
            elif _ai_provider == "custom":
                st.text_input(
                    t("ai_custom_name_label"),
                    key="_ai_custom_name",
                    placeholder=t("ai_custom_name_placeholder"),
                )
                st.selectbox(
                    t("ai_custom_api_mode_label"),
                    options=["openai_compat"],
                    format_func=lambda x: t("ai_custom_api_mode_openai"),
                    key="_ai_custom_api_mode",
                )
                st.text_input(
                    t("ai_custom_key_label"),
                    type="password",
                    key="_ai_custom_key",
                    help=t("ai_custom_key_help"),
                )
                _host_col, _path_col = st.columns(2)
                with _host_col:
                    st.text_input(
                        t("ai_custom_host_label"),
                        key="_ai_custom_host",
                        placeholder="https://api.example.com/v1",
                    )
                with _path_col:
                    st.text_input(
                        t("ai_custom_path_label"),
                        key="_ai_custom_path",
                        placeholder="/chat/completions",
                        value=st.session_state.get("_ai_custom_path", "/chat/completions"),
                    )
                _host_val = st.session_state.get("_ai_custom_host", "").rstrip("/")
                _path_val = st.session_state.get("_ai_custom_path", "/chat/completions")
                if _host_val:
                    st.caption(f"{t('ai_custom_url_preview')}{_host_val}{_path_val}")

                if "_ai_custom_models" not in st.session_state:
                    st.session_state["_ai_custom_models"] = []

                _m_label_col, _m_add_col, _m_reset_col, _m_fetch_col = st.columns([2, 1, 1, 1])
                with _m_label_col:
                    st.markdown(f"**{t('ai_custom_models_header')}**")
                with _m_add_col:
                    if st.button(t("ai_custom_models_add"), key="_btn_custom_add"):
                        st.session_state["_ai_custom_model_adding"] = True
                with _m_reset_col:
                    if st.button(t("ai_custom_models_reset"), key="_btn_custom_reset"):
                        st.session_state["_ai_custom_models"] = []
                        st.session_state.pop("_ai_custom_model_adding", None)
                with _m_fetch_col:
                    if st.button(t("ai_custom_models_fetch"), key="_btn_custom_fetch"):
                        _fetch_host = st.session_state.get("_ai_custom_host", "").rstrip("/")
                        _fetch_key = st.session_state.get("_ai_custom_key", "").strip()
                        if _fetch_host and _fetch_key:
                            try:
                                import openai as _oa
                                _fc = _oa.OpenAI(api_key=_fetch_key, base_url=_fetch_host)
                                _models_resp = _fc.models.list()
                                _fetched = sorted([m.id for m in _models_resp.data])
                                st.session_state["_ai_custom_models"] = _fetched
                                st.success(t("ai_custom_fetch_ok").format(len(_fetched)))
                            except Exception as _fe:
                                st.error(t("ai_custom_fetch_fail").format(str(_fe)))

                if st.session_state.get("_ai_custom_model_adding"):
                    st.text_input(
                        "",
                        key="_ai_custom_new_model_input",
                        placeholder=t("ai_custom_model_new_placeholder"),
                        label_visibility="collapsed",
                    )
                    _confirm_col, _cancel_col = st.columns(2)
                    with _confirm_col:
                        if st.button("✔", key="_btn_custom_confirm"):
                            _nm = st.session_state.get("_ai_custom_new_model_input", "").strip()
                            if _nm and _nm not in st.session_state["_ai_custom_models"]:
                                st.session_state["_ai_custom_models"].append(_nm)
                            st.session_state.pop("_ai_custom_model_adding", None)
                            st.rerun()
                    with _cancel_col:
                        if st.button("✘", key="_btn_custom_cancel"):
                            st.session_state.pop("_ai_custom_model_adding", None)
                            st.rerun()

                _custom_models = st.session_state.get("_ai_custom_models", [])
                for _mi, _mname in enumerate(_custom_models):
                    _mrow_cols = st.columns([4, 1])
                    with _mrow_cols[0]:
                        st.text(_mname)
                    with _mrow_cols[1]:
                        if st.button("⊖", key=f"_btn_del_model_{_mi}"):
                            st.session_state["_ai_custom_models"].pop(_mi)
                            st.rerun()

                if _custom_models:
                    st.selectbox(
                        t("ai_model_label"),
                        options=_custom_models,
                        key="_ai_model_select",
                    )
                else:
                    st.session_state["_ai_model_select"] = ""
            else:
                st.selectbox(
                    t("ai_model_label"),
                    options=CEREBRAS_MODEL_OPTIONS,
                    index=0,
                    key="_ai_model_select",
                    help="\n".join(f"• {k}: {v}" for k, v in CEREBRAS_MODEL_DESCRIPTIONS.items()),
                )

            st.session_state.ai_system_prompt = DEFAULT_SYSTEM_PROMPT

            st.slider(
                t("ai_max_tokens"), min_value=256, max_value=32768, value=8192, step=256,
                key="_ai_max_tokens",
                help=t("ai_max_tokens_help"),
            )
            st.slider(
                t("ai_temperature"), min_value=0.0, max_value=2.0, value=0.7, step=0.1,
                key="_ai_temperature",
                help=t("ai_temperature_help"),
            )

        # ── About / Contact section ──────────────────────────────
        st.divider()
        with st.expander(t("tab_contact"), expanded=False):
            st.subheader(t("contact_title"))
            st.markdown(t("contact_wechat"))
            st.markdown(t("contact_wechat_id"))
            st.markdown(t("contact_qq"))
            st.subheader(t("contact_other_apps"))
            _contact_apps = [
                ("https://iching.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/ichingshifa/master/pic/iching.png"),
                ("https://kintaiyi.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/Untitled-1.png"),
                ("https://kinliuren.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinliuren/master/pic/Untitled-33.png"),
                ("https://kinwuzhao.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwuzhao/refs/heads/main/pic/wuzhao.png"),
                ("https://kintaixuan.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/taixuanshifa/master/pic/taixuan.png"),
                ("https://kinwangji.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwangji/refs/heads/main/pic/kwj.png"),
                ("https://jingjue.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/jingjue/master/pic/jingjue.png"),
                ("https://liangtouqian.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/liangtouqian/main/pic/Untitled-44.png"),
            ]
            _contact_cols = st.columns(3)
            for _ci, (_curl, _cimg) in enumerate(_contact_apps):
                with _contact_cols[_ci % 3]:
                    st.markdown(
                        f'<a href="{_curl}" target="_blank"><img src="{_cimg}" style="max-width:100%;height:auto;margin-bottom:8px;"></a>',
                        unsafe_allow_html=True,
                    )
            st.image(
                "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/20231205113526.jpg",
                width='stretch',
            )
