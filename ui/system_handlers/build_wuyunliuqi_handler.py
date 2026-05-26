"""五運六氣 (Wu Yun Liu Qi) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler

_ACCEPTED_WUYUNLIUQI_KEYS = {"year", "month", "day", "hour", "minute"}


def build_wuyunliuqi_handler(
    *,
    compute_wuyunliuqi,
    render_wuyunliuqi_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 五運六氣 (Wu Yun Liu Qi) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        filtered_payload = {k: v for k, v in params_payload.items() if k in _ACCEPTED_WUYUNLIUQI_KEYS}
        return compute_wuyunliuqi(**filtered_payload, **extra_kwargs)

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
        # render_streamlit (aliased as render_wuyunliuqi_chart) does not accept after_chart_hook
        render_wuyunliuqi_chart(result)
        ai_button_sink("tab_wuyunliuqi", result, "wuyunliuqi", "")

    return SystemHandler(
        system_id="tab_wuyunliuqi",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Wuyunliuqi handler."""
    from astro.wuyunliuqi.calculator import compute_wuyunliuqi
    from astro.wuyunliuqi.renderer import render_streamlit as render_wuyunliuqi_chart

    handler = build_wuyunliuqi_handler(
        compute_wuyunliuqi=compute_wuyunliuqi,
        render_wuyunliuqi_chart=render_wuyunliuqi_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
