"""UI handler for system **tab_astro_geomancy**.

Render layer for astronomical_geomancy. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    build_geomancy_wheel_svg,
    render_input_panel,
    render_streamlit,
)

__all__ = [
    "build_geomancy_wheel_svg", "render_input_panel", "render_streamlit",
]
