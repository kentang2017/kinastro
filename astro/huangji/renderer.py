"""Streamlit renderer for Huangji Jingshi (皇極經世)."""

from __future__ import annotations

import math
from typing import Callable

from astro.chart_renderer_v2 import build_cultural_svg


def _build_huangji_wheel_svg(gua: dict[str, str]) -> str:
    labels = [
        ("正", gua.get("正卦", "")),
        ("運", gua.get("運卦", "")),
        ("世", gua.get("世卦", "")),
        ("旬", gua.get("旬卦", "")),
        ("年", gua.get("年卦", "")),
        ("月", gua.get("月卦", "")),
        ("日", gua.get("日卦", "")),
        ("時", gua.get("時卦", "")),
    ]
    base_r = 186
    cx, cy = 260, 260
    nodes = []
    for i, (k, v) in enumerate(labels):
        ang = i * 45 - 90
        x = cx + base_r * math.cos(math.radians(ang))
        y = cy + base_r * math.sin(math.radians(ang))
        nodes.append(
            f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="33" fill="#1f1b2e" stroke="#b89a5a" stroke-width="1.2" />'
            f'<text x="{x:.1f}" y="{y-5:.1f}" text-anchor="middle" fill="#e6d4a1" font-size="16">{k}</text>'
            f'<text x="{x:.1f}" y="{y+14:.1f}" text-anchor="middle" fill="#f4e8c7" font-size="20">{v}</text></g>'
        )
    return (
        '<svg viewBox="0 0 520 520" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="520" height="520" fill="#120f19"/>'
        '<circle cx="260" cy="260" r="215" fill="none" stroke="#6c5833" stroke-width="2" />'
        '<circle cx="260" cy="260" r="150" fill="none" stroke="#5a4a2f" stroke-width="1.2" stroke-dasharray="3 6" />'
        '<text x="260" y="248" text-anchor="middle" fill="#d8c59a" font-size="24">皇極經世</text>'
        '<text x="260" y="276" text-anchor="middle" fill="#b7a377" font-size="14">元・會・運・世</text>'
        + "".join(nodes)
        + '</svg>'
    )


def render_streamlit(chart, *, lang: str = "zh", after_chart_hook: Callable[[], None] | None = None) -> None:
    import streamlit as st

    t_basic = "基本盤" if lang == "zh" else "Core Pan"
    t_cycles = "大週期" if lang == "zh" else "Macro Cycles"
    t_cross = "跨體系對照" if lang == "zh" else "Cross-System"
    t_history = "歷史年表" if lang == "zh" else "Historical Timeline"
    t_title = "### 🏮 皇極經世（邵雍先天易數）" if lang == "zh" else "### 🏮 Huangji Jingshi (Shao Yong's Prenatal Number Doctrine)"
    t_caption = (
        "宋代書卷氣 × 現代極簡神秘風，觀物取象，推宇宙大數。"
        if lang == "zh"
        else "Song literati aesthetics × modern minimal mystery, observing macro-cycles through symbols."
    )

    p = chart.huangji_pan

    st.markdown(t_title)
    st.caption(t_caption)

    tab1, tab2, tab3, tab4 = st.tabs([t_basic, t_cycles, t_cross, t_history])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("元", p.yuan)
        c2.metric("會", p.hui)
        c3.metric("運", p.yun)
        c4.metric("世", p.shi)

        c5, c6, c7 = st.columns(3)
        c5.metric("世內年份", f"{p.year_in_shi}/30")
        c6.metric("運內年份", f"{p.year_in_yun}/360")
        c7.metric("會內年份", f"{p.year_in_hui}/10800")

        st.caption(f"節氣（kinwangji）：{p.jieqi_kinwangji} ｜ 節氣（Swiss）：{p.jieqi_swiss}")
        st.dataframe(
            [{"層位": k, "卦": v, "動爻": p.moving_lines.get(f"{k}動爻", "")} for k, v in p.gua.items()],
            width="stretch",
            hide_index=True,
        )
        wheel = build_cultural_svg(_build_huangji_wheel_svg(p.gua), "tab_huangji", title="皇極四卦輪盤", animate_spin=False)
        st.markdown(wheel, unsafe_allow_html=True)
        if after_chart_hook:
            after_chart_hook()

    with tab2:
        st.markdown("#### 元會運世時間軸")
        st.dataframe(p.major_cycle_milestones, width="stretch", hide_index=True)
        st.code(chart.board_text, language="text")

    with tab3:
        rows = [
            {"系統": "Hellenistic Zodiacal Releasing", "當前定位": chart.cross_system.zodiacal_releasing_l1 or "—"},
            {"系統": "Annual Profections", "當前定位": chart.cross_system.annual_profection or "—"},
            {"系統": "Vedic Dasha", "當前定位": chart.cross_system.vedic_dasha or "—"},
            {"系統": "紫微大限", "當前定位": chart.cross_system.ziwei_daxian or "—"},
        ]
        st.dataframe(rows, width="stretch", hide_index=True)
        current_gua = p.gua.get("世卦") or p.gua.get("運卦") or "—"
        if lang == "zh":
            ai_hint = (
                f"AI 交叉解讀模板：你當前位於皇極第{p.yun}運第{p.shi}世（{current_gua}卦），"
                "可與西方釋放期、紫微大限、Vedic 大運形成同頻綜合判讀。"
            )
        else:
            ai_hint = (
                f"AI synthesis template: you are currently in Huangji Yun {p.yun}, Shi {p.shi} "
                f"({current_gua} hexagram), aligned with Zodiacal Releasing, Ziwei Daxian, and Vedic Dasha."
            )
        st.info(ai_hint)

    with tab4:
        if p.historical_context:
            st.dataframe([
                {
                    "朝代/時代": h.dynasty,
                    "年號/政權": h.era,
                    "稱號": h.title,
                    "起始": h.start_year,
                    "年數": h.duration,
                }
                for h in p.historical_context
            ], width="stretch", hide_index=True)
        else:
            st.caption("該年份無可用歷史對照資料。")
