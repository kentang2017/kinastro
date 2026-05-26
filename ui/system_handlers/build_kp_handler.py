"""KP 占星 (KP Astrology) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_kp_handler(
    *,
    compute_kp_chart,
    render_kp_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for KP 占星 (KP Astrology) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove unsupported shared birth fields for this system
        params_payload = {
            k: v
            for k, v in params_payload.items()
            if k not in {"gender", "location_name"}
        }
        return compute_kp_chart(**params_payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Remove unsupported shared birth fields for this system
        payload.pop("gender", None)
        payload.pop("location_name", None)
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_kp_chart(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_kp", result, "kp", ""
            ),
        )

    return SystemHandler(
        system_id="tab_kp",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for KP 占星 handler (modular lazy pattern)."""
    from astro.kp import compute_kp_chart, render_kp_chart

    handler = build_kp_handler(
        compute_kp_chart=compute_kp_chart,
        render_kp_chart=render_kp_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
