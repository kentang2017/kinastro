"""南極神數 (Nanji) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_nanji_handler(
    *,
    compute_nanji_chart,
    render_nanji_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 南極神數 (Nanji) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_nanji_chart(**params_payload, **extra_kwargs)

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
        # nanji render_streamlit does not explicitly support after_chart_hook
        render_nanji_chart(result)
        ai_button_sink("tab_nanji", result, "nanji", "")

    return SystemHandler(
        system_id="tab_nanji",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Nanji handler."""
    from astro.nanji import NanJiShenShu, render_streamlit as render_nanji_chart

    handler = build_nanji_handler(
        compute_nanji_chart=lambda **kw: NanJiShenShu().calculate(**kw),
        render_nanji_chart=render_nanji_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
