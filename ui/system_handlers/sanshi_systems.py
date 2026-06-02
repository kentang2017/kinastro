"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t

_LEGACY_NAMES = ('compute_medical_chart', 'compute_qimen_luming', 'compute_shanghan_qianfa', 'compute_taiyi_chart', 'render_horary_chart', 'render_medical_astrology_chart', 'render_qimen_luming', 'render_shanghan_qianfa_chart', 'render_sports_astrology_chart', 'render_taiyi_chart')

def _bind_legacy() -> None:
    from core import legacy_bridge as _legacy_bridge

    for _name in _LEGACY_NAMES:
        if hasattr(_legacy_bridge, _name):
            globals()[_name] = getattr(_legacy_bridge, _name)

def _render_ai_button(system_key: str, chart_obj, page_content: str = "", **_kwargs) -> None:
    set_ai_context(system_key, chart_obj, page_content)


def render_tab_taiyi() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_taiyi"
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
            _g = st.session_state["_calc_gender"]
            _taiyi_gender = "male" if _g in ("male", "男", "M") else "female"
            with st.spinner(t("spinner_taiyi")):
                _taiyi_chart = compute_taiyi_chart(**_p, gender=_taiyi_gender)
            render_taiyi_chart(
                _taiyi_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_taiyi", _taiyi_chart, btn_key="taiyi"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_taiyi"))


def render_tab_qimen_luming() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_qimen_luming"
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
            with st.spinner(t("spinner_qimen_luming")):
                _qm_luming = compute_qimen_luming(**_p)
            render_qimen_luming(
                _qm_luming,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_qimen_luming", _qm_luming, btn_key="qimen_luming"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_qimen_luming"))


def render_tab_medical_astrology() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_medical_astrology"
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
            with st.spinner(t("spinner_medical_astrology")):
                _medical_result = compute_medical_chart(**_p)
            render_medical_astrology_chart(_medical_result)
            _render_ai_button("tab_medical_astrology", _medical_result, btn_key="medical_astrology")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_medical_astrology_prompt"))
        st.markdown(t("desc_medical_astrology"))


def render_tab_shanghan_qianfa() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_shanghan_qianfa"
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

    if not _is_calculated:
        st.info(t("info_shanghan_qianfa_prompt"))
        st.markdown(t("desc_shanghan_qianfa"))
        return

    # ── Onset date & method version inputs ────────────────────────────────
    _col_onset, _col_method = st.columns(2)
    with _col_onset:
        _onset_val = st.session_state.get("_shanghan_onset_date") or date.today()
        _onset_date = st.date_input(
            t("shanghan_onset_date_label"),
            value=_onset_val,
            help=t("shanghan_onset_date_help"),
            key="shanghan_onset_date_input",
        )
        st.session_state["_shanghan_onset_date"] = _onset_date
    with _col_method:
        _method_options = [t("shanghan_method_v1"), t("shanghan_method_v2")]
        _method_saved = st.session_state.get("_shanghan_method_version", "v1")
        _method_default_idx = 1 if _method_saved == "v2" else 0
        _method_label = st.selectbox(
            t("shanghan_method_version_label"),
            options=_method_options,
            index=_method_default_idx,
            key="shanghan_method_select",
        )
        _method_version = "v2" if _method_label == t("shanghan_method_v2") else "v1"
        st.session_state["_shanghan_method_version"] = _method_version

    try:
        _p = st.session_state["_calc_params"]
        with st.spinner(t("spinner_shanghan_qianfa")):
            _shanghan_result = compute_shanghan_qianfa(
                **_p,
                onset_year=_onset_date.year,
                onset_month=_onset_date.month,
                onset_day=_onset_date.day,
                method_version=_method_version,
            )
        render_shanghan_qianfa_chart(_shanghan_result)
        _render_ai_button("tab_shanghan_qianfa", _shanghan_result, btn_key="shanghan_qianfa")
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_horary() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_horary"
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
    try:
        _p = st.session_state.get("_calc_params", {})
        try:
            render_horary_chart(
                year=_p.get("year", 2024),
                month=_p.get("month", 1),
                day=_p.get("day", 1),
                hour=_p.get("hour", 12),
                minute=_p.get("minute", 0),
                timezone=_p.get("timezone", 0.0),
                latitude=_p.get("latitude", 25.033),
                longitude=_p.get("longitude", 121.565),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_sports_astrology() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_sports_astrology"
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
    try:
        _p = st.session_state.get("_calc_params", {})
        try:
            render_sports_astrology_chart(
                year=_p.get("year", 2024),
                month=_p.get("month", 1),
                day=_p.get("day", 1),
                hour=_p.get("hour", 12),
                minute=_p.get("minute", 0),
                timezone=_p.get("timezone", 0.0),
                latitude=_p.get("latitude", 25.033),
                longitude=_p.get("longitude", 121.565),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)
