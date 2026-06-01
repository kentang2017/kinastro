"""UI handler for system **tab_beiji**.

Render layer for beiji. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_beiji_chart,
    render_beiji_search,
    render_streamlit,
)

__all__ = [
    "render_beiji_chart", "render_beiji_search", "render_streamlit",
]
