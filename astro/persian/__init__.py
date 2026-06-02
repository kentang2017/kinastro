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

from astro.persian.sassanian_chart_renderer import (
    generate_sassanian_chart,
    render_sassanian_banner_chart,
    get_sassanian_color_palette,
)

from astro.persian.sassanian_astronomy import (
    calculate_sassanian_ayanamsa,
    get_royal_stars_positions,
    compute_sassanian_planet_positions,
)

from astro.persian.sassanian_symbols import (
    get_pahlavi_name,
    get_royal_star_pahlavi,
    render_faravahar_element,
    render_eight_pointed_star,
)

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
    # 高階計算 (讓舊 API 仍可 import)
    "calculate_firdar",
    "calculate_hyleg_alcocoden",
    "calculate_profections",
    "calculate_almuten_figuris",
    "calculate_persian_lots",
    "get_royal_stars_prominence",
    # 進階版 (lazy-loaded)
    "compute_deep_sassanian_chart",
    "render_deep_streamlit",
]


def compute_deep_sassanian_chart(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the advanced Sassanian chart calculator."""
    from .calculator import compute_deep_sassanian_chart as _fn
    return _fn(*args, **kwargs)


def render_deep_streamlit(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the advanced Sassanian Streamlit renderer.

    The legacy ``astro.persian.renderer`` module was moved to
    ``ui.handlers.tab_persian.render`` during the phase-7 compute /
    render split, so we re-route here.
    """
    from ui.handlers.tab_persian.render import render_streamlit as _fn
    return _fn(*args, **kwargs)
