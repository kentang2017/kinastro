"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t
from core.cached_computations import (
    compute_asteroids_cached,
    compute_fixed_stars_cached,
    compute_heliacal_cached,
    compute_parans_cached,
    compute_solar_return_cached,
    compute_synastry_cached,
    compute_love_synastry_cached,
    compute_western_transits_cached,
    get_or_compute_chart,
    get_ptolemy_calculator,
    _birth_sig,
)

_LEGACY_NAMES = ('ACG_LINE_COLORS', 'ACG_PLANETS', 'ACG_PLANET_COLORS', 'ASTEROID_GROUPS', 'PLANET_GLYPHS', 'PtolPlanet', 'SIGN_NAMES', 'STAR_CATALOG_ALL', '_fludd_config_from_dict', '_render_global_ai_chat', 'auto_cn', 'build_babylonian_planisphere_svg', 'build_greek_horoscope_svg', 'compute_astrocartography', 'compute_astrocartography_transit', 'compute_babylonian_chart', 'compute_cosmobiology_chart', 'compute_esoteric_chart', 'compute_hellenistic_chart', 'compute_hellenistic_extended', 'compute_human_design_chart', 'compute_multi_harmonic', 'compute_primary_directions', 'compute_uranian_chart', 'compute_western_chart', 'datetime', 'dignity_to_chinese', 'find_conjunctions', 'format_acg_for_prompt', 'generate_natal_summary', 'get_asteroid_aspects', 'get_lang', 'render_alchemical_tab', 'render_annual_profections', 'render_babylonian_chart', 'render_cosmobiology', 'render_draconic_chart', 'render_electional_chart', 'render_esoteric_chart', 'render_extended_lots', 'render_fludd_rota', 'render_harmonic', 'render_harmonic_chart', 'render_hellenistic_chart', 'render_human_design_chart', 'render_mundane_chart', 'render_predictive_suite', 'render_primary_directions', 'render_rectification_page', 'render_trutine_chart', 'render_uranian_chart', 'render_valens_combinations', 'render_western_chart', 'render_wiki', 'render_zodiacal_releasing', 'time')

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


