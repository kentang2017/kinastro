"""
astro/trutine_of_hermes — 赫密士出生前世盤（Trutine of Hermes / Prenatal Epoch）

Implements the classical Hellenistic Prenatal Epoch technique attributed to
Hermes Trismegistus and described in Ptolemy's *Centiloquium* (Karpos),
as well as the systematic treatment by E.H. Bailey in
*The Prenatal Epoch* (1916).

Public API:
    compute_epoch_chart   — compute the Prenatal Epoch and Natal charts
    render_streamlit      — Streamlit UI renderer
    PrenatalEpochChart    — result dataclass
    TrutineVariant        — enum of supported calculation variants
"""

from .calculator import (
    compute_epoch_chart,
    PrenatalEpochChart,
    EpochPlanetPosition,
    TrutineVariant,
)


# Lazy re-export: the renderer module moved to ``ui.handlers.tab_trutine_of_hermes.render`` during
# the phase-7 compute/render split, but legacy callers still expect to
# find the names at ``astro.trutine_of_hermes.<name>``. PEP 562 __getattr__ keeps
# ``import astro.astro.trutine_of_hermes`` free of streamlit until a caller actually
# accesses the symbol.
_NEW_HOME = "ui.handlers.tab_trutine_of_hermes.render"
_NAMES = ['render_streamlit']
_LEGACY = "trutine_of_hermes.renderer"


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
    "compute_epoch_chart",
    "PrenatalEpochChart",
    "EpochPlanetPosition",
    "TrutineVariant",
    "render_streamlit",
]
