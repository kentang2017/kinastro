from __future__ import annotations

from datetime import datetime
from typing import Optional

import streamlit as st

from astro.chart_renderer_v2 import build_cultural_svg
from astro.horary.renderer import render_western_horary_svg
from astro.i18n import auto_cn, get_lang
from .sports_horary import (
    SportsHoraryResult,
    TeamNatalInput,
    analyze_event_chart_with_team_natal,
    analyze_sports_horary,
    build_ai_interpretation_prompt,
)


_SPORTS_CSS = """
<style>
.sports-header {
    background: linear-gradient(135deg, #0b1622 0%, #112437 55%, #18324a 100%);
    border: 1px solid rgba(80, 190, 120, 0.35);
    border-left: 6px solid #2ecc71;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 14px;
}
.sports-header h2 { margin: 0; color: #e8fff0; }
.sports-header p { margin: 6px 0 0; color: #9fd8b5; font-size: .9rem; }
.sports-card {
    background: rgba(10, 16, 24, .75);
    border: 1px solid rgba(110, 140, 170, .25);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.bar-wrap { display: flex; gap: 8px; align-items: center; margin: 4px 0; }
.bar-l { height: 10px; background: #2ecc71; border-radius: 99px; }
.bar-r { height: 10px; background: #e74c3c; border-radius: 99px; }
.disclaimer {
    background: rgba(241, 196, 15, .09);
    border-left: 4px solid #f1c40f;
    border-radius: 8px;
    padding: 10px 12px;
    color: #f6e48d;
    font-size: .87rem;
}
</style>
"""


def _render_dashboard(result: SportsHoraryResult, lang: str) -> None:
    p1 = result.match_analysis.winner_probability[result.team1]
    p2 = result.match_analysis.winner_probability[result.team2]
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="sports-card">', unsafe_allow_html=True)
        st.subheader(auto_cn("勝率儀表板", "Win Probability"))
        st.write(f"{result.team1}: **{p1:.1%}**")
        st.markdown(f'<div class="bar-wrap"><div class="bar-l" style="width:{int(p1*100)}%"></div></div>', unsafe_allow_html=True)
        st.write(f"{result.team2}: **{p2:.1%}**")
        st.markdown(f'<div class="bar-wrap"><div class="bar-r" style="width:{int(p2*100)}%"></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="sports-card">', unsafe_allow_html=True)
        st.subheader(auto_cn("進階指標", "Advanced Indicators"))
        st.write(auto_cn(f"傷病風險（{result.team1}/{result.team2}）：{result.advanced.injury_risk_team1:.1%} / {result.advanced.injury_risk_team2:.1%}",
                         f"Injury risk ({result.team1}/{result.team2}): {result.advanced.injury_risk_team1:.1%} / {result.advanced.injury_risk_team2:.1%}"))
        st.write(auto_cn(f"爆冷/逆轉指標：{result.advanced.upset_indicator:.1%}",
                         f"Upset index: {result.advanced.upset_indicator:.1%}"))
        st.caption(result.advanced.season_trend_hint)
        st.caption(result.advanced.electional_hint)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sports-card">', unsafe_allow_html=True)
    st.subheader(auto_cn("核心證據（Testimonies）", "Core Testimonies"))
    for t in result.match_analysis.key_testimonies[:10]:
        st.write(f"- {(t.description_zh if lang == 'zh' else t.description_en)}")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_examples(lang: str) -> None:
    st.markdown('<div class="sports-card">', unsafe_allow_html=True)
    st.subheader(auto_cn("真實範例（足球 / 籃球 / 拳擊）", "Real-world examples (Football / Basketball / Boxing)"))
    st.markdown(
        auto_cn(
            "- 足球：英超焦點戰（主隊受讓）\n- 籃球：季後賽 G7（背靠背疲勞）\n- 拳擊：世界拳王戰（中立場地）",
            "- Football: EPL headliner (home underdog)\n- Basketball: Playoff Game 7 (back-to-back fatigue)\n- Boxing: World title fight (neutral venue)",
        )
    )
    st.markdown('</div>', unsafe_allow_html=True)


