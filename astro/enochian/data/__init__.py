"""Structured data loaders for Enochian module."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

_DATA_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def _load_json(filename: str) -> Dict[str, Any]:
    path = _DATA_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_angel_tables() -> Dict[str, Any]:
    return _load_json("angels.json")


@lru_cache(maxsize=1)
def load_sigillum_rules() -> Dict[str, Any]:
    return _load_json("sigillum_rules.json")


@lru_cache(maxsize=1)
def load_watchtower_aethyr_rules() -> Dict[str, Any]:
    return _load_json("watchtower_aethyr_rules.json")


__all__ = [
    "load_angel_tables",
    "load_sigillum_rules",
    "load_watchtower_aethyr_rules",
]
