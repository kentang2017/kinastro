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
    # 完整星盤計算
    "compute_sassanian_chart",
    "SassanianChart",
    "SassanianPlanet",
    "FirdarPeriod",
    "HylegResult",
]
