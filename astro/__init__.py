"""KinAstro package public API.

This ``__init__`` used to eagerly import ``astro.laos`` (≈310ms cold
import — the single biggest cold-start cost in the package) just so
``from astro import LaoHorasat`` would work. The vast majority of
call sites do ``from astro.qizheng import …`` or
``from astro.western import …`` and never touch laos, so the eager
import was paying for nothing on every single streamlit rerun.

We now expose the laos re-exports through a PEP 562 ``__getattr__``
hook so importing the parent package no longer drags in laos. The
public surface (``LaoHorasat``, ``compute_lao_chart``,
``create_lao_horasat``, ``render_lao_horasat``) is unchanged.
"""

from __future__ import annotations

__all__ = [
    "laos",
    "LaoHorasat",
    "compute_lao_chart",
    "create_lao_horasat",
    "render_lao_horasat",
]


_LAZY_MAP: dict[str, tuple[str, str]] = {
    "LaoHorasat": (".laos", "LaoHorasat"),
    "compute_lao_chart": (".laos", "compute_lao_chart"),
    "create_lao_horasat": (".laos", "create_lao_horasat"),
    "render_lao_horasat": (".laos", "render_lao_horasat"),
}


def __getattr__(name: str):
    if name == "laos":
        import importlib
        mod = importlib.import_module(".laos", __name__)
        globals()[name] = mod
        return mod
    if name in _LAZY_MAP:
        import importlib
        mod = importlib.import_module(_LAZY_MAP[name][0], __name__)
        value = getattr(mod, _LAZY_MAP[name][1])
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
