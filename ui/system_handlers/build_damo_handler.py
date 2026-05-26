"""達摩一掌經 (Damo) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_damo_handler(
    *,
    compute_damo_chart,
    render_damo_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 達摩一掌經 (Damo) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_damo_chart(**params_payload, **extra_kwargs)

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
        render_damo_chart(result)
        ai_button_sink("tab_damo", result, "damo", "")

    return SystemHandler(
        system_id="tab_damo",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Damo handler (modular lazy pattern)."""
    from astro.damo import compute_damo_chart, render_damo_chart

    handler = build_damo_handler(
        compute_damo_chart=compute_damo_chart,
        render_damo_chart=render_damo_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
