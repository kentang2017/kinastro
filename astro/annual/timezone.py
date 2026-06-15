"""Julian day ↔ local civil datetime helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

import swisseph as swe


def jd_to_utc_datetime(jd: float) -> datetime:
    year, month, day, hour = swe.revjul(jd)
    whole_hours = int(hour)
    minutes = int((hour - whole_hours) * 60)
    seconds = int(((hour - whole_hours) * 60 - minutes) * 60)
    micro = int((((hour - whole_hours) * 60 - minutes) * 60 - seconds) * 1_000_000)
    return datetime(year, month, int(day), whole_hours, minutes, seconds, micro)


def jd_to_local_datetime(jd: float, timezone_offset: float) -> datetime:
    """Convert UT Julian day to local civil datetime using a fixed hour offset."""
    utc_dt = jd_to_utc_datetime(jd)
    return utc_dt + timedelta(hours=float(timezone_offset))


def local_datetime_to_components(local_dt: datetime) -> dict[str, int]:
    return {
        "year": local_dt.year,
        "month": local_dt.month,
        "day": local_dt.day,
        "hour": local_dt.hour,
        "minute": local_dt.minute,
    }