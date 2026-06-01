"""UI handler for system **tab_horary**.

Render layer for horary. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_streamlit,
    render_vedic_prashna_svg,
    render_western_horary_svg,
)

__all__ = [
    "render_streamlit", "render_vedic_prashna_svg", "render_western_horary_svg",
]
