"""Pydantic models for the solar-return annual flow timeline."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import Field, field_validator

from astro.models import BirthData, KinAstroModel, WesternChartResult


class FortuneLevel(str, Enum):
    EXCELLENT = "大吉"
    GOOD = "吉"
    NEUTRAL = "平"
    CAUTION = "凶"
    CRITICAL = "大凶"


class ReturnLocation(KinAstroModel):
    latitude: float
    longitude: float
    timezone: float
    location_name: str = ""

    @classmethod
    def from_birth(cls, birth: BirthData) -> ReturnLocation:
        return cls(
            latitude=birth.latitude,
            longitude=birth.longitude,
            timezone=birth.timezone,
            location_name=birth.location_name,
        )


class SanChuanReading(KinAstroModel):
    name: Literal["初傳", "中傳", "末傳"]
    zhi: str = ""
    jiang: str = ""
    jiang_fullname: str = ""
    liuqin: str = ""
    is_kong: bool = False
    jixiong: Literal["吉", "凶", "中"] = "中"
    note: str = ""


class PalaceAffair(KinAstroModel):
    palace: str
    branch: str = ""
    tian_jiang: str = ""
    liuqin: str = ""
    score: float = Field(50.0, ge=0, le=100)
    summary: str = ""
    keywords: list[str] = Field(default_factory=list)


class LiurenJixiong(KinAstroModel):
    score: float = Field(50.0, ge=0, le=100)
    level: FortuneLevel = FortuneLevel.NEUTRAL
    san_chuan: list[SanChuanReading] = Field(default_factory=list)
    san_chuan_summary: str = ""
    yong_shen: str = ""
    yong_shen_palace: str = ""
    yong_shen_strength: Literal["旺", "相", "休", "囚", "死", ""] = ""
    yong_shen_jiang: str = ""
    yong_shen_jixiong: Literal["吉", "凶", "中"] = "中"
    geju: list[str] = Field(default_factory=list)
    geju_level: Literal["上格", "中格", "下格", "無格"] = "無格"
    liunian_zhi: str = ""
    liunian_jiang: str = ""
    taisui_impact: str = ""
    yue_jiang: str = ""
    yue_jiang_impact: str = ""
    palace_affairs: list[PalaceAffair] = Field(default_factory=list)
    key_palaces: dict[str, str] = Field(default_factory=dict)
    affair_summary: str = ""
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    lunming_excerpt: dict[str, Any] = Field(default_factory=dict)


class WesternSRSummary(KinAstroModel):
    score: float = Field(50.0, ge=0, le=100)
    level: FortuneLevel = FortuneLevel.NEUTRAL
    asc_sign: str = ""
    asc_degree: float | None = None
    sr_sun_house: int | None = None
    sr_moon_house: int | None = None
    angular_planets: list[str] = Field(default_factory=list)
    natal_aspects: list[str] = Field(default_factory=list)
    summary: str = ""


class ChineseSystemSnapshot(KinAstroModel):
    system: Literal["ziwei", "bazi", "qizheng", "qimen", "taiyi"]
    score: float = Field(50.0, ge=0, le=100)
    level: FortuneLevel = FortuneLevel.NEUTRAL
    summary: str = ""
    highlights: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class AnnualFlowYear(KinAstroModel):
    year: int
    age: int
    age_kind: Literal["virtual", "western"] = "virtual"

    exact_sr_datetime_utc: datetime
    exact_sr_datetime_local: datetime
    sr_jd: float
    return_location: ReturnLocation

    sr_day_gz: str = ""
    sr_hour_gz: str = ""
    liunian_zhi: str = ""
    liunian_gz: str = ""
    benming_zhi: str = ""

    western_sr: WesternSRSummary | None = None
    western_sr_chart: WesternChartResult | None = None
    liuren_chart: dict[str, Any] = Field(default_factory=dict)
    liuren_jixiong: LiurenJixiong | None = None
    liuren_lunming: dict[str, Any] = Field(default_factory=dict)
    other_chinese_systems: dict[str, ChineseSystemSnapshot] = Field(default_factory=dict)

    system_scores: dict[str, float] = Field(default_factory=dict)
    integrated_interpretation: str = ""
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SolarReturnTimelineRequest(KinAstroModel):
    birth_data: BirthData
    start_year: int
    end_year: int
    return_location: ReturnLocation | None = None
    include_systems: list[str] = Field(
        default_factory=lambda: ["western", "liuren", "ziwei", "bazi", "qizheng"]
    )
    benming_zhi: str | None = None
    age_kind: Literal["virtual", "western"] = "virtual"
    include_full_western_chart: bool = False

    @field_validator("end_year")
    @classmethod
    def _validate_range(cls, value: int, info) -> int:
        start = info.data.get("start_year")
        if start is not None and value < start:
            raise ValueError("end_year must be >= start_year")
        if start is not None and value - start > 60:
            raise ValueError("year range cannot exceed 60 years")
        return value


class SolarReturnTimeline(KinAstroModel):
    request: SolarReturnTimelineRequest
    natal_birth_data: BirthData
    natal_sun_longitude: float
    benming_zhi: str
    years: list[AnnualFlowYear] = Field(default_factory=list)
    system_average_scores: dict[str, float] = Field(default_factory=dict)
    best_years_by_system: dict[str, int] = Field(default_factory=dict)
    caution_years_by_system: dict[str, list[int]] = Field(default_factory=dict)
    trend_summary: str = ""
    computed_at: datetime
    engine_version: str = "1.0.0"
    warnings: list[str] = Field(default_factory=list)


__all__ = [
    "AnnualFlowYear",
    "ChineseSystemSnapshot",
    "FortuneLevel",
    "LiurenJixiong",
    "PalaceAffair",
    "ReturnLocation",
    "SanChuanReading",
    "SolarReturnTimeline",
    "SolarReturnTimelineRequest",
    "WesternSRSummary",
]