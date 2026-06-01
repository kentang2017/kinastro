# -*- coding: utf-8 -*-
"""
astro/bazi/__init__.py — 子平八字模組公開介面
Ziping Bazi Astrology Module — Public API
"""
from .calculator import BaziChart, DayunStep, Pillar, ShenSha, compute_bazi, TEST_CASES

def render_bazi_chart_svg(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_bazi_chart_svg renderer for this package."""
    from ui.handlers.tab_bazi.render import render_bazi_chart_svg as _fn
    return _fn(*args, **kwargs)

def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_streamlit renderer for this package."""
    from ui.handlers.tab_bazi.render import render_streamlit as _fn
    return _fn(*args, **kwargs)

__all__ = [
    "BaziChart",
    "DayunStep",
    "Pillar",
    "ShenSha",
    "compute_bazi",
    "render_bazi_chart_svg",
    "render_streamlit",
    "TEST_CASES",
]
