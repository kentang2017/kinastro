"""UI handler for system **tab_human_design**.

Render layer for human_design. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_bodygraph_svg,
    render_streamlit,
)

__all__ = [
    "render_bodygraph_svg", "render_streamlit",
]
