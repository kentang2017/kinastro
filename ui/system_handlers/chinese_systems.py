"""Auto-extracted system handlers from app.py."""

from __future__ import annotations

from datetime import date, time as time_cls

import streamlit as st

from ui.ai_chat import set_ai_context
from ui.helpers import t
from core.cached_computations import (
    build_tieban_svg_cached,
    compute_dasha_cached,
    compute_shensha_cached,
    compute_taixuan_natal_cached,
    compute_tieban_result_cached,
    compute_transit_cached,
    compute_transit_now_cached,
    compute_zhangguo_cached,
    get_or_compute_chart,
    get_swe,
    get_wanhua_tool,
    _birth_sig,
)

_LEGACY_NAMES = ('_system_cache_key', 'auto_cn', 'build_twelve_ci_svg', 'compute_bazi_chart', 'compute_damo_chart', 'compute_diqiyijue_chart', 'compute_liuren_chart', 'compute_lunming', 'compute_twelve_ci_chart', 'compute_wuyunliuqi', 'datetime', 'ganzhi', 'get_lang', 'get_qizheng_dasha_reading', 'render_aspect_summary', 'render_bazi', 'render_bazi_chart', 'render_beiji_chart', 'render_cetian_ziwei_chart', 'render_chart_info', 'render_chunzi_chart', 'render_damo_chart', 'render_dasha', 'render_diqiyijue_chart', 'render_electional_tool', 'render_financial_tab', 'render_full_chart', 'render_house_table', 'render_kaiyuan_chart', 'render_liuren_chart', 'render_lunming_report', 'render_mansion_text_panel', 'render_ming_gong_interpretations', 'render_nanji_chart', 'render_planet_table', 'render_qigua_ui', 'render_shensha', 'render_taixuan_chart', 'render_taixuan_intro', 'render_transit_comparison', 'render_twelve_ci_chart', 'render_wuyunliuqi_chart', 'render_wuyunliuqi_intro', 'render_zhangguo')

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


def render_tab_chinese() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_chinese"
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
            with st.spinner(t("spinner_chinese")):
                chart = get_or_compute_chart(
                    "tab_chinese",
                    _p,
                    {"gender": _g, "location_name": _p.get("location_name", "")},
                )

            # 子 tabs for the Chinese chart
            _ch_tab_natal, _ch_tab_shensha, _ch_tab_dasha, _ch_tab_transit, _ch_tab_zhangguo, _ch_tab_elect, _ch_tab_financial, _ch_tab_mansion = st.tabs([
                t("ch_subtab_natal"),
                t("ch_subtab_shensha"),
                t("ch_subtab_dasha"),
                t("ch_subtab_transit"),
                t("ch_subtab_zhangguo"),
                t("ch_subtab_electional"),
                t("ch_subtab_financial"),
                t("ch_subtab_mansion"),
            ])

            with _ch_tab_natal:
                # 計算流時盤 for overlay
                _transit_now = compute_transit_now_cached(timezone=input_tz)

                # 選擇是否顯示流時對盤
                _show_transit_overlay = st.checkbox(
                    t("show_transit_overlay"), value=False,
                )
                _transit_for_ring = _transit_now if _show_transit_overlay else None

                # Full chart: circle + info panel side by side
                render_full_chart(chart, transit=_transit_for_ring)
                _render_ai_button("tab_chinese", chart, btn_key="chinese")
                st.divider()
                render_chart_info(chart)
                st.divider()
                render_bazi(chart)
                st.divider()
                render_planet_table(chart)
                st.divider()
                render_house_table(chart)
                st.divider()
                render_aspect_summary(chart)
                st.divider()
                render_ming_gong_interpretations(chart)

            with _ch_tab_shensha:
                _shensha = compute_shensha_cached(
                    _system_cache_key("tab_chinese", _p, {"gender": _g}),
                    year=chart.year,
                    solar_month=chart.solar_month,
                    julian_day=chart.julian_day,
                    hour_branch=chart.hour_branch,
                    timezone=chart.timezone,
                    ming_gong_branch=chart.ming_gong_branch,
                )
                render_shensha(chart, _shensha)

            with _ch_tab_dasha:
                from datetime import datetime as _dt
                _current_year = _dt.now().year
                _dasha = compute_dasha_cached(
                    _system_cache_key("tab_chinese", _p, {"gender": _g}),
                    birth_year=chart.year,
                    ming_gong_branch=chart.ming_gong_branch,
                    gender=_g,
                    houses=chart.houses,
                    current_year=_current_year,
                )
                render_dasha(chart, _dasha)
                # Dasha interpretation
                if _dasha.current_period_idx >= 0:
                    _cur_period = _dasha.periods[_dasha.current_period_idx]
                    _reading = get_qizheng_dasha_reading(_cur_period.lord, get_lang())
                    if _reading:
                        st.divider()
                        st.subheader(t("dasha_reading_header"))
                        st.info(f"**{_cur_period.lord}** — {_reading}")

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

                _transit_custom = compute_transit_cached(
                    year=_t_date.year, month=_t_date.month, day=_t_date.day,
                    hour=_t_time.hour, minute=_t_time.minute,
                    timezone=_t_tz,
                )
                render_transit_comparison(chart, _transit_custom)

            with _ch_tab_zhangguo:
                _zhangguo = compute_zhangguo_cached(
                    _system_cache_key("tab_chinese", _p, {"gender": _g}),
                    planets=chart.planets,
                    houses=chart.houses,
                    gender=_g,
                )
                render_zhangguo(chart, _zhangguo)

            with _ch_tab_elect:
                render_electional_tool(timezone=input_tz)

            with _ch_tab_financial:
                render_financial_tab(
                    chart=chart,
                    params=_p,
                    input_tz=input_tz,
                )

            with _ch_tab_mansion:
                render_mansion_text_panel(chart)

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_chinese"))


