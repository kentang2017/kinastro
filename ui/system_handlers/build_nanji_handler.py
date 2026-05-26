"""南極神數 (Nanji) Astrology handler."""

from __future__ import annotations

import inspect
from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def _normalize_nanji_gender(gender: str | None) -> str:
    """Normalize UI gender values to 南極神數 expected labels."""
    if gender in ("female", "女"):
        return "女"
    return "男"


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
        sig = inspect.signature(compute_nanji_chart)
        valid_params = set(sig.parameters.keys())
        params_payload = {
            k: v for k, v in params_payload.items() if k in valid_params
        }
        if "gender" in valid_params:
            params_payload["gender"] = _normalize_nanji_gender(
                params_payload.get("gender")
            )
        return compute_nanji_chart(**params_payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        payload["gender"] = params.gender
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_nanji_chart(
            year=params.year,
            month=params.month,
            day=params.day,
            hour=params.hour,
            minute=params.minute,
            gender=_normalize_nanji_gender(params.gender),
        )
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

    def _compute_nanji_chart(
        *,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        gender: str = "男",
        **_kwargs,
    ):
        njs = NanJiShenShu.from_solar_datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            gender=_normalize_nanji_gender(gender),
        )
        return njs.compute()

    handler = build_nanji_handler(
        compute_nanji_chart=_compute_nanji_chart,
        render_nanji_chart=render_nanji_chart,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
