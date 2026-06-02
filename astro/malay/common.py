"""Shared utilities for Malay Ilmu Nujum modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from astro.bintang_duabelas.abjad import AbjadCalculator


@dataclass(frozen=True)
class DirectionInfo:
    """Eight-direction metadata used by multiple Malay systems."""

    index: int
    key: str
    direction_zh: str
    direction_en: str
    direction_ms: str
    animal_zh: str
    animal_en: str
    angle_deg: float


_EIGHT_DIRECTIONS: tuple[DirectionInfo, ...] = (
    DirectionInfo(0, "north", "北", "North", "Utara", "魚", "Fish", 0.0),
    DirectionInfo(1, "northeast", "東北", "Northeast", "Timur Laut", "鹿", "Deer", 45.0),
    DirectionInfo(2, "east", "東", "East", "Timur", "鳥", "Bird", 90.0),
    DirectionInfo(3, "southeast", "東南", "Southeast", "Tenggara", "蛇", "Serpent", 135.0),
    DirectionInfo(4, "south", "南", "South", "Selatan", "虎", "Tiger", 180.0),
    DirectionInfo(5, "southwest", "西南", "Southwest", "Barat Daya", "龍", "Dragon", 225.0),
    DirectionInfo(6, "west", "西", "West", "Barat", "龜", "Turtle", 270.0),
    DirectionInfo(7, "northwest", "西北", "Northwest", "Barat Laut", "馬", "Horse", 315.0),
)


def get_eight_directions() -> list[DirectionInfo]:
    """Return a mutable list of the canonical eight directions."""
    return list(_EIGHT_DIRECTIONS)


def direction_by_index(index: int) -> DirectionInfo:
    """Return direction metadata by modulo-8 index."""
    return _EIGHT_DIRECTIONS[index % 8]


def compute_name_abjad_profile(name: str, script_hint: str = "auto") -> dict[str, object]:
    """Reusable abjad profile payload for Malay Nujum modules."""
    calc = AbjadCalculator()
    normalized = calc.normalize(name, script_hint=script_hint)
    breakdown = calc.get_letter_breakdown(name, script_hint=script_hint)
    total = calc.name_to_abjad(name, script_hint=script_hint)
    full_total = calc.name_to_abjad_full(name, script_hint=script_hint)
    return {
        "input_name": name,
        "script_hint": script_hint,
        "normalized": normalized.normalized,
        "source_script": normalized.source_script,
        "used_override": normalized.used_override,
        "abjad_total": total,
        "abjad_full_total": full_total,
        "letter_breakdown": [{"letter": letter, "value": value} for letter, value in breakdown],
    }


def summarize_moment(moment: datetime) -> dict[str, object]:
    """Shared birth/query datetime summary payload."""
    return {
        "iso": moment.isoformat(),
        "weekday_index": moment.weekday(),
        "weekday_name_en": moment.strftime("%A"),
        "hour": moment.hour,
        "minute": moment.minute,
        "day": moment.day,
        "month": moment.month,
        "year": moment.year,
    }


__all__ = [
    "DirectionInfo",
    "compute_name_abjad_profile",
    "direction_by_index",
    "get_eight_directions",
    "summarize_moment",
]
