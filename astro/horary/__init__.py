"""
astro/horary — Traditional Horary Astrology Module

Implements both Western (Lilly/Bonatti) and Vedic (Prashna Marga) horary systems.

Western tradition (William Lilly, Guido Bonatti):
  - Strict traditional rules: Significators, Essential + Accidental Dignities
  - Aspects (applying/separating), Reception, Translation/Collection of Light
  - Void of Course Moon with Lilly's exception signs
  - Strictures Against Judgment
  - Rule-based judgment for common question types

Vedic tradition (Prasna Marga):
  - Prasna Lagna, Arudha Lagna
  - Lagna Lord and Moon assessment
  - Optional number-based Lagna (1-108)
  - Sidereal positions (Lahiri Ayanamsa)

Sources:
  - William Lilly, "Christian Astrology" (1647)
  - Guido Bonatti, "Liber Astronomiae" (~1277)
  -《Prasna Marga》(Traditional Kerala Jyotish Prashna text)
"""

from .calculator import (
    compute_western_horary,
    compute_vedic_prashna,
    compute_horary_chart,
    WesternHoraryChart,
    VedicPrashnaChart,
)

def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_streamlit renderer for this package."""
    from ui.handlers.tab_horary.render import render_streamlit as _fn
    return _fn(*args, **kwargs)


def render_western_horary_svg(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_western_horary_svg renderer for this package."""
    from ui.handlers.tab_horary.render import render_western_horary_svg as _fn
    return _fn(*args, **kwargs)


def render_vedic_prashna_svg(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_vedic_prashna_svg renderer for this package."""
    from ui.handlers.tab_horary.render import render_vedic_prashna_svg as _fn
    return _fn(*args, **kwargs)

__all__ = [
    "compute_western_horary",
    "compute_vedic_prashna",
    "compute_horary_chart",
    "WesternHoraryChart",
    "VedicPrashnaChart",
    "render_streamlit",
    "render_western_horary_svg",
    "render_vedic_prashna_svg",
]
