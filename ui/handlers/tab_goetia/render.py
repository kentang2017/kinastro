"""
ui/handlers/tab_goetia/render.py — Goetia / Solomonic Astrology Streamlit UI

完整的 Goetia 占星 Streamlit 介面，包含：
  - 個人化魔神推薦卡片（前 5 名）
  - 魔神印記（Sigil）SVG 視覺化
  - Goetia Natal Overview 圓形命盤圖
  - 元素平衡分析
  - 選時占星窗口表（未來 30 天）
  - 72 柱魔神完整瀏覽器
  - 儀式步驟與召喚語
  - 遣返步驟與安全提示

設計符合：
  - CONTRIBUTING.md：render_* 函式可使用 Streamlit
  - 現有專案風格：CSS 卡片、st.columns、st.expander
  - 中英雙語支援
  - 與 Enochian 模組視覺風格一致
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from astro.goetia.constants import (
    GoetiaChart,
    DemonData,
    DemonRecommendation,
    ElectionalWindow,
    ELEMENT_COLORS,
    PLANET_COLORS,
    RANK_ZH,
    ELEMENT_ZH,
    PLANET_ZH,
)
from astro.goetia.visualization import (
    render_demon_sigil_svg,
    render_goetia_natal_svg,
    render_element_balance_svg,
    render_recommendation_summary_svg,
)
from astro.i18n import t
from astro.system_guides import get_system_guide

# ============================================================
# CSS 樣式
# ============================================================

_GOETIA_CSS = """
<style>
.goetia-header {
    background: linear-gradient(135deg, #0a0a1e 0%, #1a0520 40%, #0d1a0d 100%);
    border-left: 4px solid #8B0000;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 14px;
}
.goetia-header h2 { color: #C0392B; margin: 0 0 4px 0; font-size: 1.3rem; }
.goetia-header p  { color: #b07060; margin: 0; font-size: 0.85rem; }

.demon-card {
    background: rgba(20, 5, 10, 0.88);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
    border: 1px solid rgba(200, 60, 40, 0.35);
}
.demon-card-title {
    color: #FFD700;
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 6px;
}
.demon-card-sub {
    color: #c08060;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
.demon-card-text { color: #d0c8a0; font-size: 0.9rem; }

.rec-score-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
}
.rec-score-label { color: #b07060; font-size: 0.8rem; width: 70px; }
.rec-score-fill  { height: 8px; border-radius: 4px; flex-shrink: 0; }

.electional-card {
    background: rgba(10, 5, 20, 0.9);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-left: 3px solid var(--qual-color, #C0392B);
}
.electional-title { color: #FFD700; font-weight: bold; font-size: 0.95rem; }
.electional-text  { color: #d0c8a0; font-size: 0.85rem; }

.ritual-box {
    background: rgba(20, 5, 5, 0.88);
    border: 1px solid rgba(180, 60, 30, 0.35);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #d0b090;
    font-size: 0.88rem;
    font-style: italic;
}
.invocation-box {
    background: rgba(10, 3, 20, 0.92);
    border: 1px solid rgba(120, 40, 180, 0.4);
    border-radius: 8px;
    padding: 12px 16px;
    color: #b8a0e0;
    font-size: 0.88rem;
    font-style: italic;
    line-height: 1.6;
}
.safety-box {
    background: rgba(20, 5, 0, 0.9);
    border: 1px solid rgba(200, 100, 0, 0.4);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #e0c090;
    font-size: 0.85rem;
}
.demon-browser-card {
    background: rgba(15, 5, 10, 0.7);
    border-radius: 6px;
    padding: 8px 12px;
    margin: 4px 0;
    border: 1px solid rgba(150, 50, 30, 0.2);
}
</style>
"""

# ============================================================
# 輔助函式
# ============================================================

def _lang() -> str:
    return st.session_state.get("lang", "zh")


def _is_zh() -> bool:
    return _lang() in ("zh", "zh_cn")


def _elem_color(element: str) -> str:
    return ELEMENT_COLORS.get(element, "#888888")


def _rank_color(rank: str) -> str:
    colors = {
        "King":      "#FFD700",
        "Duke":      "#FF69B4",
        "Prince":    "#FF8C00",
        "Marquis":   "#C0C0C0",
        "President": "#87CEEB",
        "Count":     "#808080",
        "Earl":      "#808080",
        "Knight":    "#8B6914",
    }
    return colors.get(rank, "#C0392B")


def _quality_color(quality: str) -> str:
    return {"Excellent": "#FFD700", "Good": "#90EE90", "Fair": "#87CEEB"}.get(quality, "#888")


def _render_html(html: str, height: int) -> None:
    st.components.v1.html(html, height=height, scrolling=False)


def _render_system_guide(system_id: str, is_zh: bool) -> None:
    """Render shared educational guide content for the current system."""
    guide = get_system_guide(system_id)
    if guide is None:
        return
    expander_label = (
        "🧭 體系原理與使用情境"
        if is_zh
        else "🧭 Principles, Use Cases, and Differences"
    )
    with st.expander(expander_label, expanded=False):
        st.markdown(
            f"**{'原理' if is_zh else 'Principle'}**\n\n"
            f"{guide.principle_zh if is_zh else guide.principle_en}"
        )
        use_cases = guide.use_cases_zh if is_zh else guide.use_cases_en
        if use_cases:
            st.markdown(
                f"**{'使用情境' if is_zh else 'Use Cases'}**\n\n- "
                + "\n- ".join(use_cases)
            )
        differences = guide.differences_zh if is_zh else guide.differences_en
        if differences:
            st.markdown(
                f"**{'與其他系統差異' if is_zh else 'How It Differs'}**\n\n- "
                + "\n- ".join(differences)
            )
        related = guide.related_systems_zh if is_zh else guide.related_systems_en
        if related:
            st.caption(
                ("相關體系：" if is_zh else "Related systems: ")
                + " · ".join(related)
            )


# ============================================================
# 主要渲染函式 / Main Render Function
# ============================================================

def render_streamlit(chart: Optional[GoetiaChart] = None) -> None:
    """
    Goetia / Solomonic Astrology Streamlit UI 入口點。

    Args:
        chart: GoetiaChart 物件。若提供則直接渲染；
               若未提供則顯示提示訊息。
    """
    # 注入 CSS
    st.markdown(_GOETIA_CSS, unsafe_allow_html=True)

    is_zh = _is_zh()

    # ── 標題 ───────────────────────────────────────────────
    st.markdown("""
<div class="goetia-header">
  <h2>⬡ Goetia / Solomonic Astrology — 所羅門占星</h2>
  <p>Lesser Key of Solomon · 72 Spirit System · Ars Goetia · 魔神召喚與占星整合</p>
</div>
""", unsafe_allow_html=True)
    _render_system_guide("tab_goetia", is_zh)

    if chart is None:
        st.info(
            "👈 請輸入出生資料後點擊「開始排盤」，進行格提亞占星分析。" if is_zh
            else "👈 Enter birth data and click 'Calculate Chart' to begin the Goetia analysis."
        )
        st.markdown(t("desc_goetia"))
        return

    # ── 分頁 UI ────────────────────────────────────────────
    tabs = st.tabs([
        "👿 " + ("魔神推薦" if is_zh else "Demon Recommendations"),
        "🌐 " + ("命盤概覽" if is_zh else "Natal Overview"),
        "⏰ " + ("選時占星" if is_zh else "Electional Timing"),
        "📖 " + ("72 柱魔神" if is_zh else "72 Demons"),
        "🕯️ " + ("儀式建議" if is_zh else "Ritual Guide"),
    ])

    with tabs[0]:
        _render_recommendations_tab(chart, is_zh)

    with tabs[1]:
        _render_natal_overview_tab(chart, is_zh)

    with tabs[2]:
        _render_electional_tab(chart, is_zh)

    with tabs[3]:
        _render_demon_browser_tab(chart, is_zh)

    with tabs[4]:
        _render_ritual_tab(chart, is_zh)


# ============================================================
# Tab 1: 個人化魔神推薦
# ============================================================

def _render_recommendations_tab(chart: GoetiaChart, is_zh: bool) -> None:
    """渲染個人化推薦分頁。"""

    # 路徑摘要
    st.subheader("🔮 " + ("你的 Goetia 路徑" if is_zh else "Your Goetia Path"))

    path_text = chart.path_summary_zh if is_zh else chart.path_summary_en
    st.markdown(
        f'<div class="ritual-box" style="border-color:rgba(200,100,30,0.5)">'
        f'{path_text}</div>',
        unsafe_allow_html=True,
    )

    # 最強行星 / 主導元素
    col1, col2, col3 = st.columns(3)
    with col1:
        pl = chart.strongest_planet_zh if is_zh else chart.strongest_planet
        pl_color = PLANET_COLORS.get(chart.strongest_planet, "#FFD700")
        st.markdown(
            f'<div style="text-align:center;padding:8px;background:rgba(20,10,5,0.7);'
            f'border-radius:8px;border:1px solid {pl_color}40">'
            f'<div style="color:{pl_color};font-size:0.75rem">{"最強行星" if is_zh else "Dominant Planet"}</div>'
            f'<div style="color:{pl_color};font-size:1.4rem;font-weight:bold">{pl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        el = chart.dominant_element_zh if is_zh else chart.dominant_element
        el_color = _elem_color(chart.dominant_element)
        st.markdown(
            f'<div style="text-align:center;padding:8px;background:rgba(20,10,5,0.7);'
            f'border-radius:8px;border:1px solid {el_color}40">'
            f'<div style="color:{el_color};font-size:0.75rem">{"主導元素" if is_zh else "Dominant Element"}</div>'
            f'<div style="color:{el_color};font-size:1.4rem;font-weight:bold">{el}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        asc = chart.ascendant_sign_zh if is_zh else chart.ascendant_sign
        st.markdown(
            f'<div style="text-align:center;padding:8px;background:rgba(20,10,5,0.7);'
            f'border-radius:8px;border:1px solid #FFD70040">'
            f'<div style="color:#b0a070;font-size:0.75rem">{"上升星座" if is_zh else "Ascendant"}</div>'
            f'<div style="color:#FFD700;font-size:1.4rem;font-weight:bold">{asc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 推薦摘要 SVG
    rec_svg = render_recommendation_summary_svg(chart, size=680)
    _render_html(rec_svg, height=150)

    st.markdown("---")
    st.subheader("👿 " + ("個人化魔神推薦（前 5 名）" if is_zh else "Personalized Demon Recommendations (Top 5)"))

    for i, rec in enumerate(chart.recommendations):
        _render_recommendation_card(rec, i + 1, is_zh)


def _render_recommendation_card(rec: DemonRecommendation, rank: int, is_zh: bool) -> None:
    """渲染單一推薦魔神卡片。"""
    demon = rec.demon
    el_color = _elem_color(demon.element)
    rank_color = _rank_color(demon.rank)

    name_display = f"{demon.name} — {demon.name_zh}"
    rank_display = f"{demon.rank_zh} ({demon.rank})" if is_zh else demon.rank
    planet_display = demon.planet_zh if is_zh else demon.planet
    element_display = demon.element_zh if is_zh else demon.element
    sign_display = demon.sign_zh if is_zh else demon.zodiac_sign
    powers = "、".join(demon.powers_zh[:3]) if is_zh else "; ".join(demon.powers_en[:3])
    score_label = rec.score_zh if is_zh else f"{rec.score * 100:.0f}% match"

    score_pct = int(rec.score * 100)

    st.markdown(f"""
<div class="demon-card">
  <div class="demon-card-title">
    <span style="color:#888;font-size:0.85rem">#{rank}</span>
    &nbsp;{name_display}
    <span style="color:{rank_color};font-size:0.85rem;font-weight:normal;margin-left:8px">
      {rank_display}
    </span>
  </div>
  <div class="demon-card-sub">
    <span style="color:{PLANET_COLORS.get(demon.planet,'#FFD700')}">{planet_display}</span>
    &nbsp;|&nbsp;
    <span style="color:{el_color}">{element_display}</span>
    &nbsp;|&nbsp;{sign_display}
    &nbsp;|&nbsp;{demon.legion_count} {"legions" if not is_zh else "個軍團"}
  </div>
  <div class="demon-card-text">
    {"能力：" if is_zh else "Powers: "}{powers}
  </div>
  <div class="rec-score-bar">
    <div class="rec-score-label">{score_label}</div>
    <div style="flex:1;background:rgba(80,50,30,0.3);height:8px;border-radius:4px">
      <div class="rec-score-fill"
           style="width:{score_pct}%;background:{rank_color};height:8px"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    with st.expander(
        f"🔍 " + (f"查看 {demon.name_zh} 詳情" if is_zh else f"View {demon.name} details"),
        expanded=(rank == 1),
    ):
        col_sigil, col_info = st.columns([1, 2])

        with col_sigil:
            sigil_svg = render_demon_sigil_svg(demon, size=260, highlighted=(rank == 1))
            _render_html(sigil_svg, height=270)

        with col_info:
            # 推薦理由
            st.markdown(f"**{'推薦理由' if is_zh else 'Why Recommended'}**")
            reasons = rec.reasons_zh if is_zh else rec.reasons_en
            for reason in reasons:
                st.markdown(f"• {reason}")

            # 命盤連結
            connections = rec.natal_connections_zh if is_zh else rec.natal_connections
            if connections:
                st.markdown(f"**{'命盤連結' if is_zh else 'Natal Connections'}**")
                for conn in connections:
                    st.caption(f"🔗 {conn}")

            # 最佳用途
            purpose = rec.best_purpose_zh if is_zh else rec.best_purpose_en
            st.markdown(
                f'<div class="ritual-box">{"🎯 最佳用途：" if is_zh else "🎯 Best Purpose: "}'
                f'{purpose}</div>',
                unsafe_allow_html=True,
            )

            # 外貌描述
            appearance = demon.appearance_zh if is_zh else demon.appearance_en
            if appearance:
                st.caption(f"{'👁 外貌：' if is_zh else '👁 Appearance: '}{appearance}")

        # 召喚語
        st.markdown(f"**{'召喚語' if is_zh else 'Invocation'}**")
        invocation = demon.invocation_zh if is_zh else demon.invocation_en
        st.markdown(f'<div class="invocation-box">📜 {invocation}</div>', unsafe_allow_html=True)

        # 安全提示
        safety = demon.safety_note_zh if is_zh else demon.safety_note_en
        if safety:
            st.markdown(
                f'<div class="safety-box">⚠️ {"安全提示：" if is_zh else "Safety Note: "}'
                f'{safety}</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# Tab 2: 命盤概覽
# ============================================================

def _render_natal_overview_tab(chart: GoetiaChart, is_zh: bool) -> None:
    """渲染命盤概覽分頁。"""
    st.subheader("🌐 " + ("Goetia 命盤概覽" if is_zh else "Goetia Natal Overview"))

    col_chart, col_elem = st.columns([3, 2])

    with col_chart:
        natal_svg = render_goetia_natal_svg(chart, size=500)
        _render_html(natal_svg, height=510)

    with col_elem:
        # 元素平衡圖
        st.markdown(f"**{'元素平衡' if is_zh else 'Elemental Balance'}**")
        elem_svg = render_element_balance_svg(chart, size=320)
        _render_html(elem_svg, height=170)

        st.markdown("---")

        # 工作目的
        st.markdown(f"**{'魔法工作目的' if is_zh else 'Magical Working Purpose'}**")
        purpose = chart.working_purpose_zh if is_zh else chart.working_purpose_en
        st.markdown(f'<div class="ritual-box">{purpose}</div>', unsafe_allow_html=True)

    # 行星 Goetia 對應表
    st.markdown("---")
    st.subheader("🪐 " + ("行星與魔神對應" if is_zh else "Planet–Demon Correspondences"))

    for pp in chart.planet_points:
        el_color = _elem_color(pp.element)
        planet_color = PLANET_COLORS.get(pp.planet_name, "#888")
        planet_display = pp.planet_zh if is_zh else pp.planet_name
        sign_display = pp.sign_zh if is_zh else pp.sign
        element_display = pp.element_zh if is_zh else pp.element
        retro = " ℞" if pp.is_retrograde else ""
        demons_list = ", ".join(pp.associated_demons[:3]) if pp.associated_demons else "—"

        st.markdown(
            f"<span style='color:{planet_color}'>**{planet_display}**</span>"
            f" {sign_display}{retro} (H{pp.house}) — "
            f"<span style='color:{el_color}'>{element_display}</span>"
            f" — Demons: `{demons_list}`",
            unsafe_allow_html=True,
        )


# ============================================================
# Tab 3: 選時占星
# ============================================================

def _render_electional_tab(chart: GoetiaChart, is_zh: bool) -> None:
    """渲染選時占星分頁。"""
    st.subheader("⏰ " + ("選時占星：未來 30 天最佳召喚時機" if is_zh else "Electional: Best Calling Windows (30 Days)"))

    primary = chart.primary_demon
    name_display = primary.name_zh if is_zh else primary.name
    planet_display = primary.planet_zh if is_zh else primary.planet

    st.info(
        f"{'為主要推薦魔神' if is_zh else 'Electional windows for primary demon'} "
        f"**{name_display}** "
        f"({'統治行星：' if is_zh else 'ruling planet: '}{planet_display})"
    )

    if not chart.electional_windows:
        st.warning("No electional windows computed." if not is_zh else "尚未計算選時窗口。")
        return

    # 品質篩選
    quality_filter = st.selectbox(
        "Filter by quality / 篩選品質" if is_zh else "Filter by quality",
        options=["All", "Excellent", "Good", "Fair"],
        index=0,
        key="goetia_quality_filter",
    )

    shown = 0
    for window in chart.electional_windows:
        if quality_filter != "All" and window.quality != quality_filter:
            continue
        shown += 1
        _render_electional_card(window, is_zh)

    if shown == 0:
        st.info(f"No {quality_filter} windows found." if not is_zh else f"未找到{quality_filter}品質的窗口。")

    # 注意事項
    st.markdown("---")
    st.markdown(
        f'<div class="safety-box">'
        f'{"⚠️ 選時建議僅供參考。實際召喚請結合更詳盡的行星時選擇（Planetary Hour Calculation），並確保充分的儀式準備。" if is_zh else "⚠️ Electional windows are guidelines only. For actual workings, also compute precise Planetary Hours and ensure full ritual preparation."}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_electional_card(window: ElectionalWindow, is_zh: bool) -> None:
    """渲染單一選時窗口卡片。"""
    qual_color = _quality_color(window.quality)
    quality_display = window.quality_zh if is_zh else window.quality
    reason = window.reason_zh if is_zh else window.reason_en
    ritual_prep = window.ritual_preparation_zh if is_zh else window.ritual_preparation_en
    day_display = window.day_of_week_zh if is_zh else window.day_of_week
    date_str = f"{window.year}-{window.month:02d}-{window.day:02d}"

    st.markdown(f"""
<div class="electional-card" style="--qual-color:{qual_color}">
  <div class="electional-title">
    <span style="color:{qual_color}">{quality_display}</span>
    &nbsp;·&nbsp;{date_str} ({day_display})
    &nbsp;·&nbsp;{window.hour_start}:00–{window.hour_end}:00
  </div>
  <div class="electional-text">
    {reason}<br/>
    <small style="color:#a09080">{ritual_prep}</small>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Tab 4: 72 柱魔神瀏覽器
# ============================================================

def _render_demon_browser_tab(chart: GoetiaChart, is_zh: bool) -> None:
    """渲染 72 柱魔神完整瀏覽器分頁。"""
    st.subheader("📖 " + ("72 柱魔神完整資料庫" if is_zh else "72 Demons Complete Database"))

    if not chart.all_demons:
        st.warning("Demon database not loaded." if not is_zh else "魔神資料庫未載入。")
        return

    # 篩選器
    col_planet, col_elem, col_rank, col_search = st.columns(4)

    planets = ["All"] + sorted(set(d.planet for d in chart.all_demons))
    elements = ["All"] + sorted(set(d.element for d in chart.all_demons))
    ranks = ["All"] + sorted(set(d.rank for d in chart.all_demons))

    with col_planet:
        planet_filter = st.selectbox(
            "Planet / 行星" if is_zh else "Planet",
            options=planets,
            key="goetia_planet_filter",
        )
    with col_elem:
        elem_filter = st.selectbox(
            "Element / 元素" if is_zh else "Element",
            options=elements,
            key="goetia_elem_filter",
        )
    with col_rank:
        rank_filter = st.selectbox(
            "Rank / 等級" if is_zh else "Rank",
            options=ranks,
            key="goetia_rank_filter",
        )
    with col_search:
        search_query = st.text_input(
            "Search / 搜尋" if is_zh else "Search",
            key="goetia_search",
            placeholder="Name / 名稱",
        )

    # 篩選
    filtered = chart.all_demons
    if planet_filter != "All":
        filtered = [d for d in filtered if d.planet == planet_filter]
    if elem_filter != "All":
        filtered = [d for d in filtered if d.element == elem_filter]
    if rank_filter != "All":
        filtered = [d for d in filtered if d.rank == rank_filter]
    if search_query:
        sq = search_query.lower()
        filtered = [
            d for d in filtered
            if sq in d.name.lower() or sq in d.name_zh or sq in " ".join(d.keywords_en).lower()
        ]

    st.caption(f"{'顯示' if is_zh else 'Showing'} {len(filtered)} / 72 {'柱魔神' if is_zh else 'demons'}")

    # 列表顯示
    for demon in filtered:
        el_color = _elem_color(demon.element)
        rank_color = _rank_color(demon.rank)
        powers_short = "、".join(demon.powers_zh[:2]) if is_zh else "; ".join(demon.powers_en[:2])

        header = (
            f"#{demon.number:02d} **{demon.name}** — {demon.name_zh} "
            f"({demon.rank_zh}/{demon.rank}) "
            f"| {demon.planet_zh if is_zh else demon.planet} "
            f"| {demon.element_zh if is_zh else demon.element}"
        )

        with st.expander(header, expanded=False):
            col_sigil, col_detail = st.columns([1, 3])

            with col_sigil:
                sigil_svg = render_demon_sigil_svg(demon, size=180, show_labels=False)
                _render_html(sigil_svg, height=190)

            with col_detail:
                st.markdown(f"**{'能力' if is_zh else 'Powers'}:** {powers_short}")
                appearance = demon.appearance_zh if is_zh else demon.appearance_en
                if appearance:
                    st.caption(f"{'外貌' if is_zh else 'Appearance'}: {appearance}")

                keywords = "、".join(demon.keywords_zh) if is_zh else ", ".join(demon.keywords_en)
                st.markdown(
                    f"<small style='color:{el_color}'>🔑 {keywords}</small>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<small style='color:{rank_color}'>"
                    f"{'方向' if is_zh else 'Direction'}: {demon.direction_zh if is_zh else demon.direction}"
                    f" | {'星座' if is_zh else 'Sign'}: {demon.sign_zh if is_zh else demon.zodiac_sign}"
                    f" | {'軍團' if is_zh else 'Legions'}: {demon.legion_count}"
                    f"</small>",
                    unsafe_allow_html=True,
                )

            # 召喚語
            invocation = demon.invocation_zh if is_zh else demon.invocation_en
            if invocation:
                st.markdown(
                    f'<div class="invocation-box" style="margin-top:8px">📜 {invocation}</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# Tab 5: 儀式建議
# ============================================================

def _render_ritual_tab(chart: GoetiaChart, is_zh: bool) -> None:
    """渲染儀式建議分頁。"""
    st.subheader("🕯️ " + ("儀式建議與召喚指南" if is_zh else "Ritual Guide & Summoning Instructions"))

    primary = chart.primary_demon

    # 主要魔神召喚語
    st.markdown(f"### {'主要魔神召喚語' if is_zh else 'Primary Demon Invocation'}")
    name_display = primary.name_zh if is_zh else primary.name
    st.markdown(f"**{name_display}** ({primary.rank_zh if is_zh else primary.rank})")

    invocation = chart.primary_invocation_zh if is_zh else chart.primary_invocation_en
    st.markdown(f'<div class="invocation-box">📜 {invocation}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 儀式步驟
    st.markdown(f"### {'標準儀式步驟' if is_zh else 'Standard Ritual Steps'}")
    steps = chart.ritual_steps_zh if is_zh else chart.ritual_steps_en
    for i, step in enumerate(steps, 1):
        st.markdown(f"{i}. {step}")

    st.markdown("---")

    # 遣返步驟
    st.markdown(f"### {'遣返與收場步驟' if is_zh else 'Banishing & Closing Steps'}")
    banishing = chart.banishing_steps_zh if is_zh else chart.banishing_steps_en
    for i, step in enumerate(banishing, 1):
        st.markdown(f"{i}. {step}")

    st.markdown("---")

    # 安全概述
    st.markdown(f"### {'安全提示與注意事項' if is_zh else 'Safety Overview'}")
    safety = chart.safety_overview_zh if is_zh else chart.safety_overview_en
    st.markdown(f'<div class="safety-box">⚠️ {safety}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 印記參考
    st.markdown(f"### {'前 3 名推薦魔神印記' if is_zh else 'Top 3 Demon Sigils'}")
    sig_cols = st.columns(3)
    for i, rec in enumerate(chart.recommendations[:3]):
        with sig_cols[i]:
            sigil_svg = render_demon_sigil_svg(rec.demon, size=220, highlighted=True)
            _render_html(sigil_svg, height=230)
            st.caption(
                f"{rec.demon.name} — {rec.demon.name_zh}\n"
                f"{rec.demon.rank} of {rec.demon.legion_count} Legions"
            )

    # 參考書目
    with st.expander("📚 " + ("參考資料" if is_zh else "References"), expanded=False):
        st.markdown("""
- **S.L. MacGregor Mathers & Aleister Crowley**: *The Goetia — The Lesser Key of Solomon* (1904)
- **Joseph H. Peterson**: *The Lesser Key of Solomon — Lemegeton Clavicula Salomonis* (Ibis Press, 2001)
- **Stephen Skinner & David Rankine**: *The Goetia of Dr Rudd* (Golden Hoard, 2007)
- **Lon Milo DuQuette**: *The Key to Solomon's Key* (CCC Publishing, 2006)
- **Israel Regardie**: *The Golden Dawn* (Llewellyn, 1971)
- **Jake Stratton-Kent**: *The True Grimoire* (Scarlet Imprint, 2009)
""")
