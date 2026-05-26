"""Vedic system renderer adapter."""

from __future__ import annotations

from typing import Any, Callable

from ui.components.birth_form import BirthChartParams


def render(
    chart: Any,
    params: BirthChartParams,
    options: dict[str, Any],
    ai_hook: Callable[[], None] | None = None,
) -> None:
    from astro.vedic.indian import render_vedic_chart

    render_vedic_chart(chart, after_chart_hook=ai_hook)
