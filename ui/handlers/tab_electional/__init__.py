"""UI handler for system **tab_electional**.

Render layer for electional. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_streamlit,
    render_vedic_muhurta_svg,
    render_western_electional_svg,
)

__all__ = [
    "render_streamlit", "render_vedic_muhurta_svg", "render_western_electional_svg",
]
