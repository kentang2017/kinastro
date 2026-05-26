"""世俗占星 (Mundane) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_mundane_handler(
    *,
    compute_mundane_chart,
    render_mundane_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 世俗占星 (Mundane) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return render_mundane_chart(**params_payload, **extra_kwargs)

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
        render_mundane_chart(result)
        ai_button_sink("tab_mundane", result, "mundane", "")

    return SystemHandler(
        system_id="tab_mundane",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )
