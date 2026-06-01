"""UI handler for system **tab_wuyunliuqi**.

Render layer for wuyunliuqi. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_streamlit,
    render_wuyunliuqi_intro,
)

__all__ = [
    "render_streamlit", "render_wuyunliuqi_intro",
]
