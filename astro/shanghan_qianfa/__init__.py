# -*- coding: utf-8 -*-
"""
astro/shanghan_qianfa — 傷寒鈐法模組

Classical Chinese medical divination based on the Shang Han Lun (傷寒論),
using stem-branch (干支) Qianfa push-calculation to identify the Six Channels
(六經辨證) and recommend classical formulas (經方).
"""

from .calculator import compute_shanghan_qianfa, ShanghanResult


# Lazy re-export: the renderer module moved to ``ui.handlers.tab_shanghan_qianfa.render`` during
# the phase-7 compute/render split, but legacy callers still expect to
# find the names at ``astro.shanghan_qianfa.<name>``. PEP 562 __getattr__ keeps
# ``import astro.astro.shanghan_qianfa`` free of streamlit until a caller actually
# accesses the symbol.
_NEW_HOME = "ui.handlers.tab_shanghan_qianfa.render"
_NAMES = ['render_streamlit']
_LEGACY = "shanghan_qianfa.renderer"


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

__all__ = ["compute_shanghan_qianfa", "ShanghanResult", "render_streamlit"]
