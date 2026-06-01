"""UI handler for system **tab_tojeong**.

Render layer for tojeong. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_tojeong_chart,
    render_tojeong_svg,
)

__all__ = [
    "render_tojeong_chart", "render_tojeong_svg",
]
