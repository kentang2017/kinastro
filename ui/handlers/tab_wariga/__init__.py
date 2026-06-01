"""UI handler for system **tab_wariga**.

Render layer for wariga. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_modern_table,
    render_palalintangan_html,
    render_streamlit,
    render_svg,
    render_text,
)

__all__ = [
    "render_modern_table", "render_palalintangan_html", "render_streamlit", "render_svg", "render_text",
]
