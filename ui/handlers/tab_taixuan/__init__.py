"""UI handler for system **tab_taixuan**.

Render layer for taixuan. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    build_taixuan_svg,
    build_zhan_radar_svg,
    render_annual_timeline,
    render_qigua_ui,
    render_taixuan_chart,
    render_taixuan_intro,
)

__all__ = [
    "build_taixuan_svg", "build_zhan_radar_svg", "render_annual_timeline", "render_qigua_ui", "render_taixuan_chart", "render_taixuan_intro",
]
