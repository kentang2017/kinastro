"""
astro/goetia/__init__.py — Goetia / Solomonic Astrology 子包

格提亞占星（Goetia / Solomonic Astrology）體系：
  - 所羅門魔法傳統 72 柱魔神的占星整合系統
  - 根據出生盤推薦個人化魔神
  - 選時占星（Electional）功能：建議最佳召喚時機
  - 魔神印記（Sigil）SVG 視覺化
  - 儀式建議與召喚語（中英雙語）
  - 與 Enochian 模組風格保持一致

Public API:
    compute_goetia_chart      — 計算完整的個人化 Goetia 命盤 (pure function)
    render_streamlit          — Streamlit UI 渲染器（延遲載入）
    render_demon_sigil_svg    — 魔神印記 SVG
    render_goetia_natal_svg   — Goetia Natal Overview 圓形圖 SVG
    render_element_balance_svg — 元素平衡圖 SVG
    render_recommendation_summary_svg — 推薦魔神摘要 SVG
    GoetiaChart               — 命盤結果 dataclass
    DemonData                 — 魔神資料 dataclass
    DemonRecommendation       — 推薦結果 dataclass
    ElectionalWindow          — 選時窗口 dataclass
"""

from .goetia import compute_goetia_chart

from .constants import (
    GoetiaChart,
    DemonData,
    DemonRecommendation,
    ElectionalWindow,
    GoetiaPlanetPoint,
    SIGNS_EN,
    SIGNS_ZH,
    SIGN_PLANET,
    SIGN_ELEMENT,
    ELEMENT_SIGNS,
    ELEMENT_ZH,
    PLANET_ZH,
    PLANET_COLORS,
    RANK_ZH,
)

from .visualization import (
    render_demon_sigil_svg,
    render_goetia_natal_svg,
    render_element_balance_svg,
    render_recommendation_summary_svg,
)

from .data import (
    load_demons,
    load_demon_by_number,
    load_demons_by_planet,
    load_demons_by_sign,
    load_demons_by_element,
)


def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Streamlit renderer for this package."""
    from ui.handlers.tab_goetia.render import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = [
    # Core computation
    "compute_goetia_chart",
    # Data classes
    "GoetiaChart",
    "DemonData",
    "DemonRecommendation",
    "ElectionalWindow",
    "GoetiaPlanetPoint",
    # Renderer (Streamlit)
    "render_streamlit",
    # SVG visualizations
    "render_demon_sigil_svg",
    "render_goetia_natal_svg",
    "render_element_balance_svg",
    "render_recommendation_summary_svg",
    # Constants
    "SIGNS_EN",
    "SIGNS_ZH",
    "SIGN_PLANET",
    "SIGN_ELEMENT",
    "ELEMENT_SIGNS",
    "ELEMENT_ZH",
    "PLANET_ZH",
    "PLANET_COLORS",
    "RANK_ZH",
    # Data loaders
    "load_demons",
    "load_demon_by_number",
    "load_demons_by_planet",
    "load_demons_by_sign",
    "load_demons_by_element",
]
