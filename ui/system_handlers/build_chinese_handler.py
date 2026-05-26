"""Chinese (Qizheng 七政四餘) handler —本命盤、神煞、大運、流年、張果星宗."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_chinese_handler(
    *,
    compute_chart,
    render_full_chart,
    render_chart_info_panel,
    render_bazi,
    render_planet_table,
    render_house_table,
    render_aspect_summary,
    compute_shensha,
    render_shensha,
    compute_dasha,
    render_dasha,
    compute_transit_now,
    render_transit_comparison,
    compute_zhangguo,
    render_zhangguo,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for Chinese Qizheng Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute_natal(params_payload: dict[str, Any], gender: str):
        return compute_chart(**params_payload, gender=gender)

    @st.cache_data(show_spinner=False)
    def _cached_compute_shensha(chart_data: dict[str, Any]):
        return compute_shensha(
            year=chart_data["year"],
            solar_month=chart_data["solar_month"],
            julian_day=chart_data["julian_day"],
            hour_branch=chart_data["hour_branch"],
            timezone=chart_data["timezone"],
            ming_gong_branch=chart_data["ming_gong_branch"],
        )

    @st.cache_data(show_spinner=False)
    def _cached_compute_dasha(birth_year: int):
        return compute_dasha(birth_year=birth_year)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> dict[str, Any]:
        """Compute based on sub-tab selection."""
        payload = params.to_dict()
        gender = params.gender or "male"
        natal_chart = _cached_compute_natal(payload, gender)

        sub_tab = options.get("sub_tab", "natal")
        result = {"natal": natal_chart, "type": "natal"}

        if sub_tab == "shensha":
            chart_data = vars(natal_chart) if hasattr(natal_chart, "__dict__") else natal_chart
            result["shensha"] = _cached_compute_shensha(chart_data)
            result["type"] = "shensha"

        elif sub_tab == "dasha":
            result["dasha"] = _cached_compute_dasha(birth_year=natal_chart.year)
            result["type"] = "dasha"

        elif sub_tab == "transit":
            result["transit"] = compute_transit_now(timezone=params.timezone)
            result["type"] = "transit"

        elif sub_tab == "zhangguo":
            result["zhangguo"] = compute_zhangguo(natal_chart)
            result["type"] = "zhangguo"

        return result

    def _render(result: dict[str, Any], params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render based on result type."""
        result_type = result.get("type", "natal")
        chart = result["natal"]

        if result_type == "shensha":
            render_full_chart(chart)
            st.subheader("神煞分析")
            render_shensha(chart, result["shensha"])
        elif result_type == "dasha":
            render_full_chart(chart)
            st.subheader("大運分析")
            render_dasha(chart, result["dasha"])
        elif result_type == "transit":
            render_full_chart(chart, transit=result.get("transit"))
            st.subheader("流年對盤")
            render_transit_comparison(chart, result["transit"])
        elif result_type == "zhangguo":
            render_full_chart(chart)
            st.subheader("張果星宗")
            render_zhangguo(result["zhangguo"])
        else:
            # Natal main view — render the full chart then attach AI analysis button.
            # (render_full_chart does not accept after_chart_hook; call the sink directly.)
            render_full_chart(chart)
            ai_button_sink("tab_chinese", chart, "qizheng", "")

    return SystemHandler(
        system_id="tab_chinese",
        compute=_compute,
        render=_render,
        options_schema={
            "sub_tab": str,
            "show_transit_overlay": bool,
        },
    )


def register(registry, ai_button_sink):
    """Self-registration for Chinese (Qizheng) handler."""
    from astro.qizheng.calculator import compute_chart
    from astro.qizheng.chart_renderer import (
        render_full_chart, render_chart_info_panel, render_bazi,
        render_planet_table, render_house_table, render_aspect_summary,
        render_shensha, render_dasha, render_transit_comparison, render_zhangguo
    )
    from astro.qizheng.shensha import compute_shensha
    from astro.qizheng.qizheng_dasha import compute_dasha
    from astro.qizheng.qizheng_transit import compute_transit_now
    from astro.qizheng.zhangguo import compute_zhangguo

    handler = build_chinese_handler(
        compute_chart=compute_chart,
        render_full_chart=render_full_chart,
        render_chart_info_panel=render_chart_info_panel,
        render_bazi=render_bazi,
        render_planet_table=render_planet_table,
        render_house_table=render_house_table,
        render_aspect_summary=render_aspect_summary,
        compute_shensha=compute_shensha,
        render_shensha=render_shensha,
        compute_dasha=compute_dasha,
        render_dasha=render_dasha,
        compute_transit_now=compute_transit_now,
        render_transit_comparison=render_transit_comparison,
        compute_zhangguo=compute_zhangguo,
        render_zhangguo=render_zhangguo,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
