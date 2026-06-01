"""UI handler for system **tab_dogon_sirius**.

Render layer for dogon. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_dogon_sirius_chart,
)

__all__ = [
    "render_dogon_sirius_chart",
]
