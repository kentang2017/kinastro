"""Data models for Vietnam Tử Vi Đẩu Số module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

CalendarMode = Literal["solar_gregorian", "chinese_lunar_baseline", "vietnam_lunar"]
InterpretMode = Literal["traditional_cn", "trung_chau_tam_hop"]
LanguageCode = Literal["zh", "vi", "en"]


@dataclass(frozen=True)
class TuViInput:
    """Input payload for Vietnam Tử Vi computation."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str = ""
    gender: str = "男"
    calendar_mode: CalendarMode = "solar_gregorian"
    interpret_mode: InterpretMode = "trung_chau_tam_hop"
    lang: LanguageCode = "zh"
    use_lunar_input: bool = False
    lunar_year: int | None = None
    lunar_month: int | None = None
    lunar_day: int | None = None
    lunar_is_leap: bool = False


@dataclass(frozen=True)
class StarProfileVN:
    """Localized profile of a star in Vietnam Tử Vi."""

    name_zh: str
    name_vi: str
    name_en: str
    temperament: str
    strength: str
    remedies: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class InterpretationBlock:
    """Structured interpretation block for UI/API output."""

    personality: str
    physiology: str
    self_effort: str
    dai_han: str
    luu_nien: str
    key_points: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComparisonItem:
    """Comparison row between Chinese Ziwei and Vietnam Tử Vi perspectives."""

    topic: str
    chinese_view: str
    vietnam_view: str
    summary_diff: str


@dataclass
class TuViChart:
    """Aggregated Vietnam Tử Vi chart output."""

    system: str
    input_data: TuViInput
    solar_date_used: str
    lunar_profile: dict[str, object]
    base_chart: object
    interpretation_mode: InterpretMode
    language: LanguageCode
    star_profiles: dict[str, StarProfileVN]
    interpretation: InterpretationBlock
    remedies: list[str] = field(default_factory=list)
    comparison: list[ComparisonItem] = field(default_factory=list)
    visual: dict[str, str] = field(default_factory=dict)
