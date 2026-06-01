"""UI handler for system **tab_maya**.

Render layer for maya. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_maya_chart,
)

__all__ = [
    "render_maya_chart",
]
