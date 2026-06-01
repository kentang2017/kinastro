"""UI handler for system **tab_esoteric**.

Render layer for esoteric. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_esoteric_chart_svg,
    render_streamlit,
)

__all__ = [
    "render_esoteric_chart_svg", "render_streamlit",
]
