"""UI handler for system **tab_kp**.

Render layer for kp. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_horary_interface,
    render_kp_chart,
)

__all__ = [
    "render_horary_interface", "render_kp_chart",
]
