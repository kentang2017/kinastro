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


# Lazy re-export: the renderer module moved to ``ui.handlers.tab_picatrix_behenian.render`` during
# the phase-7 compute/render split, but legacy callers still expect to
# find the names at ``astro.picatrix_behenian.<name>``. PEP 562 __getattr__ keeps
# ``import astro.astro.picatrix_behenian`` free of streamlit until a caller actually
# accesses the symbol.
_NEW_HOME = "ui.handlers.tab_picatrix_behenian.render"
_NAMES = ['render_streamlit']
_LEGACY = "picatrix_behenian.renderer"


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
    "BEHENIAN_STARS",
    "BehenianStar",
    "BehenianActivation",
    "detect_activations",
    "compute_today_magic",
    "find_electional_windows",
    "render_streamlit",
]
