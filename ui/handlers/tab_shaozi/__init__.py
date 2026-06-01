"""UI handler for system **tab_shaozi**.

Render layer for shaozi. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_shaozi_64key_section,
    render_shaozi_placeholder,
    render_shaozi_result,
    render_shaozi_tiaowen_browser,
)

__all__ = [
    "render_shaozi_64key_section", "render_shaozi_placeholder", "render_shaozi_result", "render_shaozi_tiaowen_browser",
]
