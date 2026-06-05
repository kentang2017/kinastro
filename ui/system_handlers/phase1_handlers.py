"""Phase 1 representative handlers.

目前先遷移 `tab_ziwei`，其餘仍走 legacy fallback 以保證相容。
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_ziwei_handler(
    *,
    compute_ziwei_chart,
    render_ziwei_chart,
    compute_vietnam_tu_vi_chart,
    render_vietnam_tu_vi_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for ZiWei system."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], vietnam_mode: bool):
        return compute_ziwei_chart(**params_payload, vietnam_mode=vietnam_mode)

    @st.cache_data(show_spinner=False)
    def _cached_compute_vietnam(
        params_payload: dict[str, Any],
        calendar_mode: str,
        interpret_mode: str,
        lang: str,
    ):
        return compute_vietnam_tu_vi_chart(
            **params_payload,
            calendar_mode=calendar_mode,
            interpret_mode=interpret_mode,
            lang=lang,
        )

    def _compute(params: BirthChartParams, options: dict[str, Any]):
        # `to_dict()` intentionally preserves legacy compute kwargs only.
        # Gender is injected separately for systems that need it.
        payload = {**params.to_dict(), "gender": params.gender}
        if bool(options.get("vietnam_full_mode", False)):
            return _cached_compute_vietnam(
                payload,
                str(options.get("calendar_mode", "solar_gregorian")),
                str(options.get("interpret_mode", "trung_chau_tam_hop")),
                str(options.get("lang", "zh")),
            )
        return _cached_compute(payload, bool(options.get("vietnam_mode", False)))

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        if bool(options.get("vietnam_full_mode", False)):
            render_vietnam_tu_vi_chart(
                result,
                after_chart_hook=lambda: ai_button_sink("tab_ziwei", result, ""),
            )
            return
        render_ziwei_chart(
            result,
            after_chart_hook=lambda: ai_button_sink("tab_ziwei", result, ""),
        )

    return SystemHandler(
        system_id="tab_ziwei",
        compute=_compute,
        render=_render,
        options_schema={
            "vietnam_mode": bool,
            "vietnam_full_mode": bool,
            "calendar_mode": str,
            "interpret_mode": str,
            "lang": str,
        },
    )
