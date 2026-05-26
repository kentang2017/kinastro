"""TaiXuan page renderer extracted from app.py."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

import streamlit as st

from astro.chinese.taixuan import TaiXuanCalculator
from astro.chinese.taixuan.taixuan_renderer import (
    render_qigua_ui,
    render_taixuan_chart,
    render_taixuan_intro,
)


def _build_taixuan_ai_payload(result: Any) -> dict[str, Any]:
    """Build AI payload from TaiXuan result."""
    return {
        "shou_name": result.shou.name,
        "gua_title": result.shou.gua_title,
        "gua_text": result.shou.gua_text,
        "zhan_name": result.shou.zhan_name,
        "zhan_text": result.shou.zhan_text,
        "year_gz": result.year_gz,
        "day_gz": result.day_gz,
        "sishi": result.sishi,
        "mansion": result.shou.mansion,
        "planet": result.shou.planet,
    }


def _compute_taixuan_natal(calc_params: Mapping[str, Any]) -> Any:
    """Compute TaiXuan natal chart."""
    return TaiXuanCalculator(
        year=calc_params["year"],
        month=calc_params["month"],
        day=calc_params["day"],
        hour=calc_params["hour"],
        mode="natal",
    ).calculate()


def render_taixuan_page(
    *,
    is_calculated: bool,
    calc_params: Mapping[str, Any] | None,
    translate: Callable[[str], str],
    render_ai_button: Callable[..., None],
) -> None:
    """Render TaiXuan page (natal + qigua)."""
    tx_tab_natal, tx_tab_qigua = st.tabs(
        [translate("taixuan_natal_tab"), translate("taixuan_qigua_tab")]
    )

    with tx_tab_natal:
        if is_calculated and calc_params:
            try:
                with st.spinner(translate("spinner_taixuan")):
                    tx_result = _compute_taixuan_natal(calc_params)
                render_taixuan_chart(
                    tx_result,
                    after_chart_hook=lambda _result: render_ai_button(
                        "tab_taixuan",
                        _build_taixuan_ai_payload(tx_result),
                        btn_key="taixuan_natal",
                    ),
                )
            except Exception as err:
                st.error(f"{translate('error_tab_compute')}：{err}")
                st.exception(err)
        else:
            render_taixuan_intro()

    with tx_tab_qigua:
        render_qigua_ui(
            after_chart_hook=lambda _result: render_ai_button(
                "tab_taixuan",
                {"mode": "qigua"},
                btn_key="taixuan_qigua",
            )
        )
