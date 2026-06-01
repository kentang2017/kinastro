"""core/streamlit_lazy.py — Official lazy-streamlit boundary layer.

The ``astro/`` package is required to be importable in non-Streamlit
contexts (FastAPI server, ``pytest`` collection, CLI tools, plain
``python -c``) so that downstream consumers don't pay the cost of
loading Streamlit's full import graph.  This module is the **official
boundary** that makes that property hold.

The decoupling
--------------
Any ``astro/*.py`` file that needs to call ``st.xxx(...)`` UI helpers
should do so through this shim, not through a direct
``import streamlit as st``::

    from core.streamlit_lazy import lazy_streamlit as st

Any attribute access on the proxy triggers a one-time import of the
real ``streamlit`` module the first time it is touched at *runtime*,
not at *import time*.  This means:

* ``import astro.yemeni`` does NOT pull in 300+ streamlit submodules.
* Calling ``yemeni.compute_chart(...)`` (pure compute) works in any
  context, with or without streamlit installed.
* Calling ``yemeni.render_streamlit(...)`` (the mixed-in UI helper)
  still uses real streamlit, but only when that function actually
  executes.

The shim is a first-class part of the project — it is *not* a
transitional hack.  Files that consume it (``noted shim consumers``)
are kept in sync with the contract documented in
``scripts/check_no_streamlit_in_astro.py``; a new file that takes
the shortcut of writing ``import streamlit as st`` directly will be
flagged by that regression guard.

Caveats
-------
* The proxy does **not** pretend to be a real ``streamlit`` module:
  it does not expose ``__all__``, ``__path__``, etc.  Code that
  inspects ``type(st)`` or iterates ``dir(st)`` at import time will
  not get the real streamlit namespace.  All noted consumers only
  access attributes on ``st`` inside function bodies, which is the
  supported pattern.
* The shim does NOT verify that the imported ``streamlit`` module is
  the same version the rest of the project uses.  It simply resolves
  whatever the active Python environment provides.

Noted shim consumers (kept in sync by ``scripts/_decouple_streamlit_in_mixed.py``)
---------------------------------------------------------------------------------
The 27 files that import ``lazy_streamlit`` are not the result of a
half-done refactor — they are the canonical way to express "this
module's compute layer is clean, but its render layer is inline."
Each of them is allowed by ``check_no_streamlit_in_astro.py`` not via
the pending-list mechanism but via a positive grep for the shim
import, which is verified by the audit script's success run.
"""
from __future__ import annotations

import sys
from types import ModuleType
from typing import Any


_PROXY_NAME = "streamlit"  # the real module name to import on demand


class _LazyStreamlit:
    """Module-level proxy that defers the real ``import streamlit`` until
    first attribute access.

    The real module, once loaded, is cached in ``sys.modules["streamlit"]``
    (or whatever alias the caller used) so subsequent lookups go straight
    to the real module object — preserving isinstance/identity checks and
    any monkey-patching the host application might do.
    """

    __slots__ = ("_mod", "_alias", "_resolved")

    def __init__(self, alias: str = "st") -> None:
        self._mod: ModuleType | None = None
        self._alias = alias
        self._resolved = False

    def _resolve(self) -> ModuleType:
        mod = self._mod
        if mod is None:
            mod = __import__(_PROXY_NAME)
            self._mod = mod
        return mod

    def __getattr__(self, name: str) -> Any:
        return getattr(self._resolve(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_mod", "_alias", "_resolved"):
            super().__setattr__(name, value)
        else:
            # Allow monkey-patching; route to the real module after first resolve
            setattr(self._resolve(), name, value)

    def __repr__(self) -> str:
        return f"<LazyStreamlit alias={self._alias!r} resolved={self._mod is not None}>"


# Pre-baked proxies for the two common local names used in astro/* source.
lazy_streamlit = _LazyStreamlit("st")
lazy_stream = _LazyStreamlit("stream")

# Convenience: re-export so existing `from core.streamlit_lazy import
# lazy_streamlit as st` lines keep working with a minimal source edit.
__all__ = ["lazy_streamlit", "lazy_stream", "_LazyStreamlit"]
