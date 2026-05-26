"""希臘占星 (Hellenistic) Astrology handler."""

from __future__ import annotations

import inspect
from datetime import datetime
from typing import Any

import streamlit as st

from astro.i18n import auto_cn, get_lang, t
from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_hellenistic_handler(
    *,
    compute_hellenistic_chart,
    render_hellenistic_chart,
    compute_western_chart,
    render_western_chart,
    build_greek_horoscope_svg,
    compute_hellenistic_extended,
    render_extended_lots,
    render_valens_combinations,
    render_annual_profections,
    render_zodiacal_releasing,
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
        current_year = datetime.now().year
        hellenistic_chart = compute_hellenistic_chart(
            western_chart,
            birth_year=birth_year,
            current_year=current_year,
        )
        hellenistic_extended = compute_hellenistic_extended(western_chart, hellenistic_chart)
        return {
            "western_chart": western_chart,
            "hellenistic_chart": hellenistic_chart,
            "hellenistic_extended": hellenistic_extended,
        }

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Remove gender parameter - this system doesn\'t use it
        payload.pop("gender", None)
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        hellen_chart = result["hellenistic_chart"]
        western_chart = result["western_chart"]
        hellen_extended = result["hellenistic_extended"]

        def hook(_chart=None):
            ai_button_sink("tab_hellenistic", hellen_chart, "hellenistic", "")

        render_sig = inspect.signature(render_hellenistic_chart)
        has_after_hook = "after_chart_hook" in render_sig.parameters
        has_varkw = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in render_sig.parameters.values()
        )
        (
            tab_chart,
            tab_natal,
            tab_prof,
            tab_zr,
            tab_lots,
            tab_ext_lots,
            tab_synkrasis,
            tab_centiloquy,
        ) = st.tabs(
            [
                t("hellen_subtab_chart"),
                t("hellen_subtab_natal"),
                t("hellen_subtab_profections"),
                t("hellen_subtab_zr"),
                t("hellen_subtab_lots"),
                auto_cn("📜 Extended Lots / 擴充 Lots", "📜 Extended Lots"),
                auto_cn("⚗️ Valens Synkrasis / 行星組合", "⚗️ Valens Synkrasis"),
                t("hellen_subtab_centiloquy"),
            ]
        )

        with tab_chart:
            greek_svg = build_greek_horoscope_svg(
                hellen_chart,
                year=params.year,
                month=params.month,
                day=params.day,
                hour=params.hour,
                minute=params.minute,
                tz=params.timezone,
                location=params.location_name,
            )
            st.markdown(greek_svg, unsafe_allow_html=True)
            st.caption(
                '<p style="text-align:center; color:#888; font-size:11px;">'
                "Greek Horoscope (θέμα) — Square chart form after L 497 · "
                "Whole-sign houses · ASC at left, MC at top"
                "</p>",
                unsafe_allow_html=True,
            )
            hook(hellen_chart)

        with tab_natal:
            if has_after_hook or has_varkw:
                render_hellenistic_chart(hellen_chart, after_chart_hook=hook)
            else:
                render_hellenistic_chart(hellen_chart)

        with tab_prof:
            render_annual_profections(
                asc_lon=hellen_chart.ascendant,
                birth_year=params.year,
                num_years=24,
                lang=get_lang(),
            )

        with tab_zr:
            zr_fortune_lon = next(
                (lot.longitude for lot in hellen_chart.lots if "Fortune" in lot.name),
                0.0,
            )
            zr_spirit_lon = next(
                (lot.longitude for lot in hellen_chart.lots if "Spirit" in lot.name),
                0.0,
            )
            render_zodiacal_releasing(
                fortune_lon=zr_fortune_lon,
                spirit_lon=zr_spirit_lon,
                birth_jd=western_chart.julian_day,
                target_jd=western_chart.julian_day + (datetime.now().year - params.year) * 365.25,
                lang=get_lang(),
            )

        with tab_lots:
            if hellen_chart.lots:
                st.subheader(t("hellen_lots_header"))
                st.dataframe(
                    [
                        {
                            "Name": f"{lot.name} ({auto_cn(lot.name_cn)})",
                            "Sign": lot.sign,
                            "Degree": f"{lot.sign_degree:.2f}°",
                            "House": lot.house,
                            "Formula": lot.formula_en,
                            "Meaning": auto_cn(lot.meaning_cn),
                        }
                        for lot in hellen_chart.lots
                    ],
                    width="stretch",
                )

        with tab_ext_lots:
            if hellen_extended.extended_lots:
                render_extended_lots(hellen_extended.extended_lots)

        with tab_synkrasis:
            if hellen_extended.synkrasis:
                render_valens_combinations(hellen_extended.synkrasis)

        with tab_centiloquy:
            from astro.classic.ptolemy_centiloquy import (
                format_aphorism,
                get_all_aphorisms,
                get_random_aphorism,
                search_aphorism,
            )

            st.subheader(t("centiloquy_header"))
            st.info(format_aphorism(get_random_aphorism()))

            centiloquy_query = st.text_input(t("centiloquy_search_label"), key="centiloquy_search")
            if centiloquy_query:
                results = search_aphorism(centiloquy_query)
                if results:
                    for result in results:
                        st.markdown(format_aphorism(result))
                else:
                    st.warning(t("centiloquy_no_match"))
            else:
                for aphorism in get_all_aphorisms():
                    with st.expander(t("centiloquy_aphorism_num").format(n=aphorism["id"])):
                        st.markdown(aphorism["text"])

    return SystemHandler(
        system_id="tab_hellenistic",
        compute=_compute,
        render=_render,
        options_schema={},  # Add system-specific options here
    )


def register(registry, ai_button_sink):
    """Self-registration for Hellenistic 占星 handler (modular lazy pattern)."""
    from astro.western.hellenistic import (
        build_greek_horoscope_svg,
        compute_hellenistic_chart,
        compute_hellenistic_extended,
        render_extended_lots,
        render_hellenistic_chart,
        render_valens_combinations,
    )
    from astro.western.western import compute_western_chart, render_western_chart
    from frontend.hellenistic_enhanced_renderer import (
        render_annual_profections,
        render_zodiacal_releasing,
    )

    handler = build_hellenistic_handler(
        compute_hellenistic_chart=compute_hellenistic_chart,
        render_hellenistic_chart=render_hellenistic_chart,
        compute_western_chart=compute_western_chart,
        render_western_chart=render_western_chart,
        build_greek_horoscope_svg=build_greek_horoscope_svg,
        compute_hellenistic_extended=compute_hellenistic_extended,
        render_extended_lots=render_extended_lots,
        render_valens_combinations=render_valens_combinations,
        render_annual_profections=render_annual_profections,
        render_zodiacal_releasing=render_zodiacal_releasing,
        ai_button_sink=ai_button_sink,
    )
    registry.register(handler)
