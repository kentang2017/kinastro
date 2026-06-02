"""Public API for Malay Ilmu Nujum systems."""

from __future__ import annotations

from .bintang_tujuh import compute_bintang_tujuh
from .common import compute_name_abjad_profile, direction_by_index, get_eight_directions
from .engine import MalayNujumEngine, MalayNujumMethod, MalayNujumRequest
from .mata_angin import compute_mata_angin_lapan
from .perkisaran_naga import compute_perkisaran_naga


def render_streamlit(*args, **kwargs):
    """Lazy-load and run Streamlit renderer."""
    from ui.handlers.tab_malay_nujum.render import render_streamlit as _fn

    return _fn(*args, **kwargs)


__all__ = [
    "MalayNujumEngine",
    "MalayNujumMethod",
    "MalayNujumRequest",
    "compute_bintang_tujuh",
    "compute_mata_angin_lapan",
    "compute_name_abjad_profile",
    "compute_perkisaran_naga",
    "direction_by_index",
    "get_eight_directions",
    "render_streamlit",
]
