"""UI handler for system **tab_diqiyijue**.

Render layer for diqiyijue. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_diqiyijue_chart,
)

__all__ = [
    "render_diqiyijue_chart",
]
