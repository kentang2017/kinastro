"""
astro/primary_directions — Classical Primary Directions (古典主限推運)

Implements the Hellenistic / Traditional Western Primary Directions system:

  - Zodiacal Primary Directions (黃道主限): Oblique Ascension method
    [Ptolemy, Tetrabiblos c. 150 CE]

  - Mundo Primary Directions (世間主限): Placidus Semi-Arc method
    [Placidus de Titis, Primum Mobile 1657; Gansten 2009]

  - Direct and Converse directions
  - Five major aspects: conjunction, sextile, square, trine, opposition
  - Parallel and contra-parallel of declination
  - Time keys: Naibod (default), Ptolemy (1°/yr), Solar Arc

  - Classical manuscript-style SVG timeline visualization
  - Bilingual (Chinese / English) delineations

Public API:
    compute_primary_directions    — full computation
    render_primary_directions     — Streamlit UI
    render_primary_directions_svg — standalone SVG timeline
"""

from .calculator import (
    compute_primary_directions,
    ChartPoint,
    Direction,
    PrimaryDirectionsResult,
)
from .constants import EXAMPLE_CHARTS


# Lazy re-export: the renderer module moved to ``ui.handlers.tab_primary_directions.render`` during
# the phase-7 compute/render split, but legacy callers still expect to
# find the names at ``astro.primary_directions.<name>``. PEP 562 __getattr__ keeps
# ``import astro.astro.primary_directions`` free of streamlit until a caller actually
# accesses the symbol.
_NEW_HOME = "ui.handlers.tab_primary_directions.render"
_NAMES = ['render_primary_directions', 'render_primary_directions_svg']
_LEGACY = "primary_directions.renderer"


def __getattr__(name):
    if name in _NAMES:
        try:
            import importlib
            mod = importlib.import_module(_NEW_HOME)
            value = getattr(mod, name)
        except (ImportError, AttributeError):
            try:
                import importlib
                legacy = importlib.import_module(_LEGACY, __name__)
                value = getattr(legacy, name)
            except (ImportError, AttributeError):
                raise AttributeError(
                    "module %r has no attribute %r" % (__name__, name)
                )
        globals()[name] = value
        return value
    raise AttributeError("module %r has no attribute %r" % (__name__, name))

__all__ = [
    "compute_primary_directions",
    "ChartPoint",
    "Direction",
    "PrimaryDirectionsResult",
    "render_primary_directions",
    "render_primary_directions_svg",
    "EXAMPLE_CHARTS",
]
