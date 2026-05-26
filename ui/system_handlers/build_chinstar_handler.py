"""辰星 (ChinStar) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_chinstar_handler(
    *,
    compute_chinstar_chart,
    render_chinstar_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 辰星 (ChinStar) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        return compute_chinstar_chart(**params_payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Add gender parameter - ChinStar uses it
        payload["gender"] = params.gender
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_chinstar_chart(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_chinstar", result, "chinstar", ""
            ),
        )

    return SystemHandler(
        system_id="tab_chinstar",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Chinstar handler (modular lazy pattern)."""
    from astro.chinstar import compute_chinstar_chart, render_chinstar_chart

    handler = build_chinstar_handler(
        compute_chinstar_chart=compute_chinstar_chart,
        render_chinstar_chart=render_chinstar_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
