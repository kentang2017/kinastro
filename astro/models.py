"""Unified chart data models and adapters for KinAstro.

Phase 1 introduces a common Pydantic v2 model layer so systems can share a
trustworthy interface while existing renderers continue to use legacy objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

try:  # Python 3.11+
    from typing import Self
except ImportError:  # pragma: no cover - older runtimes
    from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class KinAstroModel(BaseModel):
    """Base model with strict validation defaults for KinAstro."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class BirthData(KinAstroModel):
    """Validated birth data shared across astrology systems."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str = ""
    gender: Literal["male", "female", "男", "女"] | None = None

    @field_validator("timezone")
    @classmethod
    def _validate_timezone(cls, value: float) -> float:
        if not -14.0 <= float(value) <= 14.0:
            raise ValueError("timezone must be between -14 and +14 hours")
        return float(value)

    @field_validator("latitude")
    @classmethod
    def _validate_latitude(cls, value: float) -> float:
        if not -90.0 <= float(value) <= 90.0:
            raise ValueError("latitude must be between -90 and +90 degrees")
        return float(value)

    @field_validator("longitude")
    @classmethod
    def _validate_longitude(cls, value: float) -> float:
        if not -180.0 <= float(value) <= 180.0:
            raise ValueError("longitude must be between -180 and +180 degrees")
        return float(value)

    @field_validator("gender")
    @classmethod
    def _normalize_gender(
        cls,
        value: Literal["male", "female", "男", "女"] | None,
    ) -> Literal["male", "female", "男", "女"] | None:
        if value is None:
            return None
        lowered = value.lower() if isinstance(value, str) else value
        if lowered in {"m", "male"}:
            return "male"
        if lowered in {"f", "female"}:
            return "female"
        return value

    @model_validator(mode="after")
    def _validate_calendar_date(self) -> Self:
        datetime(self.year, self.month, self.day, self.hour, self.minute)
        return self

    @property
    def legacy_gender(self) -> str | None:
        """Return the current gender in legacy Chinese labels when needed."""
        if self.gender == "male":
            return "男"
        if self.gender == "female":
            return "女"
        return self.gender

    def to_compute_kwargs(self, *, include_gender: bool = False) -> dict[str, Any]:
        """Convert BirthData into keyword args accepted by legacy compute funcs."""
        payload = {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
        }
        if include_gender and self.legacy_gender is not None:
            payload["gender"] = self.legacy_gender
        return payload


class PlanetPosition(KinAstroModel):
    """Common planet position model."""

    name: str
    longitude: float
    latitude: float | None = None
    sign: str | None = None
    sign_glyph: str | None = None
    sign_name_zh: str | None = None
    sign_degree: float | None = None
    house: int | None = None
    element: str | None = None
    retrograde: bool = False
    dignity: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HouseCusp(KinAstroModel):
    """One house or palace boundary in a chart system."""

    number: int
    cusp_longitude: float
    sign: str | None = None
    sign_glyph: str | None = None
    sign_name_zh: str | None = None
    occupants: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HouseSystem(KinAstroModel):
    """House system definition and resolved cusps."""

    name: str
    cusps: list[HouseCusp] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Aspect(KinAstroModel):
    """Generic aspect relationship between two bodies."""

    left: str
    right: str
    kind: str
    angle: float
    orb: float
    symbol: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FixedStar(KinAstroModel):
    """Generic fixed-star contact."""

    name: str
    name_zh: str | None = None
    longitude: float
    planet_name: str | None = None
    orb: float | None = None
    meaning: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArabicPart(KinAstroModel):
    """Arabic part or lot model."""

    english_name: str
    chinese_name: str | None = None
    longitude: float
    sign: str | None = None
    sign_glyph: str | None = None
    sign_name_zh: str | None = None
    sign_degree: float | None = None
    house: int | None = None


class LunarDate(KinAstroModel):
    """Shared lunar date information."""

    year: int
    month: int
    day: int
    is_leap_month: bool = False
    year_stem_index: int | None = None
    year_branch_index: int | None = None


class ZiweiPalace(KinAstroModel):
    """Unified Ziwei palace model."""

    index: int
    name: str
    branch: int
    branch_name: str
    stem: int
    stem_name: str
    stars: list[str] = Field(default_factory=list)
    auxiliary_stars: list[str] = Field(default_factory=list)
    brightness: dict[str, str] = Field(default_factory=dict)
    sihua: dict[str, str] = Field(default_factory=dict)
    da_xian: str = ""
    da_xian_start: int = 0
    liu_nian_ages: list[int] = Field(default_factory=list)
    xiao_xian_ages: list[int] = Field(default_factory=list)


class BaseChartResult(KinAstroModel):
    """Common chart result envelope used by unified compute interfaces."""

    system: str
    birth_data: BirthData
    julian_day: float | None = None
    planets: list[PlanetPosition] = Field(default_factory=list)
    house_system: HouseSystem | None = None
    aspects: list[Aspect] = Field(default_factory=list)
    fixed_stars: list[FixedStar] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    system_specific: dict[str, Any] = Field(default_factory=dict)


class WesternChartResult(BaseChartResult):
    """Unified result model for Western astrology charts."""

    system: Literal["western"] = "western"
    ascendant: float
    midheaven: float
    asc_sign: str
    mc_sign: str
    is_day_chart: bool = False
    chart_ruler: str = "—"
    chart_ruler_dignity: str = "—"
    lot_of_fortune: float = 0.0
    arabic_parts: list[ArabicPart] = Field(default_factory=list)
    sidereal_mode: bool = False
    ayanamsa: float = 0.0


class ZiweiChartResult(BaseChartResult):
    """Unified result model for Ziwei / Tử Vi style charts."""

    system: Literal["ziwei"] = "ziwei"
    gender: str | None = None
    lunar_date: LunarDate
    hour_branch: int
    ming_gong_branch: int
    shen_gong_branch: int
    wu_xing_ju: int
    ziwei_branch: int
    yin_yang: str
    ming_zhu: str
    shen_zhu: str
    sihua: dict[str, str] = Field(default_factory=dict)
    palaces: list[ZiweiPalace] = Field(default_factory=list)
    sanhe_groups: list[list[int]] = Field(default_factory=list)
    vietnam_mode: bool = False


def western_chart_to_result(chart: Any) -> WesternChartResult:
    """Convert a legacy WesternChart dataclass into a unified model."""
    birth_data = BirthData(
        year=chart.year,
        month=chart.month,
        day=chart.day,
        hour=chart.hour,
        minute=chart.minute,
        timezone=chart.timezone,
        latitude=chart.latitude,
        longitude=chart.longitude,
        location_name=chart.location_name,
    )
    planets = [
        PlanetPosition(
            name=planet.name,
            longitude=planet.longitude,
            latitude=getattr(planet, "latitude", None),
            sign=getattr(planet, "sign", None),
            sign_glyph=getattr(planet, "sign_glyph", None),
            sign_name_zh=getattr(planet, "sign_chinese", None),
            sign_degree=getattr(planet, "sign_degree", None),
            house=getattr(planet, "house", None),
            element=getattr(planet, "element", None),
            retrograde=bool(getattr(planet, "retrograde", False)),
            dignity=getattr(planet, "essential_dignity", None),
            metadata={
                "joy_status": getattr(planet, "joy_status", "—"),
                "fixed_star_conjunctions": list(
                    getattr(planet, "fixed_star_conjunctions", [])
                ),
            },
        )
        for planet in getattr(chart, "planets", [])
    ]
    house_cusps = [
        HouseCusp(
            number=house.number,
            cusp_longitude=house.cusp,
            sign=getattr(house, "sign", None),
            sign_glyph=getattr(house, "sign_glyph", None),
            occupants=list(getattr(house, "planets", [])),
        )
        for house in getattr(chart, "houses", [])
    ]
    fixed_stars = [
        FixedStar(
            name=star.star_name,
            name_zh=getattr(star, "star_name_cn", None),
            longitude=star.star_longitude,
            planet_name=getattr(star, "planet_name", None),
            orb=getattr(star, "orb", None),
            meaning=getattr(star, "meaning", None),
        )
        for star in getattr(chart, "fixed_star_conjunctions", [])
    ]
    arabic_parts = [
        ArabicPart(
            english_name=part.english_name,
            chinese_name=getattr(part, "chinese_name", None),
            longitude=part.longitude,
            sign=getattr(part, "sign", None),
            sign_glyph=getattr(part, "sign_glyph", None),
            sign_name_zh=getattr(part, "sign_chinese", None),
            sign_degree=getattr(part, "sign_degree", None),
            house=getattr(part, "house", None),
        )
        for part in getattr(chart, "arabic_parts", [])
    ]
    return WesternChartResult(
        birth_data=birth_data,
        julian_day=getattr(chart, "julian_day", None),
        planets=planets,
        house_system=HouseSystem(
            name="Placidus",
            cusps=house_cusps,
            metadata={"sidereal_mode": bool(getattr(chart, "sidereal_mode", False))},
        ),
        fixed_stars=fixed_stars,
        metadata={"legacy_model": type(chart).__name__},
        system_specific={
            "houses": [house.model_dump() for house in house_cusps],
        },
        ascendant=chart.ascendant,
        midheaven=chart.midheaven,
        asc_sign=chart.asc_sign,
        mc_sign=chart.mc_sign,
        is_day_chart=bool(getattr(chart, "is_day_chart", False)),
        chart_ruler=getattr(chart, "chart_ruler", "—"),
        chart_ruler_dignity=getattr(chart, "chart_ruler_dignity", "—"),
        lot_of_fortune=getattr(chart, "lot_of_fortune", 0.0),
        arabic_parts=arabic_parts,
        sidereal_mode=bool(getattr(chart, "sidereal_mode", False)),
        ayanamsa=float(getattr(chart, "ayanamsa", 0.0)),
    )


def ziwei_chart_to_result(chart: Any) -> ZiweiChartResult:
    """Convert a legacy ZiweiChart dataclass into a unified model."""
    birth_data = BirthData(
        year=chart.year,
        month=chart.month,
        day=chart.day,
        hour=chart.hour,
        minute=chart.minute,
        timezone=chart.timezone,
        latitude=chart.latitude,
        longitude=chart.longitude,
        location_name=chart.location_name,
        gender=getattr(chart, "gender", None),
    )
    palaces = [
        ZiweiPalace(
            index=palace.index,
            name=palace.name,
            branch=palace.branch,
            branch_name=palace.branch_name,
            stem=palace.stem,
            stem_name=palace.stem_name,
            stars=list(getattr(palace, "stars", [])),
            auxiliary_stars=list(getattr(palace, "aux_stars", [])),
            brightness=dict(getattr(palace, "brightness", {})),
            sihua=dict(getattr(palace, "sihua", {})),
            da_xian=getattr(palace, "da_xian", ""),
            da_xian_start=getattr(palace, "da_xian_start", 0),
            liu_nian_ages=list(getattr(palace, "liu_nian_ages", [])),
            xiao_xian_ages=list(getattr(palace, "xiao_xian_ages", [])),
        )
        for palace in getattr(chart, "palaces", [])
    ]
    return ZiweiChartResult(
        birth_data=birth_data,
        julian_day=getattr(chart, "julian_day", None),
        metadata={"legacy_model": type(chart).__name__},
        system_specific={
            "lunar_year_stem": getattr(chart, "lunar_year_stem", None),
            "lunar_year_branch": getattr(chart, "lunar_year_branch", None),
        },
        gender=getattr(chart, "gender", None),
        lunar_date=LunarDate(
            year=chart.lunar_year,
            month=chart.lunar_month,
            day=chart.lunar_day,
            is_leap_month=bool(getattr(chart, "is_leap_month", False)),
            year_stem_index=getattr(chart, "lunar_year_stem", None),
            year_branch_index=getattr(chart, "lunar_year_branch", None),
        ),
        hour_branch=chart.hour_branch,
        ming_gong_branch=chart.ming_gong_branch,
        shen_gong_branch=chart.shen_gong_branch,
        wu_xing_ju=chart.wu_xing_ju,
        ziwei_branch=chart.ziwei_branch,
        yin_yang=chart.yin_yang,
        ming_zhu=chart.ming_zhu,
        shen_zhu=chart.shen_zhu,
        sihua=dict(getattr(chart, "sihua", {})),
        palaces=palaces,
        sanhe_groups=[list(group) for group in getattr(chart, "sanhe_groups", [])],
        vietnam_mode=bool(getattr(chart, "vietnam_mode", False)),
    )


def chart_result_from_legacy(system: str, chart: Any) -> BaseChartResult:
    """Convert a known legacy chart object into a unified result model."""
    normalized = system.strip().lower()
    if normalized in {"ziwei", "tab_ziwei"}:
        return ziwei_chart_to_result(chart)
    if normalized in {"western", "tab_western"}:
        return western_chart_to_result(chart)
    raise ValueError(f"Unsupported unified chart adapter for system: {system}")


__all__ = [
    "ArabicPart",
    "Aspect",
    "BaseChartResult",
    "BirthData",
    "FixedStar",
    "HouseCusp",
    "HouseSystem",
    "PlanetPosition",
    "WesternChartResult",
    "ZiweiChartResult",
    "ZiweiPalace",
    "LunarDate",
    "chart_result_from_legacy",
    "western_chart_to_result",
    "ziwei_chart_to_result",
]
