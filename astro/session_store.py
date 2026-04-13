"""
astro/session_store.py — 排盤儲存 (Chart Save/Load)

Lightweight chart parameter storage via Streamlit session state + JSON file download/upload.
"""
import json
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SavedChart:
    name: str
    system_type: str
    timestamp: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    gender: str


def create_saved_chart(name, params, system_type="all"):
    return SavedChart(
        name=name, system_type=system_type,
        timestamp=datetime.now().isoformat(),
        year=params.get("year", 2000), month=params.get("month", 1),
        day=params.get("day", 1), hour=params.get("hour", 12),
        minute=params.get("minute", 0), timezone=params.get("timezone", 0.0),
        latitude=params.get("latitude", 0.0),
        longitude=params.get("longitude", 0.0),
        location_name=params.get("location_name", ""),
        gender=params.get("gender", "male"),
    )


def init_session_store():
    import streamlit as st
    if "saved_charts" not in st.session_state:
        st.session_state["saved_charts"] = []


def save_chart(name, params, system_type="all"):
    import streamlit as st
    init_session_store()
    chart = create_saved_chart(name, params, system_type)
    charts = st.session_state["saved_charts"]
    charts.append(asdict(chart))
    if len(charts) > 20:
        charts[:] = charts[-20:]


def get_saved_charts():
    import streamlit as st
    return st.session_state.get("saved_charts", [])


def delete_chart(index):
    import streamlit as st
    charts = st.session_state.get("saved_charts", [])
    if 0 <= index < len(charts):
        charts.pop(index)


def export_saved_charts():
    import streamlit as st
    charts = st.session_state.get("saved_charts", [])
    return json.dumps(charts, ensure_ascii=False, indent=2)


def import_saved_charts(json_str):
    import streamlit as st
    init_session_store()
    data = json.loads(json_str)
    count = 0
    for item in data:
        st.session_state["saved_charts"].append(item)
        count += 1
    return count


def render_chart_manager():
    """Render chart save/load UI in sidebar."""
    import streamlit as st
    init_session_store()

    st.subheader("📋 Chart Manager / 排盤記錄")

    with st.expander("💾 Save Current / 儲存", expanded=False):
        chart_name = st.text_input("Name / 名稱", key="save_chart_name")
        if st.button("Save / 儲存", key="save_chart_btn") and chart_name:
            st.success(f"Use save_chart() from app.py to save '{chart_name}'")

    saved = get_saved_charts()
    if saved:
        with st.expander(f"📂 Saved ({len(saved)}) / 已儲存"):
            for i, chart in enumerate(saved):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{chart.get('name','')}** — "
                             f"{chart.get('location_name','')} "
                             f"({chart.get('year','')}/{chart.get('month','')}/{chart.get('day','')})")
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        delete_chart(i)
                        st.rerun()

    with st.expander("📤 Export/Import / 匯出匯入"):
        if saved:
            st.download_button("📥 Export All / 匯出",
                             data=export_saved_charts(),
                             file_name="kinastro_charts.json",
                             mime="application/json",
                             key="export_charts_btn")
        uploaded = st.file_uploader("📤 Import / 匯入", type=["json"],
                                    key="import_file")
        if uploaded:
            content = uploaded.read().decode("utf-8")
            count = import_saved_charts(content)
            st.success(f"Imported {count} charts / 已匯入 {count} 個排盤")