def render_tab_cetian_ziwei() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_cetian_ziwei"
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
            _gender = st.session_state.get("_calc_gender", "男")
            with st.spinner(t("spinner_cetian_ziwei")):
                ct_chart = get_or_compute_chart(
                    "tab_cetian_ziwei",
                    _p,
                    {"gender": _gender, "location_name": _p.get("location_name", "")},
                )
            render_cetian_ziwei_chart(ct_chart, after_chart_hook=lambda: _render_ai_button("tab_cetian_ziwei", ct_chart, btn_key="cetian_ziwei"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_cetian_ziwei"))


def render_tab_tieban() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_tieban"
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
    _tb_tab_main, _tb_tab_tiaowen, _tb_tab_kunji = st.tabs([
        auto_cn("🔮 命盤"), auto_cn("📚 完整條文庫"), auto_cn("🔑 坤集扣入法"),
    ])
    with _tb_tab_main:
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_tieban") if hasattr(t, "spinner_tieban") else "計算鐵板神數..."):
                    tb_result = compute_tieban_result_cached(
                        _birth_sig(_p),
                        st.session_state.get("_calc_gender", "男"),
                    )
            
                # ── 鐵板神數主界面（先圖後字，手機優先）──────────────
                # ① 圖：SVG 星盤（響應式，已用 components.v1.html 渲染）
                svg_chart = build_tieban_svg_cached(
                    _birth_sig(_p),
                    st.session_state.get("_calc_gender", "男"),
                    get_lang(),
                )
                _render_interactive_html(
                    html=svg_chart,
                    height=760,
                    key="tieban-main-svg",
                )

                # ② 核心數字卡片（HTML，手機單列）
                _tb_lang = get_lang()
                _tb_num_label   = "神數號碼"   if _tb_lang != "en" else "Divine Number"
                _tb_ke_label    = "刻"         if _tb_lang != "en" else "Ke"
                _tb_fen_label   = "分"         if _tb_lang != "en" else "Fen"
                _tb_helo_label  = "河洛數"     if _tb_lang != "en" else "He Luo"
                _tb_ming_label  = "命宮"       if _tb_lang != "en" else "Life Palace"
                _tb_shen_label  = "身宮"       if _tb_lang != "en" else "Body Palace"
                _tb_wx_label    = "五行局"     if _tb_lang != "en" else "Element Cycle"
                _tb_code_label  = "密碼"       if _tb_lang != "en" else "Secret Code"
                st.markdown(f"""
    <div style="
        display:flex;flex-wrap:wrap;gap:8px;
        margin:0 0 16px 0;
    ">
      <div style="flex:1 1 140px;min-width:140px;
          background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.4);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_num_label}</div>
        <div style="font-size:26px;font-weight:700;color:#FF6B35;letter-spacing:3px;">{tb_result.tieban_number}</div>
      </div>
      <div style="flex:1 1 80px;min-width:80px;
          background:rgba(255,217,61,0.08);border:1px solid rgba(255,217,61,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_ke_label}</div>
        <div style="font-size:22px;font-weight:700;color:#FFD93D;">{tb_result.ke}</div>
      </div>
      <div style="flex:1 1 80px;min-width:80px;
          background:rgba(255,217,61,0.08);border:1px solid rgba(255,217,61,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_fen_label}</div>
        <div style="font-size:22px;font-weight:700;color:#FFD93D;">{tb_result.fen}</div>
      </div>
      <div style="flex:1 1 80px;min-width:80px;
          background:rgba(107,203,119,0.08);border:1px solid rgba(107,203,119,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_helo_label}</div>
        <div style="font-size:22px;font-weight:700;color:#6BCB77;">{tb_result.he_luo_number}</div>
      </div>
      <div style="flex:1 1 100px;min-width:100px;
          background:rgba(107,203,119,0.08);border:1px solid rgba(107,203,119,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_ming_label}</div>
        <div style="font-size:18px;font-weight:700;color:#6BCB77;">{tb_result.ming_palace}</div>
      </div>
      <div style="flex:1 1 100px;min-width:100px;
          background:rgba(107,203,119,0.08);border:1px solid rgba(107,203,119,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_shen_label}</div>
        <div style="font-size:18px;font-weight:700;color:#6BCB77;">{tb_result.shen_palace}</div>
      </div>
      <div style="flex:1 1 100px;min-width:100px;
          background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_wx_label}</div>
        <div style="font-size:15px;font-weight:700;color:#C9A84C;">{tb_result.wuxing_ju}</div>
      </div>
      <div style="flex:1 1 100px;min-width:100px;
          background:rgba(233,69,96,0.08);border:1px solid rgba(233,69,96,0.25);
          border-radius:12px;padding:12px 14px;text-align:center;">
        <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_code_label}</div>
        <div style="font-size:15px;font-weight:700;color:#E94560;">{tb_result.secret_code}</div>
      </div>
    </div>""", unsafe_allow_html=True)

                # ③ 字：坤集條文（tiaowen_full_12000.json 主條文）
                st.divider()
                _tb_kunji_title = auto_cn("🔑 坤集條文")
                st.subheader(_tb_kunji_title)

                # 坤集扣入法天干序列 + 條文編號
                if tb_result.kunji_tiangan:
                    _tg_str = "　".join(tb_result.kunji_tiangan)
                    _tiaowen_num_label = auto_cn("坤集編號") + f" {tb_result.tiaowen_number}"
                    _ke_lbl = tb_result.ke_label or str(tb_result.ke)
                    st.markdown(
                        f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;">'
                        f'<span style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FF9966;">'
                        f'#{_tiaowen_num_label}</span>'
                        f'<span style="background:rgba(255,217,61,0.10);border:1px solid rgba(255,217,61,0.3);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FFD93D;">'
                        f'{auto_cn("扣入天干")}：{_tg_str}</span>'
                        f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.25);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">'
                        f'{auto_cn("刻")}：{_ke_lbl}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # 坤集主條文（tiaowen_full_12000.json）
                _tw = tb_result.tiaowen_data
                if _tw and _tw.get("text"):
                    st.markdown(
                        f'<div style="background:rgba(255,107,53,0.08);border-left:4px solid #FF6B35;'
                        f'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                        f'color:#f0d9c8;line-height:1.9;letter-spacing:0.5px;">'
                        f'{_tw["text"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if _tw.get("note") and _tw["note"].strip() not in ("", "0 0"):
                        st.caption(auto_cn(f"備注：{_tw['note']}"))
                else:
                    # 如坤集無此條，退而顯示 verses.json 條文
                    st.info(tb_result.verse)

                # 算盤打數條文（suanpan_tiaowen_full.json）
                st.divider()
                st.subheader(auto_cn("🧮 算盤打數條文"))
                st.caption(auto_cn("曹展碩實務版 · 金鎖銀匙歌 · 算盤打數五部條文"))
                from astro.tieban.suanpan_full_structure import (
                    suanpan_calculate,
                    SuanpanTiaowenDatabase,
                )
                _sp_calc = suanpan_calculate(
                    year_gz=str(ganzhi["year"]),
                    month_gz=str(ganzhi["month"]),
                    day_gz=str(ganzhi["day"]),
                    hour_gz=str(ganzhi["hour"]),
                    gender=st.session_state.get("_calc_gender", "男"),
                )
                _sp_db = SuanpanTiaowenDatabase()
                _sp_tiaowen = _sp_db.get_by_result(_sp_calc)

                # 基本定部資訊卡
                _sp_nayin_label = auto_cn("納音")
                _sp_dept_label  = auto_cn("五行部")
                _sp_num_label   = auto_cn("算盤總數")
                _sp_key_label   = auto_cn("條文鍵")
                st.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">'
                    f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.3);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">'
                    f'{_sp_nayin_label}：{_sp_calc.nayin or "未知"}</span>'
                    f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.3);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">'
                    f'{_sp_dept_label}：{_sp_calc.department or "未知"}部</span>'
                    f'<span style="background:rgba(255,217,61,0.10);border:1px solid rgba(255,217,61,0.3);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FFD93D;">'
                    f'{_sp_num_label}：{_sp_calc.total_number}</span>'
                    f'<span style="background:rgba(255,107,53,0.10);border:1px solid rgba(255,107,53,0.3);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FF9966;">'
                    f'{_sp_key_label}：{_sp_calc.tiaowen_key}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # 算盤打數條文內文
                if _sp_tiaowen and _sp_tiaowen.get("text"):
                    _sp_raw = _sp_tiaowen.get("raw_key", "")
                    _sp_raw_badge = (
                        f'<span style="font-size:11px;color:#9090b0;margin-left:8px;">'
                        f'（{_sp_raw}）</span>'
                    ) if _sp_raw else ""
                    st.markdown(
                        f'<div style="background:rgba(107,203,119,0.06);border-left:4px solid #6BCB77;'
                        f'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                        f'color:#d4f0d8;line-height:1.9;letter-spacing:0.5px;">'
                        f'{_sp_tiaowen["text"]}{_sp_raw_badge}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info(auto_cn(f"（算盤打數條文鍵 {_sp_calc.tiaowen_key} 暫無資料）"))

                # 歲運條文（流年歲運）
                _sp_suiyun = _sp_db.get_suiyun_by_result(_sp_calc)
                if _sp_suiyun and _sp_suiyun.get("text"):
                    st.markdown(f"**{auto_cn('🌀 歲運條文')}**")
                    _sp_sy_raw = _sp_suiyun.get("raw_key", "")
                    _sp_sy_raw_badge = (
                        f'<span style="font-size:11px;color:#9090b0;margin-left:8px;">'
                        f'（{_sp_sy_raw}）</span>'
                    ) if _sp_sy_raw else ""
                    st.markdown(
                        f'<div style="background:rgba(201,168,76,0.06);border-left:4px solid #C9A84C;'
                        f'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                        f'color:#f0e8c0;line-height:1.9;letter-spacing:0.5px;">'
                        f'{_sp_suiyun["text"]}{_sp_sy_raw_badge}</div>',
                        unsafe_allow_html=True,
                    )

                # 計算步驟展開
                with st.expander(auto_cn("查看算盤打數計算步驟"), expanded=False):
                    for _step in _sp_calc.calculation_steps:
                        st.markdown(f"- {_step}")

                # 九十六刻表 & 六親刻分圖查詢結果
                _bake = tb_result.bake_fuqin_info
                _six = tb_result.six_qin_qizi_info
                if _bake or _six:
                    st.divider()
                    st.markdown(f"**{auto_cn('⏰ 刻分六親')}**")
                    _kf_cards = ""
                    if _bake:
                        _kf_cards += (
                            f'<div style="border-left:3px solid rgba(255,217,61,0.5);'
                            f'padding:8px 12px;margin-bottom:8px;'
                            f'background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">'
                            f'<div style="font-size:11px;color:#9090b0;margin-bottom:2px;">'
                            f'{auto_cn("父母兄弟（九十六刻）")}</div>'
                            f'<div style="font-size:13px;color:#FFD93D;">{_bake}</div></div>'
                        )
                    if _six:
                        _kf_cards += (
                            f'<div style="border-left:3px solid rgba(107,203,119,0.5);'
                            f'padding:8px 12px;margin-bottom:8px;'
                            f'background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">'
                            f'<div style="font-size:11px;color:#9090b0;margin-bottom:2px;">'
                            f'{auto_cn("妻子（六親刻分）")}</div>'
                            f'<div style="font-size:13px;color:#6BCB77;">{_six}</div></div>'
                        )
                    st.markdown(f'<div style="width:100%;">{_kf_cards}</div>', unsafe_allow_html=True)

                # 十二宮條文詳情
                st.divider()
                st.markdown("**🏛️ " + (t("tieban_palace_verses") if hasattr(t, "tieban_palace_verses") else auto_cn("十二宮條文")) + "**")

                expander_label = t("tieban_view_palace_verses") if hasattr(t, "tieban_view_palace_verses") else auto_cn("查看十二宮詳細條文")
                with st.expander(expander_label, expanded=False):
                    palace_order = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
                                   "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"]
                    palace_names_en = {
                        "命宮": "Life", "兄弟宮": "Siblings", "夫妻宮": "Spouse",
                        "子女宮": "Children", "財帛宮": "Wealth", "疾厄宮": "Health",
                        "遷移宮": "Travel", "交友宮": "Friends", "官祿宮": "Career",
                        "田宅宮": "Property", "福德宮": "Fortune", "父母宮": "Parents",
                    }
                    category_trans = {
                        "綜合": "General", "父母": "Parents", "兄弟": "Siblings",
                        "夫妻": "Spouse", "子女": "Children", "財運": "Wealth",
                        "事業": "Career", "健康": "Health", "災厄": "Disaster",
                        "遷移": "Travel",
                    }
                    # 手機友好：以 HTML 卡片列表代替三列
                    _palace_cards = ""
                    for palace_name in palace_order:
                        palace_info = tb_result.palace_verses.get(palace_name, {})
                        verse = palace_info.get("verse", t("no_verse") if hasattr(t, "no_verse") else auto_cn("暫無條文"))
                        category = palace_info.get("category", "")
                        branch = palace_info.get("branch", "")
                        display_name = palace_names_en.get(palace_name, palace_name) if get_lang() == "en" else palace_name
                        display_category = category_trans.get(category, category) if get_lang() == "en" else category
                        cat_badge = (
                            f'<span style="font-size:10px;color:#FF6B35;margin-left:6px;">'
                            f'【{display_category}】</span>'
                        ) if display_category else ""
                        _palace_cards += f"""
    <div style="border-left:3px solid rgba(255,107,53,0.5);
         padding:10px 12px;margin-bottom:10px;
         background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">
      <div style="font-size:13px;font-weight:700;color:#FFD93D;margin-bottom:4px;">
        {display_name}
        <span style="font-size:11px;color:#9090b0;font-weight:400;margin-left:4px;">({branch})</span>
        {cat_badge}
      </div>
      <div style="font-size:13px;color:#c8c8e8;line-height:1.6;">{verse}</div>
    </div>"""
                    st.markdown(f'<div style="width:100%;">{_palace_cards}</div>', unsafe_allow_html=True)

                # AI 分析按鈕
                _render_ai_button("tab_tieban", {"result": tb_result}, btn_key="tieban")

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            st.markdown("""
    <div style="
        background:linear-gradient(135deg,#1a0828 0%,#0f1e35 100%);
        border:1px solid rgba(255,107,53,0.35);
        border-radius:16px;
        padding:28px 24px 24px 24px;
        margin-bottom:20px;
        text-align:center;
    ">
      <div style="font-size:52px;margin-bottom:12px;">🔮</div>
      <div style="font-size:22px;font-weight:700;color:#FF6B35;letter-spacing:2px;margin-bottom:6px;">
        鐵板神數
      </div>
      <div style="font-size:12px;color:#9090b0;margin-bottom:14px;letter-spacing:1px;">
        Tie Ban Shen Shu &middot; Iron Plate Divine Numbers
      </div>
      <div style="font-size:13px;color:#8888aa;line-height:1.8;max-width:380px;margin:0 auto 18px auto;">
        源自宋代邵雍《皇極經世》，清代發展為精密考刻分系統<br>
        每時分 8 刻、每刻 15 分（共 120 分）<br>
        號稱「鐵口直斷」，中國傳統術數中最精密的查表法系統
      </div>
      <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:18px;">
        <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
             border-radius:8px;padding:7px 13px;font-size:12px;color:#FF9966;">
          📅 輸入出生年月日時
        </div>
        <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
             border-radius:8px;padding:7px 13px;font-size:12px;color:#FF9966;">
          ⚡ 一鍵推算神數
        </div>
        <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
             border-radius:8px;padding:7px 13px;font-size:12px;color:#FF9966;">
          📜 查閱十二宮條文
        </div>
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

    with _tb_tab_tiaowen:
        from astro.tieban.tieban_browser import (
            render_tiaowen_full_browser_inline,
            render_suanpan_tiaowen_browser_inline,
        )
        _tiaowen_db_choice = st.radio(
            auto_cn("條文庫"),
            [auto_cn("📚 坤集扣入法（12000 條）"), auto_cn("🧮 算盤打數五部條文")],
            horizontal=True,
            label_visibility="collapsed",
            key="tb_tiaowen_db_choice",
        )
        st.divider()
        if _tiaowen_db_choice == auto_cn("📚 坤集扣入法（12000 條）"):
            render_tiaowen_full_browser_inline()
        else:
            render_suanpan_tiaowen_browser_inline()

    with _tb_tab_kunji:
        from astro.tieban.kunji_full_structure import (
            KUNJI_TIANGAN_CODE, BAKE_96_KE, SIX_QIN_KE_FEN,
            kou_ru_fa, advanced_kou_ru_fa,
        )
        st.subheader("🔑 坤集密碼表")
        st.caption("天干扣入法核心：各天干對應數字，用於萬千百十條文編號解碼")
        _code_rows = [{"天干": k, "密碼數": v} for k, v in KUNJI_TIANGAN_CODE.items()]
        st.dataframe(_code_rows, width="stretch", hide_index=True)

        st.divider()
        st.subheader("🔢 扣入法查詢")
        _kunji_num = st.number_input(
            "輸入條文編號（1001–13000）",
            min_value=1001, max_value=13000, value=1001, step=1,
            key="kunji_num_input",
        )
        if st.button("解碼天干序列", key="kunji_decode_btn"):
            _seq = kou_ru_fa(int(_kunji_num))
            st.success(f"條文 {int(_kunji_num)} → 扣入天干序列：{'  '.join(_seq)}")
            _adv = advanced_kou_ru_fa(int(_kunji_num))
            st.info(f"基礎天干：{'  '.join(_adv['base_tiangan'])}")

        st.divider()
        st.subheader("⏰ 九十六刻天干數表")
        st.caption("各時辰（父母兄弟 / 妻子）刻分對應坤集天干")
        _ke_hour = st.selectbox(
            "選擇時辰",
            options=list(BAKE_96_KE.keys()),
            key="kunji_ke_hour",
        )
        _ke_data = BAKE_96_KE.get(_ke_hour, {})
        for _rel, _kes in _ke_data.items():
            st.markdown(f"**{_rel}**")
            _ke_rows = [{"刻/分": k, "天干結果": v} for k, v in _kes.items()]
            st.dataframe(_ke_rows, width="stretch", hide_index=True)

        st.divider()
        st.subheader("👨\u200d👩\u200d👧 六親刻分圖")
        st.caption("各時辰六親（父母兄弟 / 妻子）刻分對應")
        _qin_hour = st.selectbox(
            "選擇時辰",
            options=list(SIX_QIN_KE_FEN.keys()),
            key="kunji_qin_hour",
        )
        _qin_data = SIX_QIN_KE_FEN.get(_qin_hour, {})
        for _rel, _fens in _qin_data.items():
            st.markdown(f"**{_rel}**")
            _qin_rows = [{"刻/分": k, "六親結果": v} for k, v in _fens.items()]
            st.dataframe(_qin_rows, width="stretch", hide_index=True)


def render_tab_shaozi() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_shaozi"
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
    _sz_tab_main, _sz_tab_64keys, _sz_tab_tiaowen = st.tabs([
        auto_cn("🔯 命盤"), auto_cn("🗝️ 64鑰匙"), auto_cn("📚 條文庫"),
    ])
    with _sz_tab_main:
        if _is_calculated:
            try:
                from astro.shaozi import ShaoziShenShu, ShaoziBirthData
                from ui.handlers.tab_shaozi.render import render_shaozi_result

                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_shaozi")):
                    _sz_engine = ShaoziShenShu()
                    _sz_birth = ShaoziBirthData(
                        birth_dt=datetime(
                            _p["year"], _p["month"], _p["day"],
                            _p["hour"], _p.get("minute", 0),
                        ),
                        gender=st.session_state.get("_calc_gender", "男"),
                    )
                    _sz_result = _sz_engine.calculate(_sz_birth)

                render_shaozi_result(_sz_result)
                _render_ai_button(
                    "tab_shaozi",
                    {
                        "tiaowen_id": _sz_result.tiaowen_id,
                        "gua": _sz_result.gua_name,
                        "tiaowen": _sz_result.tiaowen_text,
                        "year_gz": _sz_result.year_gz,
                        "day_gz": _sz_result.day_gz,
                    },
                    btn_key="shaozi",
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            from ui.handlers.tab_shaozi.render import render_shaozi_placeholder
            render_shaozi_placeholder()

    with _sz_tab_64keys:
        if _is_calculated:
            try:
                from astro.shaozi import ShaoziShenShu as _SzMain, ShaoziBirthData
                from astro.shaozi.shaozi_full_structure import ShaoziFullShenShu as _SzFull
                from ui.handlers.tab_shaozi.render import render_shaozi_64key_section

                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_shaozi")):
                    # 取得四柱干支（復用主盤計算結果或重新推算）
                    _sz_main_engine = _SzMain()
                    _sz_birth = ShaoziBirthData(
                        birth_dt=datetime(
                            _p["year"], _p["month"], _p["day"],
                            _p["hour"], _p.get("minute", 0),
                        ),
                        gender=st.session_state.get("_calc_gender", "男"),
                    )
                    _sz_base = _sz_main_engine.calculate(_sz_birth)

                    # 使用 shaozi_full_structure 進行64鑰匙起盤
                    _sz_full_engine = _SzFull()
                    _sz_full_result = _sz_full_engine.cast_plate(
                        year_gz=_sz_base.year_gz,
                        month_gz=_sz_base.month_gz,
                        day_gz=_sz_base.day_gz,
                        hour_gz=_sz_base.hour_gz,
                    )

                render_shaozi_64key_section(_sz_full_result)
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            from ui.handlers.tab_shaozi.render import render_shaozi_placeholder
            render_shaozi_placeholder()

    with _sz_tab_tiaowen:
        from ui.handlers.tab_shaozi.render import render_shaozi_tiaowen_browser
        render_shaozi_tiaowen_browser()


def render_tab_huangji() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_huangji"
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
            from astro.huangji import compute_huangji_pan, render_streamlit as render_huangji_chart

            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_huangji")):
                _huangji_chart = compute_huangji_pan(
                    **_p,
                    reference_year=datetime.now().year,
                    include_cross_system=True,
                    gender=st.session_state.get("_calc_gender", "男"),
                )
            render_huangji_chart(
                _huangji_chart,
                lang=get_lang(),
                after_chart_hook=lambda: _render_ai_button(
                    "tab_huangji",
                    _huangji_chart,
                    btn_key="huangji",
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_huangji"))


def render_tab_taixuan() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_taixuan"
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
    # 子頁籤：本命排盤 / 即時問卜
    _tx_natal_label = t("taixuan_natal_tab")
    _tx_qigua_label = t("taixuan_qigua_tab")
    _tx_tab_natal, _tx_tab_qigua = st.tabs([_tx_natal_label, _tx_qigua_label])

    with _tx_tab_natal:
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_taixuan")):
                    _tx_result = compute_taixuan_natal_cached(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                    )
                render_taixuan_chart(
                    _tx_result,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_taixuan",
                        {
                            "shou_name": _tx_result.shou.name,
                            "gua_title": _tx_result.shou.gua_title,
                            "gua_text": _tx_result.shou.gua_text,
                            "zhan_name": _tx_result.shou.zhan_name,
                            "zhan_text": _tx_result.shou.zhan_text,
                            "year_gz": _tx_result.year_gz,
                            "day_gz": _tx_result.day_gz,
                            "sishi": _tx_result.sishi,
                            "mansion": _tx_result.shou.mansion,
                            "planet": _tx_result.shou.planet,
                        },
                        btn_key="taixuan_natal",
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            render_taixuan_intro()

    with _tx_tab_qigua:
        render_qigua_ui(
            after_chart_hook=lambda: _render_ai_button(
                "tab_taixuan",
                {"mode": "qigua"},
                btn_key="taixuan_qigua",
            )
        )


def render_tab_wuyunliuqi() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_wuyunliuqi"
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
            with st.spinner(t("spinner_wuyunliuqi")):
                _wylq_result = compute_wuyunliuqi(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p.get("minute", 0),
                )
            render_wuyunliuqi_chart(_wylq_result)
            _render_ai_button("tab_wuyunliuqi", {
                "ganzhi": _wylq_result.ganzhi,
                "dayun": _wylq_result.dayun.taishao,
                "sitian": _wylq_result.sitian,
                "zaiquan": _wylq_result.zaiquan,
                "tonghua": _wylq_result.tonghua.categories,
            }, btn_key="wuyunliuqi")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        render_wuyunliuqi_intro()
        st.markdown(t("desc_wuyunliuqi"))


def render_tab_damo() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_damo"
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
            _damo_params = dict(_p)
            _damo_params["gender"] = gender
            with st.spinner(t("spinner_damo")):
                _damo_chart = compute_damo_chart(**_damo_params)
            render_damo_chart(
                _damo_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_damo", _damo_chart, btn_key="damo"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_damo"))


def render_tab_diqiyijue() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_diqiyijue"
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
            _diqiyijue_params = dict(_p)
            _diqiyijue_params["gender"] = gender
            with st.spinner(t("spinner_diqiyijue")):
                _diqiyijue_chart = compute_diqiyijue_chart(**_diqiyijue_params)
            render_diqiyijue_chart(
                _diqiyijue_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_diqiyijue", _diqiyijue_chart, btn_key="diqiyijue"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_diqiyijue_prompt"))
        st.markdown(t("desc_diqiyijue"))


def render_tab_twelve_ci() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_twelve_ci"
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
            with st.spinner(t("spinner_twelve_ci")):
                _ci_chart = compute_twelve_ci_chart(**_p)

            _ci_tab_wheel, _ci_tab_detail = st.tabs([
                t("twelve_ci_subtab_chart"),
                t("twelve_ci_subtab_detail"),
            ])

            with _ci_tab_wheel:
                _ci_svg = build_twelve_ci_svg(
                    _ci_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_ci_svg, unsafe_allow_html=True)
                _render_ai_button("tab_twelve_ci", _ci_chart, btn_key="twelve_ci")

            with _ci_tab_detail:
                render_twelve_ci_chart(
                    _ci_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_twelve_ci", _ci_chart, btn_key="twelve_ci_detail"
                    ),
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_twelve_ci"))


def render_tab_chinstar() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_chinstar"
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
    # ── Lunar date conversion (hidden) ──────────────────────────
    _chinstar_year = birth_date.year
    _chinstar_month = birth_date.month
    _chinstar_day = birth_date.day
    _chinstar_hour = birth_time.hour
    _auto_ok = False

    if _is_calculated:
        try:
            from astro.ziwei import _solar_to_lunar as _cs_solar_to_lunar
            _swe_cs = get_swe()
            _p = st.session_state["_calc_params"]
            _cs_jd = _swe_cs.julday(
                _p["year"], _p["month"], _p["day"],
                _p["hour"] + _p["minute"] / 60.0 - _p["timezone"],
            )
            _cs_ly, _cs_lm, _cs_ld, _cs_leap = _cs_solar_to_lunar(_cs_jd)
            _chinstar_year = _cs_ly
            _chinstar_month = _cs_lm
            _chinstar_day = _cs_ld
            _chinstar_hour = _p["hour"]
            _auto_ok = True
        except Exception:
            pass

    _cs_gender = "M" if gender == "male" else "F"

    if _auto_ok:
        try:
            with st.spinner(t("spinner_chinstar")):
                _cs_tool = get_wanhua_tool()
                _cs_chart = _cs_tool.build_chart(
                    year=int(_chinstar_year),
                    month=int(_chinstar_month),
                    day=int(_chinstar_day),
                    hour=int(_chinstar_hour),
                    gender=_cs_gender,
                )

            _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian = st.tabs([
                t("chinstar_subtab_chart"),
                t("chinstar_subtab_xiangtai"),
                t("chinstar_subtab_gui_jian"),
            ])

            with _cs_tab_chart:
                from astro.chinstar.chinstar import BRANCHES as _cs_branches, QIN_ELEMENT as _cs_qin_elem

                bi = _cs_chart["basic_info"]
                p = _cs_chart["palaces"]
                s = _cs_chart["stars"]
                pat = _cs_chart["pattern"]

                # ── 宮位→禽 映射 ──────────────────────────────
                _cs_palace_bird = {
                    "命宮":   s["ming_xing"],
                    "財帛宮": s["derived"].get("財帛星", ""),
                    "兄弟宮": s["derived"].get("兄弟星", ""),
                    "田宅宮": s["derived"].get("田宅星", ""),
                    "子女宮": s["derived"].get("子息星", ""),
                    "奴僕宮": s["derived"].get("奴僕星", ""),
                    "夫妻宮": s["derived"].get("妻妾星", ""),
                    "疾厄宮": s["derived"].get("疾厄星", ""),
                    "遷移宮": s["derived"].get("遷移星", ""),
                    "官祿宮": s["derived"].get("官祿星", ""),
                    "福德宮": s["derived"].get("福德星", ""),
                    "相貌宮": s["derived"].get("相貌星", ""),
                }
                # 地支→宮名（反查）
                _cs_branch_to_palace = {v: k for k, v in p["twelve"].items()}

                # 特殊宮位地支（命/身/胎）
                _cs_ming_br = p["ming_gong"]["branch"]
                _cs_shen_br = p["shen_gong"]["branch"]
                _cs_tai_br  = p["tai_gong"]["branch"]

                # 五行色彩 (dark theme)
                _cs_elem_bg = {
                    "木": "rgba(56,142,60,0.15)", "火": "rgba(198,40,40,0.15)",
                    "土": "rgba(245,127,23,0.15)", "金": "rgba(158,158,158,0.15)", "水": "rgba(21,101,192,0.15)",
                }
                _cs_elem_bd = {
                    "木": "rgba(56,142,60,0.4)", "火": "rgba(198,40,40,0.4)",
                    "土": "rgba(245,127,23,0.4)", "金": "rgba(158,158,158,0.4)", "水": "rgba(21,101,192,0.4)",
                }

                def _cs_cell(branch_char: str) -> str:
                    palace = _cs_branch_to_palace.get(branch_char, "")
                    bird   = _cs_palace_bird.get(palace, "")
                    elem   = _cs_qin_elem.get(bird, "")
                    bg     = _cs_elem_bg.get(elem, "rgba(30,27,75,0.4)")
                    bd     = _cs_elem_bd.get(elem, "rgba(167,139,250,0.3)")
                    badge  = ""
                    if branch_char == _cs_ming_br:
                        badge = '<span style="color:#ef4444;font-size:10px;">★命</span> '
                        bd    = "rgba(239,68,68,0.5)"
                        bg    = "rgba(239,68,68,0.1)"
                    elif branch_char == _cs_shen_br:
                        badge = '<span style="color:#a78bfa;font-size:10px;">☆身</span> '
                        bd    = "rgba(167,139,250,0.5)"
                        bg    = "rgba(167,139,250,0.1)"
                    elif branch_char == _cs_tai_br:
                        badge = '<span style="color:#facc15;font-size:10px;">◎胎</span> '
                        bd    = "rgba(250,204,21,0.5)"
                        bg    = "rgba(250,204,21,0.1)"
                    return (
                        f'<td style="width:25%;min-width:70px;height:88px;text-align:center;'
                        f'vertical-align:middle;border:2px solid {bd};'
                        f'background:{bg};padding:4px 2px;border-radius:8px;">'
                        f'<div style="font-size:11px;color:#b0b0d0;font-weight:bold;">'
                        f'{badge}{branch_char}宮</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;margin-top:2px;">{palace}</div>'
                        f'<div style="font-size:14px;color:#a78bfa;font-weight:bold;'
                        f'margin-top:3px;">{bird}</div>'
                        f'</td>'
                    )

                # 中央格（基本資料 + 三主星 + 格局）
                _cs_center_td = (
                    '<td colspan="2" rowspan="2" style="text-align:center;'
                    'vertical-align:middle;border:2px solid rgba(167,139,250,0.3);'
                    'background:rgba(30,27,75,0.6);padding:10px 8px;border-radius:8px;'
                    'line-height:1.6;">'
                    '<div style="font-size:15px;font-weight:bold;color:#a78bfa;'
                    'letter-spacing:2px;">萬化仙禽</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;margin-top:6px;">'
                    f'{bi["year"]}年{bi["month"]}月{bi["day"]}日 {bi["hour"]}時</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;">{bi["gender"]}命 {bi["day_night"]}</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;">{bi["season"]}季 · {bi["san_yuan"]}</div>'
                    '<hr style="margin:6px 0;border-color:rgba(167,139,250,0.2);">'
                    f'<div style="font-size:11px;color:#e0e0ff;"><b>胎星</b>：{s["tai_xing"]}</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;"><b>命星</b>：{s["ming_xing"]}</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;"><b>身星</b>：{s["shen_xing"]}</div>'
                    '<hr style="margin:6px 0;border-color:rgba(167,139,250,0.2);">'
                    f'<div style="font-size:11px;color:#e0e0ff;">'
                    f'<b>格局</b>：{pat["grade"]}</div>'
                    '</td>'
                )

                # 大六壬式四列排盤
                # Row 0: 巳(5)  午(6)  未(7)  申(8)
                # Row 1: 辰(4)  [CENTER]       酉(9)
                # Row 2: 卯(3)  [CENTER]       戌(10)
                # Row 3: 寅(2)  丑(1)  子(0)  亥(11)
                _cs_br = _cs_branches
                _cs_grid = (
                    '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
                    '<table style="border-collapse:separate;border-spacing:4px;'
                    'margin:10px auto;width:100%;table-layout:fixed;font-family:\'Noto Sans TC\',serif;">'
                    "<tr>"
                    + _cs_cell(_cs_br[5])  + _cs_cell(_cs_br[6])
                    + _cs_cell(_cs_br[7])  + _cs_cell(_cs_br[8])
                    + "</tr><tr>"
                    + _cs_cell(_cs_br[4])  + _cs_center_td + _cs_cell(_cs_br[9])
                    + "</tr><tr>"
                    + _cs_cell(_cs_br[3])  + _cs_cell(_cs_br[10])
                    + "</tr><tr>"
                    + _cs_cell(_cs_br[2])  + _cs_cell(_cs_br[1])
                    + _cs_cell(_cs_br[0])  + _cs_cell(_cs_br[11])
                    + "</tr></table></div>"
                )
                st.markdown(_cs_grid, unsafe_allow_html=True)
                _render_ai_button("tab_chinstar", _cs_chart, btn_key="chinstar")
                st.divider()

                # ── 吞啗分析 ──────────────────────────────
                st.markdown(t("chinstar_swallow_analysis_header"))
                _sw = _cs_chart["swallow_analysis"]
                if _sw:
                    _sw_rows = [{"對照": k, "判斷": v} for k, v in _sw.items()]
                    st.dataframe(_sw_rows, width='stretch', hide_index=True)
                else:
                    st.info(t("chinstar_no_swallow"))
                st.divider()

                # ── 情性賦 ──────────────────────────────
                st.markdown(t("chinstar_personality_header"))
                for _label, text in _cs_chart["personality"].items():
                    st.info(text)
                st.divider()

                # ── 格局 ──────────────────────────────
                st.markdown(t("chinstar_pattern_header").format(grade=pat["grade"]))
                st.write(pat["reason"])

                # ── 完整文字輸出（可複製） ──────────────────────
                with st.expander(t("chinstar_full_text_expander")):
                    st.code(_cs_tool.format_chart(_cs_chart), language="")

            with _cs_tab_xiangtai:
                from astro.chinstar.chinstar import lookup_xiangtai, _get_xiangtai_fu

                st.markdown(t("chinstar_xiangtai_title"))

                # 查找匹配的相胎賦
                _xt_match = lookup_xiangtai(s["ming_xing"], s["tai_xing"])
                if _xt_match:
                    st.markdown(t("chinstar_xiangtai_match").format(
                        zhu=s["ming_xing"], tai=s["tai_xing"],
                    ))
                    _xt_cols = st.columns(2)
                    with _xt_cols[0]:
                        st.metric(t("chinstar_xiangtai_xingpin"), _xt_match["xing_pin"])
                    with _xt_cols[1]:
                        st.metric(t("chinstar_xiangtai_xiji"), _xt_match["xi_ji"])
                    st.info(f'**{t("chinstar_xiangtai_desc")}**：{_xt_match["desc"]}')
                    st.success(f'**{t("chinstar_xiangtai_poem")}**：\n\n{_xt_match["poem"]}')
                else:
                    st.warning(t("chinstar_xiangtai_no_match"))

                st.divider()

                # 顯示相胎賦全覽
                with st.expander(t("chinstar_xiangtai_ref")):
                    _xt_all = _get_xiangtai_fu()
                    _xt_rows = []
                    for _xt_e in _xt_all:
                        _xt_rows.append({
                            "主星": _xt_e["zhu"],
                            "胎星": _xt_e["tai"],
                            "形品": _xt_e["xing_pin"],
                            "喜忌": _xt_e["xi_ji"],
                            "論斷": _xt_e["desc"][:50] + "…" if len(_xt_e["desc"]) > 50 else _xt_e["desc"],
                        })
                    st.dataframe(_xt_rows, width='stretch', hide_index=True)

            with _cs_tab_gui_jian:
                from astro.chinstar.chinstar import (
                    lookup_gui_ge, lookup_jian_ge,
                    lookup_fulu_patterns, lookup_pinjian_patterns,
                )

                # 取主要禽星（胎星、命星）
                _gj_stars = [s["tai_xing"], s["ming_xing"]]
                if s["shen_xing"] not in _gj_stars:
                    _gj_stars.append(s["shen_xing"])

                # ── 福祿上格 ──
                st.markdown(t("chinstar_fulu_title"))
                _fulu_found = False
                for _gj_star in _gj_stars:
                    _fl = lookup_fulu_patterns(_gj_star)
                    if _fl:
                        _fulu_found = True
                        for _fl_e in _fl:
                            st.success(f'**{_fl_e["name"]}**（{_fl_e["stars"]}）— {_fl_e["condition"]}')
                if not _fulu_found:
                    st.info("—")
                st.divider()

                # ── 貧賤下命 ──
                st.markdown(t("chinstar_pinjian_title"))
                _pj_found = False
                for _gj_star in _gj_stars:
                    _pj = lookup_pinjian_patterns(_gj_star)
                    if _pj:
                        _pj_found = True
                        for _pj_e in _pj:
                            st.error(f'**{_pj_e["name"]}**（{_pj_e["stars"]}）— {_pj_e["condition"]}')
                if not _pj_found:
                    st.info("—")
                st.divider()

                # ── 各星貴格 / 賤格 ──
                for _gj_star in _gj_stars:
                    st.markdown(t("chinstar_gui_for_star").format(star=_gj_star))
                    _gui = lookup_gui_ge(_gj_star)
                    if _gui:
                        _gui_rows = [{"格局": g["name"], "干支": g["ganzhi"]} for g in _gui]
                        st.dataframe(_gui_rows, width='stretch', hide_index=True)
                    else:
                        st.info(t("chinstar_no_gui"))

                    st.markdown(t("chinstar_jian_for_star").format(star=_gj_star))
                    _jian = lookup_jian_ge(_gj_star)
                    if _jian:
                        _jian_rows = [{"格局": j["name"], "干支": j["ganzhi"]} for j in _jian]
                        st.dataframe(_jian_rows, width='stretch', hide_index=True)
                    else:
                        st.info(t("chinstar_no_jian"))
                    st.divider()

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        # Manual input fallback or not calculated
        st.markdown(t("desc_chinstar"))
        if not _is_calculated:
            st.info(t("info_calc_prompt"))
        else:
            st.subheader(t("chinstar_lunar_input_header"))
            _cs_col1, _cs_col2, _cs_col3 = st.columns(3)
            with _cs_col1:
                _chinstar_year = st.number_input(
                    t("chinstar_lunar_year"), value=int(_chinstar_year),
                    min_value=1, max_value=2200, key="cs_year",
                )
            with _cs_col2:
                _chinstar_month = st.number_input(
                    t("chinstar_lunar_month"), value=int(_chinstar_month),
                    min_value=1, max_value=12, key="cs_month",
                )
            with _cs_col3:
                _chinstar_day = st.number_input(
                    t("chinstar_lunar_day"), value=int(_chinstar_day),
                    min_value=1, max_value=30, key="cs_day",
                )
            if st.button(t("calculate_btn"), key="chinstar_calc_btn"):
                try:
                    with st.spinner(t("spinner_chinstar")):
                        _cs_tool = get_wanhua_tool()
                        _cs_chart = _cs_tool.build_chart(
                            year=int(_chinstar_year),
                            month=int(_chinstar_month),
                            day=int(_chinstar_day),
                            hour=int(_chinstar_hour),
                            gender=_cs_gender,
                        )

                    _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian = st.tabs([
                        t("chinstar_subtab_chart"),
                        t("chinstar_subtab_xiangtai"),
                        t("chinstar_subtab_gui_jian"),
                    ])

                    with _cs_tab_chart:
                        from astro.chinstar.chinstar import BRANCHES as _cs_branches, QIN_ELEMENT as _cs_qin_elem
                        st.code(_cs_tool.format_chart(_cs_chart), language="")
                except Exception as _e:
                    st.error(f"{t('error_tab_compute')}：{_e}")
                    st.exception(_e)


def render_tab_liuren() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_liuren"
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
            with st.spinner(t("spinner_liuren")):
                _liuren_chart = compute_liuren_chart(**_p)
            # 從生年推算本命地支（年支）
            import sxtwl as _sxtwl_lr
            _lr_day = _sxtwl_lr.fromSolar(_p["year"], _p["month"], _p["day"])
            _lr_year_gz = _lr_day.getYearGZ()
            _lr_benming = list("子丑寅卯辰巳午未申酉戌亥")[_lr_year_gz.dz]
            render_liuren_chart(
                _liuren_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_liuren", _liuren_chart, btn_key="liuren"
                ),
                benming_zhi=_lr_benming,
            )
            # ── 論命分析 ──
            st.divider()
            # 本命與流年均取自排盤年份的年支
            _lunming_report = compute_lunming(
                _liuren_chart, _lr_benming, liunian_zhi=_lr_benming,
            )
            render_lunming_report(_lunming_report)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_liuren"))


def render_tab_fendjing() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_fendjing"
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
            with st.spinner(t("spinner_fendjing") if hasattr(t, "spinner_fendjing") else "計算鬼谷分定經..."):
                from astro.fendjing import compute_fendjing_chart, render_fendjing_chart
                _fendjing_chart = compute_fendjing_chart(**_p)
            render_fendjing_chart(
                _fendjing_chart,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_fendjing", _fendjing_chart, btn_key="fendjing"
                ),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_fendjing") if hasattr(t, "desc_fendjing") else "🔮 **鬼谷分定經** — 相傳為戰國時期鬼谷子所創，又名兩頭鉗，以出生年時天干排盤，配合十二宮與星曜，推斷一生命運的古典命理系統。")


def render_tab_bazi() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_bazi"
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
            with st.spinner(t("spinner_bazi")):
                _bazi_result = compute_bazi_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    gender=st.session_state.get("_calc_gender", "男"),
                    timezone=_p.get("timezone", 8.0),
                    latitude=_p.get("latitude", 25.033),
                    longitude=_p.get("longitude", 121.565),
                    location_name=_p.get("location_name", ""),
                )
            render_bazi_chart(_bazi_result)
            _render_ai_button("tab_bazi", _bazi_result, btn_key="bazi")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_bazi_prompt"))
        st.markdown(t("desc_bazi"))


def render_tab_chunzi() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_chunzi"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    try:
        with st.spinner(t("spinner_chunzi")):
            render_chunzi_chart()
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)


def render_tab_kaiyuan() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_kaiyuan"
    _p0 = st.session_state.get("_calc_params")
    _g = st.session_state.get("_calc_gender", "male")
    gender = _g
    try:
        with st.spinner(t("spinner_kaiyuan")):
            render_kaiyuan_chart()
    except Exception as _e:
        st.error(f"{t('error_tab_compute')}：{_e}")
        st.exception(_e)

        # ============================================================


def render_tab_beiji() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_beiji"
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
            with st.spinner(t("spinner_beiji")):
                render_beiji_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p["minute"],
                    gender=st.session_state.get("_calc_gender", "男"),
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_beiji_prompt"))
        st.markdown(t("desc_beiji"))


def render_tab_nanji() -> None:
    _bind_legacy()
    _is_calculated = st.session_state.get("_calculated", False)
    _cur_lang = st.session_state.get("lang", "zh")
    _selected_system = "tab_nanji"
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
            with st.spinner(t("spinner_nanji")):
                render_nanji_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p.get("minute", 0),
                    gender=st.session_state.get("_calc_gender", "男"),
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_nanji_prompt"))
        st.markdown(t("desc_nanji"))
