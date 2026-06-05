"""Lunar conversion helpers for Vietnam Tử Vi input modes."""

from __future__ import annotations

from datetime import date, timedelta

import swisseph as swe

from astro.ziwei import _solar_to_lunar
from astro.vietnam.models import TuViInput


def vietnam_lunar_to_solar_date(
    lunar_year: int,
    lunar_month: int,
    lunar_day: int,
    *,
    is_leap_month: bool = False,
    timezone: float = 7.0,
) -> date:
    """Find a matching Gregorian date by scanning dates and matching lunar fields."""
    scan_start = date(max(1, lunar_year - 1), 1, 1)
    scan_end = date(lunar_year + 1, 12, 31)
    cur = scan_start
    while cur <= scan_end:
        jd = swe.julday(cur.year, cur.month, cur.day, 12.0 - timezone)
        ly, lm, ld, leap = _solar_to_lunar(jd)
        if (ly, lm, ld, leap) == (lunar_year, lunar_month, lunar_day, is_leap_month):
            return cur
        cur += timedelta(days=1)
    raise ValueError(
        f"Cannot map lunar date to solar date: {lunar_year}-{lunar_month}-{lunar_day} leap={is_leap_month}"
    )


def resolve_birth_date(payload: TuViInput) -> tuple[int, int, int, dict[str, object]]:
    """Resolve effective solar date from input mode and return metadata."""
    if payload.use_lunar_input:
        if payload.lunar_year is None or payload.lunar_month is None or payload.lunar_day is None:
            raise ValueError("lunar_year/lunar_month/lunar_day are required when use_lunar_input=True")
        solar = vietnam_lunar_to_solar_date(
            payload.lunar_year,
            payload.lunar_month,
            payload.lunar_day,
            is_leap_month=payload.lunar_is_leap,
            timezone=payload.timezone,
        )
        return (
            solar.year,
            solar.month,
            solar.day,
            {
                "input_mode": "lunar",
                "calendar_mode": payload.calendar_mode,
                "lunar_input": {
                    "year": payload.lunar_year,
                    "month": payload.lunar_month,
                    "day": payload.lunar_day,
                    "is_leap": payload.lunar_is_leap,
                },
            },
        )

    return (
        payload.year,
        payload.month,
        payload.day,
        {
            "input_mode": "solar",
            "calendar_mode": payload.calendar_mode,
        },
    )
