"""梵天 (Brahma Jati) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_brahma_jati_handler(
    *,
    compute_brahma_jati,
    render_brahma_jati,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 梵天 (Brahma Jati) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_brahma_jati(**params_payload, **extra_kwargs)

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
        render_brahma_jati(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_brahma_jati", result, "brahma_jati", ""
            ),
        )

    return SystemHandler(
        system_id="tab_brahma_jati",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )
