"""鐵板神數 (Tie Ban) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_tieban_handler(
    *,
    compute_tieban_chart,
    render_tieban_chart_svg,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 鐵板神數 (Tie Ban) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any]):
        """Pure compute wrapped for Streamlit caching."""
        return compute_tieban_chart(**params_payload)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Remove gender parameter - this system doesn\'t use it
        payload.pop("gender", None)
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        svg = render_tieban_chart_svg(result)
        st.components.v1.html(svg, height=760, scrolling=False)
        ai_button_sink("tab_tieban", result, "tieban", "")

    return SystemHandler(
        system_id="tab_tieban",
        compute=_compute,
        render=_render,
        options_schema={},
    )


def register(registry, ai_button_sink):
    """Self-registration for Tieban handler (modular lazy pattern)."""
    from datetime import datetime as _dt
    from astro.tieban import TieBanShenShu, TieBanBirthData, render_tieban_chart_svg

    def _compute_tieban(**kw):
        tbss = TieBanShenShu()
        dt = _dt(
            int(kw["year"]), int(kw["month"]), int(kw["day"]),
            int(kw["hour"]), int(kw.get("minute", 0)),
        )
        ganzhi = tbss.calculate_ganzhi(dt)
        birth_data = TieBanBirthData(
            birth_dt=dt,
            year_gz=ganzhi["year"],
            month_gz=ganzhi["month"],
            day_gz=ganzhi["day"],
            hour_gz=ganzhi["hour"],
        )
        return tbss.calculate(birth_data)

    handler = build_tieban_handler(
        compute_tieban_chart=_compute_tieban,
        render_tieban_chart_svg=render_tieban_chart_svg,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
