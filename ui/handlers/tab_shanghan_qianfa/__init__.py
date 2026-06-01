"""UI handler for system **tab_shanghan_qianfa**.

Render layer for shanghan_qianfa. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_streamlit,
)

__all__ = [
    "render_streamlit",
]
