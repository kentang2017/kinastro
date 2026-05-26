"""八字 (Bazi) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_bazi_handler(
    *,
    compute_bazi_chart,
    render_bazi_chart_svg,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 八字 (Bazi) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any]):
        """Pure compute wrapped for Streamlit caching."""
        return compute_bazi_chart(**params_payload)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        payload["gender"] = params.gender or "male"
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_bazi_chart_svg(
            result,
            after_chart_hook=lambda chart: ai_button_sink(
                "tab_bazi", chart, "bazi", ""
            ),
        )

    return SystemHandler(
        system_id="tab_bazi",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Bazi handler (modular lazy pattern)."""
    from astro.bazi import compute_bazi as compute_bazi_chart
    from astro.bazi.renderer import render_streamlit as render_bazi_chart_svg

    handler = build_bazi_handler(
        compute_bazi_chart=compute_bazi_chart,
        render_bazi_chart_svg=render_bazi_chart_svg,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
