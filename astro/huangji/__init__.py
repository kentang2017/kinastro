"""Public API for Huangji Jingshi module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .huangji import HuangjiPanResult


def compute_huangji_pan(*args, **kwargs) -> "HuangjiPanResult":
    from .huangji import compute_huangji_pan as _fn

    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs) -> None:
    from .renderer import render_streamlit as _fn

    return _fn(*args, **kwargs)


__all__ = ["compute_huangji_pan", "render_streamlit"]
