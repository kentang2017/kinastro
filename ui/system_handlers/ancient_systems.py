"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t

_LEGACY_NAMES = ('_compute_andean_chart_fn', '_compute_armenian_chart_fn', '_compute_etruscan_chart_fn', 'compute_aztec_chart', 'compute_decan_chart', 'compute_maya_chart', 'compute_sumerian_chart', 'render_andean_chart_ui', 'render_armenian_chart_ui', 'render_aztec_chart', 'render_decan_browse', 'render_decan_chart', 'render_etruscan_chart_ui', 'render_maya_chart', 'render_sumerian_chart')

def _bind_legacy() -> None:
    from core import legacy_bridge as _legacy_bridge

    for _name in _LEGACY_NAMES:
        if hasattr(_legacy_bridge, _name):
            globals()[_name] = getattr(_legacy_bridge, _name)

def _render_ai_button(system_key: str, chart_obj, page_content: str = "", **_kwargs) -> None:
    set_ai_context(system_key, chart_obj, page_content)


def render_tab_maya() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_maya"
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
            with st.spinner(t("spinner_maya")):
                m_chart = compute_maya_chart(**_p)
            render_maya_chart(m_chart, after_chart_hook=lambda: _render_ai_button("tab_maya", m_chart, btn_key="maya"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_maya_prompt"))
        st.markdown(t("desc_maya"))


def render_tab_armenian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_armenian"
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
            with st.spinner(t("spinner_armenian")):
                _armenian_chart = _compute_armenian_chart_fn(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    timezone=_p["timezone"],
                    latitude=_p["latitude"],
                    longitude=_p["longitude"],
                    location_name=_p.get("location_name", ""),
                )
            render_armenian_chart_ui(
                _armenian_chart,
                after_chart_hook=lambda: _render_ai_button("tab_armenian", _armenian_chart, btn_key="armenian"),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_armenian_prompt"))
        st.markdown(t("desc_armenian"))


def render_tab_andean() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_andean"
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
            with st.spinner(t("spinner_andean")):
                _andean_chart = _compute_andean_chart_fn(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    timezone=_p["timezone"],
                    latitude=_p["latitude"],
                    longitude=_p["longitude"],
                    location_name=_p.get("location_name", ""),
                )
            render_andean_chart_ui(
                _andean_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_andean", _andean_chart, btn_key="andean"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_andean_prompt"))
        st.markdown(t("desc_andean"))


def render_tab_etruscan() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_etruscan"
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
            with st.spinner(t("spinner_etruscan")):
                _etruscan_chart = _compute_etruscan_chart_fn(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    timezone=_p["timezone"],
                    latitude=_p["latitude"],
                    longitude=_p["longitude"],
                    location_name=_p.get("location_name", ""),
                )
            render_etruscan_chart_ui(
                _etruscan_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_etruscan", _etruscan_chart, btn_key="etruscan"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_etruscan_prompt"))
        st.markdown(t("desc_etruscan"))


def render_tab_aztec() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_aztec"
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
            with st.spinner(t("spinner_aztec")):
                az_chart = compute_aztec_chart(**_p)
            render_aztec_chart(az_chart, after_chart_hook=lambda: _render_ai_button("tab_aztec", az_chart, btn_key="aztec"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_aztec"))


def render_tab_decans() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_decans"
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
            with st.spinner(t("spinner_decans")):
                dc_chart = compute_decan_chart(**_p)
            render_decan_chart(dc_chart)
            _render_ai_button("tab_decans", dc_chart, btn_key="decans")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_decans_prompt"))
        render_decan_browse()


def render_tab_sumerian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_sumerian"
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
            render_sumerian_chart(
                year=_p["year"],
                month=_p["month"],
                day=_p["day"],
                hour=_p["hour"],
                minute=_p.get("minute", 0),
                timezone=_p.get("timezone", 0.0),
                latitude=_p.get("latitude", 32.542),
                longitude=_p.get("longitude", 44.421),
                location_name=_p.get("location_name", ""),
            )
            _sumerian_chart = compute_sumerian_chart(
                year=_p["year"], month=_p["month"], day=_p["day"],
                hour=_p["hour"], minute=_p.get("minute", 0),
                timezone=_p.get("timezone", 0.0),
                lat=_p.get("latitude", 32.542),
                lon=_p.get("longitude", 44.421),
                location_name=_p.get("location_name", ""),
            )
            _render_ai_button("tab_sumerian", _sumerian_chart, btn_key="sumerian")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_sumerian_prompt"))
        st.markdown(t("desc_sumerian"))
