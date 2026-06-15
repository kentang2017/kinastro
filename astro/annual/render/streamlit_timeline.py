"""Streamlit UI for solar-return annual timeline."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from astro.annual.models import SolarReturnTimeline
from astro.models import BirthData
from astro.sanshi.liuren import render_liuren_chart, render_lunming_report
from core.cached_computations import _birth_sig, compute_annual_sr_timeline_cached
from ui.ai_chat import set_ai_context


LEVEL_COLORS = {
    "大吉": "#1b8a3e",
    "吉": "#4caf50",
    "平": "#f0ad4e",
    "凶": "#e67e22",
    "大凶": "#c0392b",
}


def _level_color(level: str) -> str:
    return LEVEL_COLORS.get(level, "#888888")


def _timeline_to_dataframe(timeline: SolarReturnTimeline) -> pd.DataFrame:
    rows = []
    for year in timeline.years:
        lr = year.liuren_jixiong
        rows.append(
            {
                "虛歲": year.age,
                "SR年": year.year,
                "SR時間": year.exact_sr_datetime_local.strftime("%Y-%m-%d %H:%M"),
                "六壬": year.system_scores.get("liuren"),
                "六壬等級": lr.level.value if lr else "—",
                "三傳": lr.san_chuan_summary[:30] if lr else "—",
                "紫微": year.system_scores.get("ziwei"),
                "八字": year.system_scores.get("bazi"),
                "七政": year.system_scores.get("qizheng"),
                "西洋": year.system_scores.get("western"),
                "綜合摘要": year.integrated_interpretation[:60],
            }
        )
    return pd.DataFrame(rows)


def render_annual_sr_timeline_panel(birth: BirthData) -> None:
    """Render SR annual timeline inside an existing Streamlit tab."""
    st.markdown("### 🌞 太陽回歸流年多體系時間軸")
    st.caption("以太陽回歸精確時刻起六壬祿命課，並列紫微、八字、七政、西洋 SR 獨立評分。")

    current_year = datetime.now().year
    default_start = max(birth.year + 1, current_year - 2)
    col1, col2, col3 = st.columns(3)
    with col1:
        start_year = st.number_input("起始 SR 年", min_value=birth.year, max_value=current_year + 30, value=default_start)
    with col2:
        end_year = st.number_input("結束 SR 年", min_value=int(start_year), max_value=current_year + 30, value=min(int(start_year) + 4, current_year + 5))
    with col3:
        systems = st.multiselect(
            "包含體系",
            options=["liuren", "ziwei", "bazi", "qizheng", "western"],
            default=["liuren", "ziwei", "bazi", "qizheng", "western"],
        )

    enable_ai_context = st.checkbox(
        "啟用 AI 詳斷上下文（需設定 Cerebras/OpenAI API Key）",
        value=False,
        key="annual_sr_enable_ai",
    )

    if st.button("計算 SR 流年時間軸", type="primary", key="annual_sr_compute"):
        with st.spinner("計算中…"):
            params = birth.to_compute_kwargs()
            gender = birth.legacy_gender or "male"
            st.session_state["annual_sr_timeline"] = compute_annual_sr_timeline_cached(
                _birth_sig(params),
                int(start_year),
                int(end_year),
                tuple(sorted(systems)),
                gender=gender,
            )

    timeline = st.session_state.get("annual_sr_timeline")
    if timeline is None:
        st.info("設定年份區間後，點擊「計算 SR 流年時間軸」。")
        return

    st.success(timeline.trend_summary or "計算完成")
    df = _timeline_to_dataframe(timeline)
    st.dataframe(
        df.style.applymap(
            lambda value: f"color: {_level_color(value)}; font-weight: 700"
            if value in LEVEL_COLORS
            else "",
            subset=["六壬等級"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    plot_df = pd.DataFrame(
        {
            "year": [y.year for y in timeline.years],
            "age": [y.age for y in timeline.years],
            "liuren": [y.system_scores.get("liuren", 50) for y in timeline.years],
            "ziwei": [y.system_scores.get("ziwei", 50) for y in timeline.years],
            "bazi": [y.system_scores.get("bazi", 50) for y in timeline.years],
            "qizheng": [y.system_scores.get("qizheng", 50) for y in timeline.years],
            "western": [y.system_scores.get("western", 50) for y in timeline.years],
        }
    )
    melted = plot_df.melt(id_vars=["year", "age"], var_name="體系", value_name="分數")
    fig = px.line(
        melted,
        x="year",
        y="分數",
        color="體系",
        markers=True,
        title="各體系獨立評分趨勢（虛歲對照）",
        hover_data=["age"],
    )
    fig.update_layout(height=360, legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    year_labels = [f"{y.age}歲（{y.year}）" for y in timeline.years]
    selected = st.selectbox("展開年度詳情", options=year_labels, index=len(year_labels) - 1)
    selected_year = timeline.years[year_labels.index(selected)]

    with st.expander("年度詳細解讀", expanded=True):
        st.markdown(f"**SR 精確時間：** {selected_year.exact_sr_datetime_local}")
        st.markdown(f"**綜合摘要：** {selected_year.integrated_interpretation}")
        if selected_year.liuren_jixiong:
            lr = selected_year.liuren_jixiong
            st.markdown(
                f"**大六壬 {lr.score:.0f}（{lr.level.value}）** — {lr.affair_summary}"
            )
            if lr.opportunities:
                st.markdown("機會：" + "；".join(lr.opportunities))
            if lr.risks:
                st.markdown("留意：" + "；".join(lr.risks))
        for key, snap in selected_year.other_chinese_systems.items():
            st.markdown(f"**{key} {snap.score:.0f}（{snap.level.value}）** — {snap.summary}")
        if selected_year.western_sr:
            st.markdown(f"**西洋 SR** — {selected_year.western_sr.summary}")
        qz = selected_year.other_chinese_systems.get("qizheng")
        if qz and qz.raw.get("resonance_hits"):
            hits = qz.raw["resonance_hits"][:3]
            st.markdown(
                "**七政守照共振：** "
                + "；".join(
                    f"{hit.get('star')}{hit.get('aspect')}({hit.get('score'):+})"
                    for hit in hits
                )
            )
        ziwei = selected_year.other_chinese_systems.get("ziwei")
        if ziwei:
            st.markdown(
                f"**紫微流年宮 / 小限宮：** "
                f"{ziwei.raw.get('liunian_palace', '—')} / {ziwei.raw.get('xiaoxian_palace', '—')}"
            )

    if enable_ai_context:
        from astro.annual.ai.prompts import build_annual_year_prompt

        set_ai_context(
            "tab_liuren_annual_sr",
            selected_year.model_dump(),
            build_annual_year_prompt(timeline, selected_year),
        )
        st.caption("已將本年度 SR 流年資料送入底部 AI 對話框，可直接提問。")

    if selected_year.liuren_chart:
        st.divider()
        st.markdown("#### 大六壬 SR 流年課式")
        render_liuren_chart(
            selected_year.liuren_chart,
            benming_zhi=timeline.benming_zhi,
        )
        if selected_year.liuren_lunming:
            render_lunming_report(selected_year.liuren_lunming)

    pdf_bytes = _try_generate_pdf(timeline, selected_year)
    if pdf_bytes:
        st.download_button(
            "下載本年度 PDF 報告",
            data=pdf_bytes,
            file_name=f"kinastro_sr_annual_{selected_year.year}.pdf",
            mime="application/pdf",
            key="annual_sr_pdf_download",
        )


def _try_generate_pdf(timeline: SolarReturnTimeline, year) -> bytes | None:
    try:
        from astro.annual.render.pdf_annual_report import generate_annual_sr_pdf

        return generate_annual_sr_pdf(timeline, year)
    except Exception:
        return None