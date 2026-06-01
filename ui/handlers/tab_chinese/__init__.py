"""UI handler for system **tab_chinese**.

Render layer for financial. The compute logic stays in astro/;
this package is the streamlit-side dispatcher.
"""

from __future__ import annotations

from .render import (
    render_stock_fortune_tab,
)

__all__ = [
    "render_stock_fortune_tab",
]
