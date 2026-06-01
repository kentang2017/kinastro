"""UI handler for system **tab_damo**.

Render layer for damo. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_damo_chart,
)

__all__ = [
    "render_damo_chart",
]
