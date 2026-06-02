"""Streamlit renderer for Malay Ilmu Nujum systems."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from astro.i18n import auto_cn
from astro.malay import MalayNujumEngine
from frontend.malay_nujum_renderer import render_mata_angin_wheel


def _render_process(result: dict[str, object]) -> None:
    process = result.get("process_summary", {})
    if isinstance(process, dict):
        st.markdown(f"**{auto_cn('計算摘要', 'Computation Summary')}**")
        st.write(process.get("zh"))
        st.caption(process.get("en"))


def render_streamlit(default_birth_datetime: datetime | None = None) -> dict[str, object]:
    """Render Malay Nujum tools and return last payload for AI context."""
    engine = MalayNujumEngine()
    default_dt = default_birth_datetime or datetime.now()

    st.markdown("## 🧭 馬來 Ilmu Nujum（Mata Angin · Bintang Tujuh · Naga）")
    st.caption(
        auto_cn(
            "整合馬來傳統冷門占法：Mata Angin Lapan、Bintang Tujuh、Perkisaran Naga，並提供 Bintang Duabelas 擴充解讀。",
            "Integrated Malay traditional methods: Mata Angin Lapan, Bintang Tujuh, Perkisaran Naga, plus enhanced Bintang Duabelas reading.",
        )
    )

    name_col, mother_col, date_col, time_col = st.columns([1.2, 1.2, 1, 1])
    with name_col:
        name = st.text_input(auto_cn("姓名 / Name", "Name"), key="malay_nujum_name")
    with mother_col:
        mother_name = st.text_input(auto_cn("母親姓名（十二星增強）", "Mother's name (for Duabelas+)"), key="malay_nujum_mother")
    with date_col:
        selected_date = st.date_input(auto_cn("日期", "Date"), value=default_dt.date(), key="malay_nujum_date")
    with time_col:
        selected_time = st.time_input(auto_cn("時間", "Time"), value=default_dt.time(), key="malay_nujum_time")
    moment = datetime.combine(selected_date, selected_time)

    tab_mata, tab_tujuh, tab_duabelas, tab_naga = st.tabs(
        [
            auto_cn("🧭 Mata Angin Lapan", "Mata Angin Lapan"),
            auto_cn("🌟 Bintang Tujuh", "Bintang Tujuh"),
            auto_cn("⭐ Bintang Duabelas+", "Bintang Duabelas+"),
            auto_cn("🐉 Perkisaran Naga", "Perkisaran Naga"),
        ]
    )

    latest_payload: dict[str, object] = {}

    with tab_mata:
        if name.strip():
            mata = engine.compute_mata_angin_lapan(name, moment)
            latest_payload = mata
            verdict = mata.get("fortune", {})
            st.metric(
                auto_cn("吉凶判斷", "Fortune verdict"),
                verdict.get("verdict_zh") or verdict.get("verdict", "—"),
            )
            render_mata_angin_wheel(mata, chart_key="malay_nujum_mata_angin_chart")
            _render_process(mata)
            advice = mata.get("advice", {}).get("zh", {})
            if advice.get("best_action"):
                st.markdown(f"- {advice['best_action']}")
            if advice.get("avoid_action"):
                st.markdown(f"- {advice['avoid_action']}")
            with st.expander(auto_cn("八方向細節", "Eight-direction details"), expanded=False):
                st.json(mata.get("sectors", []))
        else:
            st.info(auto_cn("請先輸入姓名以啟動 Mata Angin 計算。", "Enter a name to run Mata Angin calculations."))

    with tab_tujuh:
        if name.strip():
            tujuh = engine.compute_bintang_tujuh(name, moment)
            latest_payload = tujuh
            star = tujuh.get("star", {})
            st.metric(auto_cn("主導星", "Dominant Star"), f"{star.get('name_zh', '')} / {star.get('name_en', '')}")
            st.metric(auto_cn("吉凶", "Verdict"), tujuh.get("fortune", {}).get("verdict_zh", "—"))
            _render_process(tujuh)
            st.markdown(f"**{auto_cn('實用建議', 'Practical Advice')}**: {tujuh.get('advice', {}).get('zh', {}).get('timing', '')}")
            with st.expander(auto_cn("七星結果 JSON", "Bintang Tujuh JSON"), expanded=False):
                st.json(tujuh)
        else:
            st.info(auto_cn("請先輸入姓名以計算七星結果。", "Enter a name first to compute Bintang Tujuh."))

    with tab_duabelas:
        if name.strip() and mother_name.strip():
            duabelas = engine.compute_bintang_duabelas_plus(name, mother_name)
            latest_payload = duabelas
            reading = duabelas.get("reading", {})
            house = reading.get("house", {})
            st.metric(auto_cn("落宮", "Mapped House"), house.get("house_number", "—"))
            _render_process(duabelas)
            st.markdown(duabelas.get("interpretation_template", {}).get("zh", {}).get("summary", ""))
            with st.expander(auto_cn("完整擴充解讀 JSON", "Enhanced Reading JSON"), expanded=False):
                st.json(duabelas)
        else:
            st.info(auto_cn("請輸入本人與母親姓名以生成 Bintang Duabelas+。", "Enter both personal and mother names for Bintang Duabelas+."))

    with tab_naga:
        naga = engine.compute_perkisaran_naga(moment)
        latest_payload = naga
        rec = naga.get("recommendations", {})
        st.markdown(f"**{auto_cn('建築吉向', 'Construction directions')}**: {', '.join(rec.get('construction_zh', []))}")
        st.markdown(f"**{auto_cn('種植吉向', 'Planting directions')}**: {', '.join(rec.get('planting_zh', []))}")
        st.markdown(f"**{auto_cn('避開方向', 'Avoid directions')}**: {', '.join(rec.get('avoid_zh', []))}")
        _render_process(naga)
        with st.expander(auto_cn("龍行週期 JSON", "Dragon cycle JSON"), expanded=False):
            st.json(naga)

    return latest_payload
