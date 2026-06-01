# -*- coding: utf-8 -*-
"""六爻終身卦 (Lifetime Liu Yao Hexagram) module."""

from .calculator import LifetimeHexagramCalculator, compute_lifetime_hexagram

def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_streamlit renderer for this package."""
    from ui.handlers.tab_liuyao_lifetime.render import render_streamlit as _fn
    return _fn(*args, **kwargs)

__all__ = [
    "LifetimeHexagramCalculator",
    "compute_lifetime_hexagram",
    "render_streamlit",
]
