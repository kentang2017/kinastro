"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t
from core.cached_computations import (
    get_or_compute_chart,
)

_LEGACY_NAMES = ('build_kalachakra_mandala_svg', 'calculate_nine_palace_divination', 'calculate_thai_nine_grid', 'compute_brahma_jati', 'compute_celtic_tree_chart', 'compute_lao_chart', 'compute_lifetime_hexagram', 'compute_mahabote_chart', 'compute_nine_star_ki_chart', 'compute_polynesian_chart', 'compute_tibetan_chart', 'compute_wariga', 'compute_weton', 'compute_zurkhai_chart', 'datetime', 'get_lang', 'render_bintang_duabelas_chart', 'render_brahma_jati', 'render_brahma_jati_browse', 'render_byzantine_astrology_chart', 'render_celtic_tree_chart', 'render_jawa_weton_chart', 'render_kinketika_chart', 'render_lao_horasat', 'render_liuyao_lifetime_chart', 'render_malay_nujum_chart', 'render_mahabote_chart', 'render_nine_grid', 'render_nine_palace_divination', 'render_nine_star_ki_chart', 'render_polynesian_chart_ui', 'render_thai_chart', 'render_tibetan_chart', 'render_wariga_chart', 'render_zurkhai_chart', 'x')

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


def render_tab_thai() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_thai"
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
            with st.spinner(t("spinner_thai")):
                t_chart = get_or_compute_chart(
                    "tab_thai",
                    _p,
                    {"location_name": _p.get("location_name", "")},
                )
            thai_tab_chart, thai_tab_nine, thai_tab_brahma = st.tabs(
                [t("thai_subtab_chart"), t("thai_subtab_nine"), t("thai_subtab_brahma")]
            )
            with thai_tab_chart:
                render_thai_chart(t_chart, after_chart_hook=lambda: _render_ai_button("tab_thai", t_chart, btn_key="thai"))
            with thai_tab_nine:
                nine_grid_result = calculate_thai_nine_grid(
                    birth_date.day, birth_date.month, birth_date.year
                )
                render_nine_grid(nine_grid_result)
                st.markdown("---")
                divination_result = calculate_nine_palace_divination(t_chart)
                render_nine_palace_divination(divination_result)
            with thai_tab_brahma:
                from datetime import date as _date_cls
                _bj_bd = _date_cls(birth_date.year, birth_date.month, birth_date.day)
                _bj_weekday = _bj_bd.weekday()  # 0=Mon … 6=Sun
                _bj_age = None
                _bj_gender = None
                _bj_age_col, _bj_gender_col = st.columns(2)
                with _bj_age_col:
                    _bj_age = st.number_input(
                        "年齡 (Age)", min_value=1, max_value=120,
                        value=max(1, _date_cls.today().year - birth_date.year),
                        key="brahma_jati_age",
                    )
                with _bj_gender_col:
                    _bj_gender = st.selectbox(
                        "性別 (Gender)",
                        options=["male", "female"],
                        format_func=lambda x: "男 Male" if x == "male" else "女 Female",
                        key="brahma_jati_gender",
                    )
                _bj_reading = compute_brahma_jati(
                    ce_year=birth_date.year,
                    month=birth_date.month,
                    weekday=_bj_weekday,
                    age=_bj_age,
                    gender=_bj_gender,
                )
                render_brahma_jati(_bj_reading)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_thai"))
        render_brahma_jati_browse()