def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    **kwargs,
) -> None:
    st.markdown(_SPORTS_CSS, unsafe_allow_html=True)
    lang = get_lang()

    st.markdown(
        '<div class="sports-header">'
        f'<h2>{auto_cn("🏟️ Sports Astrology 運動占星", "🏟️ Sports Astrology")}</h2>'
        f'<p>{auto_cn("以 John Frawley 傳統 Horary 為核心，輸出勝負傾向與概率化建議。", "Frawley-style traditional horary with probabilistic match guidance.")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        match_name = st.text_input(auto_cn("比賽名稱", "Match Name"), value="EPL Match")
        team1 = st.text_input(auto_cn("主隊 / Team 1", "Home / Team 1"), value="Team A")
    with c2:
        team2 = st.text_input(auto_cn("客隊 / Team 2", "Away / Team 2"), value="Team B")
        preferred = st.selectbox(
            auto_cn("喜好隊（可選）", "Preferred Side (Optional)"),
            options=["", team1, team2],
            format_func=lambda x: auto_cn("無", "None") if x == "" else x,
        )
    with c3:
        question = st.text_input(
            auto_cn("問句（可選）", "Question (Optional)"),
            value="Who will win this match?",
        )

    if st.button(auto_cn("開始運動占星分析", "Run Sports Horary Analysis"), type="primary"):
        result = analyze_sports_horary(
            match_name=match_name,
            team1=team1,
            team2=team2,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            preferred_team=preferred or None,
            question_text=question,
        )
        st.session_state["sports_last_result"] = result

    result: Optional[SportsHoraryResult] = st.session_state.get("sports_last_result")
    if not result:
        _render_examples(lang)
        st.info(auto_cn("先輸入比賽資訊並執行分析。", "Enter match data and run analysis first."))
        return

    col_chart, col_info = st.columns([3, 2])
    with col_chart:
        svg = render_western_horary_svg(result.chart)
        wrapped = build_cultural_svg(svg, "tab_sports_astrology", title=auto_cn("比賽 Horary 星盤", "Match Horary Chart"))
        st.markdown(wrapped, unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="sports-card">', unsafe_allow_html=True)
        st.subheader(auto_cn("文字結論", "Text Conclusion"))
        st.write(result.match_analysis.explanation)
        st.markdown('</div>', unsafe_allow_html=True)

    _render_dashboard(result, lang)

    st.markdown('<div class="sports-card">', unsafe_allow_html=True)
    st.subheader(auto_cn("互動時間軸（比賽前後）", "Interactive Timeline (Pre/Post Match)"))
    for item in result.timeline_transits:
        st.write(f"- **{item['label']}**: {item['time']}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sports-card">', unsafe_allow_html=True)
    st.subheader(auto_cn("Event + Team Natal 對照（Dashboard）", "Event + Team Natal Comparison"))
    with st.expander(auto_cn("快速示例：比較兩隊本命", "Quick example: compare two natal teams"), expanded=False):
        d = datetime(year, month, day, hour, minute)
        demo = analyze_event_chart_with_team_natal(
            event_year=d.year,
            event_month=d.month,
            event_day=d.day,
            event_hour=d.hour,
            event_minute=d.minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            teams=[
                TeamNatalInput(team_name=team1, year=2000, month=1, day=1),
                TeamNatalInput(team_name=team2, year=2001, month=1, day=1),
            ],
        )
        for row in demo:
            st.write(f"- {row.team}: **{row.synastry_score:+.2f}** ({', '.join(row.key_aspects[:3]) or '—'})")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sports-card">', unsafe_allow_html=True)
    st.subheader(auto_cn("AI 解讀模板", "AI Interpretation Template"))
    st.code(build_ai_interpretation_prompt(result, lang=lang), language="text")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="disclaimer">'
        + auto_cn(
            "⚠️ 占星僅供參考，非投資或保證結果。請結合傷病、戰術、臨場與資金管理。",
            "⚠️ Astrology is for reference only, not a guaranteed betting signal. Combine with injuries, tactics, and risk management.",
        )
        + '</div>',
        unsafe_allow_html=True,
    )
