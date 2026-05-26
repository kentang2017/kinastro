"""巴厘 Wariga (Wariga) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_wariga_handler(
    *,
    compute_wariga,
    render_wariga_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 巴厘 Wariga (Wariga) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender and timezone parameters - Wariga doesn't use them
        # Map latitude/longitude to lat/lon for Wariga
        payload = {}
        for k, v in params_payload.items():
            if k == "gender" or k == "timezone" or k == "location_name":
                continue
            if k == "latitude":
                payload["lat"] = v
            elif k == "longitude":
                payload["lon"] = v
            else:
                payload[k] = v
        # Add lat/lon defaults if not present
        if "lat" not in payload:
            payload["lat"] = -8.5069  # Bali default
        if "lon" not in payload:
            payload["lon"] = 115.2625  # Bali default
        return compute_wariga(**payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        return _cached_compute(params.to_dict())

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_wariga_chart(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_wariga", result, "wariga", ""
            ),
        )

    return SystemHandler(
        system_id="tab_wariga",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )
