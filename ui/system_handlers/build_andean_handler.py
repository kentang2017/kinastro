"""Phase 2 example handler — Andean (Inca) Astrology.

This demonstrates that the SystemHandler pattern scales cleanly to
other well-structured modern packages (calculator + renderer split,
lazy __init__.py, pure compute).

Andean is an excellent second reference implementation because:
- compute_andean_chart is already documented as "pure / no Streamlit".
- __init__.py provides clean lazy entry points.
- Simple flat parameter signature (easy payload mapping).
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_andean_handler(
    *,
    compute_andean_chart,
    render_andean_chart_ui,   # the render_streamlit function
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for Andean / Inca astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any]):
        """Pure compute wrapped for Streamlit caching."""
        return compute_andean_chart(**params_payload)

    def _compute(params: BirthChartParams, options: dict[str, Any]):
        # Andean currently expects flat birth params (no extra options yet).
        payload = {
            "year": params.year,
            "month": params.month,
            "day": params.day,
            "hour": params.hour,
            "minute": params.minute,
            "timezone": params.timezone,
            "latitude": params.latitude,
            "longitude": params.longitude,
            "location_name": params.location_name or "",
        }
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        render_andean_chart_ui(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_andean", result, "andean", ""
            ),
        )

    return SystemHandler(
        system_id="tab_andean",
        compute=_compute,
        render=_render,
        options_schema={},  # no extra options for Andean at this time
    )


def register(registry, ai_button_sink):
    """Self-registration entry point for modular lazy loading."""
    from astro.andean import compute_andean_chart as _compute_andean_chart_fn
    from astro.andean import render_streamlit as render_andean_chart_ui

    handler = build_andean_handler(
        compute_andean_chart=_compute_andean_chart_fn,
        render_andean_chart_ui=render_andean_chart_ui,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
