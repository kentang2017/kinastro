"""Ziwei system compute adapter."""

from __future__ import annotations

from typing import Any


def compute(params: dict[str, Any], options: dict[str, Any]) -> Any:
    from astro.ziwei import compute_ziwei_chart

    return compute_ziwei_chart(
        year=int(params["year"]),
        month=int(params["month"]),
        day=int(params["day"]),
        hour=int(params["hour"]),
        minute=int(params["minute"]),
        timezone=float(params["timezone"]),
        latitude=float(params["latitude"]),
        longitude=float(params["longitude"]),
        location_name=str(params.get("location_name", "")),
        gender=str(params.get("gender", "male")),
        vietnam_mode=bool(options.get("vietnam_mode", False)),
    )
