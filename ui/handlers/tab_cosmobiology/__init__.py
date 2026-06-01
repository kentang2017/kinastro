"""UI handler for system **tab_cosmobiology**.

Render layer for cosmobiology. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_cosmobiology,
)

__all__ = [
    "render_cosmobiology",
]
