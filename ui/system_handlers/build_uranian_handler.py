"""天王星漢堡 (Uranian) Astrology handler."""

from __future__ import annotations

import inspect
from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_uranian_handler(
    *,
    compute_uranian_chart,
    render_uranian_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 天王星漢堡 (Uranian) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_uranian_chart(**params_payload, **extra_kwargs)

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
        hook = lambda _chart=None: ai_button_sink("tab_uranian", result, "uranian", "")
        render_sig = inspect.signature(render_uranian_chart)
        has_after_hook = "after_chart_hook" in render_sig.parameters
        has_varkw = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in render_sig.parameters.values()
        )
        if has_after_hook or has_varkw:
            render_uranian_chart(result, after_chart_hook=hook)
        else:
            render_uranian_chart(result)
            hook(result)

    return SystemHandler(
        system_id="tab_uranian",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Uranian handler (modular lazy pattern)."""
    from astro.western.uranian import compute_uranian_chart, render_uranian_chart

    handler = build_uranian_handler(
        compute_uranian_chart=compute_uranian_chart,
        render_uranian_chart=render_uranian_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
