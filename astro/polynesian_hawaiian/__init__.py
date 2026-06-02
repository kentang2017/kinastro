"""Polynesian / Hawaiian Star Lore public API."""

from __future__ import annotations


def compute_polynesian_chart(*args, **kwargs):
    """Lazy-load calculator entrypoint."""
    from .calculator import compute_polynesian_chart as _fn

    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs):
    """Lazy-load Streamlit renderer."""
    from ui.handlers.tab_polynesian.render import render_streamlit as _fn

    return _fn(*args, **kwargs)


__all__ = ["compute_polynesian_chart", "render_streamlit"]
