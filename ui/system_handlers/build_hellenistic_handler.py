"""希臘占星 (Hellenistic) Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_hellenistic_handler(
    *,
    compute_hellenistic_chart,
    render_hellenistic_chart,
    compute_western_chart,
    render_western_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 希臘占星 (Hellenistic) Astrology.

    Hellenistic chart is derived from a Western chart, so we need to compute
    Western first, then apply Hellenistic techniques.
    """

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}

        # First compute Western chart
        western_chart = compute_western_chart(**params_payload)

        # Then compute Hellenistic chart from Western chart
        birth_year = params_payload.get("year", 1990)
        current_year = 2026  # Use a fixed year for now
        hellenistic_chart = compute_hellenistic_chart(
            western_chart,
            birth_year=birth_year,
            current_year=current_year,
        )
        return hellenistic_chart

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Remove gender parameter - this system doesn\'t use it
        payload.pop("gender", None)
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_hellenistic_chart(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "tab_hellenistic", result, "hellenistic", ""
            ),
        )

    return SystemHandler(
        system_id="tab_hellenistic",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Hellenistic 占星 handler (modular lazy pattern)."""
    from astro.western.hellenistic import compute_hellenistic_chart, render_hellenistic_chart
    from astro.western.western import compute_western_chart, render_western_chart

    handler = build_hellenistic_handler(
        compute_hellenistic_chart=compute_hellenistic_chart,
        render_hellenistic_chart=render_hellenistic_chart,
        compute_western_chart=compute_western_chart,
        render_western_chart=render_western_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
