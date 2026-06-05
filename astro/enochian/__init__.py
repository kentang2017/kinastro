"""
astro/enochian/__init__.py — Enochian Astrology sub-package

伊諾克占星（Enochian Astrology）體系：
  - 將標準出生盤與 John Dee & Edward Kelley 的天使魔法系統結合
  - 30 個以太層（Aethyrs）的個人化對應
  - 四個守望塔（Watchtowers）的命盤分析
  - Sigillum Dei Aemeth 個人化視覺化
  - 守護天使（Patron/Matron Angels）解讀

Public API:
    compute_enochian_chart   — 計算完整的 Enochian 命盤 (pure function)
    render_streamlit         — Streamlit UI 渲染器
    render_sigillum_svg      — Sigillum Dei Aemeth SVG
    render_watchtower_svg    — 守望塔 2×2 網格 SVG
    render_aethyr_svg        — 30 Aethyr 層級圖 SVG
    render_enochian_summary_svg — 命盤概覽圓形圖 SVG
    EnochianChart            — 命盤結果 dataclass
"""

from .enochian import (
    compute_enochian_chart,
    EnochianChart,
    EnochianPlanetPoint,
    EnochianHousePoint,
    PatronAngel,
    AethyrReading,
    SigillumNode,
)

from .visualization import (
    render_sigillum_svg,
    render_watchtower_svg,
    render_aethyr_svg,
    render_enochian_summary_svg,
    render_element_balance_svg,
)

from .constants import (
    AETHYRS,
    AETHYR_BY_NUMBER,
    AETHYR_BY_NAME,
    WATCHTOWERS,
    ENOCHIAN_PLANETS,
    SIGN_ENOCHIAN,
    HOUSE_ENOCHIAN,
    SIGILLUM_DEI_AEMETH,
    ELEMENT_TABLE,
    AethyrData,
    WatchtowerData,
)
from .data import (
    load_angel_tables,
    load_sigillum_rules,
    load_watchtower_aethyr_rules,
)


def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Streamlit renderer for this package."""
    from ui.handlers.tab_enochian.render import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = [
    # Calculator
    "compute_enochian_chart",
    "EnochianChart",
    "EnochianPlanetPoint",
    "EnochianHousePoint",
    "PatronAngel",
    "AethyrReading",
    "SigillumNode",
    # Renderer
    "render_streamlit",
    "render_sigillum_svg",
    "render_watchtower_svg",
    "render_aethyr_svg",
    "render_enochian_summary_svg",
    "render_element_balance_svg",
    # Constants
    "AETHYRS",
    "AETHYR_BY_NUMBER",
    "AETHYR_BY_NAME",
    "WATCHTOWERS",
    "ENOCHIAN_PLANETS",
    "SIGN_ENOCHIAN",
    "HOUSE_ENOCHIAN",
    "SIGILLUM_DEI_AEMETH",
    "ELEMENT_TABLE",
    "AethyrData",
    "WatchtowerData",
    "load_angel_tables",
    "load_sigillum_rules",
    "load_watchtower_aethyr_rules",
]
