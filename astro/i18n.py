"""Lazy-loaded i18n module for KinAstro.

TRANSLATIONS used to be a 5171-line module-level dict that cost ~370ms
to parse at every streamlit rerun (the dict is referenced by ~40
``from astro.i18n import t, auto_cn, …`` statements across the
codebase, so importing it was unavoidable). It is now stored as JSON
under ``astro/data/i18n_translations.json`` and loaded once per process
on first access via a module-level cache.  The public functions
(``t``, ``auto_cn``, ``get_lang``, ``get_ui_lang``, ``set_ui_lang``)
keep the same signatures so call sites do not need to change.

The hot path (``t(key)`` / ``auto_cn(...)``) reads from a cached
``dict`` populated on first call.  All lookups stay O(1).
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

# Path to the JSON catalog; resolved once at import time so the hot
# path doesn't have to call __file__ every call.
_DATA_PATH = (
    Path(__file__).resolve().parent / "data" / "i18n_translations.json"
)

# Lazy cache. Populated on first access to TRANSLATIONS, t, or auto_cn.
_TRANSLATIONS: dict | None = None
_LOAD_LOCK = threading.Lock()


def _ensure_loaded() -> dict:
    """Populate the in-memory cache and return it (thread-safe)."""
    global _TRANSLATIONS
    if _TRANSLATIONS is not None:
        return _TRANSLATIONS
    with _LOAD_LOCK:
        if _TRANSLATIONS is None:  # double-check under lock
            with open(_DATA_PATH, encoding="utf-8") as f:
                _TRANSLATIONS = json.load(f)
    return _TRANSLATIONS


def __getattr__(name: str):
    """PEP 562: only resolve ``TRANSLATIONS`` (or its aliases) on
    access.  Anything else falls through to a normal ``AttributeError``."""
    if name == "TRANSLATIONS":
        return _ensure_loaded()
    raise AttributeError(f"module 'astro.i18n' has no attribute {name!r}")


# ── Language state ──────────────────────────────────────────────────────────
# ── Language state ──────────────────────────────────────────────────────────
_DEFAULT_LANG = "zh"
_LANG_ENV = os.environ.get("KINASTRO_LANG", _DEFAULT_LANG).lower()
_VALID_LANGS = ("zh", "en", "zh_cn", "ko", "ja", "vi", "th")  # tuple for O(1) `in` check (frozen)


def get_ui_lang() -> str:
    """Return the active UI language (zh / en / zh_cn)."""
    return _LANG_ENV


def set_ui_lang(lang: str) -> None:
    """Programmatically override the UI language for this process.

    The change is process-local; for full streamlit session control
    use ``st.session_state`` from the app entry point.
    """
    global _LANG_ENV
    if lang not in _VALID_LANGS:
        raise ValueError(f"Unknown language code: {lang!r}")
    _LANG_ENV = lang


def get_lang() -> str:
    """Return the currently active language code."""
    return _LANG_ENV


# ── Lookup helpers ─────────────────────────────────────────────────────────

def _t2s(text: str) -> str:
    """If text is an i18n key (str starting with 'key::'), resolve it.

    Plain strings are returned untouched.
    """
    if isinstance(text, str) and text.startswith("key::"):
        return t(text[5:])
    return text


def auto_cn(text: str, en_text: str = "") -> str:
    """Return the localised version of ``text``.

    The original convention is: ``text`` is the zh string, ``en_text``
    is the English fallback.  We honour that — but the underlying
    mechanism is just a TRANSLATIONS lookup, so if ``text`` happens
    to be a key (starts with ``key::``) we look that up instead.
    
    For other languages (ko, ja, vi, th), it returns:
    - The translation from i18n_translations.json if found
    - Otherwise, the en_text if provided
    - Otherwise, the original text (zh/TW)
    """
    lang = _LANG_ENV
    if lang.startswith("en"):
        return en_text or text
    # For other languages, check i18n_translations.json first
    if lang not in ("zh", "zh_cn"):
        # Try to find translation from i18n_translations.json
        # Look up both text and en_text as keys
        entry = _ensure_loaded().get(en_text)
        if entry and lang in entry:
            return entry[lang]
        # Check if text itself is a key
        entry = _ensure_loaded().get(text)
        if entry and lang in entry:
            return entry[lang]
        # Fall back to en_text if provided, otherwise text
        return en_text or text
    return text


def t(key: str) -> str:
    """Look up ``key`` in TRANSLATIONS for the active language.

    Falls back to ``en`` then to the raw key, so missing keys never
    break the UI — they just render the key string.
    """
    table = _ensure_loaded()
    entry = table.get(key)
    if entry is None:
        return key
    lang = _LANG_ENV
    if lang in entry:
        return entry[lang]
    if "en" in entry:
        return entry["en"]
    return key


__all__ = [
    "TRANSLATIONS",
    "auto_cn",
    "get_lang",
    "get_ui_lang",
    "set_ui_lang",
    "t",
    "_t2s",
]