def render_tab_western() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_western"
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
            sidereal_mode = st.checkbox(
                t("sidereal_label"),
                value=False,
                help=t("sidereal_help"),
            )
            with st.spinner(t("spinner_western")):
                w_chart = get_or_compute_chart(
                    "tab_western",
                    _p,
                    {"sidereal": sidereal_mode, "location_name": _p.get("location_name", "")},
                )

            _w_tab_natal, _w_tab_transit, _w_tab_return, _w_tab_synastry, _w_tab_love_synastry, _w_tab_dignity, _w_tab_harmonic, _w_tab_draconic, _w_tab_asteroids, _w_tab_stars, _w_tab_parans, _w_tab_heliacal, _w_tab_predictive = st.tabs([
                t("western_subtab_natal"),
                t("western_subtab_transit"),
                t("western_subtab_return"),
                t("western_subtab_synastry"),
                t("western_subtab_love_synastry"),
                t("western_subtab_dignity"),
                t("western_subtab_harmonic"),
                t("western_subtab_draconic"),
                t("western_subtab_asteroids"),
                t("western_subtab_fixed_stars"),
                t("western_subtab_parans"),
                t("western_subtab_heliacal"),
                t("western_subtab_predictive"),
            ])

            with _w_tab_natal:
                _w_gender = st.session_state.get("_calc_gender")
                # Pre-compute natal summary so it can be included in AI analysis
                _summary = generate_natal_summary(
                    w_chart.planets, w_chart.houses,
                    getattr(w_chart, 'asc_sign', ''),
                    lang=get_lang(),
                )
                render_western_chart(
                    w_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_western", w_chart,
                        btn_key="western", page_content=_summary,
                    ),
                    gender=_w_gender,
                )
                # Natal summary
                with st.expander(t("natal_summary_header"), expanded=True):
                    st.markdown(_summary)

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
                w_transits = compute_western_transits_cached(
                    _birth_sig(_p),
                    sidereal_mode,
                    _p.get("location_name", ""),
                    _wt_date.year, _wt_date.month, _wt_date.day,
                    _wt_time.hour, _wt_time.minute,
                )
                if w_transits.aspects_to_natal:
                    st.dataframe([{"Transit": a.transit_planet, "Natal": a.natal_planet,
                                   "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                   "Applying": "→" if a.is_applying else "←"}
                                  for a in w_transits.aspects_to_natal[:20]],
                                 width="stretch")
                    # Transit readings
                    st.subheader(t("transit_readings_header"))
                    _lang = get_lang()
                    for _ta in w_transits.aspects_to_natal[:5]:
                        _reading = _ta.interpretation_cn if _lang in ("zh", "zh_cn") else _ta.interpretation_en
                        _reading = auto_cn(_reading, 'reading_zh') if _reading else _reading
                        st.info(f"**{_ta.transit_planet} {_ta.aspect_symbol} {_ta.natal_planet}** (orb {_ta.orb}°)\n\n{_reading}")
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
                    sr = compute_solar_return_cached(
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
                    syn = compute_synastry_cached(
                        _birth_sig(_p),
                        sidereal_mode,
                        _p.get("location_name", ""),
                        _s_date.year,
                        _s_date.month,
                        _s_date.day,
                        _s_time.hour,
                        _s_time.minute,
                        _s_tz,
                        input_lat,
                        input_lon,
                        location_name,
                    )
                    st.metric("Harmony Score", f"{syn.harmony_summary:.3f}")
                    st.info(auto_cn(syn.summary_cn, 'summary_cn') if get_lang() in ("zh", "zh_cn") else syn.summary_en)
                    if syn.element_compatibility:
                        st.write(f"🔮 {syn.element_compatibility}")
                    if syn.inter_aspects:
                        st.dataframe([{"A": a.planet_a, "B": a.planet_b,
                                       "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                       "Score": f"{a.harmony_score:+.3f}"}
                                      for a in syn.inter_aspects[:20]],
                                     width="stretch")
                        # Synastry readings (top 5)
                        st.subheader(t("synastry_readings_header"))
                        _lang = get_lang()
                        for _sa in syn.inter_aspects[:5]:
                            _reading = _sa.interpretation_cn if _lang in ("zh", "zh_cn") else _sa.interpretation_en
                            _reading = auto_cn(_reading, 'reading_zh') if _reading else _reading
                            st.info(f"**{_sa.planet_a} {_sa.aspect_symbol} {_sa.planet_b}** (orb {_sa.orb}°)\n\n{_reading}")

            with _w_tab_love_synastry:
                _render_love_synastry_tab(
                    _p, sidereal_mode, input_tz, input_lat, input_lon, location_name,
                )

            with _w_tab_dignity:
                st.subheader(t("western_subtab_dignity"))
                _calc = get_ptolemy_calculator()
                _PLANET_MAP = {"Sun": PtolPlanet.SUN, "Moon": PtolPlanet.MOON, "Mercury": PtolPlanet.MERCURY,
                               "Venus": PtolPlanet.VENUS, "Mars": PtolPlanet.MARS, "Jupiter": PtolPlanet.JUPITER, "Saturn": PtolPlanet.SATURN}
                _dignity_rows = []
                for p in w_chart.planets:
                    _pname = p.name.split("(")[0].strip().split()[0]
                    _ptol = _PLANET_MAP.get(_pname)
                    if _ptol:
                        _sign = getattr(p, 'sign', '') or ''
                        _sign_key = _sign.split()[0] if _sign else ''
                        _degree = getattr(p, 'sign_degree', p.longitude % 30)
                        _digs = _calc.get_dignities(_ptol, _sign_key, _degree, is_day_chart=True)
                        _score = _calc.calculate_total_score(_digs)
                        _dignity_rows.append({
                            "Planet": f"{_pname} ({_ptol.value})",
                            "Sign": f"{_sign_key} ({SIGN_NAMES.get(_sign_key, '')})",
                            "Degree": f"{_degree:.2f}°",
                            "Dignities": dignity_to_chinese(_digs),
                            "Score": _score,
                        })
                if _dignity_rows:
                    st.dataframe(_dignity_rows, width="stretch")
                else:
                    st.info("No traditional planet dignity data available.")

            with _w_tab_harmonic:
                render_harmonic_chart(w_chart, lang=get_lang())

            with _w_tab_draconic:
                render_draconic_chart(w_chart, lang=get_lang())

            # ── Asteroids & Centaurs tab ──────────────────────────
            with _w_tab_asteroids:
                st.markdown(t("asteroids_header"))
                _use_adv_ast = st.session_state.get("_adv_asteroids", True)
                if _use_adv_ast:
                    _helio = st.session_state.get("_adv_helio", False)
                    _grp_keys = st.session_state.get("_adv_ast_group_keys") or list(ASTEROID_GROUPS.keys())[:3]
                    with st.spinner("Calculating asteroid positions…"):
                        _asts = compute_asteroids_cached(
                            w_chart.julian_day, _helio, tuple(_grp_keys),
                        )
                    if _asts:
                        _ast_rows = []
                        for _a in _asts:
                            _ast_rows.append({
                                t("adv_col_body"):    f"{_a.symbol} {_a.name} ({_a.name_cn})",
                                t("adv_col_sign"):    _a.sign,
                                t("adv_col_degree"):  f"{_a.sign_degree:.2f}°",
                                t("adv_col_lat"):     f"{_a.latitude:.2f}°",
                                t("adv_col_speed"):   f"{_a.speed:+.4f}°/d",
                                t("adv_col_retro"):   "℞" if _a.retrograde else "",
                                t("adv_col_meaning"): auto_cn(_a.meaning_cn, 'meaning_cn'),
                            })
                        st.dataframe(_ast_rows, width="stretch")

                        # Aspects with traditional planets
                        if st.session_state.get("_adv_ast_aspects", True):
                            _p_lons = {p.name: p.longitude for p in w_chart.planets}
                            _ast_aspects = get_asteroid_aspects(_asts, _p_lons)
                            if _ast_aspects:
                                st.markdown("##### Asteroid Aspects / 小行星相位")
                                st.dataframe([{
                                    t("adv_col_body"):   _aa.asteroid_name,
                                    "Aspect":            f"{_aa.aspect_symbol} {_aa.aspect_name}",
                                    "Planet":            _aa.planet_name,
                                    t("adv_col_orb"):    f"{_aa.orb:.2f}°",
                                } for _aa in _ast_aspects[:30]], width="stretch")
                    else:
                        st.info(t("adv_no_results"))
                else:
                    st.info("Enable 'Include Asteroids & Centaurs' in the sidebar.")

            # ── Fixed Stars tab ───────────────────────────────────
            with _w_tab_stars:
                st.markdown(t("fixed_star_conjunctions_header"))
                _use_adv_stars = st.session_state.get("_adv_fixed_stars", False)
                if _use_adv_stars:
                    _star_limit = st.session_state.get("_adv_stars_count", 30)
                    if _star_limit == STAR_CATALOG_ALL:
                        _star_limit = None  # all

                    with st.spinner("Computing fixed star positions…"):
                        _stars = compute_fixed_stars_cached(w_chart.julian_day, _star_limit)

                    _p_lons = {p.name: p.longitude for p in w_chart.planets}
                    _conjs = find_conjunctions(_stars, _p_lons)

                    st.markdown(f"**{len(_stars)}** stars computed · **{len(_conjs)}** conjunctions (orb ≤ 1.5°)")

                    if _conjs:
                        st.dataframe([{
                            t("adv_col_body"):         f"⭐ {c.star_name} ({c.star_cn})",
                            "Planet":                  c.planet_name,
                            t("adv_col_orb"):          f"{c.orb:.2f}°",
                            t("adv_col_nature"):       c.nature,
                            t("adv_col_meaning"):      auto_cn(c.meaning_cn, 'meaning_cn'),
                        } for c in _conjs], width="stretch")

                    with st.expander("All Stars / 全部恆星", expanded=False):
                        st.dataframe([{
                            t("adv_col_body"):          f"{s.name}",
                            t("adv_col_cn_name"):       s.cn_name,
                            t("adv_col_constellation"): s.constellation,
                            t("adv_col_sign"):          s.sign,
                            t("adv_col_degree"):        f"{s.sign_degree:.2f}°",
                            t("adv_col_lat"):           f"{s.latitude:.2f}°",
                            t("adv_col_magnitude"):     s.magnitude,
                            t("adv_col_nature"):        s.nature,
                            t("adv_col_meaning"):       auto_cn(s.meaning_cn, 'meaning_cn'),
                        } for s in _stars], width="stretch")
                else:
                    st.info("Enable 'Include Fixed Stars' in the sidebar.")

            # ── Parans tab ────────────────────────────────────────
            with _w_tab_parans:
                st.markdown("#### 🔱 " + t("western_subtab_parans"))
                st.caption(t("adv_parans_tooltip"))
                _use_parans = st.session_state.get("_adv_parans", False)
                if _use_parans:
                    _star_limit_p = st.session_state.get("_adv_stars_count", 30)
                    if _star_limit_p == STAR_CATALOG_ALL:
                        _star_limit_p = None

                    with st.spinner("Calculating parans…"):
                        _parans = compute_parans_cached(
                            w_chart.julian_day,
                            getattr(w_chart, "latitude", 0.0),
                            getattr(w_chart, "longitude", 0.0),
                            _star_limit_p,
                        )

                    if _parans:
                        st.dataframe([{
                            "Star / 恆星":           f"⭐ {p.star_name} ({p.star_cn})",
                            t("adv_col_star_event"): p.star_event_cn,
                            "Planet / 行星":         p.planet_name,
                            t("adv_col_planet_event"): p.planet_event_cn,
                            t("adv_col_orb"):        f"{p.orb:.2f}°",
                            t("adv_col_nature"):     p.star_nature,
                            t("adv_col_meaning"):    auto_cn(p.star_meaning_cn, 'meaning_cn'),
                        } for p in _parans[:50]], width="stretch")
                    else:
                        st.info(t("adv_no_results"))
                else:
                    st.info("Enable 'Show Parans' in the sidebar.")

            # ── Heliacal tab ──────────────────────────────────────
            with _w_tab_heliacal:
                st.markdown("#### 🌅 " + t("western_subtab_heliacal"))
                st.caption(t("adv_heliacal_tooltip"))
                _use_heliacal = st.session_state.get("_adv_heliacal", False)
                if _use_heliacal:
                    _star_limit_h = st.session_state.get("_adv_stars_count", 30)
                    _heliacal_star_cap = 30  # heliacal_ut is computationally expensive
                    if _star_limit_h == STAR_CATALOG_ALL or _star_limit_h > _heliacal_star_cap:
                        _star_limit_h = _heliacal_star_cap
                        st.caption(
                            "ℹ️ Heliacal star search capped at 30 stars for performance. "
                            "/ 偕日升沒恆星計算限於30顆以確保效能。"
                        )

                    with st.spinner("Calculating heliacal phenomena…"):
                        try:
                            _hels = compute_heliacal_cached(
                                w_chart.julian_day,
                                getattr(w_chart, "latitude", 0.0),
                                getattr(w_chart, "longitude", 0.0),
                                0.0,
                                _star_limit_h,
                            )
                        except Exception as _he:
                            _hels = []
                            st.warning(t("adv_heliacal_unavail"))
                            st.caption(str(_he))

                    if _hels:
                        st.dataframe([{
                            t("adv_col_body"):       f"{'⭐' if h.is_star else '🪐'} {h.body_name} ({h.body_cn})",
                            t("adv_col_event_type"): auto_cn(h.event_name_cn, 'event_name_cn'),
                            t("adv_col_event_date"): h.event_date,
                        } for h in _hels[:50]], width="stretch")
                    else:
                        st.info(t("adv_no_results"))
                else:
                    st.info("Enable 'Show Heliacal Phenomena' in the sidebar.")

            # ── Predictive Suite tab ──────────────────────────────────
            with _w_tab_predictive:
                try:
                    def _w_predictive_ai_callback(prompt_text: str):
                        """將預測技術 AI 提示傳給現有 AI 分析框架"""
                        _render_ai_button(
                            "tab_western", w_chart,
                            btn_key="western_predictive",
                            page_content=prompt_text,
                        )
                    render_predictive_suite(
                        w_chart,
                        lang=get_lang(),
                        ai_callback=_w_predictive_ai_callback,
                    )
                except Exception as _pred_e:
                    st.error(f"預測技術計算錯誤 / Predictive error: {_pred_e}")
                    st.exception(_pred_e)

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_western"))


def _render_love_synastry_tab(
    _p: dict,
    sidereal_mode: bool,
    input_tz: float,
    input_lat: float,
    input_lon: float,
    location_name: str,
) -> None:
    """Render the ❤️ Love Synastry sub-tab inside the Western chart view."""
    from datetime import date as _date, time as _time_cls
    _bind_legacy()

    _lang = get_lang()
    _is_zh = _lang in ("zh", "zh_cn")

    st.subheader(t("love_synastry_header"))

    _ls_col_name1, _ls_col_name2 = st.columns(2)
    with _ls_col_name1:
        _ls_name_a = st.text_input(t("love_synastry_name_a"), value=t("love_synastry_name_a_default"), key="ls_name_a")
    with _ls_col_name2:
        _ls_name_b = st.text_input(t("love_synastry_name_b"), value=t("love_synastry_name_b_default"), key="ls_name_b")

    st.markdown(f"**{t('love_synastry_person_b')}**")
    _ls_c1, _ls_c2, _ls_c3 = st.columns(3)
    with _ls_c1:
        _ls_date = st.date_input("Date ❤️", value=_date(1990, 6, 15), key="ls_date")
    with _ls_c2:
        _ls_time = st.time_input("Time ❤️", value=_time_cls(12, 0), key="ls_time")
    with _ls_c3:
        _ls_tz = st.number_input("TZ ❤️", value=input_tz, key="ls_tz",
                                  min_value=-12.0, max_value=14.0, step=0.5)

    if st.button(t("love_synastry_calculate"), key="ls_btn"):
        with st.spinner(t("love_synastry_calculating")):
            _ls_result = compute_love_synastry_cached(
                _birth_sig(_p),
                sidereal_mode,
                _p.get("location_name", ""),
                _ls_name_a or t("love_synastry_name_a_default"),
                _ls_date.year,
                _ls_date.month,
                _ls_date.day,
                _ls_time.hour,
                _ls_time.minute,
                _ls_tz,
                input_lat,
                input_lon,
                location_name,
                _ls_name_b or t("love_synastry_name_b_default"),
            )
        st.session_state["_ls_result"] = _ls_result

    _ls_result = st.session_state.get("_ls_result")
    if _ls_result is None:
        return

    # ── Love Scores ──────────────────────────────────────────────
    st.markdown(f"### {t('love_synastry_scores')}")
    _score_defs = [
        ("overall",    "love_synastry_overall",    "❤️"),
        ("attraction", "love_synastry_attraction",  "✨"),
        ("emotional",  "love_synastry_emotional",   "💙"),
        ("sexual",     "love_synastry_sexual",      "🔥"),
        ("longterm",   "love_synastry_longterm",    "💍"),
    ]
    for _sk, _si18n, _emoji in _score_defs:
        _sv = _ls_result.scores.get(_sk, 50.0)
        _label = f"{_emoji} {t(_si18n)}"
        st.write(f"**{_label}** — {_sv:.0f} / 100")
        # Color the progress bar: red for overall, pink shades for others
        _pct = _sv / 100
        _color = "#e74c3c" if _sk == "overall" else "#e91e8c"
        st.markdown(
            f"""<div style="background:#f0f0f0;border-radius:8px;height:14px;width:100%;margin-bottom:10px;">
              <div style="background:{_color};width:{_pct*100:.1f}%;height:14px;border-radius:8px;"></div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Romantic Summary ─────────────────────────────────────────
    st.markdown(f"### {t('love_synastry_summary')}")
    _summary_text = auto_cn(_ls_result.romantic_summary_cn, 'romantic_summary_cn') if _is_zh else _ls_result.romantic_summary_en
    st.success(f"💌 {_summary_text}")

    st.markdown(f"### {t('love_synastry_advice')}")
    _advice_text = auto_cn(_ls_result.love_advice_cn, 'love_advice_cn') if _is_zh else _ls_result.love_advice_en
    st.info(f"🌹 {_advice_text}")

    st.divider()

    # ── Key Love Aspects (top 5 highlighted) ─────────────────────
    if _ls_result.key_love_aspects:
        st.markdown(f"### {t('love_synastry_aspects')}")
        _top_aspects = _ls_result.key_love_aspects[:5]
        for _la in _top_aspects:
            _reading = _la.interpretation_cn if _is_zh else _la.interpretation_en
            if _is_zh:
                _reading = auto_cn(_reading, 'reading_zh')
            _relevance_stars = "❤️" * round(_la.love_relevance * 5)
            st.markdown(
                f"""<div style="border-left:4px solid #e91e8c;padding:10px 14px;margin:8px 0;
                    background:linear-gradient(90deg,#fff0f5,#fff);border-radius:4px;">
                  <strong style="color:#c0106a;">{_la.planet_a} {_la.aspect_symbol} {_la.planet_b}</strong>
                  &nbsp;&nbsp;<span style="color:#888;">orb {_la.orb:.1f}°</span>
                  &nbsp;&nbsp;{_relevance_stars}<br/>
                  <span style="font-size:0.9em;">{_reading}</span>
                </div>""",
                unsafe_allow_html=True,
            )

        if len(_ls_result.key_love_aspects) > 5:
            _exp_label = f"{t('love_synastry_all_aspects')} ({len(_ls_result.key_love_aspects)})"
            with st.expander(_exp_label):
                st.dataframe(
                    [{"A": a.planet_a, "B": a.planet_b, "Aspect": a.aspect_name,
                      "Orb": f"{a.orb:.1f}°", "Score": f"{a.harmony_score:+.3f}",
                      "Relevance": f"{a.love_relevance:.2f}"}
                     for a in _ls_result.key_love_aspects],
                    width="stretch",
                )

    # ── House Overlays ───────────────────────────────────────────
    if _ls_result.house_overlays:
        st.markdown(f"### {t('love_synastry_overlays')}")
        _house_icons = {5: "🎭", 7: "💍", 8: "🌑"}
        for _ov in _ls_result.house_overlays:
            _ov_meaning = auto_cn(_ov.meaning_cn, 'meaning_cn') if _is_zh else _ov.meaning_en
            _icon = _house_icons.get(_ov.house_number, "🏠")
            st.markdown(
                f"""<div style="border-left:4px solid #ff6b9d;padding:10px 14px;margin:8px 0;
                    background:#fff8fa;border-radius:4px;">
                  {_icon} <strong style="color:#c0106a;">{_ov.planet_owner} 的 {_ov.planet_name}</strong>
                  落入 <strong>{_ov.house_owner}</strong> 的
                  <strong>第 {_ov.house_number} 宮</strong>
                  {"(" + _ov.house_sign + ")" if _ov.house_sign else ""}<br/>
                  <span style="font-size:0.9em;color:#555;">{_ov_meaning}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    # ── Composite Core Planets ───────────────────────────────────
    if _ls_result.composite_planets:
        st.markdown(f"### {t('love_synastry_composite')}")
        _cp_glyphs = {"Sun": "☉", "Moon": "☽", "Venus": "♀", "Mars": "♂"}
        _cp_cols = st.columns(len(_ls_result.composite_planets))
        for _ci, _cp in enumerate(_ls_result.composite_planets):
            with _cp_cols[_ci]:
                _glyph = _cp_glyphs.get(_cp.name, "★")
                _sign_label = _cp.sign_zh if _is_zh else _cp.sign
                st.metric(
                    label=f"{_glyph} {_cp.name}",
                    value=f"{_sign_label} {_cp.sign_degree:.1f}°",
                )


def render_tab_sabian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_sabian"
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
            sidereal_mode = st.checkbox(
                t("sidereal_label"),
                value=False,
                help=t("sidereal_help"),
            )
            with st.spinner(t("spinner_western")):
                w_params = dict(**_p, sidereal=sidereal_mode)
                w_chart = compute_western_chart(**w_params)
        
            st.header(t("sabian_system_label"))
            st.caption(t("sabian_symbols_help"))
        
            try:
                from astro.sabian import get_sabian_for_planet, render_sabian_svg, load_sabian_symbols
            
                # Major planets list
                _sabian_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                                   "Jupiter", "Saturn", "Ascendant", "Midheaven"]
            
                # Pass full chart data including ascendant and midheaven
                _chart_data = {
                    "planets": w_chart.planets,
                    "ascendant": w_chart.ascendant,
                    "midheaven": w_chart.midheaven,
                }
            
                # Pre-fetch all Sabian data
                _sabian_lang = st.session_state.get("lang", "zh")
                _sabian_data_list = []
                for _pname in _sabian_planets:
                    try:
                        _sabian = get_sabian_for_planet(_chart_data, _pname)
                        if _sabian:
                            _sabian_data_list.append((_pname, _sabian))
                    except Exception:
                        pass

                # Build a horizontal-scroll card strip at the top
                _planet_glyphs = {
                    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
                    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
                    "Ascendant": "AC", "Midheaven": "MC",
                }
                _cards_html = ""
                for _pname, _sabian in _sabian_data_list:
                    _svg = render_sabian_svg(
                        _sabian['planet_longitude'],
                        size=220,
                        language=_sabian_lang,
                    )
                    _glyph = _planet_glyphs.get(_pname, _pname[:2])
                    _cards_html += f"""
                    <div style="
                        display:inline-block;
                        vertical-align:top;
                        width:220px;
                        margin-right:12px;
                        flex-shrink:0;
                    ">
                        <div style="text-align:center;font-size:11px;font-weight:600;
                                    margin-bottom:4px;opacity:0.7;">{_glyph} {_pname}</div>
                        {_svg}
                    </div>"""

                _scroll_component = f"""
                <div style="
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                    white-space: nowrap;
                    padding: 8px 4px 12px 4px;
                    scroll-snap-type: x mandatory;
                ">
                    {_cards_html}
                </div>
                <p style="text-align:center;font-size:10px;opacity:0.5;margin-top:2px;">
                    {t('sabian_scroll_hint')}
                </p>
                """
                _render_interactive_html(
                    html=_scroll_component,
                    height=360,
                    key="sabian-scroll-strip",
                )

                st.divider()

                # Detail section: use tabs for each planet (compact vertical space)
                _tab_labels = [f"{_planet_glyphs.get(n, '')} {n}" for n, _ in _sabian_data_list]
                _tabs = st.tabs(_tab_labels)
                for _idx, (_tab, (_pname, _sabian)) in enumerate(zip(_tabs, _sabian_data_list)):
                    with _tab:
                        _svg = render_sabian_svg(
                            _sabian['planet_longitude'],
                            size=300,
                            language=_sabian_lang,
                        )
                        _render_interactive_html(
                            html=f'<div style="width:100%;max-width:320px;margin:0 auto">{_svg}</div>',
                            height=380,
                            key=f"sabian-detail-{_idx}",
                        )
                        st.markdown(f"*{t('sabian_formula_label')}:* {_sabian['formula']}")
                        st.markdown(f"*{t('sabian_positive_label')}:* {_sabian['positive']}")
                        st.markdown(f"*{t('sabian_negative_label')}:* {_sabian['negative']}")
                        st.markdown(f"*{t('sabian_interpretation_label')}:* {_sabian['interpretation']}")
            
                # Optional: Show all 360 symbols in an expander
                with st.expander(t("sabian_show_all")):
                    st.caption("360 Sabian Symbols (Marc Edmund Jones, 1953)")
                    _all_symbols = load_sabian_symbols()
                    for _sym in _all_symbols[:360]:
                        st.markdown(f"**{_sym['degree']}° {_sym['sign']}:** {_sym['symbol']}")
                    
            except ImportError as _ie:
                st.error("Sabian Symbols module not available.")
                st.exception(_ie)
            except Exception as _se:
                st.error(f"Error loading Sabian Symbols: {_se}")
                st.exception(_se)
            
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_sabian") if hasattr(t, "desc_sabian") else "🔮 薩比恩符號：Marc Edmund Jones (1953) 原著的 360 個象徵圖像，每個黃道度數對應一個獨特的心理原型。")


def render_tab_hellenistic() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_hellenistic"
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
            # Hellenistic needs a western chart first
            with st.spinner(t("spinner_western")):
                _hellen_w = compute_western_chart(**_p)
            with st.spinner(t("spinner_hellenistic")):
                _hellen_chart = compute_hellenistic_chart(
                    _hellen_w,
                    birth_year=birth_date.year,
                    current_year=datetime.now().year,
                )
                _hellen_ext = compute_hellenistic_extended(_hellen_w, _hellen_chart)
            _h_tab_chart, _h_tab_natal, _h_tab_prof, _h_tab_zr, _h_tab_lots, _h_tab_ext_lots, _h_tab_synkrasis, _h_tab_centiloquy = st.tabs([
                t("hellen_subtab_chart"),
                t("hellen_subtab_natal"),
                t("hellen_subtab_profections"),
                t("hellen_subtab_zr"),
                t("hellen_subtab_lots"),
                "📜 Extended Lots / 擴充 Lots",
                "⚗️ Valens Synkrasis / 行星組合",
                t("hellen_subtab_centiloquy"),
            ])
            with _h_tab_chart:
                _greek_svg = build_greek_horoscope_svg(
                    _hellen_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
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
                _render_ai_button("tab_hellenistic", _hellen_chart, btn_key="hellenistic")
            with _h_tab_natal:
                render_hellenistic_chart(_hellen_chart)
            with _h_tab_prof:
                render_annual_profections(
                    asc_lon=_hellen_chart.ascendant,
                    birth_year=birth_date.year,
                    num_years=24,
                    lang=get_lang(),
                )
            with _h_tab_zr:
                # Retrieve Lot of Fortune and Lot of Spirit longitudes
                _zr_fortune_lon = next(
                    (l.longitude for l in _hellen_chart.lots if "Fortune" in l.name), 0.0
                )
                _zr_spirit_lon = next(
                    (l.longitude for l in _hellen_chart.lots if "Spirit" in l.name), 0.0
                )
                render_zodiacal_releasing(
                    fortune_lon=_zr_fortune_lon,
                    spirit_lon=_zr_spirit_lon,
                    birth_jd=_hellen_w.julian_day,
                    target_jd=_hellen_w.julian_day + (datetime.now().year - birth_date.year) * 365.25,
                    lang=get_lang(),
                )
            with _h_tab_lots:
                if _hellen_chart.lots:
                    st.subheader(t("hellen_lots_header"))
                    st.dataframe([{"Name": f"{l.name} ({auto_cn(l.name_cn, 'name_cn')})",
                                   "Sign": l.sign, "Degree": f"{l.sign_degree:.2f}°",
                                   "House": l.house, "Formula": l.formula_en,
                                   "Meaning": auto_cn(l.meaning_cn, 'meaning_cn')}
                                  for l in _hellen_chart.lots],
                                 width="stretch")

            with _h_tab_ext_lots:
                if _hellen_ext.extended_lots:
                    render_extended_lots(_hellen_ext.extended_lots)
            with _h_tab_synkrasis:
                if _hellen_ext.synkrasis:
                    render_valens_combinations(_hellen_ext.synkrasis)

            with _h_tab_centiloquy:
                st.subheader(t("centiloquy_header"))
                from astro.classic.ptolemy_centiloquy import get_random_aphorism, search_aphorism, get_all_aphorisms, format_aphorism
                # Daily aphorism
                st.info(format_aphorism(get_random_aphorism()))
                # Search
                _cent_query = st.text_input(t("centiloquy_search_label"), key="centiloquy_search")
                if _cent_query:
                    _results = search_aphorism(_cent_query)
                    if _results:
                        for _r in _results:
                            st.markdown(format_aphorism(_r))
                    else:
                        st.warning(t("centiloquy_no_match"))
                else:
                    for _a in get_all_aphorisms():
                        with st.expander(t("centiloquy_aphorism_num").format(n=_a['id'])):
                            st.markdown(_a["text"])

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_hellenistic"))


def render_tab_babylonian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_babylonian"
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
            with st.spinner(t("spinner_babylonian")):
                _bab_chart = compute_babylonian_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    timezone=_p["timezone"],
                    lat=_p["latitude"], lon=_p["longitude"],
                )
            _bab_tab_chart, _bab_tab_natal, _bab_tab_omens = st.tabs([
                t("babylonian_subtab_chart"),
                t("babylonian_subtab_natal"),
                t("babylonian_subtab_omens"),
            ])
            with _bab_tab_chart:
                _bab_svg = build_babylonian_planisphere_svg(
                    _bab_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_bab_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center; color:#888; font-size:11px;">'
                    'Babylonian Planisphere (K.8538 style) — 8-sector clay disc · '
                    'Sidereal zodiac · MUL.APIN sign names'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_babylonian", _bab_chart, btn_key="babylonian")
            with _bab_tab_natal:
                render_babylonian_chart(_bab_chart)
            with _bab_tab_omens:
                st.subheader("📜 Enūma Anu Enlil " + t("babylonian_subtab_omens"))
                for _omen in _bab_chart.omens:
                    _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                    st.markdown(
                        f"{_omen_icon} **{_omen.planet}** ({_omen.god_name}) — "
                        f"*{_omen.condition.upper()}*: {_omen.text}"
                    )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_babylonian"))


def render_tab_acg() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_acg"
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
            with st.spinner(t("spinner_acg")):
                _acg_result = compute_astrocartography(**_p)

            st.markdown(f"### {t('acg_title')}")

            _acg_tab_map, _acg_tab_table, _acg_tab_transit = st.tabs([
                t("acg_subtab_map"),
                t("acg_subtab_table"),
                t("acg_subtab_transit"),
            ])

            # ── Sub-tab 1: 互動地圖 Interactive Map ──
            with _acg_tab_map:
                import plotly.graph_objects as go

                # Planet & line type filters
                _acg_col1, _acg_col2 = st.columns(2)
                with _acg_col1:
                    _acg_planets = st.multiselect(
                        t("acg_planet_filter"),
                        options=list(ACG_PLANETS.keys()),
                        default=["Sun", "Moon", "Venus", "Mars", "Jupiter"],
                        key="acg_planet_sel",
                    )
                with _acg_col2:
                    _acg_lines = st.multiselect(
                        t("acg_line_filter"),
                        options=["AC", "MC", "IC", "DC"],
                        default=["AC", "MC", "IC", "DC"],
                        key="acg_line_sel",
                    )

                # Build Plotly map
                _acg_fig = go.Figure()

                # Line dash patterns for each line type
                _acg_dashes = {"AC": "solid", "MC": "dash", "IC": "dot", "DC": "dashdot"}

                for _planet in _acg_planets:
                    _planet_data = _acg_result.lines.get(_planet, {})
                    _glyph = PLANET_GLYPHS.get(_planet, "")
                    _p_color = ACG_PLANET_COLORS.get(_planet, "#888")

                    for _lt in _acg_lines:
                        _pts = _planet_data.get(_lt, [])
                        if not _pts:
                            continue

                        _lons = [p[0] for p in _pts]
                        _lats = [p[1] for p in _pts]

                        # Get meaning for hover
                        _meaning = _acg_result.meanings.get(_planet, {}).get(_lt, "")

                        _acg_fig.add_trace(go.Scattergeo(
                            lon=_lons,
                            lat=_lats,
                            mode="lines",
                            line=dict(
                                color=_p_color,
                                width=2,
                                dash=_acg_dashes.get(_lt, "solid"),
                            ),
                            name=f"{_planet} {_glyph} {_lt}",
                            hovertemplate=(
                                f"<b>{_planet} {_glyph} {_lt}</b><br>"
                                f"經度: %{{lon:.1f}}°<br>"
                                f"緯度: %{{lat:.1f}}°<br>"
                                f"<i>{_meaning[:40]}</i>"
                                "<extra></extra>"
                            ),
                        ))

                # Add Paran points as markers
                if _acg_result.parans:
                    _paran_lons = [p.longitude for p in _acg_result.parans[:50]]
                    _paran_lats = [p.latitude for p in _acg_result.parans[:50]]
                    _paran_texts = [
                        f"{p.planet1} {p.line_type1} × {p.planet2} {p.line_type2}"
                        for p in _acg_result.parans[:50]
                    ]

                    _acg_fig.add_trace(go.Scattergeo(
                        lon=_paran_lons,
                        lat=_paran_lats,
                        mode="markers",
                        marker=dict(
                            size=8,
                            color="#FFD700",
                            symbol="star",
                            line=dict(width=1, color="#333"),
                        ),
                        text=_paran_texts,
                        name="Paran ✦",
                        hovertemplate=(
                            "<b>Paran 交叉點</b><br>"
                            "%{text}<br>"
                            "經度: %{lon:.1f}°, 緯度: %{lat:.1f}°"
                            "<extra></extra>"
                        ),
                    ))

                # Add birth location marker
                _acg_fig.add_trace(go.Scattergeo(
                    lon=[_p["longitude"]],
                    lat=[_p["latitude"]],
                    mode="markers+text",
                    marker=dict(size=12, color="#e74c3c", symbol="diamond"),
                    text=[_p.get("location_name", "Birth")],
                    textposition="top center",
                    name="出生地 Birth",
                    hovertemplate=(
                        "<b>出生地</b><br>"
                        f"{_p.get('location_name', '')}<br>"
                        f"經度: {_p['longitude']:.2f}°, 緯度: {_p['latitude']:.2f}°"
                        "<extra></extra>"
                    ),
                ))

                _acg_fig.update_geos(
                    showcountries=True,
                    countrycolor="rgba(100,100,100,0.3)",
                    showcoastlines=True,
                    coastlinecolor="rgba(150,150,150,0.4)",
                    showland=True,
                    landcolor="rgba(30,30,50,0.8)",
                    showocean=True,
                    oceancolor="rgba(20,20,40,0.9)",
                    showlakes=False,
                    projection_type="natural earth",
                    bgcolor="rgba(0,0,0,0)",
                )

                _acg_fig.update_layout(
                    height=550,
                    margin=dict(l=0, r=0, t=30, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=10),
                    ),
                    geo=dict(bgcolor="rgba(0,0,0,0)"),
                )

                st.plotly_chart(_acg_fig, width="stretch")

                # Legend
                _legend_cols = st.columns(4)
                _legend_items = [
                    ("acg_line_ac", ACG_LINE_COLORS["AC"], "solid"),
                    ("acg_line_mc", ACG_LINE_COLORS["MC"], "dashed"),
                    ("acg_line_ic", ACG_LINE_COLORS["IC"], "dotted"),
                    ("acg_line_dc", ACG_LINE_COLORS["DC"], "dashdot"),
                ]
                for _col, (_key, _color, _style) in zip(_legend_cols, _legend_items):
                    with _col:
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:6px;">'
                            f'<div style="width:24px;height:3px;background:{_color};'
                            f'border-style:{_style};"></div>'
                            f'<span style="font-size:12px;">{t(_key)}</span></div>',
                            unsafe_allow_html=True,
                        )

                # Paran section
                if _acg_result.parans:
                    with st.expander(t("acg_paran_header"), expanded=False):
                        import pandas as pd
                        _paran_rows = []
                        for _pr in _acg_result.parans[:30]:
                            _paran_rows.append({
                                "行星1": f"{_pr.planet1} {PLANET_GLYPHS.get(_pr.planet1, '')}",
                                "線型1": _pr.line_type1,
                                "行星2": f"{_pr.planet2} {PLANET_GLYPHS.get(_pr.planet2, '')}",
                                "線型2": _pr.line_type2,
                                "緯度": f"{_pr.latitude:.1f}°",
                                "經度": f"{_pr.longitude:.1f}°",
                            })
                        if _paran_rows:
                            st.dataframe(pd.DataFrame(_paran_rows), hide_index=True, width="stretch")

                # AI button
                _render_ai_button("tab_acg", _acg_result, btn_key="acg_map",
                                  page_content=format_acg_for_prompt(_acg_result))

            # ── Sub-tab 2: 行星線資料表 Planet Line Data Table ──
            with _acg_tab_table:
                import pandas as pd
                st.subheader(t("acg_subtab_table"))

                _table_rows = []
                for _planet_name, _line_dict in _acg_result.lines.items():
                    _glyph = PLANET_GLYPHS.get(_planet_name, "")
                    for _lt in ("AC", "MC", "IC", "DC"):
                        _pts = _line_dict.get(_lt, [])
                        _meaning = _acg_result.meanings.get(_planet_name, {}).get(_lt, "")
                        if _pts:
                            _mid = len(_pts) // 2
                            _table_rows.append({
                                "行星 Planet": f"{_planet_name} {_glyph}",
                                "線型 Type": _lt,
                                "黃經 Lon": f"{_acg_result.planet_longitudes.get(_planet_name, 0):.2f}°",
                                "代表經度 Geo Lon": f"{_pts[_mid][0]:.1f}°",
                                "點數 Points": len(_pts),
                                "解釋 Meaning": _meaning,
                            })
                if _table_rows:
                    st.dataframe(pd.DataFrame(_table_rows), hide_index=True, width="stretch")

                _render_ai_button("tab_acg", _acg_result, btn_key="acg_table",
                                  page_content=format_acg_for_prompt(_acg_result))

            # ── Sub-tab 3: 流年搬遷線 Transit ACG ──
            with _acg_tab_transit:
                st.subheader(t("acg_subtab_transit"))

                _tr_col1, _tr_col2 = st.columns(2)
                with _tr_col1:
                    _tr_date = st.date_input(
                        t("acg_transit_date"),
                        value=datetime.now().date(),
                        key="acg_tr_date",
                    )
                with _tr_col2:
                    _tr_time = st.time_input(
                        t("acg_transit_time"),
                        value=time(12, 0),
                        key="acg_tr_time",
                    )

                # Year slider for quick navigation
                _tr_year_slider = st.slider(
                    "Year / 年份",
                    min_value=1950,
                    max_value=2050,
                    value=_tr_date.year,
                    key="acg_tr_year_slider",
                )

                # Compute transit ACG
                with st.spinner(t("spinner_acg")):
                    _tr_acg = compute_astrocartography_transit(
                        natal_year=_p["year"], natal_month=_p["month"],
                        natal_day=_p["day"], natal_hour=_p["hour"],
                        natal_minute=_p["minute"], natal_timezone=_p["timezone"],
                        transit_year=_tr_year_slider,
                        transit_month=_tr_date.month,
                        transit_day=_tr_date.day,
                        transit_hour=_tr_time.hour,
                        transit_minute=_tr_time.minute,
                        transit_timezone=_p["timezone"],
                    )

                # Transit map
                import plotly.graph_objects as go
                _tr_fig = go.Figure()

                _tr_planets_sel = st.multiselect(
                    t("acg_planet_filter"),
                    options=list(ACG_PLANETS.keys()),
                    default=["Sun", "Moon", "Jupiter", "Saturn"],
                    key="acg_tr_planet_sel",
                )
                _tr_dashes = {"AC": "solid", "MC": "dash", "IC": "dot", "DC": "dashdot"}

                for _planet in _tr_planets_sel:
                    _planet_data = _tr_acg.lines.get(_planet, {})
                    _glyph = PLANET_GLYPHS.get(_planet, "")
                    _p_color = ACG_PLANET_COLORS.get(_planet, "#888")

                    for _lt in ("AC", "MC", "IC", "DC"):
                        _pts = _planet_data.get(_lt, [])
                        if not _pts:
                            continue
                        _lons = [p[0] for p in _pts]
                        _lats = [p[1] for p in _pts]

                        _tr_fig.add_trace(go.Scattergeo(
                            lon=_lons,
                            lat=_lats,
                            mode="lines",
                            line=dict(color=_p_color, width=2,
                                      dash=_tr_dashes.get(_lt, "solid")),
                            name=f"{_planet} {_glyph} {_lt} (Transit)",
                        ))

                _tr_fig.update_geos(
                    showcountries=True,
                    countrycolor="rgba(100,100,100,0.3)",
                    showcoastlines=True,
                    coastlinecolor="rgba(150,150,150,0.4)",
                    showland=True,
                    landcolor="rgba(30,30,50,0.8)",
                    showocean=True,
                    oceancolor="rgba(20,20,40,0.9)",
                    projection_type="natural earth",
                    bgcolor="rgba(0,0,0,0)",
                )
                _tr_fig.update_layout(
                    height=500,
                    margin=dict(l=0, r=0, t=30, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                                xanchor="center", x=0.5, font=dict(size=10)),
                    geo=dict(bgcolor="rgba(0,0,0,0)"),
                )

                st.plotly_chart(_tr_fig, width="stretch")

                _render_ai_button("tab_acg", _tr_acg, btn_key="acg_transit",
                                  page_content=format_acg_for_prompt(_tr_acg))

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_acg"))


def render_tab_uranian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_uranian"
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
            with st.spinner(t("spinner_uranian")):
                _uranian_result = compute_uranian_chart(**_p)
            render_uranian_chart(_uranian_result)
            _render_ai_button("tab_uranian", _uranian_result, btn_key="uranian")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_uranian"))


def render_tab_cosmobiology() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_cosmobiology"
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
            with st.spinner(t("spinner_cosmobiology")):
                _cosmo_result = compute_cosmobiology_chart(**_p)
            render_cosmobiology(_cosmo_result)
            _render_ai_button("tab_cosmobiology", _cosmo_result, btn_key="cosmobiology")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_cosmobiology"))


def render_tab_harmonic() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_harmonic"
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
            with st.spinner(t("spinner_harmonic")):
                _harmonic_result = compute_multi_harmonic(**_p)
            render_harmonic(_harmonic_result)
            _render_ai_button("tab_harmonic", _harmonic_result, btn_key="harmonic")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_harmonic"))


def render_tab_primary_directions() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_primary_directions"
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
            with st.spinner(t("spinner_primary_directions")):
                _pd_result = compute_primary_directions(**_p)
            render_primary_directions(_pd_result)
            _render_ai_button("tab_primary_directions", _pd_result, btn_key="primary_directions")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_primary_directions_prompt"))
        st.markdown(t("desc_primary_directions"))


def render_tab_rectification() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_rectification"
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
    render_rectification_page(
        default_date=(
            date(_p["year"], _p["month"], _p["day"])
            if _p else None
        ),
        default_lat=_p.get("latitude", 22.3193),
        default_lon=_p.get("longitude", 114.1694),
        default_tz=_p.get("timezone", 8.0),
    )


def render_tab_trutine_of_hermes() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_trutine_of_hermes"
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
            render_trutine_chart(
                year=_p["year"],
                month=_p["month"],
                day=_p["day"],
                hour=_p["hour"],
                minute=_p.get("minute", 0),
                timezone=_p.get("timezone", 0.0),
                latitude=_p.get("latitude", 25.033),
                longitude=_p.get("longitude", 121.565),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_trutine_of_hermes_prompt"))
        st.markdown(t("desc_trutine_of_hermes"))


def render_tab_esoteric() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_esoteric"
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
            with st.spinner(t("spinner_esoteric")):
                _esoteric_result = compute_esoteric_chart(**_p)
            render_esoteric_chart(_esoteric_result)
            _render_ai_button("tab_esoteric", _esoteric_result, btn_key="esoteric")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_esoteric_prompt"))
        st.markdown(t("desc_esoteric"))

        # ============================================================


def render_tab_human_design() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_human_design"
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
            with st.spinner(t("spinner_human_design")):
                _hd_result = compute_human_design_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    timezone=_p.get("timezone", 8.0),
                    latitude=_p.get("latitude", 25.033),
                    longitude=_p.get("longitude", 121.565),
                    location_name=_p.get("location_name", ""),
                )
            render_human_design_chart(_hd_result)
            _render_ai_button("tab_human_design", _hd_result, btn_key="human_design")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_human_design_prompt"))
        st.markdown(t("desc_human_design"))

        # ============================================================


def render_tab_electional() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_electional"
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
            render_electional_chart(
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

            # ============================================================
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_mundane() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_mundane"
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
            _p = st.session_state.get("_calc_params", {})
            render_mundane_chart(
                year=_p.get("year"),
                month=_p.get("month"),
                day=_p.get("day"),
                hour=_p.get("hour"),
                minute=_p.get("minute"),
                timezone=_p.get("timezone"),
                latitude=_p.get("latitude"),
                longitude=_p.get("longitude"),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

            # ============================================================
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_fludd_rota() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_fludd_rota"
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
        _fludd_auto_cfg = None
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_fludd_rota")):
                    _fw = compute_western_chart(**_p)
                def _planet_lon(_name_prefix: str) -> float | None:
                    for _pl in _fw.planets:
                        if _pl.name.startswith(_name_prefix):
                            return _pl.longitude
                    return None
                _lons = {
                    k: _planet_lon(v)
                    for k, v in [
                        ("sun", "Sun"), ("moon", "Moon"),
                        ("mercury", "Mercury"), ("venus", "Venus"),
                        ("mars", "Mars"), ("jupiter", "Jupiter"),
                        ("saturn", "Saturn"),
                    ]
                }
                _nn_lon = _planet_lon("North Node")
                # Only build auto_config when all required planets are present
                if all(v is not None for v in _lons.values()) and _nn_lon is not None:
                    _fludd_auto_cfg = _fludd_config_from_dict({
                        **_lons,
                        "ascendant": _fw.ascendant,
                        "north_node": _nn_lon,
                        "south_node": (_nn_lon + 180.0) % 360.0,
                    })
            except Exception as _fludd_err:
                import logging as _logging
                _logging.getLogger(__name__).warning(
                    "Fludd Rota auto-config failed: %s", _fludd_err
                )
        render_fludd_rota(
            auto_config=_fludd_auto_cfg,
            after_chart_hook=lambda: _render_ai_button(
                "tab_fludd_rota",
                st.session_state.get("fludd_rota_reading"),
                btn_key="fludd_rota",
            )
        )
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)

        # ============================================================


def render_tab_alchemical_astrology() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_alchemical_astrology"
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
        _alch_lons: dict | None = None
        if _is_calculated:
            with st.spinner(t("spinner_alchemical_astrology")):
                _alch_fw = compute_western_chart(**st.session_state["_calc_params"])
            # pl.name format in WesternChart is "<PlanetName> [retrograde]"
            # split()[0] extracts the planet name reliably (e.g. "Sun", "Moon")
            _alch_lons = {
                pl.name.split()[0].lower(): pl.longitude
                for pl in _alch_fw.planets
                if pl.name.split()[0] in {
                    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"
                }
            }
        render_alchemical_tab(
            planet_longitudes=_alch_lons,
            after_chart_hook=lambda: _render_ai_button(
                "tab_alchemical_astrology",
                st.session_state.get("alchemical_reading"),
                btn_key="alchemical_astrology",
            ) if _is_calculated else None,
        )
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)

    # ── Global AI chatbox — fixed at the bottom of every page ──────────────────
    _render_global_ai_chat()


def render_tab_history() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_history"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    try:
        st.header("📜 " + t("tab_history"))
        st.caption("占星術是人類最古老的知識體系之一，跨越五千年文明，連結天上與地下。" if _cur_lang in ("zh", "zh_cn") else "Astrology is one of humanity's oldest knowledge systems, spanning five millennia of civilization.")

        st.divider()

        # Load and render markdown file
        try:
            with open("docs/astrology_history.md", "r", encoding="utf-8") as f:
                history_md = f.read()
            st.markdown(history_md)
        except FileNotFoundError:
            st.error("占星歷史文件尚未建立 / Astrology history file not found: `docs/astrology_history.md`")
            st.info("請先建立文件 / Please create the document first.")

        _render_ai_button("tab_history", {"system": "astrology_history"}, btn_key="history")
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_wiki() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_wiki"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    try:
        render_wiki(lang=_cur_lang)
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)
