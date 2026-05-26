"""Vedic system compute adapter."""

from __future__ import annotations

from typing import Any


def compute(params: dict[str, Any], options: dict[str, Any]) -> Any:
    from astro.vedic.indian import compute_vedic_chart

    return compute_vedic_chart(
        year=int(params["year"]),
        month=int(params["month"]),
        day=int(params["day"]),
        hour=int(params["hour"]),
        minute=int(params["minute"]),
        timezone=float(params["timezone"]),
        latitude=float(params["latitude"]),
        longitude=float(params["longitude"]),
    )
