"""Streamlit renderer for Myanmar Bedin / Mahabote."""

from __future__ import annotations

from .models import LanguageCode, MyanmarMahaboteChart


def render_streamlit(chart: MyanmarMahaboteChart, *, lang: LanguageCode = "zh", show_house_board: bool = True) -> None:
    """Render a computed Myanmar Mahabote chart in Streamlit."""
    import streamlit as st

    title = "緬甸 Bedin / Mahabote（強化版）" if lang == "zh" else "Myanmar Bedin / Mahabote (Enhanced)"
    st.subheader(title)
    st.markdown(chart.zodiac_wheel_svg, unsafe_allow_html=True)

    if show_house_board:
        st.markdown(chart.house_board_svg, unsafe_allow_html=True)

    st.markdown("### 核心摘要 / Core Summary")
    st.write(
        {
            "myanmar_year": chart.myanmar_year,
            "year_mod7": chart.year_mod7,
            "start_house": chart.start_house_name_zh if lang == "zh" else chart.start_house_name_en,
            "start_lord": chart.start_lord_planet_zh if lang == "zh" else chart.start_lord_planet_en,
            "natal_animal": chart.natal_animal_zh if lang == "zh" else chart.natal_animal_en,
        }
    )

    st.markdown("### 性格與方位 / Traits & Directions")
    st.write(list(chart.natal_traits_zh if lang == "zh" else chart.natal_traits_en))
    st.write(list(chart.direction_advice_zh if lang == "zh" else chart.direction_advice_en))

    st.markdown("### 流年對照 / Flow-Year Overlay")
    overlay = chart.current_year_overlay if lang == "zh" else chart.target_year_overlay
    if overlay:
        st.write(
            {
                "year": overlay.gregorian_year,
                "animal": overlay.animal_zh if lang == "zh" else overlay.animal_en,
                "direction": overlay.direction_zh if lang == "zh" else overlay.direction_en,
                "summary": overlay.summary_zh if lang == "zh" else overlay.summary_en,
            }
        )

    st.markdown("### Remedies")
    st.write(list(chart.natal_remedies_zh if lang == "zh" else chart.natal_remedies_en))
