"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t
from core.cached_computations import (
    build_mazzalot_svg_cached,
    get_or_compute_chart,
    _birth_sig,
)

_LEGACY_NAMES = ('_compute_geomancy_chart', '_mode', '_render_geomancy_input', '_render_geomancy_ui', '_render_reference_library', 'analyze_bahre_hasab_date', 'build_yemeni_manzil_mandala_svg', 'compute_albiruni_lots', 'compute_amazigh_chart', 'compute_arabic_chart', 'compute_dogon_sirius_chart', 'compute_kabbalistic_chart', 'compute_moon_longitude', 'compute_yemeni_chart', 'get_lang', 'render_amazigh_chart', 'render_amazigh_sky_svg', 'render_arabic_chart', 'render_arabic_lots_dashboard', 'render_bahre_hasab_tab', 'render_deep_sassanian_chart', 'render_dogon_sirius_chart', 'render_european_geomancy', 'render_kabbalistic_chart', 'render_mansion_lookup', 'render_mazzalot_chart', 'render_ms164_browse', 'render_picatrix_behenian', 'render_picatrix_browse', 'render_picatrix_invocations', 'render_planetary_hours_tool', 'render_shams_browse', 'render_shams_chart', 'render_talisman_generator', 'render_yemeni_chart')

def _bind_legacy() -> None:
    from core import legacy_bridge as _legacy_bridge

    for _name in _LEGACY_NAMES:
        if hasattr(_legacy_bridge, _name):
            globals()[_name] = getattr(_legacy_bridge, _name)

def _render_ai_button(system_key: str, chart_obj, page_content: str = "", **_kwargs) -> None:
    set_ai_context(system_key, chart_obj, page_content)

def _render_interactive_html(*, html: str, height: int, key: str) -> None:
    """Render embedded HTML/SVG with lightweight hover + click zoom tooltip UX."""
    component = f"""
    <div id="{key}" class="ka-interactive-frame">
      {html}
      <div class="ka-svg-tip" id="{key}-tip"></div>
    </div>
    <script>
    (function(){{
      const root = document.getElementById("{key}");
      if (!root) return;
      const tip = document.getElementById("{key}-tip");
      const svg = root.querySelector("svg");
      if (!svg) return;
      root.classList.add("ka-interactive-ready");
      let zoomed = false;
      svg.style.cursor = "zoom-in";
      svg.addEventListener("click", function(){{
        zoomed = !zoomed;
        svg.style.transition = "transform .25s ease";
        svg.style.transformOrigin = "50% 50%";
        svg.style.transform = zoomed ? "scale(1.22)" : "scale(1)";
      }});
      svg.addEventListener("mousemove", function(e){{
        const el = e.target;
        const txt = (el.getAttribute("aria-label") || el.getAttribute("title") || el.textContent || "").trim();
        if (!txt || txt.length < 2) {{
          tip.style.opacity = "0";
          return;
        }}
        tip.textContent = txt.slice(0, 52);
        tip.style.left = (e.clientX + 12) + "px";
        tip.style.top = (e.clientY + 12) + "px";
        tip.style.opacity = "1";
      }});
      svg.addEventListener("mouseleave", function(){{ tip.style.opacity = "0"; }});
    }})();
    </script>
    """
    st.components.v1.html(component, height=height, scrolling=False)


