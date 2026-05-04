"""
五運六氣 Streamlit 渲染模組 (Wu Yun Liu Qi Renderer)

提供完整的 Streamlit UI：
1. 年度五運六氣排盤 — 大運、六步主客運氣、司天在泉
2. 當前時刻精細位置 — 所處步數與進度
3. 運氣同化分析 — 天符歲會等特殊年份判斷
4. 勝復鬱發 — 五行勝復與調護建議
5. 運氣變化曲線 — 任意時間段每分鐘運氣狀態

古法依據：《黃帝內經·素問》運氣七篇
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import streamlit as st

from .calculator import (
    WuYunLiuQiResult, CurrentQiPosition,
    WuYunLiuQiCalculator, compute_wuyunliuqi,
)
from .constants import (
    QI_ATTRIBUTES, YUN_ATTRIBUTES, HEALTH_ADVICE,
    TONG_HUA_DESC, YUFA, WUXING,
)


# ============================================================
# 色彩主題 — 仿古典中醫運氣圖風格
# ============================================================
_BG       = "#0A1628"    # 深藏青底色（夜天）
_CARD     = "#112240"    # 卡片背景
_BORDER   = "#C0933E"    # 金邊
_HEADER   = "#F5D06A"    # 金色標題
_TEXT     = "#D4C9A8"    # 米白主文字
_SUBTLE   = "#7A8BA0"    # 次要文字
_ACCENT   = "#E8A020"    # 強調橙金
_GREEN    = "#4CAF82"    # 順化綠
_RED      = "#E05050"    # 逆氣紅
_BLUE     = "#5BA8D8"    # 水氣藍
_YELLOW   = "#E8C840"    # 土氣黃
_GREY     = "#6A7585"    # 中性灰


# 五行配色
_WX_COLOR = {
    "木": "#4CAF82",  # 青綠
    "火": "#E05050",  # 赤紅
    "土": "#E8C840",  # 黃
    "金": "#C8C8C8",  # 白銀
    "水": "#5BA8D8",  # 藍
}

# 關係配色
_JIALIN_COLOR = {
    "同化": _GREEN,
    "順化": _GREEN,
    "小逆": _YELLOW,
    "不和": "#E8A020",
    "逆":   _RED,
    "一般": _GREY,
}


def _escape(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def _wx_badge(wuxing: str, extra_style: str = "") -> str:
    """回傳五行色彩標籤 HTML"""
    color = _WX_COLOR.get(wuxing, _GREY)
    return (
        f'<span style="background:{color}22; color:{color}; '
        f'border:1px solid {color}; border-radius:4px; '
        f'padding:2px 8px; font-size:0.85em; {extra_style}">'
        f'{_escape(wuxing)}</span>'
    )


def _qi_badge(qi_name: str, extra_style: str = "") -> str:
    """回傳氣名稱標籤 HTML"""
    attrs = QI_ATTRIBUTES.get(qi_name, {})
    symbol = attrs.get("symbol", "")
    nature = attrs.get("nature", "")
    return (
        f'<span style="color:{_ACCENT}; font-weight:bold; {extra_style}">'
        f'{symbol} {_escape(qi_name)}</span>'
        f' <small style="color:{_SUBTLE};">({_escape(nature)})</small>'
    )


# ============================================================
# 主入口點
# ============================================================

def render_streamlit(result: WuYunLiuQiResult) -> None:
    """
    Streamlit 主渲染函數 — 五運六氣完整排盤

    參數：
        result (WuYunLiuQiResult): 計算結果
    """
    # ── 頂部標題橫幅 ──────────────────────────────────────────
    _render_header(result)

    # ── 頁籤 ──────────────────────────────────────────────────
    tab_overview, tab_wuyun, tab_liuqi, tab_jialin, tab_tonghua, tab_curve = st.tabs([
        "📋 年度概覽",
        "🌀 五運詳解",
        "🌊 六氣詳解",
        "⚖️ 客主加臨",
        "🔮 運氣同化",
        "📈 運氣曲線",
    ])

    with tab_overview:
        _render_overview(result)

    with tab_wuyun:
        _render_wuyun(result)

    with tab_liuqi:
        _render_liuqi(result)

    with tab_jialin:
        _render_jialin(result)

    with tab_tonghua:
        _render_tonghua(result)

    with tab_curve:
        _render_curve_ui(result)


# ============================================================
# 各頁籤渲染函數
# ============================================================

def _render_header(result: WuYunLiuQiResult) -> None:
    """頂部標題橫幅"""
    pos = result.current_position
    cur_info = ""
    if pos:
        cur_info = (
            f"<div style='font-size:0.9em; color:{_SUBTLE}; margin-top:6px;'>"
            f"當前：{_escape(pos.current_zhuqi.step_name)}·{_escape(pos.current_zhuqi.qi_name)}"
            f" ／ {_escape(pos.current_zhuyun.step_name)}·{_escape(pos.current_zhuyun.taishao)}"
            f"</div>"
        )

    tonghua_tags = "".join(
        f'<span style="background:{_ACCENT}33; color:{_ACCENT}; border:1px solid {_ACCENT}; '
        f'border-radius:4px; padding:2px 8px; font-size:0.8em; margin:0 3px;">{_escape(c)}</span>'
        for c in result.tonghua.categories
    )

    st.markdown(
        f"""
        <div style="
          background: linear-gradient(135deg, {_BG}, #0D2040);
          border: 2px solid {_BORDER};
          border-radius: 10px;
          padding: 22px 24px;
          text-align: center;
          margin-bottom: 16px;
        ">
          <div style="font-size:0.85em; color:{_SUBTLE}; letter-spacing:0.12em; margin-bottom:4px;">
            ☯ 黃帝內經·五運六氣推演 ☯
          </div>
          <div style="font-size:2.4em; font-weight:bold; color:{_HEADER}; letter-spacing:0.08em;">
            {_escape(result.ganzhi)}年 五運六氣
          </div>
          <div style="font-size:1.1em; color:{_TEXT}; margin-top:6px;">
            {_escape(result.yinyang)}年 ·
            大運：<strong style="color:{_WX_COLOR.get(result.dayun.wuxing, _ACCENT)}">{_escape(result.dayun.taishao)}</strong> ·
            司天：<strong style="color:{_ACCENT}">{_escape(result.sitian)}</strong> ·
            在泉：<strong style="color:{_BLUE}">{_escape(result.zaiquan)}</strong>
          </div>
          <div style="margin-top:8px;">{tonghua_tags}</div>
          {cur_info}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_overview(result: WuYunLiuQiResult) -> None:
    """年度概覽頁籤"""
    # 基本資訊
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("干支年", result.ganzhi)
        st.metric("天干", f"{result.tiangan}（{result.yinyang}）")
        st.metric("地支", result.dizhi)
    with col2:
        wx_color = _WX_COLOR.get(result.dayun.wuxing, _GREY)
        st.metric("大運", result.dayun.taishao)
        st.metric("大運五行", result.dayun.wuxing)
        st.metric("太/少", "太過（有餘）" if result.dayun.is_tai else "不及（不足）")
    with col3:
        st.metric("司天之氣", result.sitian)
        st.metric("在泉之氣", result.zaiquan)
        st.metric("運氣特徵", " · ".join(result.tonghua.categories))

    st.divider()

    # 當前精細位置
    pos = result.current_position
    if pos:
        st.subheader("📍 當前時刻運氣位置")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**五運位置**")
            st.progress(int(pos.zhuyun_progress_pct) / 100,
                        text=f"{pos.current_zhuyun.step_name}·{pos.current_zhuyun.taishao} "
                             f"（{pos.zhuyun_progress_pct:.1f}%）")
            st.caption(f"客運：{pos.current_keyun.step_name}·{pos.current_keyun.taishao}")
        with c2:
            st.markdown("**六氣位置**")
            st.progress(int(pos.zhuqi_progress_pct) / 100,
                        text=f"{pos.current_zhuqi.step_name}·{pos.current_zhuqi.qi_name} "
                             f"（{pos.zhuqi_progress_pct:.1f}%）")
            st.caption(f"客氣：{pos.current_keqi.step_name}·{pos.current_keqi.qi_name}")

        st.markdown(
            f"<div style='background:{_CARD}; border-left:4px solid {_ACCENT}; "
            f"border-radius:6px; padding:12px 16px; margin-top:8px;'>"
            f"<b>客主加臨</b>：主氣 {_escape(pos.jialin.zhuqi)} × 客氣 {_escape(pos.jialin.keqi)} → "
            f"<span style='color:{_JIALIN_COLOR.get(pos.jialin.relation, _GREY)}'>"
            f"<b>{_escape(pos.jialin.relation)}</b></span><br/>"
            f"<small style='color:{_SUBTLE}'>{_escape(pos.jialin.effect)}</small>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # 年度健康提示
    st.subheader("🏥 年度醫學氣候提示")
    is_tai_str = "太過" if result.dayun.is_tai else "不及"
    health_note = HEALTH_ADVICE.get(is_tai_str, "")
    st.info(
        f"**{result.ganzhi}年 {result.dayun.wuxing}運{is_tai_str}**\n\n"
        f"{health_note}\n\n"
        f"司天{result.sitian}：{QI_ATTRIBUTES.get(result.sitian, {}).get('disease', '')}\n\n"
        f"在泉{result.zaiquan}：{QI_ATTRIBUTES.get(result.zaiquan, {}).get('disease', '')}"
    )

    # 勝復
    sf = result.shengfu
    st.subheader("⚡ 勝復規律")
    col_sf1, col_sf2 = st.columns(2)
    with col_sf1:
        st.markdown(f"**勝氣**：{sf.sheng_qi}")
        st.caption(sf.sheng_desc)
    with col_sf2:
        st.markdown(f"**復氣**：{sf.fu_qi}")
        st.caption(sf.fu_desc)

    # 鬱發治則
    st.subheader("🌿 五鬱治則（《素問·六元正紀大論》）")
    yufa_cols = st.columns(5)
    for i, wx in enumerate(WUXING):
        with yufa_cols[i]:
            color = _WX_COLOR.get(wx, _GREY)
            st.markdown(
                f"<div style='background:{color}22; border:1px solid {color}; "
                f"border-radius:6px; padding:10px; text-align:center;'>"
                f"<div style='color:{color}; font-size:1.3em; font-weight:bold;'>{_escape(wx)}鬱</div>"
                f"<div style='color:{_TEXT}; font-size:0.9em; margin-top:4px;'>{_escape(YUFA[wx])}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


def _render_wuyun(result: WuYunLiuQiResult) -> None:
    """五運詳解頁籤"""
    pos = result.current_position

    st.subheader(f"🌀 {result.ganzhi}年 大運：{result.dayun.taishao}")

    # 大運卡片
    wx = result.dayun.wuxing
    color = _WX_COLOR.get(wx, _GREY)
    attrs = YUN_ATTRIBUTES.get(wx, {})
    tai_str = "太過（有餘）" if result.dayun.is_tai else "不及（不足）"
    climate = attrs.get("climate_tai" if result.dayun.is_tai else "climate_shao", "")
    disease = attrs.get("disease_tai" if result.dayun.is_tai else "disease_shao", "")

    st.markdown(
        f"""
        <div style="background:{_CARD}; border:2px solid {color}; border-radius:8px; padding:16px; margin-bottom:16px;">
          <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <span style="font-size:2.5em;">{_escape(attrs.get('symbol', ''))}</span>
            <div>
              <div style="font-size:1.5em; font-weight:bold; color:{color};">{_escape(result.dayun.taishao)}</div>
              <div style="color:{_TEXT};">五行：{_escape(wx)} ｜ 五音：{_escape(result.dayun.tone)} ｜ {_escape(tai_str)}</div>
            </div>
          </div>
          <hr style="border-color:{color}44; margin:10px 0;"/>
          <div style="color:{_TEXT}; line-height:1.8;">
            <b>氣候特徵：</b>{_escape(climate)}<br/>
            <b>易發疾病：</b>{_escape(disease)}<br/>
            <b>主臟腑：</b>{_escape(attrs.get('organ', ''))}<br/>
            <b>對應季節：</b>{_escape(attrs.get('season', ''))}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # 主運五步表
    st.subheader("主運五步（固定順序，木→火→土→金→水）")
    rows = []
    for i, step in enumerate(result.zhuyun_steps):
        is_cur = pos and pos.current_zhuyun_index == i
        rows.append({
            "步名": step.step_name,
            "五行": step.wuxing,
            "五音": step.tone,
            "太少": step.taishao,
            "起始（大寒後天數）": f"{step.start_day:.1f}",
            "終止（大寒後天數）": f"{step.end_day:.1f}",
            "當前": "◀ 當前" if is_cur else "",
        })

    df_zhuyun = pd.DataFrame(rows)
    st.dataframe(df_zhuyun, width="stretch")

    st.divider()

    # 客運五步表
    st.subheader("客運五步（以大運為初運，按相生推演）")
    rows_ke = []
    for i, step in enumerate(result.keyun_steps):
        is_cur = pos and pos.current_keyun_index == i
        rows_ke.append({
            "步名": step.step_name,
            "五行": step.wuxing,
            "五音": step.tone,
            "太少": step.taishao,
            "當前": "◀ 當前" if is_cur else "",
        })
    df_keyun = pd.DataFrame(rows_ke)
    st.dataframe(df_keyun, width="stretch")

    # 說明
    st.caption(
        "主運：每年固定，初運木角，依木→火→土→金→水相生順序各73.05天。\n"
        "客運：每年不同，以當年大運為初運，按相生順序推五步，太少與大運相應。"
    )


def _render_liuqi(result: WuYunLiuQiResult) -> None:
    """六氣詳解頁籤"""
    pos = result.current_position

    # 司天在泉
    col_st, col_zq = st.columns(2)
    with col_st:
        st.subheader(f"☁️ 司天之氣：{result.sitian}")
        attrs = QI_ATTRIBUTES.get(result.sitian, {})
        st.markdown(
            f"**自然象**：{attrs.get('nature', '')}  "
            f"｜ **主臟**：{attrs.get('organ', '')}  "
            f"｜ **對應季**：{attrs.get('season', '')}"
        )
        st.info(f"氣候：{attrs.get('climate', '')}  \n疾病：{attrs.get('disease', '')}")

    with col_zq:
        st.subheader(f"🌊 在泉之氣：{result.zaiquan}")
        attrs2 = QI_ATTRIBUTES.get(result.zaiquan, {})
        st.markdown(
            f"**自然象**：{attrs2.get('nature', '')}  "
            f"｜ **主臟**：{attrs2.get('organ', '')}  "
            f"｜ **對應季**：{attrs2.get('season', '')}"
        )
        st.info(f"氣候：{attrs2.get('climate', '')}  \n疾病：{attrs2.get('disease', '')}")

    st.divider()

    # 主氣六步
    st.subheader("主氣六步（年年固定，厥陰→少陰→少陽→太陰→陽明→太陽）")
    rows_zhu = []
    for i, step in enumerate(result.zhuqi_steps):
        is_cur = pos and pos.current_zhuqi_index == i
        a = step.attributes
        rows_zhu.append({
            "步名": step.step_name,
            "氣名": step.qi_name,
            "氣性": step.nature,
            "主臟": a.get("organ", ""),
            "起始（大寒後天數）": f"{step.start_day:.1f}",
            "終止（大寒後天數）": f"{step.end_day:.1f}",
            "當前": "◀ 當前" if is_cur else "",
        })
    st.dataframe(pd.DataFrame(rows_zhu), width="stretch")

    st.divider()

    # 客氣六步
    st.subheader("客氣六步（以司天為三之氣，按步序排列）")
    rows_ke = []
    for i, step in enumerate(result.keqi_steps):
        is_cur = pos and pos.current_keqi_index == i
        a = step.attributes
        rows_ke.append({
            "步名": step.step_name,
            "氣名": step.qi_name,
            "氣性": step.nature,
            "主臟": a.get("organ", ""),
            "當前": "◀ 當前" if is_cur else "",
        })
    st.dataframe(pd.DataFrame(rows_ke), width="stretch")

    st.caption(
        "主氣：六步固定不變，大寒→春分→小滿→大暑→秋分→小雪，每步約60.875天。\n"
        "客氣：每年不同，三之氣=司天，按厥陰(0)→少陰(1)→太陰(2)→少陽(3)→陽明(4)→太陽(5)步序排列。"
    )


def _render_jialin(result: WuYunLiuQiResult) -> None:
    """客主加臨頁籤"""
    pos = result.current_position

    st.subheader("⚖️ 客主加臨（六步）")
    st.caption(
        "客主加臨：客氣覆臨於主氣之上，相互作用影響氣候與疾病。\n"
        "順化：主生客（最吉）｜同化：同氣（和平）｜小逆：客生主（稍差）"
        "｜不和：客克主（較差）｜逆：主克客（最差）"
    )

    rows = []
    for i, jl in enumerate(result.jialin_steps):
        is_cur = pos and pos.current_zhuqi_index == i
        rows.append({
            "步名": jl.step_name,
            "主氣": jl.zhuqi,
            "客氣": jl.keqi,
            "加臨關係": jl.relation,
            "影響": jl.effect[:30] + "…" if len(jl.effect) > 30 else jl.effect,
            "當前": "◀ 當前" if is_cur else "",
        })
    st.dataframe(pd.DataFrame(rows), width="stretch")

    # 詳細說明
    if pos:
        jl = pos.jialin
        rel_color = _JIALIN_COLOR.get(jl.relation, _GREY)
        st.markdown(
            f"<div style='background:{_CARD}; border:2px solid {rel_color}; "
            f"border-radius:8px; padding:16px; margin-top:12px;'>"
            f"<b style='font-size:1.1em; color:{rel_color}'>當前 {_escape(jl.step_name)} 客主加臨</b><br/>"
            f"主氣：{_escape(jl.zhuqi)} × 客氣：{_escape(jl.keqi)}<br/>"
            f"<b>關係：<span style='color:{rel_color}'>{_escape(jl.relation)}</span></b><br/>"
            f"<span style='color:{_TEXT}'>{_escape(jl.effect)}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_tonghua(result: WuYunLiuQiResult) -> None:
    """運氣同化頁籤"""
    th = result.tonghua

    st.subheader("🔮 運氣同化分析")

    # 同化狀態
    cats = th.categories
    main_cat = cats[0] if cats else "平氣之年"
    cat_color = _ACCENT if main_cat != "平氣之年" else _GREEN

    st.markdown(
        f"""
        <div style="background:{_CARD}; border:2px solid {cat_color};
                    border-radius:10px; padding:20px; text-align:center; margin-bottom:16px;">
          <div style="font-size:2em; font-weight:bold; color:{cat_color}; margin-bottom:8px;">
            {_escape(main_cat)}
          </div>
          <div style="color:{_TEXT}; line-height:1.8;">
            {_escape(th.description)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 各條件判斷
    st.subheader("運氣同化條件判斷")
    col1, col2 = st.columns(2)
    checks = [
        ("天符", th.is_tianfu,
         f"大運五行（{result.dayun.wuxing}）= 司天五行（{result.sitian}）"),
        ("歲會", th.is_suihui,
         f"大運五行（{result.dayun.wuxing}）= 歲支五行（{result.dizhi}）"),
        ("太乙天符", th.is_taiyi_tianfu, "天符 且 歲會（最強氣化）"),
        ("同天符", th.is_tong_tianfu,
         f"陽年大運與司天同五行（{result.yinyang}年）"),
        ("同歲會", th.is_tong_suihui,
         f"陰年大運與歲支同五行（{result.yinyang}年）"),
    ]
    for i, (name, val, desc) in enumerate(checks):
        with (col1 if i % 2 == 0 else col2):
            icon = "✅" if val else "⭕"
            color = _GREEN if val else _GREY
            st.markdown(
                f"<div style='border:1px solid {color}; border-radius:6px; "
                f"padding:10px; margin-bottom:8px;'>"
                f"<b style='color:{color}'>{icon} {_escape(name)}</b><br/>"
                f"<small style='color:{_SUBTLE}'>{_escape(desc)}</small>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("運氣同化說明（《素問·六微旨大論》）")
    for key, desc in TONG_HUA_DESC.items():
        with st.expander(key):
            st.write(desc)


def _render_curve_ui(result: WuYunLiuQiResult) -> None:
    """運氣變化曲線頁籤（每分鐘精細計算）"""
    st.subheader("📈 運氣變化曲線（每分鐘精細計算）")
    st.caption("選擇時間範圍，以指定間隔計算各時刻的運氣位置，生成變化曲線。")

    col_s, col_e, col_step = st.columns(3)
    with col_s:
        start_date = st.date_input(
            "起始日期",
            value=datetime(result.year, 1, 20).date(),
            key="wylq_curve_start",
        )
    with col_e:
        end_date = st.date_input(
            "結束日期",
            value=datetime(result.year, 12, 31).date(),
            key="wylq_curve_end",
        )
    with col_step:
        step = st.selectbox(
            "計算間隔",
            options=[1, 10, 30, 60, 360, 1440],
            format_func=lambda x: {
                1: "1分鐘", 10: "10分鐘", 30: "30分鐘",
                60: "1小時", 360: "6小時", 1440: "1天",
            }[x],
            index=3,
            key="wylq_curve_step",
        )

    if st.button("▶ 計算運氣曲線", key="wylq_calc_curve"):
        start_dt = datetime(start_date.year, start_date.month, start_date.day)
        end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59)
        total_mins = int((end_dt - start_dt).total_seconds() / 60)
        expected_pts = total_mins // step + 1

        if expected_pts > 10000:
            st.warning(f"計算點數過多（{expected_pts}點），請縮小範圍或增大間隔。")
            return

        with st.spinner(f"計算中（{expected_pts}個時間點）…"):
            calc = WuYunLiuQiCalculator(
                start_date.year, start_date.month, start_date.day
            )
            series = calc.compute_minute_series(start_dt, end_dt, step)

        if not series:
            st.error("無法生成曲線，請檢查時間範圍。")
            return

        df = pd.DataFrame(series)
        df["時間"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M")

        # 主氣步索引（用於曲線）
        zhuqi_order = ["初之氣", "二之氣", "三之氣", "四之氣", "五之氣", "終之氣"]
        df["主氣步索引"] = df["zhuqi"].apply(
            lambda x: zhuqi_order.index(x.split("·")[0]) if "·" in x else 0
        )
        df["主運步索引"] = df["zhuyun"].apply(
            lambda x: ["初運", "二運", "三運", "四運", "終運"].index(x.split("·")[0])
            if "·" in x else 0
        )
        df["主氣進度(%)"] = df["zhuqi_progress"]
        df["主運進度(%)"] = df["zhuyun_progress"]

        # 顯示曲線
        tab_c1, tab_c2, tab_c3 = st.tabs(["六氣步進圖", "五運步進圖", "原始數據"])

        with tab_c1:
            st.line_chart(df.set_index("時間")["主氣步索引"],
                          use_container_width=True)
            st.caption("縱軸：0=初之氣 … 5=終之氣")

        with tab_c2:
            st.line_chart(df.set_index("時間")["主運步索引"],
                          use_container_width=True)
            st.caption("縱軸：0=初運 … 4=終運")

        with tab_c3:
            show_cols = ["時間", "ganzhi", "dayun", "zhuyun", "keyun",
                         "zhuqi", "keqi", "sitian", "zaiquan", "jialin_relation"]
            st.dataframe(df[show_cols].rename(columns={
                "ganzhi": "干支",
                "dayun": "大運",
                "zhuyun": "主運",
                "keyun": "客運",
                "zhuqi": "主氣",
                "keqi": "客氣",
                "sitian": "司天",
                "zaiquan": "在泉",
                "jialin_relation": "加臨關係",
            }), width="stretch")


def render_wuyunliuqi_intro() -> None:
    """五運六氣簡介（未計算時顯示）"""
    st.markdown(
        f"""
        <div style="background:{_CARD}; border:1px solid {_BORDER};
                    border-radius:8px; padding:20px; margin-bottom:12px;">
          <h3 style="color:{_HEADER};">☯ 五運六氣 — 古典中醫宇宙觀</h3>
          <p style="color:{_TEXT}; line-height:1.8;">
            五運六氣（Wu Yun Liu Qi）源自《黃帝內經·素問》運氣七篇，
            是中醫最完整的天地氣化推演體系，用於預測自然氣候與疾病發生規律。
          </p>
          <ul style="color:{_TEXT}; line-height:2.0;">
            <li><b style="color:{_ACCENT};">五運</b>：木火土金水五行之氣運行——大運、主運、客運</li>
            <li><b style="color:{_ACCENT};">六氣</b>：風熱火濕燥寒六氣輪轉——司天、在泉、主氣、客氣</li>
            <li><b style="color:{_ACCENT};">客主加臨</b>：客氣覆臨主氣，推演氣候與疾病</li>
            <li><b style="color:{_ACCENT};">運氣同化</b>：天符、歲會、太乙天符等特殊年份</li>
            <li><b style="color:{_ACCENT};">勝復鬱發</b>：五行勝復與五鬱治則</li>
          </ul>
          <p style="color:{_SUBTLE}; font-size:0.85em;">
            依據：《素問·天元紀大論》《五運行大論》《六微旨大論》《氣交變大論》
            《五常政大論》《六元正紀大論》《至真要大論》
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
