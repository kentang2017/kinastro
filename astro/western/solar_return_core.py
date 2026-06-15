"""Core solar / lunar return calculations without Streamlit dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import swisseph as swe

SUN_DAILY_MOTION = 0.9856
MOON_DAILY_MOTION = 13.2


def _angle_diff_signed(target: float, current: float) -> float:
    diff = (target - current) % 360
    return diff - 360 if diff > 180 else diff


def jd_to_datetime_str(jd: float) -> str:
    """Format Julian day as ``YYYY-MM-DD HH:MM:SS`` in UT."""
    year, month, day, hour = swe.revjul(jd)
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    return f"{year:04d}-{month:02d}-{int(day):02d} {hours:02d}:{minutes:02d}:{seconds:02d}"


def find_solar_return_jd(natal_sun_lon: float, target_year: int) -> float:
    """Return Julian day when the Sun reaches *natal_sun_lon* in *target_year*."""
    jd_start = swe.julday(target_year, 3, 21, 12.0)
    jd = jd_start
    for _ in range(50):
        xx, _ = swe.calc_ut(jd, swe.SUN)
        diff = _angle_diff_signed(natal_sun_lon, xx[0])
        if abs(diff) < 0.00001:
            break
        jd += diff / SUN_DAILY_MOTION
    return jd


def find_lunar_return_jd(natal_moon_lon: float, after_jd: float) -> float:
    """Return Julian day of the next lunar return after *after_jd*."""
    jd = after_jd
    for _ in range(50):
        xx, _ = swe.calc_ut(jd, swe.MOON)
        diff = _angle_diff_signed(natal_moon_lon, xx[0])
        if abs(diff) < 0.00001:
            break
        jd += diff / MOON_DAILY_MOTION
    return jd


@dataclass
class SolarReturnCoreResult:
    natal_sun_longitude: float
    return_year: int
    return_jd: float
    return_date_ut: str
    return_chart: Any

    @property
    def return_date(self) -> str:
        """Backward-compatible alias used by legacy callers."""
        return self.return_date_ut


@dataclass
class LunarReturnCoreResult:
    natal_moon_longitude: float
    return_jd: float
    return_date_ut: str
    return_chart: Any

    @property
    def return_date(self) -> str:
        return self.return_date_ut


def compute_solar_return_core(
    natal_sun_lon: float,
    target_year: int,
    latitude: float,
    longitude: float,
    timezone: float = 0.0,
    location_name: str = "",
) -> SolarReturnCoreResult:
    """Find the solar-return moment and cast a western chart at the return location."""
    from astro.western.western import compute_western_chart

    jd = find_solar_return_jd(natal_sun_lon, target_year)
    year, month, day, hour = swe.revjul(jd)
    chart = compute_western_chart(
        year=year,
        month=month,
        day=int(day),
        hour=int(hour),
        minute=int((hour - int(hour)) * 60),
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )
    return SolarReturnCoreResult(
        natal_sun_longitude=natal_sun_lon,
        return_year=target_year,
        return_jd=jd,
        return_date_ut=jd_to_datetime_str(jd),
        return_chart=chart,
    )


def compute_lunar_return_core(
    natal_moon_lon: float,
    after_jd: float,
    latitude: float,
    longitude: float,
    timezone: float = 0.0,
    location_name: str = "",
) -> LunarReturnCoreResult:
    """Find the next lunar-return moment and cast a western chart."""
    from astro.western.western import compute_western_chart

    jd = find_lunar_return_jd(natal_moon_lon, after_jd)
    year, month, day, hour = swe.revjul(jd)
    chart = compute_western_chart(
        year=year,
        month=month,
        day=int(day),
        hour=int(hour),
        minute=int((hour - int(hour)) * 60),
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )
    return LunarReturnCoreResult(
        natal_moon_longitude=natal_moon_lon,
        return_jd=jd,
        return_date_ut=jd_to_datetime_str(jd),
        return_chart=chart,
    )