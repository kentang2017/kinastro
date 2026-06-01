"""Shared UI helpers for KinAstro.

Provides the `t()` translation function and other small utilities that
are needed across the handler modules without importing from app.py.
"""

from __future__ import annotations

import streamlit as st

from astro.i18n import TRANSLATIONS, _t2s, auto_cn  # noqa: F401 — re-exported


def t(key: str) -> str:
    """Return the translated string for *key* in the current UI language.

    For zh_cn (Simplified Chinese), falls back to zh (Traditional) if no
    explicit zh_cn entry exists, and automatically converts to Simplified
    Chinese.
    """
    lang = st.session_state.get("lang", "zh")
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    if lang == "zh_cn":
        val = entry.get("zh_cn")
        if val is not None:
            return val
        return _t2s(entry.get("zh", key))
    return entry.get(lang, entry.get("zh", key))
