"""
astro/persian/__init__.py — 波斯薩珊傳統占星模組

Sassanian/Persian Traditional Astrology (3rd–7th century CE)
基於薩珊王朝古文獻（Bundahishn、Dorotheus Pahlavi 譯本）與出土文物重建

References
----------
- Greater Bundahishn (Iranian Bundahishn, tr. Anklesaria, 1956)
- Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
- Al-Biruni, "The Chronology of Ancient Nations" (tr. Sachau, 1879)
- Pingree, D. (1963). "Classical and Byzantine Astrology in Sassanian Persia"
- Sassanian silver plates and rock reliefs (Metropolitan Museum, Louvre)
"""

from astro.persian.sassanian_astrology import (
    compute_sassanian_chart,
    SassanianChart,
    SassanianPlanet,
    FirdarPeriod,
    HylegResult,
    calculate_firdar,
    calculate_hyleg_alcocoden,
    calculate_profections,
    calculate_almuten_figuris,
    calculate_persian_lots,
    get_royal_stars_prominence,
)
from astro.persian.sassanian_astronomy import (
    calculate_sassanian_ayanamsa,
    get_royal_stars_positions,
    compute_sassanian_planet_positions,
)


def generate_sassanian_chart(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Sassanian chart SVG generator."""
    from astro.persian.sassanian_chart_renderer import generate_sassanian_chart as _fn
    return _fn(*args, **kwargs)


def render_sassanian_banner_chart(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Sassanian banner renderer."""
    from astro.persian.sassanian_chart_renderer import render_sassanian_banner_chart as _fn
    return _fn(*args, **kwargs)


def get_sassanian_color_palette(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the Sassanian color palette helper."""
    from astro.persian.sassanian_chart_renderer import get_sassanian_color_palette as _fn
    return _fn(*args, **kwargs)

__all__ = [
    # 星盤渲染
    "generate_sassanian_chart",
    "render_sassanian_banner_chart",
    "get_sassanian_color_palette",
    # 天文計算
    "calculate_sassanian_ayanamsa",
    "get_royal_stars_positions",
    "compute_sassanian_planet_positions",
    # 符號系統
    "get_pahlavi_name",
    "get_royal_star_pahlavi",
    "render_faravahar_element",
    "render_eight_pointed_star",
    # 完整星盤計算 (基礎版)
    "compute_sassanian_chart",
    "SassanianChart",
    "SassanianPlanet",
    "FirdarPeriod",
    "HylegResult",
    # 進階版 (lazy-loaded)
    "compute_deep_sassanian_chart",
    "render_deep_streamlit",
]


def compute_deep_sassanian_chart(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the advanced Sassanian chart calculator."""
    from .calculator import compute_deep_sassanian_chart as _fn
    return _fn(*args, **kwargs)


def render_deep_streamlit(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the advanced Sassanian Streamlit renderer."""
    from ui.handlers.tab_persian.render import render_streamlit as _fn
    return _fn(*args, **kwargs)
