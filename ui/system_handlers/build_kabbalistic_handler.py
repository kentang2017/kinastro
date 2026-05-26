"""卡巴拉 (Kabbalah) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_kabbalistic_handler(
    *,
    compute_kabbalistic_chart,
    render_kabbalistic_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 卡巴拉 (Kabbalah) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - Kabbalistic chart doesn't use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_kabbalistic_chart(**params_payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Kabbalistic chart doesn't use gender, remove it
        payload.pop("gender", None)
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_kabbalistic_chart(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_kabbalistic", result, "kabbalistic", ""
            ),
        )

    return SystemHandler(
        system_id="tab_kabbalistic",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )
