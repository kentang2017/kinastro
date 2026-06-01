"""UI handler for system **tab_laos**.

Render layer for laos. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    build_lao_brahma_wheel_svg,
    render_lao_horasat,
    render_streamlit,
)

__all__ = [
    "build_lao_brahma_wheel_svg", "render_lao_horasat", "render_streamlit",
]
