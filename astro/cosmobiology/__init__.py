"""
astro/cosmobiology — 宇宙生物學 Cosmobiology (Ebertin 中點樹占星)

100% faithful to Reinhold Ebertin's original teachings:
  - The Combination of Stellar Influences (COSI, 1972 English edition)
  - Applied Cosmobiology

Public API:
    compute_cosmobiology_chart  — natal midpoint tree + COSI interpretations
    render_cosmobiology         — Streamlit renderer
"""

from .calculator import compute_cosmobiology_chart, ComsobioChart

def render_cosmobiology(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_cosmobiology renderer for this package."""
    from ui.handlers.tab_cosmobiology.render import render_cosmobiology as _fn
    return _fn(*args, **kwargs)

__all__ = [
    "compute_cosmobiology_chart",
    "ComsobioChart",
    "render_cosmobiology",
]
