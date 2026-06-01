"""UI handler for system **tab_western**.

Render layer for the Western natal chart. The compute logic stays in
``astro/western/``; this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    build_western_wheel_svg,
    render_streamlit,
)

__all__ = [
    "build_western_wheel_svg",
    "render_streamlit",
]
