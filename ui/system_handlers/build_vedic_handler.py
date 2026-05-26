"""Vedic (Indian) Astrology handler —本命盤、Dasha、Yogas、Varga."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_vedic_handler(
    *,
    compute_vedic_chart,
    render_vedic_chart,
    compute_vimshottari,
    compute_yogini,
    compute_yogas,
    compute_ashtakavarga,
    compute_varga_chart,
    render_varga_chart,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for Vedic Astrology systems."""

    @st.cache_data(show_spinner=False)
    def _cached_compute_natal(params_payload: dict[str, Any]):
        return compute_vedic_chart(**params_payload)

    @st.cache_data(show_spinner=False)
    def _cached_compute_vimshottari(natal_result):
        return compute_vimshottari(natal_result)

    @st.cache_data(show_spinner=False)
    def _cached_compute_yogini(natal_result):
        return compute_yogini(natal_result)

    @st.cache_data(show_spinner=False)
    def _cached_compute_yogas(natal_result):
        return compute_yogas(natal_result)

    @st.cache_data(show_spinner=False)
    def _cached_compute_ashtakavarga(natal_result):
        return compute_ashtakavarga(natal_result)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> dict[str, Any]:
        """Compute based on sub-tab selection."""
        payload = params.to_dict()
        natal_chart = _cached_compute_natal(payload)

        sub_tab = options.get("sub_tab", "natal")

        result = {"natal": natal_chart, "type": "natal"}

        if sub_tab == "dasha":
            dasha_type = options.get("dasha_type", "vimshottari")
            if dasha_type == "vimshottari":
                result["dasha"] = _cached_compute_vimshottari(natal_chart)
            elif dasha_type == "yogini":
                result["dasha"] = _cached_compute_yogini(natal_chart)
            result["dasha_type"] = dasha_type
            result["type"] = "dasha"

        elif sub_tab == "yogas":
            result["yogas"] = _cached_compute_yogas(natal_chart)
            result["type"] = "yogas"

        elif sub_tab == "ashtakavarga":
            result["ashtakavarga"] = _cached_compute_ashtakavarga(natal_chart)
            result["type"] = "ashtakavarga"

        elif sub_tab == "varga":
            varga_key = options.get("varga_key", "D9")
            result["varga"] = compute_varga_chart(varga_key, natal_chart.planets, natal_chart.ascendant)
            result["varga_key"] = varga_key
            result["type"] = "varga"

        return result

    def _render(result: dict[str, Any], params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render based on result type."""
        result_type = result.get("type", "natal")

        if result_type == "dasha":
            render_vedic_chart(result["natal"], after_chart_hook=lambda: None)
            st.subheader(f"Dasha Periods ({result.get('dasha_type', 'Vimshottari')})")
            # TODO: Add dasha-specific rendering
        elif result_type == "yogas":
            render_vedic_chart(result["natal"], after_chart_hook=lambda: None)
            st.subheader("Planetary Yogas")
            # TODO: Add yogas rendering
        elif result_type == "ashtakavarga":
            render_vedic_chart(result["natal"], after_chart_hook=lambda: None)
            st.subheader("Ashtakavarga")
            # TODO: Add ashtakavarga rendering
        elif result_type == "varga":
            st.subheader(f"Varga Chart: {result.get('varga_key', 'D9')}")
            render_varga_chart(result["varga"])
        else:
            render_vedic_chart(
                result["natal"],
                after_chart_hook=lambda: ai_button_sink("tab_indian", result["natal"], "vedic", ""),
            )

    return SystemHandler(
        system_id="tab_indian",
        compute=_compute,
        render=_render,
        options_schema={
            "sub_tab": str,
            "dasha_type": str,
            "varga_key": str,
        },
    )


def register(registry, ai_button_sink):
    """Self-registration for Vedic handler (modular lazy pattern)."""
    from astro.vedic.indian import compute_vedic_chart, render_vedic_chart
    from astro.vedic.vedic_dasha import compute_vimshottari, compute_yogini
    from astro.vedic.vedic_yogas import compute_yogas
    from astro.vedic.ashtakavarga import compute_ashtakavarga
    from astro.vedic.varga import compute_varga_chart, render_single_varga

    handler = build_vedic_handler(
        compute_vedic_chart=compute_vedic_chart,
        render_vedic_chart=render_vedic_chart,
        compute_vimshottari=compute_vimshottari,
        compute_yogini=compute_yogini,
        compute_yogas=compute_yogas,
        compute_ashtakavarga=compute_ashtakavarga,
        compute_varga_chart=compute_varga_chart,
        render_varga_chart=render_single_varga,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
