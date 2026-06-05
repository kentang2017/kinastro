"""
ui/handlers/tab_enochian/render.py — Enochian Astrology Streamlit UI

完整的 Enochian 占星 Streamlit 介面，包含：
  - 個人守護天使（Patron/Matron/Ascendant Angels）卡片
  - 四個守望塔分析（含強度條和互動說明）
  - 主要以太層（Aethyr）解讀和冥想建議
  - Sigillum Dei Aemeth 個人化 SVG 視覺化
  - 守望塔 2×2 網格 SVG
  - 30 Aethyr 層級圖 SVG（含高亮）
  - 儀式和魔法實踐建議
  - 與西方占星的對照說明

設計符合：
  - CONTRIBUTING.md：render_* 函式可使用 Streamlit
  - 現有專案風格：CSS 卡片、st.columns、st.expander
  - 中英雙語支援
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from astro.enochian.calculator import (
    EnochianChart,
    compute_enochian_chart,
)
from astro.enochian.renderer import (
    render_sigillum_svg,
    render_watchtower_svg,
    render_aethyr_svg,
    render_enochian_summary_svg,
    render_element_balance_svg,
)
from astro.enochian.constants import (
    AETHYRS,
    WATCHTOWERS,
    ELEMENT_TABLE,
    SIGILLUM_DEI_AEMETH,
    ENOCHIAN_PLANETS,
)
from astro.i18n import t

# ============================================================
# CSS 樣式
# ============================================================

_ENOCHIAN_CSS = """
<style>
.enoch-header {
    background: linear-gradient(135deg, #0a0a1e 0%, #1a0535 40%, #0d1545 100%);
    border-left: 4px solid #FFD700;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 14px;
}
.enoch-header h2 { color: #FFD700; margin: 0 0 4px 0; font-size: 1.3rem; }
.enoch-header p  { color: #b0a070; margin: 0; font-size: 0.85rem; }

.angel-card {
    background: rgba(20, 5, 40, 0.85);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
    border: 1px solid rgba(200, 160, 60, 0.35);
}
.angel-card-title {
    color: #FFD700;
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 6px;
}
.angel-card-sub {
    color: #c0a060;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
.angel-card-text { color: #d0c8a0; font-size: 0.9rem; }

.aethyr-card {
    background: rgba(10, 5, 30, 0.9);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-left: 3px solid var(--aethyr-color, #FFD700);
}
.aethyr-card-title { color: #FFD700; font-weight: bold; font-size: 1rem; }
.aethyr-card-text  { color: #d0c8a0; font-size: 0.88rem; }

.wt-score-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
}
.wt-score-label { color: #b0a070; font-size: 0.8rem; width: 60px; }
.wt-score-fill  { height: 8px; border-radius: 4px; flex-shrink: 0; }

.enoch-cross-ref {
    background: rgba(15, 10, 35, 0.8);
    border: 1px solid rgba(100, 80, 160, 0.3);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #a090c0;
    font-family: monospace;
}
.ritual-box {
    background: rgba(20, 10, 5, 0.85);
    border: 1px solid rgba(200, 80, 20, 0.35);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #d0b090;
    font-size: 0.88rem;
    font-style: italic;
}
.invocation-box {
    background: rgba(10, 5, 25, 0.9);
    border: 1px solid rgba(150, 100, 220, 0.35);
    border-radius: 8px;
    padding: 10px 14px;
    color: #b8a8e0;
    font-size: 0.85rem;
    font-style: italic;
}
</style>
"""


# ============================================================
# 輔助渲染函式
# ============================================================

def _lang() -> str:
    return st.session_state.get("lang", "zh")


def _is_zh() -> bool:
    return _lang() in ("zh", "zh_cn")


def _t(key: str) -> str:
    return t(key)


def _render_interactive_html(html: str, height: int, key: str) -> None:
    """嵌入 SVG 為 Streamlit HTML 元件。"""
    st.components.v1.html(html, height=height, scrolling=False)


def _element_badge(element: str, element_zh: str) -> str:
    """生成元素色彩標籤 HTML。"""
    colors = {
        "Fire": "#FF4500", "Water": "#4169E1",
        "Air": "#87CEEB", "Earth": "#8B4513", "Spirit": "#8B5CF6",
    }
    c = colors.get(element, "#888")
    return (
        f'<span style="background:{c}20;border:1px solid {c}60;'
        f'color:{c};border-radius:4px;padding:1px 6px;font-size:0.8rem">'
        f'{element_zh} ({element})</span>'
    )


def _render_angel_card(angel, title_label_zh: str, title_label_en: str) -> None:
    """渲染守護天使卡片。"""
    is_zh = _is_zh()
    wt = WATCHTOWERS.get(angel.watchtower)
    el_color_map = {
        "Fire": "#FF4500", "Water": "#4169E1",
        "Air": "#87CEEB", "Earth": "#8B4513", "Spirit": "#8B5CF6",
    }
    wt_el_color = el_color_map.get(wt.element, "#FFD700") if wt else "#FFD700"

    title = title_label_zh if is_zh else title_label_en
    angel_display = angel.name_zh if is_zh else angel.name
    determined = angel.determined_zh if is_zh else angel.determined_by
    wt_display = angel.watchtower_zh + "方守望塔" if is_zh else f"{angel.watchtower} Watchtower"
    aethyr_display = angel.primary_aethyr.name_zh if is_zh else angel.primary_aethyr.name
    attrs = " · ".join(angel.attributes_zh[:3] if is_zh else angel.attributes_en[:3])

    st.markdown(f"""
<div class="angel-card">
  <div class="angel-card-title">
    {title}：<span style="color:#c0a060">{angel.name}</span>
    <span style="color:#888;font-size:0.85rem;font-weight:normal">（{angel.name_zh}）</span>
  </div>
  <div class="angel-card-sub">
    {"由" + determined + "決定" if is_zh else f"Determined by: {determined}"}　·　
    <span style="color:{wt_el_color}">{wt_display}</span>　·　
    {"主要以太層：" if is_zh else "Primary Aethyr: "}<strong>{aethyr_display}</strong>
  </div>
  <div class="angel-card-text">
    {"屬性：" if is_zh else "Attributes: "}{attrs}
  </div>
</div>
""", unsafe_allow_html=True)

    with st.expander("🔮 " + ("召喚語 / Invocation" if is_zh else "Invocation"), expanded=False):
        invoc = angel.invocation_zh if is_zh else angel.invocation_en
        st.markdown(f'<div class="invocation-box">{invoc}</div>', unsafe_allow_html=True)


def _render_watchtower_section(chart: EnochianChart) -> None:
    """渲染四個守望塔分析區塊。"""
    is_zh = _is_zh()

    st.subheader("🗼 " + ("四個守望塔分析" if is_zh else "Four Watchtowers Analysis"))

    # SVG 網格
    wt_svg = render_watchtower_svg(chart=chart, size=480)
    _render_interactive_html(wt_svg, height=490, key="enoch_watchtower")

    # 守望塔詳情
    st.markdown("---")
    cols = st.columns(2)
    wt_order = ["East", "West", "North", "South"]
    for i, direction in enumerate(wt_order):
        col = cols[i % 2]
        with col:
            wt = WATCHTOWERS[direction]
            score = chart.watchtower_scores.get(direction, 0.0)
            is_dom = direction == chart.dominant_watchtower
            el_color_map = {
                "Fire": "#FF4500", "Water": "#4169E1",
                "Air": "#87CEEB", "Earth": "#8B4513",
            }
            el_c = el_color_map.get(wt.element, "#FFD700")

            dom_label = " ★" if is_dom else ""
            wt_name = wt.name_zh if is_zh else wt.name
            st.markdown(
                f"**<span style='color:{el_c}'>{wt.direction_zh}方{dom_label}</span>** "
                f"— {wt.element_zh}元素 | {int(score * 100)}%",
                unsafe_allow_html=True,
            )

            # 強度條
            bar_html = (
                f'<div class="wt-score-bar">'
                f'<div class="wt-score-label">{int(score * 100)}%</div>'
                f'<div style="flex:1;background:rgba(80,80,80,0.3);height:8px;border-radius:4px">'
                f'<div class="wt-score-fill" style="width:{int(score*100)}%;background:{el_c};"></div>'
                f'</div></div>'
            )
            st.markdown(bar_html, unsafe_allow_html=True)

            purpose = wt.ritual_purpose_zh if is_zh else wt.ritual_purpose_en
            st.caption(purpose)


def _render_aethyr_section(chart: EnochianChart) -> None:
    """渲染以太層分析區塊。"""
    is_zh = _is_zh()

    st.subheader("🌌 " + ("以太層（Aethyr）分析" if is_zh else "Aethyr Analysis"))

    col1, col2 = st.columns([2, 3])

    with col1:
        # Aethyr 層級圖
        aethyr_svg = render_aethyr_svg(chart=chart, width=220, height=700, show_all=True)
        _render_interactive_html(aethyr_svg, height=710, key="enoch_aethyr_hierarchy")

    with col2:
        # 主要 Aethyr
        primary = chart.primary_aethyr
        el_colors = {
            "Fire": "#FF4500", "Water": "#4169E1",
            "Air": "#87CEEB", "Earth": "#8B4513", "Spirit": "#8B5CF6",
        }
        pc = el_colors.get(primary.element, "#FFD700")

        st.markdown(f"**{'主要以太層' if is_zh else 'Primary Aethyr'}**")
        primary_name = primary.name_zh if is_zh else primary.name
        keywords = " · ".join(primary.keywords_zh[:3] if is_zh else primary.keywords_en[:3])
        meditation = primary.meditation_zh if is_zh else primary.meditation_en
        level = primary.level_zh if is_zh else primary.level
        governors = "、".join(primary.governors[:3])

        st.markdown(f"""
<div class="aethyr-card" style="--aethyr-color:{pc}">
  <div class="aethyr-card-title">
    #{primary.number} {primary.name} — {primary_name}
  </div>
  <div class="aethyr-card-text">
    {"層次：" if is_zh else "Level: "}{level}　·　
    {"元素：" if is_zh else "Element: "}
    <span style="color:{pc}">{primary.element_zh}</span>　·　
    {"行星：" if is_zh else "Planet: "}{primary.planet_zh}<br/>
    {"關鍵字：" if is_zh else "Keywords: "}<em>{keywords}</em><br/>
    {"守護者：" if is_zh else "Governors: "}{governors}
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown(f'<div class="ritual-box">🧘 {meditation}</div>', unsafe_allow_html=True)

        # 次要 Aethyrs
        if chart.secondary_aethyrs:
            st.markdown(f"**{'次要以太層' if is_zh else 'Secondary Aethyrs'}**")
            for sec in chart.secondary_aethyrs[:3]:
                sc = el_colors.get(sec.element, "#888")
                sec_name = sec.name_zh if is_zh else sec.name
                sec_kw = " · ".join(sec.keywords_zh[:2] if is_zh else sec.keywords_en[:2])
                st.markdown(
                    f"<small style='color:{sc}'>#{sec.number} **{sec.name}** ({sec_name}) "
                    f"— {sec.element_zh} — {sec_kw}</small>",
                    unsafe_allow_html=True,
                )

        # 重要 Aethyr 解讀（前 3 個）
        st.markdown("---")
        st.markdown(f"**{'需要工作的以太層' if is_zh else 'Aethyrs to Work With'}**")
        for reading in chart.aethyr_readings[:3]:
            a = reading.aethyr
            ac = el_colors.get(a.element, "#888")
            a_name = a.name_zh if is_zh else a.name
            themes = " · ".join(reading.key_themes_zh[:2] if is_zh else reading.key_themes_en[:2])
            work = reading.work_needed_zh if is_zh else reading.work_needed_en
            ritual = reading.ritual_suggestion_zh if is_zh else reading.ritual_suggestion_en
            with st.expander(f"#{a.number} {a.name} — {a_name} ({int(reading.relevance_score * 100)}%)"):
                st.markdown(f"<small style='color:{ac}'>🔑 {themes}</small>", unsafe_allow_html=True)
                st.markdown(f'<div class="ritual-box">🧘 {work}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ritual-box">⚗️ {ritual}</div>', unsafe_allow_html=True)


def _render_planet_table(chart: EnochianChart) -> None:
    """渲染行星 Enochian 對應表。"""
    is_zh = _is_zh()

    st.subheader("🪐 " + ("行星 Enochian 對應" if is_zh else "Planetary Enochian Correspondences"))

    el_colors = {
        "Fire": "#FF4500", "Water": "#4169E1",
        "Air": "#87CEEB", "Earth": "#8B4513", "Spirit": "#8B5CF6",
    }

    for point in chart.planet_points:
        ec = el_colors.get(point.element, "#888")
        planet_display = point.planet_zh if is_zh else point.planet_name
        sign_display = point.sign_zh if is_zh else point.sign
        angel_display = point.angel_zh if is_zh else point.enochian_angel
        wt_display = point.watchtower_zh + "方" if is_zh else point.watchtower
        aethyr_display = point.aethyr.name_zh if is_zh else point.aethyr.name
        retro = " ℞" if point.is_retrograde else ""
        keywords = " · ".join(point.keywords_zh[:2] if is_zh else point.keywords_en[:2])

        interp = point.interpretation_zh if is_zh else point.interpretation_en

        with st.expander(
            f"{'⬇ ' if point.is_retrograde else ''}"
            f"**{point.planet_name}** {planet_display}{retro} — "
            f"{sign_display} | H{point.house} | "
            f"{point.enochian_angel}"
        ):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
| {"項目" if is_zh else "Item"} | {"值" if is_zh else "Value"} |
|------|------|
| {"天使" if is_zh else "Angel"} | **{point.enochian_angel}** ({point.angel_zh}) |
| {"守望塔" if is_zh else "Watchtower"} | <span style='color:{ec}'>{wt_display}</span> |
| {"以太層" if is_zh else "Aethyr"} | #{point.aethyr.number} {point.aethyr.name} |
| {"元素" if is_zh else "Element"} | <span style='color:{ec}'>{point.element_zh}</span> |
| Call | #{point.call_number} |
""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{'解讀' if is_zh else 'Reading'}:** {interp}")
                st.markdown(f"<small style='color:{ec}'>🔑 {keywords}</small>", unsafe_allow_html=True)


def _render_sigillum_section(chart: EnochianChart) -> None:
    """渲染 Sigillum Dei Aemeth 區塊。"""
    is_zh = _is_zh()

    st.subheader("⭕ " + ("Sigillum Dei Aemeth — 神之印" if is_zh else "Sigillum Dei Aemeth — Seal of God"))

    col1, col2 = st.columns([2, 1])

    with col1:
        sig_svg = render_sigillum_svg(chart=chart, size=400, show_labels=True)
        _render_interactive_html(sig_svg, height=410, key="enoch_sigillum")

    with col2:
        desc = SIGILLUM_DEI_AEMETH["description_zh" if is_zh else "description_en"]
        st.caption(desc)

        st.markdown(f"**{'個人化資訊' if is_zh else 'Personalized Info'}**")
        st.markdown(
            f"{'Sigillum 對應號碼' if is_zh else 'Sigillum Personal Number'}: "
            f"**{chart.sigillum_personal_number}**"
        )
        st.markdown(
            f"{'激活天使' if is_zh else 'Activated Angels'}: "
            f"{' · '.join(chart.sigillum_active_angels)}"
        )

        # 七個天使說明
        st.markdown(f"**{'七位天使（七芒星節點）' if is_zh else '7 Angels (Heptagram Nodes)'}**")
        for i, (angel, angel_zh) in enumerate(zip(
            SIGILLUM_DEI_AEMETH["seven_angels"],
            SIGILLUM_DEI_AEMETH["seven_angels_zh"]
        )):
            is_active = angel in chart.sigillum_active_angels or angel == chart.patron_angel.name
            style = "color:#FFD700;font-weight:bold" if is_active else "color:#807050"
            planet = SIGILLUM_DEI_AEMETH["seven_planets"][i]
            st.markdown(
                f"<small style='{style}'>{'★ ' if is_active else ''}"
                f"**{angel}** ({angel_zh}) — {planet}</small>",
                unsafe_allow_html=True,
            )


def _render_summary_section(chart: EnochianChart) -> None:
    """渲染命盤概覽圓形圖和整體解讀。"""
    is_zh = _is_zh()

    st.subheader("🌐 " + ("命盤概覽" if is_zh else "Chart Overview"))

    col1, col2 = st.columns([2, 3])

    with col1:
        summary_svg = render_enochian_summary_svg(chart=chart, size=400)
        _render_interactive_html(summary_svg, height=410, key="enoch_summary")

    with col2:
        # 整體路徑
        st.markdown(f"**{'整體靈性路徑' if is_zh else 'Overall Spiritual Path'}**")
        path = chart.overall_path_zh if is_zh else chart.overall_path_en
        st.markdown(
            f'<div class="angel-card"><div class="angel-card-text">{path}</div></div>',
            unsafe_allow_html=True,
        )

        # 魔法目的
        st.markdown(f"**{'魔法目的' if is_zh else 'Magical Purpose'}**")
        purpose = chart.magical_purpose_zh if is_zh else chart.magical_purpose_en
        st.markdown(
            f'<div class="ritual-box">{purpose}</div>',
            unsafe_allow_html=True,
        )

        # 元素平衡
        st.markdown(f"**{'元素平衡' if is_zh else 'Elemental Balance'}**")
        el_colors = {
            "Fire": "#FF4500", "Water": "#4169E1",
            "Air": "#87CEEB", "Earth": "#8B4513",
        }
        el_labels = {"Fire": "火", "Water": "水", "Air": "風", "Earth": "土"}
        for el, score in sorted(chart.element_scores.items(), key=lambda x: -x[1]):
            ec = el_colors.get(el, "#888")
            el_name = el_labels.get(el, el)
            pct = int(score * 100)
            dom = " ★" if el == chart.dominant_element else ""
            bar_html = (
                f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0">'
                f'<span style="color:{ec};width:50px;font-size:0.8rem">{el_name}{dom}</span>'
                f'<div style="flex:1;background:rgba(80,80,80,0.3);height:7px;border-radius:4px">'
                f'<div style="width:{pct}%;height:7px;background:{ec};border-radius:4px"></div>'
                f'</div>'
                f'<span style="color:{ec};font-size:0.8rem">{pct}%</span>'
                f'</div>'
            )
            st.markdown(bar_html, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Elemental Balance SVG**")
        st.components.v1.html(
            render_element_balance_svg(chart.element_scores, width=360, height=210),
            height=220,
            scrolling=False,
        )


def _render_cross_reference(chart: EnochianChart) -> None:
    """渲染與西方占星的對照說明。"""
    is_zh = _is_zh()

    with st.expander("📋 " + ("與西方占星的對照 / Western Astrology Cross-Reference" if is_zh
                              else "Western Astrology Cross-Reference")):
        st.markdown(
            f"{'以下表格顯示每個行星在標準西方出生盤中的位置，以及對應的 Enochian 分析：' if is_zh else 'The table below shows each planet in the standard Western natal chart and its Enochian correspondence.'}"
        )
        for planet, ref in chart.western_cross_reference.items():
            st.markdown(
                f'<div class="enoch-cross-ref">{ref}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        intro = (
            "**Enochian 占星與西方占星的關係**\n\n"
            "Enochian 占星並非取代西方占星，而是在其基礎上加入天使魔法層次的解讀。"
            "西方占星告訴我們行星的世俗意義（個性、事業、關係），"
            "Enochian 系統則揭示每個行星連結到哪個靈性力量場（守望塔）、"
            "哪個意識層次（Aethyr）、以及哪位天使守護者在背後運作。\n\n"
            "實踐者可將兩者結合：利用西方占星識別生命挑戰，"
            "再用 Enochian 系統尋找對應的天使援助和冥想工作。"
        ) if is_zh else (
            "**Enochian Astrology & Western Astrology**\n\n"
            "Enochian Astrology does not replace Western Astrology but adds an angelic-magical layer of interpretation. "
            "Western Astrology reveals mundane meanings (personality, career, relationships), "
            "while the Enochian system reveals which spiritual force field (Watchtower), "
            "consciousness level (Aethyr), and angelic guardian work behind each planet.\n\n"
            "Practitioners can combine both: use Western Astrology to identify life challenges, "
            "then use Enochian system to find corresponding angelic assistance and meditation work."
        )
        st.markdown(intro)


# ============================================================
# 主渲染函式
# ============================================================

def render_streamlit(chart: Optional[EnochianChart] = None) -> None:
    """
    完整的 Enochian 占星 Streamlit UI 渲染器。

    Args:
        chart: EnochianChart 物件。若提供則直接渲染；
               若未提供則嘗試從 session_state 計算。
    """
    # 注入 CSS
    st.markdown(_ENOCHIAN_CSS, unsafe_allow_html=True)

    is_zh = _is_zh()

    # ── 頁面標題 ─────────────────────────────────────────────
    st.markdown("""
<div class="enoch-header">
  <h2>🔮 Enochian Astrology / 伊諾克占星</h2>
  <p>John Dee & Edward Kelley's Angelic Magic System · 天使魔法系統</p>
</div>
""", unsafe_allow_html=True)

    if chart is None:
        st.info(
            "👈 請輸入出生資料後點擊「開始排盤」，進行伊諾克占星分析。" if is_zh
            else "👈 Enter birth data and click 'Calculate Chart' to begin the Enochian Astrology analysis."
        )
        st.markdown(t("desc_enochian"))
        return

    # ── 守護天使區塊 ─────────────────────────────────────────
    st.subheader("👼 " + ("個人守護天使" if is_zh else "Personal Guardian Angels"))

    col1, col2, col3 = st.columns(3)
    with col1:
        _render_angel_card(chart.patron_angel, "守護天使（太陽）", "Patron Angel (Sun)")
    with col2:
        _render_angel_card(chart.matron_angel, "守護女神天使（月亮）", "Matron Angel (Moon)")
    with col3:
        _render_angel_card(chart.asc_angel, "上升點天使", "Ascendant Angel")

    col4, col5 = st.columns(2)
    with col4:
        _render_angel_card(chart.chart_ruler_angel, "命主星天使", "Chart Ruler Angel")
    with col5:
        _render_angel_card(chart.strongest_planet_angel, "最強行星天使", "Strongest Planet Angel")

    st.divider()

    # ── 命盤概覽 SVG ─────────────────────────────────────────
    _render_summary_section(chart)

    st.divider()

    # ── Sigillum Dei Aemeth ───────────────────────────────────
    _render_sigillum_section(chart)

    st.divider()

    # ── 守望塔 ──────────────────────────────────────────────
    _render_watchtower_section(chart)

    st.divider()

    # ── 以太層分析 ────────────────────────────────────────────
    _render_aethyr_section(chart)

    st.divider()

    # ── 行星對應表 ────────────────────────────────────────────
    _render_planet_table(chart)

    st.divider()

    # ── 西方占星對照 ──────────────────────────────────────────
    _render_cross_reference(chart)

    # ── 說明文字 ──────────────────────────────────────────────
    with st.expander("📖 " + ("關於伊諾克占星 / About Enochian Astrology" if is_zh
                              else "About Enochian Astrology")):
        if is_zh:
            st.markdown("""
**伊諾克占星（Enochian Astrology）** 是現代魔法師將標準出生盤（natal chart）
與約翰·迪伊（John Dee, 1527–1608）和愛德華·凱利（Edward Kelley, 1555–1597）
記錄的天使魔法系統（Enochian Magic）結合的現代應用。

### 核心系統
- **30 個以太層（Aethyrs/Aires）**：意識的層次結構，從第 30 層（最高天界）到第 1 層（最接近物質世界）
- **四個守望塔（Four Watchtowers）**：對應四元素的天使力量場（東/風、西/水、南/火、北/土）
- **Sigillum Dei Aemeth（神之印）**：七芒星形式的魔法護符，包含七位天界天使的名稱
- **守護天使（Patron Angels）**：通過太陽、月亮和上升點對應的個人天使守護者

### 參考資料
- Lon Milo DuQuette: *Enochian Vision Magick* (Weiser, 2008)
- Stephen Skinner: *The Complete Magician's Tables* (Golden Hoard, 2007)
- Aaron Leitch: *Secrets of the Magickal Grimoires* (Llewellyn, 2005)
- Israel Regardie: *The Golden Dawn* (Llewellyn, 1971)
""")
        else:
            st.markdown("""
**Enochian Astrology** is a modern application combining the standard natal chart
with the Angelic Magic system recorded by John Dee (1527–1608) and Edward Kelley (1555–1597).

### Core Systems
- **30 Aethyrs/Aires**: A hierarchy of consciousness levels, from Aethyr 30 (highest celestial) to Aethyr 1 (closest to material reality)
- **Four Watchtowers**: Elemental force fields of angelic power (East/Air, West/Water, South/Fire, North/Earth)
- **Sigillum Dei Aemeth**: The Seal of God — a magical talisman in heptagram form containing names of celestial angels
- **Patron Angels**: Personal angelic guardians determined through the Sun, Moon, and Ascendant

### References
- Lon Milo DuQuette: *Enochian Vision Magick* (Weiser, 2008)
- Stephen Skinner: *The Complete Magician's Tables* (Golden Hoard, 2007)
- Aaron Leitch: *Secrets of the Magickal Grimoires* (Llewellyn, 2005)
- Israel Regardie: *The Golden Dawn* (Llewellyn, 1971)
""")
