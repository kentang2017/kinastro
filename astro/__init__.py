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
# pylint: disable=import-outside-toplevel,invalid-name

from __future__ import annotations

from typing import Callable

LaoHorasat = None
compute_lao_chart = None
create_lao_horasat = None
render_lao_horasat = None
BaseChartResult = None
BirthData = None
WesternChartResult = None
ZiweiChartResult = None
chart_result_from_legacy = None

__all__ = [
    "laos",
    "LaoHorasat",
    "compute_lao_chart",
    "compute_chart",
    "get_chart_computer",
    "register_chart_computer",
    "create_lao_horasat",
    "render_lao_horasat",
    "BaseChartResult",
    "BirthData",
    "WesternChartResult",
    "ZiweiChartResult",
    "chart_result_from_legacy",
]


_LAZY_MAP: dict[str, tuple[str, str]] = {
    "BaseChartResult": (".models", "BaseChartResult"),
    "BirthData": (".models", "BirthData"),
    "LaoHorasat": (".laos", "LaoHorasat"),
    "WesternChartResult": (".models", "WesternChartResult"),
    "ZiweiChartResult": (".models", "ZiweiChartResult"),
    "chart_result_from_legacy": (".models", "chart_result_from_legacy"),
    "compute_lao_chart": (".laos", "compute_lao_chart"),
    "create_lao_horasat": (".laos", "create_lao_horasat"),
    "render_lao_horasat": (".laos", "render_lao_horasat"),
}


def _compute_western_unified(birth_data):
    from .western.western import compute_western_chart

    return compute_western_chart(**birth_data.to_compute_kwargs(), as_model=True)


def _compute_ziwei_unified(birth_data):
    from .ziwei import compute_ziwei_chart

    payload = birth_data.to_compute_kwargs(include_gender=True)
    if "gender" not in payload:
        payload["gender"] = "男"
    return compute_ziwei_chart(**payload, as_model=True)


_UNIFIED_COMPUTE_REGISTRY: dict[str, Callable] = {
    "western": _compute_western_unified,
    "tab_western": _compute_western_unified,
    "ziwei": _compute_ziwei_unified,
    "tab_ziwei": _compute_ziwei_unified,
}


def register_chart_computer(system: str, computer: Callable) -> None:
    """Register or override a unified chart computer."""
    if not isinstance(system, str) or not system.strip():
        raise ValueError("system must be a non-empty string")
    _UNIFIED_COMPUTE_REGISTRY[system.strip().lower()] = computer


def get_chart_computer(system: str) -> Callable:
    """Return the registered unified chart computer for a system."""
    if not isinstance(system, str) or not system.strip():
        raise ValueError("system must be a non-empty string")
    normalized = system.strip().lower()
    compute_func = _UNIFIED_COMPUTE_REGISTRY.get(normalized)
    if compute_func is None:
        supported = ", ".join(sorted(_UNIFIED_COMPUTE_REGISTRY))
        raise ValueError(
            f"Unsupported unified chart system: {system}. Supported keys: {supported}"
        )
    return compute_func


def compute_chart(system: str, birth_data):
    """Compute a chart through the unified model interface."""
    return get_chart_computer(system)(birth_data)


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
