"""UI-optional caching shim.

Use these decorators in ``astro/`` (and anywhere else that should remain
importable without Streamlit) instead of ``@st.cache_data`` /
``@st.cache_resource`` directly.

Behavior
--------
* **Inside a running Streamlit app** (detected via
  ``streamlit.runtime.scriptrunner.get_script_run_ctx() is not None``):
  delegates to the real ``streamlit.cache_data`` /
  ``streamlit.cache_resource`` decorators.  Cross-rerun persistence, shared
  cache between users, and TTL semantics behave exactly as the Streamlit
  docs describe.  No code change is required at the call site.

* **Outside Streamlit** (CLI, ``pytest``, FastAPI, Jupyter, plain
  ``python -c``): falls back to a lightweight in-process implementation.
  ``cache_resource`` becomes ``functools.lru_cache(maxsize=128)``;
  ``cache_data`` becomes a tiny TTL dict with a hard cap of 1024 entries.
  The fallback is process-local — there is no cross-process persistence.

Why we need it
--------------
Many ``astro/`` modules used ``@st.cache_data`` for memoizing pure
computation, which transitively forced every consumer of those modules
(including the FastAPI ``api_server.py`` and the ``pytest`` collection
step) to import Streamlit.  That made the API server unrunnable in any
environment without the full Streamlit stack, and broke 16 test files at
collection time.

Caveats of the fallback
-----------------------
* ``cache_data(ttl=...)`` is honored best-effort with a monotonic clock;
  cache entries are stored in the current process only.
* ``cache_data`` requires hashable positional and keyword arguments.
  The 28 audited call sites all pass simple scalars/strings/tuples, so
  this is sufficient.  Do not use ``cache_data`` for functions whose
  arguments include unhashable types (lists, dicts, sets, dataclass
  instances) when running outside Streamlit — call ``compute_*`` directly
  with the data unravelled into hashable args, or wrap the call yourself
  with ``functools.lru_cache``.

Public API
----------
* ``cache_data(ttl=None, show_spinner=True, **kwargs)``
* ``cache_resource(*args, **kwargs)``  — supports both ``@cache_resource``
  (no parens) and ``@cache_resource(...)`` (with kwargs) call styles,
  matching Streamlit's behavior.
"""

from __future__ import annotations

import functools
import sys
import time
from typing import Any, Callable


def _in_streamlit() -> bool:
    """Return True iff we are executing inside a live Streamlit script run.

    We use a deliberately conservative probe: we only return True if
    Streamlit is *already* in ``sys.modules`` (meaning some other code
    has imported it, which typically only happens inside an actual
    ``streamlit run`` session).  In CLI / FastAPI / pytest contexts,
    Streamlit is absent from ``sys.modules`` at the time the first
    ``astro.*`` module is imported, and we return False without ever
    touching the Streamlit import graph.

    This is the key to keeping ``astro.*`` importable in non-Streamlit
    environments: doing a runtime ``importlib.util.find_spec`` or
    ``import streamlit...`` here would drag in 300+ Streamlit
    submodules at first import, defeating the whole point of the
    caching shim.
    """
    if "streamlit" not in sys.modules:
        return False
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False
    try:
        return get_script_run_ctx() is not None
    except Exception:
        return False


# We resolve the real streamlit decorators lazily, only after a positive
# ``_in_streamlit()`` check.  This keeps the import graph tiny when
# streamlit is *not* the runtime, which is exactly the property the
# decoupling refactor is trying to guarantee.
if _in_streamlit():
    from streamlit import cache_data as cache_data  # type: ignore[no-redef]  # noqa: F401
    from streamlit import cache_resource as cache_resource  # type: ignore[no-redef]  # noqa: F401
else:
    # ── In-process fallback ────────────────────────────────────────────────
    _DATA_CACHE_MAX_ENTRIES = 1024

    def cache_data(
        ttl: int | None = None,
        show_spinner: bool = True,
        **_unused: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """In-process TTL-bounded memoization.

        Args:
            ttl: Seconds before a stored entry is considered stale. ``None``
                means entries never expire. Ignored when running inside
                Streamlit (the real decorator is used).
            show_spinner: Accepted for API parity with Streamlit. Has no
                effect in fallback mode.
        """
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            store: dict[tuple, tuple[float, Any]] = {}

            def _key(args: tuple, kwargs: dict) -> tuple:
                return (args, tuple(sorted(kwargs.items())))

            @functools.wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    key = _key(args, kwargs)
                except TypeError:
                    # Unhashable argument — fall through to a direct call.
                    return fn(*args, **kwargs)
                now = time.monotonic()
                hit = store.get(key)
                if hit is not None and (ttl is None or now - hit[0] < ttl):
                    return hit[1]
                value = fn(*args, **kwargs)
                store[key] = (now, value)
                if len(store) > _DATA_CACHE_MAX_ENTRIES:
                    oldest_key = min(store, key=lambda k: store[k][0])
                    store.pop(oldest_key, None)
                return value

            def cache_clear() -> None:
                store.clear()

            wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
            return wrapper

        return decorator

    def cache_resource(*args: Any, **kwargs: Any) -> Any:
        """In-process LRU memoization for resources (e.g. swisseph init).

        Accepts both ``@cache_resource`` (no parens) and
        ``@cache_resource(...)`` (with kwargs) call styles.
        """
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return functools.lru_cache(maxsize=128)(args[0])

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            return functools.lru_cache(maxsize=128)(fn)

        return decorator


__all__ = ["cache_data", "cache_resource"]
