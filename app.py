"""
堅占星 (KinAstro) — Multi-System Astrology Application
Multi-System Astrology Chart Application

支援七政四餘（中國）、紫微斗數、策天飛星、十二星次、達摩一掌經、太玄數占星、五運六氣、
萬化仙禽、鐵板神數、邵子神數、鬼谷分定經、大六壬、奇門祿命、太乙命法、
西洋占星、Sabian 符號、希臘（Hellenistic）、Astrocartography、天王星漢堡學派、凱爾特樹木曆、
印度占星（Vedic）、Jaimini、納迪（Nadi）、KP 克里希納穆提、紅皮書（Lal Kitab）、
宿曜道、泰國占星、緬甸（Mahabote）、巴厘 Wariga、爪哇 Weton、蒙古祖爾海（Zurkhai）、
藏傳時輪金剛、九星氣學、土亭數、高棉占星、波利尼西亞／夏威夷、
卡巴拉、猶太 Mazzalot、薩珊波斯、阿拉伯占星、也門占星、Picatrix 占星魔法、
瑪雅、阿茲特克、古埃及十度區間（Decans）、巴比倫占星

共八十八種體系，使用 pyswisseph 進行天文計算。
"""
# pylint: disable=wrong-import-position,invalid-name,import-outside-toplevel
# pylint: disable=broad-exception-caught,too-many-locals,ungrouped-imports
# pylint: disable=redefined-outer-name

from __future__ import annotations

import contextlib
from datetime import date, time
from typing import Any

import streamlit as st

