"""Liu Ren adapter for solar-return annual charts."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from astro.sanshi.liuren import compute_liuren_chart, compute_lunming


def compute_liuren_at_sr(
    sr_local: datetime,
    timezone: float,
    benming_zhi: str,
    liunian_zhi: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    chart = compute_liuren_chart(
        year=sr_local.year,
        month=sr_local.month,
        day=sr_local.day,
        hour=sr_local.hour,
        minute=sr_local.minute,
        timezone=timezone,
    )
    lunming = compute_lunming(chart, benming_zhi, liunian_zhi=liunian_zhi)
    return chart, lunming