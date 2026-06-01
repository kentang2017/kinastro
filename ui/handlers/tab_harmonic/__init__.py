"""UI handler for system **tab_harmonic**.

Render layer for harmonic. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_harmonic,
    render_harmonic_chart_svg,
    render_multi_harmonic_summary_svg,
)

__all__ = [
    "render_harmonic", "render_harmonic_chart_svg", "render_multi_harmonic_summary_svg",
]
