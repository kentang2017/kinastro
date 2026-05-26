"""KinAstro Bintang Duabelas public API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from .abjad import AbjadCalculator
from .azimat import AzimatGenerator
from .core import BintangDuabelas, BintangDuabelasEngine, BintangDuabelasRequest
from .hisab import HisabNama
from .hours import PlanetaryHours
from .houses import TwelveHouses
from .normalization import NameNormalization, normalize_name, roman_to_jawi
from .yearly import YearlyFortune


def compute_bintang_duabelas(
    name: str = "",
    day_name: Optional[str] = None,
    birth_datetime: Optional[datetime] = None,
    script_hint: str = "auto",
) -> Dict[str, Any]:
    """Compute Bintang Duabelas chart.

    Args:
        name: Person's name
        day_name: Day of week (e.g., "ahad", "isnin")
        birth_datetime: Birth datetime for planetary hours
        script_hint: Script hint for name normalization

    Returns:
        Dict containing Abjad, Hisab, and other calculations
    """
    engine = BintangDuabelasEngine()
    result: Dict[str, Any] = {}

    if name.strip():
        result["abjad_total"] = engine.name_to_abjad(name, script_hint=script_hint)
        result["hisab_total"], result["hisab_remainder"] = engine.hisab_nama(
            name, script_hint=script_hint
        )
        result["day_name"] = day_name or engine._resolve_day_name(None, birth_datetime)

    return result


def render_streamlit(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_streamlit as _fn

    return _fn(*args, **kwargs)

__all__ = [
    "AbjadCalculator",
    "AzimatGenerator",
    "BintangDuabelas",
    "BintangDuabelasEngine",
    "BintangDuabelasRequest",
    "HisabNama",
    "NameNormalization",
    "PlanetaryHours",
    "TwelveHouses",
    "YearlyFortune",
    "compute_bintang_duabelas",
    "normalize_name",
    "roman_to_jawi",
    "render_streamlit",
]
