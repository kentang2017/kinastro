"""KinAstro modular Streamlit entrypoint.

Lightweight app shell that keeps input/selection orchestration in one place,
then delegates compute/render to registry-managed system modules.
"""

from __future__ import annotations

import importlib
from datetime import date, time
from typing import Any

import streamlit as st

from astro.i18n import TRANSLATIONS
from core.system_registry import get_or_compute, render_system, supports_modern_runtime
from ui.components.birth_form import build_birth_params
from ui.components.system_selector import render_system_selector
from ui.state import SessionKeys, init_session_state_defaults


SUPPORTED_MODERN_SYSTEMS = {
    "tab_western",
    "tab_ziwei",
    "tab_indian",
}


def t(key: str) -> str:
    lang = st.session_state.get(SessionKeys.LANG, "zh")
    table = TRANSLATIONS.get(key)
    if isinstance(table, dict):
        return table.get(lang, table.get("zh", key))
    return key


def _init_runtime_state() -> None:
    init_session_state_defaults(st)
    st.session_state.setdefault("charts", {})
    st.session_state.setdefault("perf_metrics", {"hits": 0, "misses": 0, "last_compute_seconds": 0.0})
    st.session_state.setdefault("global_ai_chat", [])


def _language_switcher() -> None:
    st.sidebar.selectbox(
        "Language",
        options=["zh", "en"],
        key=SessionKeys.LANG,
        format_func=lambda x: "繁體中文" if x == "zh" else "English",
    )


def _birth_form() -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader(t("sidebar_header"))

    default_date = date(
        int(st.session_state.get("_birth_year", 1990)),
        int(st.session_state.get("_birth_month", 1)),
        int(st.session_state.get("_birth_day", 1)),
    )
    default_time = time(
        int(st.session_state.get("_birth_hour", 12)),
        int(st.session_state.get("_birth_minute", 0)),
    )

    with st.sidebar.form("birth_form", clear_on_submit=False):
        birth_date = st.date_input(t("birth_date"), value=default_date)
        birth_time = st.time_input(t("birth_time"), value=default_time, step=60)
        timezone = st.number_input(t("timezone"), min_value=-12.0, max_value=14.0, value=float(st.session_state.get("_timezone", 8.0)), step=0.5)
        latitude = st.number_input(t("latitude"), min_value=-90.0, max_value=90.0, value=float(st.session_state.get("_latitude", 22.3193)), format="%.6f")
        longitude = st.number_input(t("longitude"), min_value=-180.0, max_value=180.0, value=float(st.session_state.get("_longitude", 114.1694)), format="%.6f")
        location_name = st.text_input(t("custom_location"), value=str(st.session_state.get("_location_name", "Hong Kong")))
        gender = st.selectbox("Gender", ["male", "female"], index=0 if st.session_state.get("_gender", "male") == "male" else 1)

        submitted = st.form_submit_button(t("generate_chart_btn"), width="stretch", type="primary")

    if not submitted:
        return

    params = build_birth_params(
        birth_date=birth_date,
        birth_time=birth_time,
        timezone=float(timezone),
        latitude=float(latitude),
        longitude=float(longitude),
        location_name=location_name.strip(),
        gender=gender,
    )

    st.session_state[SessionKeys.CONFIRMED_PARAMS] = params.to_dict()
    st.session_state[SessionKeys.CONFIRMED_GENDER] = gender
    st.session_state[SessionKeys.CALC_PARAMS] = params.to_dict()
    st.session_state[SessionKeys.CALC_GENDER] = gender
    st.session_state[SessionKeys.CALCULATED] = True


def _system_picker() -> str | None:
    st.sidebar.markdown("---")
    query = st.sidebar.text_input("🔎 Search", value="", key="_sys_query")
    current = st.session_state.get(SessionKeys.SYSTEM_SELECT)
    selected = render_system_selector(
        st_module=st,
        t=t,
        search_query=query,
        current_system=current,
    )
    st.session_state[SessionKeys.SYSTEM_SELECT] = selected
    return selected


def _build_current_params() -> Any | None:
    payload = st.session_state.get(SessionKeys.CALC_PARAMS)
    if not payload:
        return None
    gender = str(st.session_state.get(SessionKeys.CALC_GENDER, "male"))
    return build_birth_params(
        birth_date=date(int(payload["year"]), int(payload["month"]), int(payload["day"])),
        birth_time=time(int(payload["hour"]), int(payload["minute"])),
        timezone=float(payload["timezone"]),
        latitude=float(payload["latitude"]),
        longitude=float(payload["longitude"]),
        location_name=str(payload.get("location_name", "")),
        gender=gender,
    )


def _render_perf_panel() -> None:
    metrics = st.session_state.get("perf_metrics", {})
    hits = int(metrics.get("hits", 0))
    misses = int(metrics.get("misses", 0))
    total = hits + misses
    hit_rate = (hits / total * 100.0) if total else 0.0
    compute_time = float(metrics.get("last_compute_seconds", 0.0))

    with st.expander("⚡ Performance", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Last Compute (s)", f"{compute_time:.3f}")
        c2.metric("Cache Hit Rate", f"{hit_rate:.1f}%")
        c3.metric("Cache Hits", str(hits))


def _render_global_chatbox() -> None:
    st.markdown("---")
    st.subheader("💬 Global AI Chatbox")

    for msg in st.session_state.get("global_ai_chat", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about your chart...")
    if not prompt:
        return

    st.session_state["global_ai_chat"].append({"role": "user", "content": prompt})
    response = "AI 分析模組可接入既有 provider；目前顯示為重構後佔位回覆。"
    st.session_state["global_ai_chat"].append({"role": "assistant", "content": response})
    st.rerun()


def _run_legacy_app() -> None:
    st.warning("This system is still served by legacy runtime. Loading full compatibility mode...")
    importlib.import_module("legacy_app")
    st.stop()


def main() -> None:
    st.set_page_config(page_title="KinAstro", page_icon="⭐", layout="wide")
    _init_runtime_state()

    st.title(t("app_title"))
    st.caption("Modular runtime with lazy system imports and session-aware caching")

    _language_switcher()
    _birth_form()
    selected_system = _system_picker()

    if not selected_system:
        st.info("請從左側選擇占星體系。")
        _render_global_chatbox()
        return

    if selected_system not in SUPPORTED_MODERN_SYSTEMS or not supports_modern_runtime(selected_system):
        _run_legacy_app()
        return

    if not st.session_state.get(SessionKeys.CALCULATED):
        st.info("請先提交出生資料以開始排盤。")
        _render_global_chatbox()
        return

    params = _build_current_params()
    if params is None:
        st.error("出生資料缺失，請重新提交。")
        _render_global_chatbox()
        return

    options: dict[str, Any] = {}
    if selected_system == "tab_ziwei":
        options["vietnam_mode"] = st.toggle("Vietnam mode", value=False, key="_ziwei_vietnam_mode")

    with st.spinner("Computing..."):
        compute_result = get_or_compute(selected_system, params, options)

    if compute_result["from_cache"]:
        st.success("Loaded from cache")

    render_system(
        selected_system,
        compute_result["result"],
        params,
        options,
        ai_hook=None,
    )

    _render_perf_panel()
    _render_global_chatbox()


main()