def render_tab_kabbalistic() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_kabbalistic"
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
            with st.spinner(t("spinner_kabbalistic")):
                k_chart = compute_kabbalistic_chart(**_p)
            render_kabbalistic_chart(k_chart, after_chart_hook=lambda: _render_ai_button("tab_kabbalistic", k_chart, btn_key="kabbalistic"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_kabbalistic"))


def render_tab_mazzalot() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_mazzalot"
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
            with st.spinner(t("spinner_mazzalot")):
                _mz_chart = get_or_compute_chart(
                    "tab_mazzalot",
                    _p,
                    {"location_name": _p.get("location_name", "")},
                )
            _mz_tab_star, _mz_tab_natal, _mz_tab_omens = st.tabs([
                t("mazzalot_subtab_star"),
                t("mazzalot_subtab_natal"),
                t("mazzalot_subtab_omens"),
            ])
            with _mz_tab_star:
                _mz_svg = build_mazzalot_svg_cached(_birth_sig(_p), location_name)
                st.markdown(_mz_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center; color:#888; font-size:11px;">'
                    'Star of David Wheel (Magen David) — Sidereal zodiac · '
                    '12 Mazzalot · Sefer Yetzirah letters · Twelve Tribes'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_mazzalot", _mz_chart, btn_key="mazzalot")
            with _mz_tab_natal:
                render_mazzalot_chart(_mz_chart)
            with _mz_tab_omens:
                st.subheader("📜 " + t("mazzalot_omens_title"))
                for _omen in _mz_chart.omens:
                    _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                    _en_part = f"  \n_{_omen.text_en}_" if _omen.text_en else ""
                    st.markdown(
                        f"{_omen_icon} **{_omen.planet}** — "
                        f"*{_omen.condition.upper()}*: {_omen.text}{_en_part}"
                    )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_mazzalot"))


def render_tab_arabic() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_arabic"
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
            arabic_subtab_chart, arabic_subtab_lots, arabic_subtab_picatrix, arabic_subtab_invocation, arabic_subtab_shams, arabic_subtab_ref, arabic_subtab_ms164 = st.tabs([
                t("arabic_subtab_chart"),
                t("arabic_subtab_lots"),
                t("arabic_subtab_picatrix"),
                t("arabic_subtab_invocation"),
                t("arabic_subtab_shams"),
                t("arabic_subtab_reference"),
                t("arabic_subtab_ms164"),
            ])

            with arabic_subtab_chart:
                with st.spinner(t("spinner_arabic")):
                    a_chart = compute_arabic_chart(**_p)
                render_arabic_chart(a_chart, after_chart_hook=lambda: _render_ai_button("tab_arabic", a_chart, btn_key="arabic"))

            with arabic_subtab_lots:
                _lots_mode_options = {
                    "tropical": t("arabic_lots_tropical"),
                    "sidereal": t("arabic_lots_sidereal"),
                }
                _lots_mode = st.selectbox(
                    t("arabic_lots_zodiac_mode"),
                    options=list(_lots_mode_options.keys()),
                    format_func=lambda _mode: _lots_mode_options[_mode],
                    index=0,
                    key="arabic_lots_mode",
                )
                with st.spinner(t("spinner_arabic_lots")):
                    _lots_result = compute_albiruni_lots(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        timezone=_p["timezone"],
                        latitude=_p["latitude"],
                        longitude=_p["longitude"],
                        zodiac_mode=_lots_mode,
                    )
                render_arabic_lots_dashboard(_lots_result, t)

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
                    render_picatrix_browse(chart_key_prefix="arabic_picatrix_tab")

                with ptab_mansions:
                    st.info(t("picatrix_moon_lon_info").format(lon=_birth_moon_lon))
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

            with arabic_subtab_invocation:
                render_picatrix_invocations()

            # --- 太陽知識大全 (Shams al-Maʻārif) ---
            with arabic_subtab_shams:
                st.subheader(t("shams_subheader"))
                st.caption(t("shams_source"))

                # Compute Arabic chart if not already done
                try:
                    _a_chart_for_shams = a_chart
                except NameError:
                    with st.spinner(t("spinner_arabic")):
                        _a_chart_for_shams = compute_arabic_chart(**_p)
                _shams_planets = {
                    p.name.split("(")[0].strip().split()[-1]: p.longitude
                    for p in _a_chart_for_shams.planets
                }
                _shams_sun_idx: int | None = None
                for p in _a_chart_for_shams.planets:
                    if "Sun" in p.name:
                        _shams_sun_idx = int(p.longitude / 30.0)
                        break
                render_shams_chart(chart_planets=_shams_planets,
                                   birth_sign_idx=_shams_sun_idx)

            with arabic_subtab_ref:
                st.subheader(t("arabic_subtab_reference"))
                _render_reference_library()

            with arabic_subtab_ms164:
                render_ms164_browse()

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        arabic_subtab_chart, arabic_subtab_lots, arabic_subtab_picatrix, arabic_subtab_invocation, arabic_subtab_shams, arabic_subtab_ref, arabic_subtab_ms164 = st.tabs([
            t("arabic_subtab_chart"),
            t("arabic_subtab_lots"),
            t("arabic_subtab_picatrix"),
            t("arabic_subtab_invocation"),
            t("arabic_subtab_shams"),
            t("arabic_subtab_reference"),
            t("arabic_subtab_ms164"),
        ])

        with arabic_subtab_chart:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_arabic"))

        with arabic_subtab_lots:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_arabic_lots"))

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
                render_picatrix_browse(chart_key_prefix="arabic_picatrix_tab")

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

        with arabic_subtab_invocation:
            render_picatrix_invocations()

        with arabic_subtab_shams:
            st.subheader(t("shams_subheader"))
            st.caption(t("shams_source"))
            st.markdown(t("desc_shams"))
            render_shams_browse()

        with arabic_subtab_ref:
            st.subheader(t("arabic_subtab_reference"))
            _render_reference_library()

        with arabic_subtab_ms164:
            render_ms164_browse()


def render_tab_yemeni() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_yemeni"
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
            with st.spinner(t("spinner_yemeni")):
                _yemeni_chart = compute_yemeni_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    timezone=_p["timezone"],
                    latitude=_p["latitude"], longitude=_p["longitude"],
                    location_name=location_name,
                )
            _y_tab_mandala, _y_tab_natal, _y_tab_omens = st.tabs([
                t("yemeni_subtab_mandala"),
                t("yemeni_subtab_natal"),
                t("yemeni_subtab_omens"),
            ])
            with _y_tab_mandala:
                _yemeni_svg = build_yemeni_manzil_mandala_svg(
                    _yemeni_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_yemeni_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center; color:#888; font-size:11px;">'
                    'Yemeni Manzil Mandala — 28-mansion disc · '
                    'Rasulid manuscript style · Sidereal zodiac'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_yemeni", _yemeni_chart, btn_key="yemeni")
            with _y_tab_natal:
                render_yemeni_chart(_yemeni_chart)
            with _y_tab_omens:
                st.subheader("📜 al-Ashraf " + t("yemeni_subtab_omens"))
                for _omen in _yemeni_chart.omens:
                    _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                    st.markdown(
                        f"{_omen_icon} **{_omen.planet}** ({_omen.planet_cn}) — "
                        f"*{_omen.condition.upper()}*: {_omen.text} / {_omen.text_en}"
                    )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_yemeni"))


def render_tab_picatrix_behenian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_picatrix_behenian"
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
    _p = st.session_state.get("_calc_params", {})
    if _is_calculated and _p:
        try:
            from astro.western.western import compute_western_chart as _cwc
            with st.spinner(t("spinner_picatrix_behenian")):
                _pb_chart = _cwc(**_p)
            render_picatrix_behenian(
                chart=_pb_chart,
                year=_p["year"], month=_p["month"], day=_p["day"],
                hour=_p["hour"], minute=_p["minute"],
                timezone_offset=_p["timezone"],
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_picatrix_behenian"))
        # Show compendium even without a chart
        try:
            from astro.picatrix_behenian.renderer import _render_compendium_tab
            _render_compendium_tab()
        except Exception:
            pass


def render_tab_bahre_hasab() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_bahre_hasab"
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
            _probe = analyze_bahre_hasab_date(date(_p["year"], _p["month"], _p["day"]))
            with st.spinner(t("spinner_bahre_hasab")):
                render_bahre_hasab_tab(
                    calc_params=_p,
                    after_chart_hook=lambda: _render_ai_button("tab_bahre_hasab", _probe, btn_key="bahre_hasab"),
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_bahre_hasab_prompt"))
        st.markdown(t("desc_bahre_hasab"))


def render_tab_dogon_sirius() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_dogon_sirius"
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
            with st.spinner(t("spinner_dogon_sirius")):
                _dogon_chart = compute_dogon_sirius_chart(**_p)
            render_dogon_sirius_chart(
                _dogon_chart,
                after_chart_hook=lambda: _render_ai_button("tab_dogon_sirius", _dogon_chart, btn_key="dogon_sirius"),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_dogon_sirius_prompt"))
        st.markdown(t("desc_dogon_sirius"))


def render_tab_amazigh() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_amazigh"
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
            with st.spinner(t("spinner_amazigh")):
                _amazigh_chart = compute_amazigh_chart(
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
            _amz_tab_sky, _amz_tab_chart = st.tabs([
                "ⵣ 星空圖 Sky Chart",
                "📊 占星資料 Chart Data",
            ])
            with _amz_tab_sky:
                st.markdown(render_amazigh_sky_svg(_amazigh_chart), unsafe_allow_html=True)
                if _amazigh_chart.direction:
                    st.caption(
                        f"{_amazigh_chart.direction.name_zh} / {_amazigh_chart.direction.name_en} · "
                        f"{_amazigh_chart.direction.season_zh} / {_amazigh_chart.direction.season_en}"
                    )
                _render_ai_button("tab_amazigh", _amazigh_chart, btn_key="amazigh_sky")
            with _amz_tab_chart:
                render_amazigh_chart(
                    _amazigh_chart,
                    after_chart_hook=lambda: _render_ai_button("tab_amazigh", _amazigh_chart, btn_key="amazigh_chart"),
                )
                st.markdown(t("desc_amazigh"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_amazigh_prompt"))
        st.markdown(t("desc_amazigh"))


def render_tab_persian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_persian"
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
            with st.spinner(t("spinner_persian")):
                from astro.persian import compute_sassanian_chart
            
                p_chart = compute_sassanian_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    latitude=_p.get("latitude", 0.0), longitude=_p.get("longitude", 0.0),
                    timezone=_p.get("timezone", 0.0),
                    language=get_lang()
                )
        
            # 波斯傳統占星 - 直接顯示星盤圖案（緊湊佈局）
        
            # 薩珊傳統星盤圖（方形格式，純 SVG）
            try:
                from astro.persian.sassanian_chart_renderer import generate_sassanian_svg
            
                chart_data = {
                    "year": _p["year"], "month": _p["month"], "day": _p["day"],
                    "hour": _p["hour"], "minute": _p["minute"],
                    "longitude": _p.get("longitude", 0.0),
                    "latitude": _p.get("latitude", 0.0),
                    "timezone": _p.get("timezone", 0.0),
                }
            
                # 生成 SVG 並直接顯示（響應式設計，PC/手機皆 100% 顯示）
                svg_content = generate_sassanian_svg(
                    chart_data=chart_data,
                    width=500,
                    height=650,
                    show_pahlavi=False,
                    show_royal_stars=True,
                    show_firdar=True,
                )
            
                # 使用 st.components.v1.html 顯示 SVG（響應式高度）
                # viewBox 500x650，使用 width: 100% 確保 PC/手機皆完整顯示
                _render_interactive_html(
                    html=f'''<div style="width: 100%; max-width: 600px; margin: 0 auto;">
                        {svg_content}
                    </div>''',
                    height=720,
                    key="sassanian-main-svg",
                )
            
            except Exception as e:
                st.error(f"星盤渲染失敗：{str(e)}")
        
            # Basic chart info（緊貼星盤下方）
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**{t('persian_current_firdar')}:** {p_chart.current_firdar.lord} ({p_chart.current_firdar.lord_cn})" if p_chart.current_firdar else "當前 Firdar: N/A")
            with col2:
                st.info(f"**{t('persian_current_sub')}:** {p_chart.current_sub_period.lord} ({p_chart.current_sub_period.lord_cn})" if p_chart.current_sub_period else "當前子週期：N/A")
        
            # Main tabs for Persian astrology
            _p_tab_intro, _p_tab_firdar, _p_tab_hyleg, _p_tab_profections, _p_tab_almuten, _p_tab_stars, _p_tab_lots = st.tabs([
                t("western_subtab_natal"),
                t("persian_firdar_title"),
                t("persian_hyleg_title"),
                t("persian_profections_title"),
                t("persian_almuten_title"),
                t("persian_royal_stars_title"),
                t("persian_lots_title"),
            ])
        
            with _p_tab_intro:
                st.header(t("tab_persian"))
                st.caption(t("desc_persian"))
            
                # Planet positions table
                st.subheader("行星位置")
                planet_data = []
                for planet in p_chart.planets:
                    planet_data.append({
                        "行星": f"{planet.name} ({planet.name_cn})",
                        "經度": f"{planet.longitude:.2f}°",
                        "星座": f"{planet.sign_cn} {planet.sign_degree:.1f}°",
                        "宮位": f"第{planet.house}宮",
                        "尊嚴": planet.essential_dignity,
                        "逆行": "✓" if planet.retrograde else "",
                    })
                st.dataframe(planet_data, width="stretch")
            
                # AI Analysis button
                _render_ai_button("tab_persian", p_chart, btn_key="persian")
        
            with _p_tab_firdar:
                st.header(t("persian_firdar_title"))
                st.caption(t("persian_firdar_help"))
            
                # Timeline visualization
                st.subheader("Firdar 生命週期時間軸")
            
                for i, firdar_period in enumerate(p_chart.firdar):
                    is_current = (p_chart.current_firdar and firdar_period.lord == p_chart.current_firdar.lord)
                    expander_label = f"**{i+1}. {firdar_period.lord} ({firdar_period.lord_cn})** — {firdar_period.start_date} 至 {firdar_period.end_date} ({firdar_period.duration_years:.1f}年)"
                    if is_current:
                        expander_label = f"🔮 {expander_label} **(當前)**"
                
                    with st.expander(expander_label, expanded=is_current):
                        # Sub-periods table
                        sub_data = []
                        for sp in firdar_period.sub_periods:
                            is_current_sub = (p_chart.current_sub_period and sp.lord == p_chart.current_sub_period.lord and sp.start_date == p_chart.current_sub_period.start_date)
                            sub_data.append({
                                "子週期": f"{'🔮 ' if is_current_sub else ''}{sp.lord} ({sp.lord_cn})",
                                "起始": sp.start_date,
                                "結束": sp.end_date,
                                "年數": f"{sp.duration_years:.2f}",
                            })
                        st.dataframe(sub_data, width="stretch")
        
            with _p_tab_hyleg:
                st.header(t("persian_hyleg_title"))
                st.caption(t("persian_hyleg_help"))
            
                col1, col2 = st.columns(2)
            
                with col1:
                    st.subheader(t("persian_hyleg_label"))
                    if p_chart.hyleg:
                        st.info(f"**類型:** {p_chart.hyleg.hyleg_type} ({p_chart.hyleg.hyleg_name_cn})\\n\\n"
                               f"**位置:** {p_chart.hyleg.sign} {p_chart.hyleg.degree:.1f}°\\n\\n"
                               f"**宮位:** 第{p_chart.hyleg.house}宮\\n\\n"
                               f"**原因:** {p_chart.hyleg.reason}")
                    else:
                        st.warning("無法計算 Hyleg")
            
                with col2:
                    st.subheader(t("persian_alcocoden_label"))
                    if p_chart.alcocoden:
                        st.info(f"**守護星:** {p_chart.alcocoden.alcocoden_lord} ({p_chart.alcocoden.alcocoden_lord_cn})\\n\\n"
                               f"**{t('persian_planetary_years')}:** {p_chart.alcocoden.planetary_years}年\\n\\n"
                               f"**{t('persian_modified_years')}:** {p_chart.alcocoden.modified_years:.1f}年\\n\\n"
                               f"**{t('persian_aspects')}:** {', '.join(p_chart.alcocoden.aspects) if p_chart.alcocoden.aspects else '無'}\\n\\n"
                               f"**說明:** {p_chart.alcocoden.reason}")
                    else:
                        st.warning("無法計算 Alcocoden")
        
            with _p_tab_profections:
                st.header(t("persian_profections_title"))
                st.caption("波斯式年度主限：每年移動 30°，從上升點開始連續計算。")
            
                # Show first 30 years
                prof_data = []
                for prof in p_chart.profections[:30]:
                    prof_data.append({
                        "年齡": prof.age,
                        "主限星座": f"{prof.profection_sign_cn} {prof.profection_degree:.1f}°",
                        "年度守護星": f"{prof.lord_of_year} ({prof.lord_of_year_cn})",
                        "起始": prof.start_date,
                        "結束": prof.end_date,
                    })
                st.dataframe(prof_data, width="stretch")
        
            with _p_tab_almuten:
                st.header(t("persian_almuten_title"))
                st.caption("Almuten Figuris 是根據薩珊尊嚴規則計算的最強行星，代表命主星。")
            
                if p_chart.almuten_figuris:
                    st.info(f"**最強行星:** {p_chart.almuten_figuris.planet} ({p_chart.almuten_figuris.planet_cn})\\n\\n"
                           f"**{t('persian_dignity_score')}:** {p_chart.almuten_figuris.total_score}\\n\\n"
                           f"**說明:** {p_chart.almuten_figuris.reason}")
                
                    # Dignity breakdown
                    if p_chart.almuten_figuris.dignity_scores:
                        st.subheader("尊嚴分數細項")
                        score_data = []
                        for key, score in p_chart.almuten_figuris.dignity_scores.items():
                            score_data.append({"關鍵點": key, "分數": score})
                        st.dataframe(score_data, width="stretch")
                else:
                    st.warning("無法計算 Almuten Figuris")
        
            with _p_tab_stars:
                st.header(t("persian_royal_stars_title"))
                st.caption("四顆皇家恆星是波斯傳統的重要恆星，與行星合相時具有特殊意義。")
            
                prominent_stars = [rs for rs in p_chart.royal_stars if rs.is_prominent]
            
                if prominent_stars:
                    st.success(f"找到 {len(prominent_stars)} 顆顯著的皇家恆星：")
                    for rs in prominent_stars:
                        st.info(f"**{rs.star_name} ({rs.star_name_cn})**\\n\\n"
                               f"**合相行星:** {rs.conjunction_planet} ({rs.conjunction_planet_cn})\\n\\n"
                               f"**容許度:** {rs.orb}°\\n\\n"
                               f"**意義:** {rs.meaning_cn}")
                else:
                    st.info(t("persian_no_prominent_stars"))
            
                # Show all royal stars
                st.subheader("所有皇家恆星")
                star_data = []
                for rs in p_chart.royal_stars:
                    star_data.append({
                        "恆星": f"{rs.star_name} ({rs.star_name_cn})",
                        "經度": f"{rs.star_longitude:.1f}°",
                        "合相": f"{rs.conjunction_planet} ({rs.conjunction_planet_cn})" if rs.conjunction_planet else "無",
                        "容許度": f"{rs.orb}°" if rs.orb > 0 else "—",
                        "顯著": "✓" if rs.is_prominent else "",
                    })
                st.dataframe(star_data, width="stretch")
        
            with _p_tab_lots:
                st.header(t("persian_lots_title"))
                st.caption("波斯敏感點（Lots）是根據上升點、太陽、月亮計算的敏感點位。")
            
                lots_data = []
                for lot in p_chart.persian_lots:
                    lots_data.append({
                        "名稱": f"{lot.name_en}\\n({lot.name_cn})",
                        "阿拉伯名": lot.name_arabic,
                        "經度": f"{lot.longitude:.2f}°",
                        "星座": f"{lot.sign_cn} {lot.degree:.1f}°",
                        "宮位": f"第{lot.house}宮",
                    })
                st.dataframe(lots_data, width="stretch")
            
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_persian"))


def render_tab_persian_deep() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_persian_deep"
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
            with st.spinner(t("spinner_persian_deep")):
                render_deep_sassanian_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p.get("minute", 0),
                    timezone=_p.get("timezone", 0.0),
                    latitude=_p.get("latitude", 0.0),
                    longitude=_p.get("longitude", 0.0),
                    location_name=_p.get("location_name", ""),
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_persian_deep_prompt"))
        st.markdown(t("desc_persian_deep"))


def render_tab_astro_geomancy() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_astro_geomancy"
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
        try:
            _geo_key = "geo_chart_result"
            _geo_input = _render_geomancy_input()
            if _geo_input is not None:
                # User submitted a new question — recompute
                with st.spinner(t("spinner_astro_geomancy")):
                    _geo_chart = _compute_geomancy_chart(
                        question=_geo_input["question"],
                        question_type=_geo_input["question_type"],
                        seed_mode=_geo_input["seed_mode"],
                        mode=_geo_input.get("mode", "horary"),
                        layout=_geo_input.get("layout", "square"),
                    )
                st.session_state[_geo_key] = _geo_chart
            if _geo_key in st.session_state:
                _geo_chart = st.session_state[_geo_key]
                _render_geomancy_ui(
                    _geo_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_astro_geomancy", _geo_chart, btn_key="astro_geomancy"
                    ),
                )
            else:
                st.info(t("info_astro_geomancy_prompt"))
                st.markdown(t("desc_astro_geomancy"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_european_geomancy() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_european_geomancy"
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
        try:
            with st.spinner(t("spinner_european_geomancy")):
                render_european_geomancy(
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_european_geomancy",
                        st.session_state.get("_eg_reading"),
                        btn_key="european_geomancy",
                    )
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

            # ── 弗拉德命運輪盤 ──
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)
