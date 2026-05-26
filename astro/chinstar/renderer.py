"""ChinStar (WanHua XianQin) renderer for Streamlit."""

from __future__ import annotations

from typing import Any, Callable, Dict

import streamlit as st


def render_chinstar_chart(
    chart_data: Dict[str, Any],
    after_chart_hook: Callable[[], None] | None = None,
) -> None:
    """Render ChinStar chart in Streamlit.

    Args:
        chart_data: Chart data from compute_chinstar_chart
        after_chart_hook: Optional callback to run after rendering (e.g., AI button)
    """
    from astro.chinstar.chinstar import WanHuaXianQin

    # Format the chart
    formatted = WanHuaXianQin.format_chart(chart_data)

    st.markdown("### 萬化仙禽 - WanHua XianQin Chart")

    # Basic info
    basic = chart_data.get("basic_info", {})
    if basic:
        cols = st.columns(4)
        cols[0].metric("Year", basic.get("year", ""))
        cols[1].metric("Month", basic.get("month", ""))
        cols[2].metric("Day", basic.get("day", ""))
        cols[3].metric("Hour", basic.get("hour", ""))

        cols2 = st.columns(4)
        cols2[0].info(f"Gender: {basic.get('gender', '')}")
        cols2[1].info(f"San Yuan: {basic.get('san_yuan', '')}")
        cols2[2].info(f"Day/Night: {basic.get('day_night', '')}")
        cols2[3].info(f"Season: {basic.get('season', '')}")

    # Palaces
    palaces = chart_data.get("palaces", {})
    if palaces:
        st.markdown("#### Palaces")
        palace_cols = st.columns(3)
        if "tai_gong" in palaces:
            palace_cols[0].success(f"**Tai Gong **(胎宮): {palaces['tai_gong']['branch']}")
        if "ming_gong" in palaces:
            palace_cols[1].success(f"**Ming Gong **(命宮): {palaces['ming_gong']['branch']}")
        if "shen_gong" in palaces:
            palace_cols[2].success(f"**Shen Gong **(身宮): {palaces['shen_gong']['branch']}")

        # Twelve palaces
        twelve = palaces.get("twelve", {})
        if twelve:
            st.markdown("##### Twelve Palaces")
            for palace_name, branch in twelve.items():
                st.text(f"{palace_name}: {branch}")

    # Stars
    stars = chart_data.get("stars", {})
    if stars:
        st.markdown("#### Main Stars")
        star_cols = st.columns(3)
        star_cols[0].info(f"**Tai Xing **(胎星): {stars.get('tai_xing', '')}")
        star_cols[1].info(f"**Ming Xing **(命星): {stars.get('ming_xing', '')}")
        star_cols[2].info(f"**Shen Xing **(身星): {stars.get('shen_xing', '')}")

        # Derived stars
        derived = stars.get("derived", {})
        if derived:
            st.markdown("##### Derived Stars")
            for star_name, star_qin in derived.items():
                st.text(f"{star_name}: {star_qin}")

    # Swallow analysis
    swallow = chart_data.get("swallow_analysis", {})
    if swallow:
        st.markdown("#### Swallow Analysis (吞啗)")
        for pair, result in swallow.items():
            st.text(f"{pair}: {result}")

    # Personality
    personality = chart_data.get("personality", {})
    if personality:
        st.markdown("#### Personality")
        st.text(personality.get("tai_xing", ""))
        st.text(personality.get("ming_xing", ""))

    # Pattern
    pattern = chart_data.get("pattern", {})
    if pattern:
        st.markdown("#### Pattern Analysis")
        st.info(pattern)

    # Run hook if provided
    if after_chart_hook:
        after_chart_hook()
