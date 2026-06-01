"""
阿拉伯占星 (Arabic Astrology) sub-package
=========================================

Includes Arabic chart, Picatrix star magic, Shams al-Maʻārif (太陽知識大全),
planetary properties, zodiac signs, spells, riyada, wafq, and talisman generator.

Layered architecture
--------------------
* ``astro/arabic/arabic.py`` — pure compute (ArabicChart, compute_arabic_chart,
  helper math). **Must not** import streamlit.
* ``ui/handlers/tab_arabic/render.py`` — streamlit UI renderer.

``render_streamlit`` is exposed here as a lazy dispatcher so existing
callers (``astro.arabic.render_streamlit(...)``) keep working without
dragging streamlit into the import graph.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from astro.arabic.arabic import ArabicChart


def compute_arabic_chart(*args, **kwargs) -> "ArabicChart":
    """Lazy-load and call the Arabic chart compute function."""
    from astro.arabic.arabic import compute_arabic_chart as _fn
    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from ui.handlers.tab_arabic.render import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = ["compute_arabic_chart", "render_streamlit"]
