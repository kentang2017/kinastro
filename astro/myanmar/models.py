"""Data models for the Myanmar Bedin / Mahabote module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


LanguageCode = Literal["zh", "en"]


@dataclass(frozen=True)
class ZodiacAnimal:
    """Metadata for one of the 8 Mahabote zodiac sectors."""

    key: str
    animal_en: str
    animal_zh: str
    animal_emoji: str
    planet_en: str
    planet_zh: str
    planet_symbol: str
    direction_en: str
    direction_zh: str
    element_en: str
    element_zh: str
    color_hex: str
    traits_en: tuple[str, ...]
    traits_zh: tuple[str, ...]
    auspicious_activities_en: tuple[str, ...]
    auspicious_activities_zh: tuple[str, ...]
    caution_activities_en: tuple[str, ...]
    caution_activities_zh: tuple[str, ...]
    remedies_en: tuple[str, ...]
    remedies_zh: tuple[str, ...]
    favorable_directions_en: tuple[str, ...]
    favorable_directions_zh: tuple[str, ...]
    caution_directions_en: tuple[str, ...]
    caution_directions_zh: tuple[str, ...]


@dataclass(frozen=True)
class MahaboteHouseDefinition:
    """Static definition of one Mahabote house."""

    key: str
    name_en: str
    name_zh: str
    name_myanmar: str
    meaning_en: str
    meaning_zh: str
    polarity: Literal["positive", "liability"]


@dataclass(frozen=True)
class MahaboteHousePlacement:
    """Resolved chart placement for a single house."""

    house_index: int
    house_key: str
    house_name_en: str
    house_name_zh: str
    house_name_myanmar: str
    house_meaning_en: str
    house_meaning_zh: str
    polarity: Literal["positive", "liability"]
    zodiac: ZodiacAnimal
    is_start_house: bool


@dataclass(frozen=True)
class YearOverlay:
    """Simple annual/flow-year overlay."""

    gregorian_year: int
    myanmar_year: int
    cycle_index: int
    animal_key: str
    animal_en: str
    animal_zh: str
    direction_en: str
    direction_zh: str
    summary_en: str
    summary_zh: str


@dataclass
class MyanmarMahaboteChart:
    """Main chart payload used by API and UI."""

    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    timezone: float = 6.5
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""

    myanmar_year: int = 0
    year_mod7: int = 0
    start_house_index: int = 0
    start_house_key: str = ""
    start_house_name_en: str = ""
    start_house_name_zh: str = ""
    start_lord_key: str = ""
    start_lord_planet_en: str = ""
    start_lord_planet_zh: str = ""

    houses: list[MahaboteHousePlacement] = field(default_factory=list)
    positive_houses: list[str] = field(default_factory=list)
    liability_houses: list[str] = field(default_factory=list)

    natal_animal_key: str = ""
    natal_animal_en: str = ""
    natal_animal_zh: str = ""
    natal_direction_en: str = ""
    natal_direction_zh: str = ""
    natal_traits_en: tuple[str, ...] = field(default_factory=tuple)
    natal_traits_zh: tuple[str, ...] = field(default_factory=tuple)
    natal_remedies_en: tuple[str, ...] = field(default_factory=tuple)
    natal_remedies_zh: tuple[str, ...] = field(default_factory=tuple)

    direction_advice_en: tuple[str, ...] = field(default_factory=tuple)
    direction_advice_zh: tuple[str, ...] = field(default_factory=tuple)

    current_year_overlay: YearOverlay | None = None
    target_year_overlay: YearOverlay | None = None

    zodiac_wheel_svg: str = ""
    house_board_svg: str = ""