# ── Page config must be the first Streamlit call ──────────────────────────
st.set_page_config(
    page_title="堅占星 KinAstro | 八十八體系占星",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Core UI modules ───────────────────────────────────────────────────────
from ui.state import SessionKeys, init_session_state_defaults
from ui.helpers import t
from ui.styles import inject_custom_css, inject_star_particles
from ui.homepage import render_homepage
from ui.sidebar import render_sidebar
from ui.components.birth_form import BirthChartParams, build_birth_params
from ui.system_engine import EXECUTION_REGISTRY

# ── Compute helpers ───────────────────────────────────────────────────────
from core.cached_computations import invalidate_chart_cache_if_birth_changed

# ── Page init ─────────────────────────────────────────────────────────────
inject_custom_css()
init_session_state_defaults(st)
inject_star_particles()

# ── Language initialization ───────────────────────────────────────────────
_LANG_MAP = {
    "繁體中文": "zh",
    "简体中文": "zh_cn",
    "English": "en",
    "한국어": "ko",
    "日本語": "ja",
    "Tiếng Việt": "vi",
    "ภาษาไทย": "th",
}
_LANG_LABEL_MAP = {v: k for k, v in _LANG_MAP.items()}
_DEFAULT_LANG_LABEL = "繁體中文"
_OVERVIEW_PARAM_KEYS = (
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "timezone",
    "latitude",
    "longitude",
    "location_name",
)


def _sync_lang_from_selectbox() -> None:
    _sel = st.session_state.get("_lang_select", _DEFAULT_LANG_LABEL)
    st.session_state["lang"] = _LANG_MAP.get(_sel, "zh")


# Bridge the Streamlit session state to astro.i18n so that compute
# modules which call t() without depending on streamlit still resolve
# the active language. astro.i18n was decoupled from streamlit in the
# astro/-streamlit decoupling pass; this hook keeps the in-app
# language switch functioning.
from astro.i18n import set_ui_lang as _set_ui_lang


def _sync_astro_lang() -> None:
    _set_ui_lang(st.session_state.get("lang", "zh"))


if "_lang_select" in st.session_state:
    _sync_lang_from_selectbox()
else:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "zh"
    st.session_state["_lang_select"] = _LANG_LABEL_MAP.get(
        st.session_state.get("lang", "zh"),
        _DEFAULT_LANG_LABEL,
    )

_sync_astro_lang()


# ── Query params restore (share link) ────────────────────────────────────
def _load_from_query_params() -> bool:
    """Attempt to restore chart state from ``st.query_params``.

    Expected params: ``sys``, ``y``, ``mo``, ``d``, ``h``, ``mi``,
    ``tz``, ``lat``, ``lon``.

    Returns *True* if params were loaded, *False* otherwise.
    """
    qp = st.query_params
    if "sys" not in qp:
        return False
    try:
        sys_key = qp.get("sys", "")
        y   = int(qp.get("y",   1990))
        mo  = int(qp.get("mo",  1))
        d   = int(qp.get("d",   1))
        h   = int(qp.get("h",   12))
        mi  = int(qp.get("mi",  0))
        tz  = float(qp.get("tz",  8.0))
        lat = float(qp.get("lat", 22.3193))
        lon = float(qp.get("lon", 114.1694))
    except (ValueError, TypeError):
        return False

    # Only restore once per session to avoid overwriting user edits
    if st.session_state.get("_qp_loaded"):
        return True

    st.session_state["_system_select"] = sys_key
    st.session_state["birth_date_input"] = date(
        max(1, min(y, date.today().year)), max(1, min(mo, 12)), max(1, min(d, 31))
    )
    st.session_state["birth_time_input"] = time(
        max(0, min(h, 23)), max(0, min(mi, 59))
    )
    st.session_state["_custom_lat"] = lat
    st.session_state["_custom_lon"] = lon
    st.session_state["_custom_tz"]  = tz
    st.session_state["_birth_confirmed"] = True
    st.session_state["_confirmed_params"] = {
        "year": y,
        "month": mo,
        "day": d,
        "hour": h,
        "minute": mi,
        "timezone": tz,
        "latitude": lat,
        "longitude": lon,
        "location_name": "",
    }
    st.session_state["_confirmed_gender"] = "male"
    st.session_state["_qp_loaded"] = True
    return True


_qp_restored = _load_from_query_params()


def _build_share_url(system_key: str, params: dict[str, Any]) -> str:
    """Build a query-string share URL from chart params."""
    return (
        f"?sys={system_key}"
        f"&y={params.get('year', 1990)}"
        f"&mo={params.get('month', 1)}"
        f"&d={params.get('day', 1)}"
        f"&h={params.get('hour', 12)}"
        f"&mi={params.get('minute', 0)}"
        f"&tz={params.get('timezone', 8.0)}"
        f"&lat={params.get('latitude', 22.3193)}"
        f"&lon={params.get('longitude', 114.1694)}"
    )


# ── Render sidebar ────────────────────────────────────────────────────────
render_sidebar()

# ── Language switcher (top-right corner) ─────────────────────────────────
_lang_spacer, _lang_col = st.columns([4, 1])
with _lang_col:
    st.markdown(
        '<div class="ka-lang-switcher">🌐 ' + t("lang_switcher_label") + "</div>",
        unsafe_allow_html=True,
    )
    st.selectbox(
        t("lang_switcher_label"),
        options=[
            "繁體中文",
            "简体中文",
            "English",
            "한국어",
            "日本語",
            "Tiếng Việt",
            "ภาษาไทย",
        ],
        key="_lang_select",
        on_change=_sync_lang_from_selectbox,
        label_visibility="collapsed",
    )

# ── Homepage check — stop here when no system is selected ────────────────
if "_system_select" not in st.session_state:
    render_homepage()
    st.stop()

# ── App title (only on chart pages) ──────────────────────────────────────
st.title(t("app_title"))
st.markdown(
    '<p class="app-subtitle">' + t("app_subtitle") + "</p>",
    unsafe_allow_html=True,
)

# ── Resolve birth parameters ──────────────────────────────────────────────
_confirmed = st.session_state.get("_confirmed_params")
_confirmed_gender = st.session_state.get(SessionKeys.CONFIRMED_GENDER, "male")

if _confirmed:
    _birth_params = BirthChartParams.from_dict(_confirmed, gender=_confirmed_gender)
else:
    _birth_params = build_birth_params(
        birth_date=st.session_state.get("birth_date_input", date(1990, 1, 1)),
        birth_time=st.session_state.get("birth_time_input", time(12, 0)),
        timezone=st.session_state.get("_tz_input", 8.0),
        latitude=st.session_state.get("_lat_input", 22.3193),
        longitude=st.session_state.get("_lon_input", 114.1694),
        location_name="",
        gender=_confirmed_gender,
    )

_params = _birth_params.to_dict()
gender = _birth_params.gender

# Persist to session_state so handler modules can read birth params lazily
st.session_state[SessionKeys.CALC_PARAMS] = _params
st.session_state[SessionKeys.CALC_GENDER] = gender
st.session_state[SessionKeys.CALCULATED] = True
invalidate_chart_cache_if_birth_changed(_params)

_is_calculated = True
_selected_system = st.session_state.get(SessionKeys.SYSTEM_SELECT)
if _selected_system:
    from ui.system_handlers.dispatch import render_system_title as _render_system_title

    _render_system_title(_selected_system)

# ── Status flash after chart submission ───────────────────────────────────
if st.session_state.get("_calc_success_flash"):
    st.markdown(
        f'<div class="ka-status-success">✅ {t("status_chart_ready")}</div>',
        unsafe_allow_html=True,
    )
    st.session_state["_calc_success_flash"] = False

# ── Share-link restore notice (once) ─────────────────────────────────────
if _qp_restored and not st.session_state.get("_qp_notice_shown"):
    st.success(t("share_chart_loaded"))
    st.session_state["_qp_notice_shown"] = True

# ── Overview dashboard build helper ────────────────────────────────────────
def build_overview_items(
    params: dict[str, Any],
    birth_gender: str,
    t_fn,
) -> list[dict[str, Any]]:
    """Build overview cards for popular systems in priority order."""
    from astro.system_registry import get_system

    items: list[dict[str, Any]] = []
    overview_metrics = _build_overview_metrics(
        _freeze_overview_params(params),
        birth_gender,
    )
    for item in overview_metrics:
        system_id = item["system_id"]
        system_meta = get_system(system_id)
        if system_meta is None:
            continue
        items.append(
            {
                **item,
                "icon": system_meta.icon,
                "title": t_fn(system_meta.tab_key),
                "accent": system_meta.accent_color,
            }
        )
    return items


def _freeze_overview_params(params: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    """Return a stable, cacheable key for overview chart computations."""
    return tuple((key, params.get(key)) for key in _OVERVIEW_PARAM_KEYS)


@st.cache_data(show_spinner=False)
def _build_overview_metrics(
    frozen_params: tuple[tuple[str, Any], ...],
    birth_gender: str,
) -> list[dict[str, str]]:
    """Compute cached overview metrics for the homepage dashboard.

    Lazy imports keep initial app startup fast; caching prevents repeated
    recalculation of the same overview charts on every rerun.
    """
    # pylint: disable=import-outside-toplevel,broad-exception-caught
    params = dict(frozen_params)
    items: list[dict[str, str]] = []

    from astro.qizheng.calculator import compute_chart
    from astro.vedic.indian import compute_vedic_chart
    from astro.western.western import compute_western_chart
    from astro.ziwei import compute_ziwei_chart

    try:
        west = compute_western_chart(**params)
        sun = next(
            (
                planet
                for planet in getattr(west, "planets", [])
                if "Sun" in getattr(planet, "name", "")
            ),
            None,
        )
        sun_sign = getattr(sun, "sign_chinese", "") or getattr(sun, "sign", "") or "-"
        items.append(
            {
                "system_id": "tab_western",
                "metric_main": f"☉ {sun_sign}",
                "metric_sub": (
                    f"P:{len(getattr(west, 'planets', []))} · "
                    f"A:{len(getattr(west, 'aspects', []))}"
                ),
            }
        )
    except Exception:
        pass

    try:
        ziwei = compute_ziwei_chart(**params, gender=birth_gender)
        items.append(
            {
                "system_id": "tab_ziwei",
                "metric_main": f"{getattr(ziwei, 'ming_zhu', '-')}",
                "metric_sub": (
                    f"宮:{len(getattr(ziwei, 'palaces', []))} · "
                    f"局:{getattr(ziwei, 'wu_xing_ju', '-')}"
                ),
            }
        )
    except Exception:
        pass

    try:
        chinese = compute_chart(**params, gender=birth_gender)
        items.append(
            {
                "system_id": "tab_chinese",
                "metric_main": f"{getattr(chinese, 'solar_month', '-')}",
                "metric_sub": (
                    f"P:{len(getattr(chinese, 'planets', []))} · "
                    f"H:{len(getattr(chinese, 'houses', []))}"
                ),
            }
        )
    except Exception:
        pass

    try:
        vedic = compute_vedic_chart(**params)
        moon = next(
            (
                planet
                for planet in getattr(vedic, "planets", [])
                if "Chandra" in getattr(planet, "name", "")
            ),
            None,
        )
        nakshatra = getattr(moon, "nakshatra", "-")
        items.append(
            {
                "system_id": "tab_indian",
                "metric_main": f"☾ {nakshatra}",
                "metric_sub": (
                    f"P:{len(getattr(vedic, 'planets', []))} · "
                    f"H:{len(getattr(vedic, 'houses', []))}"
                ),
            }
        )
    except Exception:
        pass

    return items


# ── Overview dashboard (when no system selected yet) ─────────────────────
if not _selected_system:
    from ui.components.overview_dashboard import render_overview_dashboard

    with st.spinner(t("overview_dashboard_loading")):
        _overview_items = build_overview_items(_params, gender, t)
    render_overview_dashboard(
        st_module=st,
        t=t,
        items=_overview_items,
        current_system=_selected_system,
    )

# ── nullcontext shim keeps existing `with _natal_tab:` patterns intact ───
_natal_tab = contextlib.nullcontext()

# ── Share-chart button ────────────────────────────────────────────────────
with _natal_tab:
    _share_col1, _share_col2 = st.columns([4, 1])
    with _share_col2:
        _share_qs = _build_share_url(_selected_system or "", _params)
        _copy_js = f"""
<button onclick="navigator.clipboard.writeText(window.location.origin
  + window.location.pathname + '{_share_qs}')
  .then(()=>this.textContent='✅ Copied!')
  .catch(()=>this.textContent='⚠️ Failed');"
  style="background:rgba(167,139,250,0.18);border:1px solid rgba(167,139,250,0.35);
         color:#e0e0ff;border-radius:8px;padding:6px 14px;cursor:pointer;
         font-size:0.82rem;white-space:nowrap;">
  {t('share_chart_btn')}
</button>"""
        st.html(_copy_js)


# ── Register Phase 1 engine handlers (once per session) ──────────────────
def _init_execution_registry_once() -> None:
    if EXECUTION_REGISTRY.has_handler("tab_ziwei"):
        return
    from astro.vietnam import (
        compute_vietnam_tu_vi_chart,
        render_streamlit as render_vietnam_tu_vi_chart,
    )
    from astro.ziwei import compute_ziwei_chart, render_ziwei_chart
    from ui.ai_chat import set_ai_context
    from ui.system_handlers.phase1_handlers import build_ziwei_handler

    EXECUTION_REGISTRY.register(
        build_ziwei_handler(
            compute_ziwei_chart=compute_ziwei_chart,
            render_ziwei_chart=render_ziwei_chart,
            compute_vietnam_tu_vi_chart=compute_vietnam_tu_vi_chart,
            render_vietnam_tu_vi_chart=render_vietnam_tu_vi_chart,
            ai_button_sink=set_ai_context,
        )
    )


with _natal_tab:
    _init_execution_registry_once()
    _engine_options: dict[str, Any] = {}

    # Ziwei-specific Vietnam mode toggle
    if _selected_system == "tab_ziwei":
        _ziwei_col1, _ziwei_col2 = st.columns([3, 1])
        with _ziwei_col2:
            _vietnam_mode = st.toggle(
                "🇻🇳 越南 Tử Vi 模式",
                value=st.session_state.get("_ziwei_vietnam_mode", False),
                help="啟用越南 Tử Vi Đẩu Số 模式：以貓代兔、融入越南佛教與農耕文化詮釋",
                key="_ziwei_vietnam_toggle",
            )
            st.session_state["_ziwei_vietnam_mode"] = _vietnam_mode
            _engine_options["vietnam_mode"] = _vietnam_mode
            _vietnam_full_mode = st.toggle(
                "Trung Châu Tam Hợp 完整版",
                value=st.session_state.get("_ziwei_vietnam_full_mode", False),
                disabled=not _vietnam_mode,
                help="啟用獨立越南模組（解讀/對照/remedies/12宮圖）",
                key="_ziwei_vietnam_full_toggle",
            )
            st.session_state["_ziwei_vietnam_full_mode"] = _vietnam_full_mode
            _engine_options["vietnam_full_mode"] = bool(_vietnam_mode and _vietnam_full_mode)
            _engine_options["calendar_mode"] = "solar_gregorian"
            _engine_options["interpret_mode"] = "trung_chau_tam_hop"
            _engine_options["lang"] = st.session_state.get("lang", "zh")
        with _ziwei_col1:
            if _vietnam_mode:
                st.markdown(
                    '<span style="background:#DA251D;color:#FFCD00;'
                    'font-weight:bold;padding:4px 10px;border-radius:6px;font-size:13px">'
                    + (
                        '🇻🇳 越南 Tử Vi Đẩu Số 完整版已啟用</span>'
                        if _engine_options.get("vietnam_full_mode")
                        else '🇻🇳 越南 Tử Vi Đẩu Số 模式已啟用</span>'
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span style="background:#1a1a2e;color:#c8a96e;'
                    'font-weight:bold;padding:4px 10px;border-radius:6px;font-size:13px">'
                    '🌟 中國紫微斗數模式</span>',
                    unsafe_allow_html=True,
                )

    from astro.system_registry import get_system

    _meta = get_system(_selected_system or "")
    _spinner_key = _meta.spinner_key if _meta else "info_calc_prompt"

    def _engine_error_handler(err: Exception) -> None:
        st.error(f"{t('error_tab_compute')}：{err}")
        st.exception(err)

    _engine_handled = _is_calculated and EXECUTION_REGISTRY.run_system(
        system_id=_selected_system or "",
        params=_birth_params,
        options=_engine_options,
        spinner_text=t(_spinner_key),
        st_module=st,
        on_error=_engine_error_handler,
    )

# ── Fallback: dispatch to modular system handler files ────────────────────
if not _engine_handled:
    try:
        from ui.system_handlers.dispatch import render_system as _dispatch_render_system

        _handled = _dispatch_render_system(_selected_system or "")
    except Exception as _dispatch_err:
        _sys_label = _selected_system or "unknown"
        _is_zh = st.session_state.get("lang", "zh") in ("zh", "zh_cn")
        _err_prefix = (
            f"體系 **{_sys_label}** 起盤時發生錯誤："
            if _is_zh
            else f"System **{_sys_label}** raised an error: "
        )
        st.error(f"{_err_prefix}`{type(_dispatch_err).__name__}: {_dispatch_err}`")
        st.exception(_dispatch_err)
        _handled = True
    if not _handled and _selected_system:
        unknown_label = (
            "未知體系"
            if st.session_state.get("lang", "zh") in ("zh", "zh_cn")
            else "Unknown system"
        )
        st.warning(
            f"{unknown_label}: `{_selected_system}`"
        )

# ── Global AI chatbox — fixed at the bottom of every page ─────────────────
from ui.ai_chat import render_global_ai_chat

render_global_ai_chat()
