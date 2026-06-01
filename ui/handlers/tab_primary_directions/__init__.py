"""UI handler for system **tab_primary_directions**.

Render layer for primary_directions. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_primary_directions,
    render_primary_directions_svg,
)

__all__ = [
    "render_primary_directions", "render_primary_directions_svg",
]
