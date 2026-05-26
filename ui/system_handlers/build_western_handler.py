"""Western Astrology handler —本命盤、過運、合盤、回歸."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_western_handler(
    *,
    compute_western_chart,
    render_western_chart,
    compute_western_transits,
    compute_synastry,
    compute_solar_return,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for Western Astrology systems."""

    @st.cache_data(show_spinner=False)
    def _cached_compute_natal(params_payload: dict[str, Any]):
        return compute_western_chart(**params_payload)

    @st.cache_data(show_spinner=False)
    def _cached_compute_transit(natal_result, year: int, month: int, day: int):
        return compute_western_transits(natal_result, year, month, day)

    @st.cache_data(show_spinner=False)
    def _cached_compute_synastry(chart_a, chart_b):
        return compute_synastry(chart_a, chart_b)

    @st.cache_data(show_spinner=False)
    def _cached_compute_return(natal_result, year: int):
        return compute_solar_return(natal_result, year)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> dict[str, Any]:
        """Compute based on sub-tab selection."""
        payload = params.to_dict()
        natal_chart = _cached_compute_natal(payload)

        sub_tab = options.get("sub_tab", "natal")

        if sub_tab == "transit":
            transit_date = options.get("transit_date", params.to_dict())
            transit_result = _cached_compute_transit(
                natal_chart,
                transit_date.get("year", params.year),
                transit_date.get("month", params.month),
                transit_date.get("day", params.day),
            )
            return {"natal": natal_chart, "transit": transit_result, "type": "transit"}

        if sub_tab == "synastry":
            chart_b_params = options.get("chart_b_params", {})
            if chart_b_params:
                chart_b = _cached_compute_natal(chart_b_params)
                synastry_result = _cached_compute_synastry(natal_chart, chart_b)
                return {"chart_a": natal_chart, "chart_b": chart_b, "synastry": synastry_result, "type": "synastry"}
            return {"natal": natal_chart, "type": "natal"}

        if sub_tab == "return":
            return_year = options.get("return_year", params.year + 1)
            return_result = _cached_compute_return(natal_chart, return_year)
            return {"natal": natal_chart, "return": return_result, "type": "return"}

        return {"natal": natal_chart, "type": "natal"}

    def _render(result: dict[str, Any], params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render based on result type."""
        result_type = result.get("type", "natal")

        if result_type == "transit":
            # Transit rendering logic
            render_western_chart(result["natal"], after_chart_hook=lambda _chart=None: None)
            st.subheader(" Transit Chart")
            # TODO: Add transit-specific rendering
        elif result_type == "synastry":
            # Synastry rendering logic
            render_western_chart(result["chart_a"], after_chart_hook=lambda _chart=None: None)
            st.subheader("Chart B")
            render_western_chart(result["chart_b"], after_chart_hook=lambda _chart=None: None)
            st.subheader("Synastry Analysis")
            # TODO: Add synastry-specific rendering
        elif result_type == "return":
            # Solar return rendering logic
            render_western_chart(result["natal"], after_chart_hook=lambda _chart=None: None)
            st.subheader("Solar Return Chart")
            render_western_chart(result["return"], after_chart_hook=lambda _chart=None: None)
        else:
            # Natal chart rendering
            render_western_chart(
                result["natal"],
                after_chart_hook=lambda _chart=None: ai_button_sink(
                    "tab_western",
                    result["natal"],
                    "western",
                    "",
                ),
            )

    return SystemHandler(
        system_id="tab_western",
        compute=_compute,
        render=_render,
        options_schema={
            "sub_tab": str,
            "transit_date": dict,
            "chart_b_params": dict,
            "return_year": int,
        },
    )


def register(registry, ai_button_sink):
    """Self-registration for Western handler (modular lazy pattern)."""
    from astro.western.western import compute_western_chart, render_western_chart
    from astro.western.western_transit import compute_western_transits
    from astro.western.western_synastry import compute_synastry
    from astro.western.western_return import compute_solar_return

    handler = build_western_handler(
        compute_western_chart=compute_western_chart,
        render_western_chart=render_western_chart,
        compute_western_transits=compute_western_transits,
        compute_synastry=compute_synastry,
        compute_solar_return=compute_solar_return,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
