"""Public API for Laos Horasat module."""

from .calculator import (
    LaoChart,
    LaoPlanet,
    chart_to_dict,
    compute_lao_chart,
    find_best_dates,
    get_lao_auspicious_time,
    get_monthly_fortune,
    reload_all_data,
)
from .interpreter import get_planet_sign_reading, interpret_chart, interpret_planet
from .lao_horasat import LaoHorasat, compute_lao_horasat_chart, create_lao_horasat


def build_lao_brahma_wheel_svg(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Laos Brahma wheel SVG renderer."""
    from ui.handlers.tab_laos.render import build_lao_brahma_wheel_svg as _fn
    return _fn(*args, **kwargs)


def render_lao_horasat(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Laos Horasat chart renderer."""
    from ui.handlers.tab_laos.render import render_lao_horasat as _fn
    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Laos Streamlit entry point."""
    from ui.handlers.tab_laos.render import render_streamlit as _fn
    return _fn(*args, **kwargs)

__all__ = [
    # Core dataclasses
    "LaoChart",
    "LaoPlanet",
    # Calculator
    "compute_lao_chart",
    "compute_lao_horasat_chart",
    "chart_to_dict",
    "get_lao_auspicious_time",
    "find_best_dates",
    "get_monthly_fortune",
    "reload_all_data",
    # OOP interface
    "LaoHorasat",
    "create_lao_horasat",
    # Interpreter
    "interpret_chart",
    "interpret_planet",
    "get_planet_sign_reading",
    # Renderer
    "build_lao_brahma_wheel_svg",
    "render_lao_horasat",
    "render_streamlit",
]
