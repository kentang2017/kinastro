"""
astro/picatrix_behenian — Picatrix + Behenian 15 Fixed Stars Magic Module

Implements Agrippa / Hermes Trismegistus correspondences for the fifteen
Behenian stars as described in Heinrich Cornelius Agrippa's *Three Books of
Occult Philosophy* (De Occulta Philosophia, 1531) and ultimately derived from
the *Ghayat al-Hakim* (Picatrix, 10th–11th c. CE).

Exports
-------
BEHENIAN_STARS      : list[BehenianStar]
detect_activations  : detect planet–star conjunctions within the magic orb
compute_today_magic : find which Behenian stars are active right now
render_streamlit    : Streamlit page renderer
"""

from .constants import BEHENIAN_STARS, BehenianStar
from .calculator import (
    BehenianActivation,
    detect_activations,
    compute_today_magic,
    find_electional_windows,
)

def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_streamlit renderer for this package."""
    from ui.handlers.tab_picatrix_behenian.render import render_streamlit as _fn
    return _fn(*args, **kwargs)

__all__ = [
    "BEHENIAN_STARS",
    "BehenianStar",
    "BehenianActivation",
    "detect_activations",
    "compute_today_magic",
    "find_electional_windows",
    "render_streamlit",
]
