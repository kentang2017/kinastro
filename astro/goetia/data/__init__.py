"""
astro/goetia/data/__init__.py — Goetia 模組資料載入器

提供懶加載（lru_cache）的資料存取函式，讀取 72 柱魔神 JSON 資料庫。
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, List

_DATA_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def _load_json(filename: str) -> Any:
    """讀取並快取 JSON 資料檔案。"""
    path = _DATA_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Goetia data file not found: {path}. "
            f"Ensure it exists in astro/goetia/data/."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in Goetia data file: {path}. Please fix JSON syntax."
        ) from exc


@lru_cache(maxsize=1)
def load_demons() -> List[Dict[str, Any]]:
    """載入 72 柱魔神完整資料庫 / Load the full 72-demon Goetia database."""
    return _load_json("demons.json")


@lru_cache(maxsize=1)
def _demons_by_number() -> Dict[int, Any]:
    """Build a number→demon lookup dict (cached once)."""
    return {d["number"]: d for d in load_demons()}


def load_demon_by_number(number: int) -> Dict[str, Any]:
    """根據編號載入單一魔神 / Load a single demon by number (1–72)."""
    lookup = _demons_by_number()
    if number not in lookup:
        raise ValueError(f"Demon #{number} not found in Goetia database.")
    return lookup[number]


@lru_cache(maxsize=1)
def load_demons_by_planet(planet: str) -> List[Dict[str, Any]]:
    """依行星載入魔神列表 / Load demons by ruling planet."""
    return [d for d in load_demons() if d.get("planet") == planet]


@lru_cache(maxsize=1)
def load_demons_by_sign(sign: str) -> List[Dict[str, Any]]:
    """依星座載入魔神列表 / Load demons by zodiac sign."""
    return [d for d in load_demons() if d.get("zodiac_sign") == sign]


@lru_cache(maxsize=1)
def load_demons_by_element(element: str) -> List[Dict[str, Any]]:
    """依元素載入魔神列表 / Load demons by element."""
    return [d for d in load_demons() if d.get("element") == element]


__all__ = [
    "load_demons",
    "load_demon_by_number",
    "load_demons_by_planet",
    "load_demons_by_sign",
    "load_demons_by_element",
]
