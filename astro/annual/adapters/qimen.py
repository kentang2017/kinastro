"""Qimen Lu Ming adapter for solar-return annual charts."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def compute_qimen_at_sr(
    sr_local: datetime,
    *,
    method: int = 1,
) -> dict[str, Any]:
    from astro.sanshi.qimen_luming import compute_qimen_luming

    return compute_qimen_luming(
        year=sr_local.year,
        month=sr_local.month,
        day=sr_local.day,
        hour=sr_local.hour,
        minute=sr_local.minute,
        method=method,
    )