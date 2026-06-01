"""UI handler for system **tab_bazi**.

Render layer for bazi. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_bazi_chart_svg,
    render_streamlit,
)

__all__ = [
    "render_bazi_chart_svg", "render_streamlit",
]
