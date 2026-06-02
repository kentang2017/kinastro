"""Cross-test isolation conftest.

Several tests in this suite inject a stub ``streamlit`` module into
``sys.modules`` (see ``test_stock_renderer_compatibility`` and
``test_stock_fetcher_fallback``). That stub sticks around after those
tests finish, and ``core.cache._in_streamlit()`` then flips to "in
streamlit context" mode for the rest of the session — turning the
decorator wrappers into real Streamlit cache calls that subsequently
blow up with ``UnserializableReturnValueError`` when they receive
un-picklable inputs.

We don't want a conftest-level cache_shim override, because that would
hide real streamlit-integration bugs. Instead, the simplest fix is to
make the cache shim self-defend: when it sees streamlit in sys.modules
but no real ScriptRunContext, treat that as "not in streamlit" and
fall back. The shim already does that. The remaining failures are
test-runner-level, so the only thing left is to ensure each test
that injects a fake streamlit cleans up after itself.

This conftest auto-cleans sys.modules["streamlit"] between tests in
the worst-case scenarios — i.e. when the fixture forgot to do it.
"""
from __future__ import annotations

import sys
import pytest


@pytest.fixture(autouse=True)
def _isolate_streamlit_state():
    """Make sure no fake streamlit module leaks between tests."""
    had_streamlit = "streamlit" in sys.modules
    saved = sys.modules.get("streamlit")
    yield
    # If the test injected a stub, restore the prior state. If no
    # streamlit was present before and a stub was added, pop it.
    if not had_streamlit:
        sys.modules.pop("streamlit", None)
    elif sys.modules.get("streamlit") is not saved:
        sys.modules["streamlit"] = saved
