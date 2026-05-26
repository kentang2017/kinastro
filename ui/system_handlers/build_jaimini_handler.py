"""Jaimini 占星 (Jaimini) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_jaimini_handler(
    *,
    compute_jaimini_chart,
    render_jaimini_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for Jaimini 占星 (Jaimini) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_jaimini_chart(**params_payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Remove gender parameter - this system doesn\'t use it
        payload.pop("gender", None)
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_jaimini_chart(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_jaimini", result, "jaimini", ""
            ),
        )

    return SystemHandler(
        system_id="tab_jaimini",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Jaimini 占星 (Jaimini) handler (modular lazy pattern)."""
    from astro.jaimini import compute_jaimini_chart, render_jaimini_chart

    handler = build_jaimini_handler(
        compute_jaimini_chart=compute_jaimini_chart,
        render_jaimini_chart=render_jaimini_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
