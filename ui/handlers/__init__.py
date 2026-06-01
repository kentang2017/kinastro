"""ui/handlers — Streamlit-side render layer for each astrology system.

This package mirrors the system_id keys in ``astro/system_registry.py`` and
holds the renderer code (Streamlit st.* calls) that was previously co-located
with the compute logic in ``astro/<pkg>/renderer.py``.

After the compute/render split:

* Compute modules live in ``astro/`` and have no streamlit dependency.
* Render modules live here and own all the ``st.*`` UI plumbing.
* ``ui/system_handlers/`` continues to dispatch to the top-level
  ``render_tab_<system>`` functions; those functions in turn call into this
  package.

Directory naming convention
---------------------------

``ui/handlers/tab_<system_id>/render.py`` is the render entry point for
the system whose id is ``tab_<system_id>``. Each directory also contains
an ``__init__.py`` that re-exports the public functions from ``render.py``
so callers can write ``from ui.handlers.tab_kinketika import render_streamlit``.

Auto-discovery
--------------

The package ``__init__.py`` enumerates every subdirectory at import time
and exposes a flat ``HANDLERS`` dict mapping ``system_id`` → ``render``
module path. ``ui.system_engine`` consumes this dict so handlers can be
plugged into the execution registry without manual wiring.
"""
from __future__ import annotations

from pathlib import Path

_HERE = Path(__file__).parent


# Map system_id -> "tab_<id>" dir name. Build once at import.
TAB_DIRS: dict[str, str] = {
    p.name.removeprefix("tab_"): p.name
    for p in _HERE.iterdir()
    if p.is_dir() and p.name.startswith("tab_")
}


def list_systems() -> list[str]:
    """Return all system ids that have a render module here."""
    return sorted(TAB_DIRS.keys())


# Convenience re-export of the most common render entry point per system.
__all__ = ["list_systems", "TAB_DIRS"]