def render_tab_laos() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_laos"
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
            with st.spinner(t("spinner_laos")):
                lao_chart = compute_lao_chart(**_p)
            render_lao_horasat(
                lao_chart,
                lang=get_lang(),
                after_chart_hook=lambda: _render_ai_button("tab_laos", lao_chart, btn_key="tab_laos"),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_lao_prompt"))
        st.markdown(t("desc_laos"))


def render_tab_mahabote() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_mahabote"
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
            with st.spinner(t("spinner_mahabote")):
                mb_chart = compute_mahabote_chart(**_p)
            render_mahabote_chart(mb_chart, after_chart_hook=lambda: _render_ai_button("tab_mahabote", mb_chart, btn_key="mahabote"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_mahabote"))


def render_tab_nine_star_ki() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_nine_star_ki"
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
            with st.spinner(t("spinner_nine_star_ki")):
                _nsk_chart = compute_nine_star_ki_chart(**_p)
            render_nine_star_ki_chart(
                _nsk_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_nine_star_ki", _nsk_chart, btn_key="nine_star_ki"
                ),
                lang=get_lang(),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_nine_star_ki"))


def render_tab_celtic_tree() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_celtic_tree"
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
            with st.spinner(t("spinner_celtic_tree")):
                _celtic_chart = compute_celtic_tree_chart(**_p)
            render_celtic_tree_chart(
                _celtic_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_celtic_tree", _celtic_chart, btn_key="celtic_tree"
                ),
                lang=get_lang(),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_celtic_tree"))


def render_tab_khmer() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_khmer"
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
            _khmer_gender = "male" if _g in ("male", "男", "M") else "female"
            _age = _p.get("age", 2026 - _p.get("year", 1995))
            with st.spinner(t("spinner_khmer") if hasattr(t, "spinner_khmer") else "計算高棉占星盤..."):
                from astro.khmer import ReamkerAstrology, render_khmer_chart
                astro = ReamkerAstrology()
                _khmer_chart = astro.full_reading(
                    birth_year=_p.get("year", 1995),
                    gender=_khmer_gender,
                    current_age=_age,
                    language=st.session_state.get("lang", "zh")
                )
            # Render chart via components.v1.html for full CSS/flexbox support
            _khmer_lang = st.session_state.get("lang", "zh")
            _khmer_html = render_khmer_chart(_khmer_chart, language=_khmer_lang)
            _render_interactive_html(
                html=f'<div style="width:100%;font-family:\'Noto Sans\',\'Khmer OS\',Arial,sans-serif">{_khmer_html}</div>',
                height=1050,
                key="khmer-main-svg",
            )
            # AI interpretation button
            _render_ai_button("tab_khmer", _khmer_chart, btn_key="khmer")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_khmer") if hasattr(t, "desc_khmer") else "🇰🇭 **高棉占星** — 基於 François Bizot 2013 年論文與 Prochom Horasastra，重建吳哥時期失傳的 Reamker 占星系統。")


def render_tab_tojeong() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_tojeong"
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
            _tojeong_gender = "male" if _g in ("male", "男", "M") else "female"
            # compute_tojeong_chart only accepts: year, month, day, hour, gender, solar_term
            _tojeong_params = {k: v for k, v in _p.items() if k in ("year", "month", "day", "hour")}
            with st.spinner(t("spinner_tojeong") if hasattr(t, "spinner_tojeong") else "計算土亭數..."):
                from astro.tojeong import compute_tojeong_chart, render_tojeong_chart
                _tojeong_chart = compute_tojeong_chart(**_tojeong_params, gender=_tojeong_gender)
            render_tojeong_chart(
                _tojeong_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_tojeong", _tojeong_chart, btn_key="tojeong"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.markdown("""
        <div style="
    background:linear-gradient(135deg,#0f1e35 0%,#1a0d28 100%);
    border:1px solid rgba(201,168,76,0.35);
    border-radius:16px;
    padding:28px 24px 24px 24px;
    margin-bottom:20px;
    text-align:center;
        ">
          <div role="img" aria-label="韓國國旗" style="font-size:52px;margin-bottom:10px;">🇰🇷</div>
          <div style="font-size:22px;font-weight:700;color:#C9A84C;letter-spacing:2px;margin-bottom:8px;">
    土亭數命盤
          </div>
          <div style="font-size:13px;color:#8888aa;line-height:1.7;max-width:380px;margin:0 auto 18px auto;">
    朝鮮時代土亭李先生所創的占數系統<br>
    以先天數、後天數計算格局代碼<br>
    查 129 格局斷語推斷吉凶
          </div>
          <div style="
    display:inline-block;
    background:rgba(205,46,58,0.15);
    border:1px solid rgba(205,46,58,0.4);
    border-radius:8px;
    padding:8px 20px;
    font-size:13px;
    color:#f87171;
          ">👈 請在左側填寫出生年月日時，即可起盤</div>
        </div>""", unsafe_allow_html=True)


def render_tab_tibetan() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_tibetan"
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
            with st.spinner(t("spinner_tibetan")):
                _tib_chart = compute_tibetan_chart(**_p, gender=_g)
            _t_tab_mandala, _t_tab_natal, _t_tab_mewa, _t_tab_forces, _t_tab_planets = st.tabs([
                t("tibetan_subtab_mandala"),
                t("tibetan_subtab_natal"),
                t("tibetan_subtab_mewa"),
                t("tibetan_subtab_forces"),
                t("tibetan_subtab_planets"),
            ])
            with _t_tab_mandala:
                _tib_svg = build_kalachakra_mandala_svg(
                    _tib_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_tib_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center;color:#888;font-size:11px;">'
                    'Kalachakra Mandala · 時輪金剛曼荼羅 · '
                    'Outer: 12 Animals · Middle: 8 Parkha · Inner: 9 Mewa'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_mandala")
            with _t_tab_natal:
                render_tibetan_chart(_tib_chart, after_chart_hook=lambda: _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_natal"))
            with _t_tab_mewa:
                from astro.tibetan import _render_mewa_parkha
                _render_mewa_parkha(_tib_chart)
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_mewa")
            with _t_tab_forces:
                from astro.tibetan import _render_five_forces
                _render_five_forces(_tib_chart)
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_forces")
            with _t_tab_planets:
                from astro.tibetan import _render_planets
                _render_planets(_tib_chart)
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_planets")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_tibetan"))


def render_tab_zurkhai() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_zurkhai"
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
            with st.spinner(t("spinner_zurkhai")):
                zk_chart = compute_zurkhai_chart(**_p)
            render_zurkhai_chart(zk_chart, after_chart_hook=lambda: _render_ai_button("tab_zurkhai", zk_chart, btn_key="zurkhai"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_zurkhai"))


def render_tab_polynesian() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_polynesian"
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
            with st.spinner(t("spinner_polynesian")):
                _poly_result = compute_polynesian_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    lat=_p.get("latitude", 21.3),
                    lon=_p.get("longitude", -157.8),
                    timezone_offset=_p.get("timezone", 0.0),
                    location_name=_p.get("location_name", ""),
                )
            render_polynesian_chart_ui(_poly_result)
            _render_ai_button("tab_polynesian", _poly_result, btn_key="polynesian")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_polynesian"))


def render_tab_wariga() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_wariga"
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
            with st.spinner(t("spinner_wariga")):
                _wariga_result = compute_wariga(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    lat=_p["latitude"], lon=_p["longitude"],
                )
            render_wariga_chart(_wariga_result)
            _render_ai_button("tab_wariga", _wariga_result, btn_key="wariga")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_wariga"))


def render_tab_jawa_weton() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_jawa_weton"
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
            with st.spinner(t("spinner_jawa_weton")):
                _jawa_result = compute_weton(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    location_name=_p.get("location_name", ""),
                    timezone=_p.get("timezone", 7.0),
                )
            render_jawa_weton_chart(_jawa_result)
            _render_ai_button("tab_jawa_weton", _jawa_result, btn_key="jawa_weton")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_jawa_weton"))


def render_tab_bintang_duabelas() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_bintang_duabelas"
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
        _default_birth_datetime = None
        if _is_calculated:
            _p = st.session_state["_calc_params"]
            _default_birth_datetime = datetime(
                _p["year"],
                _p["month"],
                _p["day"],
                _p["hour"],
                _p["minute"],
            )
        st.info(t("info_bintang_duabelas_prompt"))
        with st.spinner(t("spinner_bintang_duabelas")):
            render_bintang_duabelas_chart(_default_birth_datetime)
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_malay_nujum() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    try:
        _default_birth_datetime = None
        if _is_calculated:
            _p = st.session_state["_calc_params"]
            _default_birth_datetime = datetime(
                _p["year"],
                _p["month"],
                _p["day"],
                _p["hour"],
                _p["minute"],
            )
        st.info(t("info_malay_nujum_prompt"))
        with st.spinner(t("spinner_malay_nujum")):
            render_malay_nujum_chart(_default_birth_datetime)
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_kinketika() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_kinketika"
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
        _default_birth_datetime = None
        if _is_calculated:
            _p = st.session_state["_calc_params"]
            _default_birth_datetime = datetime(
                _p["year"],
                _p["month"],
                _p["day"],
                _p["hour"],
                _p["minute"],
            )
        st.info(t("info_kinketika_prompt"))
        with st.spinner(t("spinner_kinketika")):
            _kinketika_report = render_kinketika_chart(_default_birth_datetime)
        _render_ai_button("tab_kinketika", _kinketika_report, btn_key="kinketika")
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_liuyao_lifetime() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_liuyao_lifetime"
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
            with st.spinner(t("spinner_liuyao_lifetime")):
                _liuyao_result = compute_lifetime_hexagram(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    location_name=_p.get("location_name", ""),
                )
            render_liuyao_lifetime_chart(_liuyao_result)
            _render_ai_button("tab_liuyao_lifetime", _liuyao_result, btn_key="liuyao_lifetime")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_liuyao_lifetime"))


def render_tab_byzantine_astrology() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_byzantine_astrology"
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
            render_byzantine_astrology_chart(
                year=_p["year"],
                month=_p["month"],
                day=_p["day"],
                hour=_p["hour"],
                minute=_p.get("minute", 0),
                timezone=_p.get("timezone", 0.0),
                latitude=_p.get("latitude", 41.016),
                longitude=_p.get("longitude", 28.977),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_byzantine_astrology_prompt"))
        st.markdown(t("desc_byzantine_astrology"))
