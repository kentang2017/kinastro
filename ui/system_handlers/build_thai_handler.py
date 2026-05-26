"""泰國占星 (Thai) Astrology handler."""

from __future__ import annotations

from datetime import date as date_cls
from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_thai_handler(
    *,
    compute_thai_chart,
    render_thai_chart,
    calculate_thai_nine_grid,
    render_nine_grid,
    calculate_nine_palace_divination,
    render_nine_palace_divination,
    compute_brahma_jati,
    render_brahma_jati,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for 泰國占星 (Thai) Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn\'t use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_thai_chart(**params_payload, **extra_kwargs)

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
        thai_tab_chart, thai_tab_nine, thai_tab_brahma = st.tabs(
            ["📊 Chart", "🔢 Nine Grid", "📖 Brahma Jati"]
        )

        with thai_tab_chart:
            render_thai_chart(
                result,
                after_chart_hook=lambda chart: ai_button_sink(
                    "tab_thai", chart, "thai", ""
                ),
            )

        with thai_tab_nine:
            nine_grid_result = calculate_thai_nine_grid(
                params.day, params.month, params.year
            )
            render_nine_grid(nine_grid_result)
            st.markdown("---")
            divination_result = calculate_nine_palace_divination(result)
            render_nine_palace_divination(divination_result)

        with thai_tab_brahma:
            birth_day = date_cls(params.year, params.month, params.day)
            age_default = max(1, date_cls.today().year - params.year)
            age_col, gender_col = st.columns(2)
            with age_col:
                age = st.number_input(
                    "年齡 (Age)",
                    min_value=1,
                    max_value=120,
                    value=age_default,
                    key="brahma_jati_age",
                )
            with gender_col:
                gender_options = ["male", "female"]
                gender = st.selectbox(
                    "性別 (Gender)",
                    options=gender_options,
                    index=gender_options.index(params.gender) if params.gender in gender_options else 0,
                    format_func=lambda value: "男 Male" if value == "male" else "女 Female",
                    key="brahma_jati_gender",
                )
            brahma_reading = compute_brahma_jati(
                ce_year=params.year,
                month=params.month,
                weekday=birth_day.weekday(),
                age=int(age),
                gender=gender,
            )
            render_brahma_jati(brahma_reading)

    return SystemHandler(
        system_id="tab_thai",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for 泰國占星 (Thai) handler (modular lazy pattern)."""
    from astro.brahma_jati import compute_brahma_jati, render_brahma_jati
    from astro.thai import (
        calculate_nine_palace_divination,
        calculate_thai_nine_grid,
        compute_thai_chart,
        render_nine_grid,
        render_nine_palace_divination,
        render_thai_chart,
    )

    handler = build_thai_handler(
        compute_thai_chart=compute_thai_chart,
        render_thai_chart=render_thai_chart,
        calculate_thai_nine_grid=calculate_thai_nine_grid,
        render_nine_grid=render_nine_grid,
        calculate_nine_palace_divination=calculate_nine_palace_divination,
        render_nine_palace_divination=render_nine_palace_divination,
        compute_brahma_jati=compute_brahma_jati,
        render_brahma_jati=render_brahma_jati,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
