"""UI handler for system **tab_etruscan**.

Render layer for etruscan. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    build_piacenza_liver_svg,
    render_streamlit,
)

__all__ = [
    "build_piacenza_liver_svg", "render_streamlit",
]
