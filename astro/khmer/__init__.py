# -*- coding: utf-8 -*-
"""
Khmer Astrology Module - Reamker Lost Astrology System
高棉占星模組 - 羅摩衍那失傳占星系統
"""

from .reamker_calculator import ReamkerAstrology


def render_khmer_chart(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Khmer Reamker renderer."""
    try:
        from ui.handlers.tab_khmer.render import render_khmer_chart as _fn  # type: ignore[attr-defined]
    except ModuleNotFoundError:
        from .renderer import render_khmer_chart as _fn
    return _fn(*args, **kwargs)


def render_reamker_grid_svg(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Reamker grid SVG renderer."""
    try:
        from ui.handlers.tab_khmer.render import render_reamker_grid_svg as _fn  # type: ignore[attr-defined]
    except ModuleNotFoundError:
        from .renderer import render_reamker_grid_svg as _fn
    return _fn(*args, **kwargs)

__all__ = ["ReamkerAstrology", "render_khmer_chart", "render_reamker_grid_svg"]
