"""Taiyi adapter for solar-return annual charts."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def compute_taiyi_at_sr(
    sr_local: datetime,
    timezone: float,
    gender: str,
) -> dict[str, Any]:
    from astro.sanshi.taiyi import compute_taiyi_chart

    taiyi_gender = "male" if gender in ("male", "男", "M") else "female"
    return compute_taiyi_chart(
        year=sr_local.year,
        month=sr_local.month,
        day=sr_local.day,
        hour=sr_local.hour,
        minute=sr_local.minute,
        gender=taiyi_gender,
        timezone=timezone,
    )