"""UI handler for system **tab_arabic**.

Render layer for arabic. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_arabic_chart,
    render_streamlit,
)

__all__ = [
    "render_arabic_chart",
    "render_streamlit",
]
