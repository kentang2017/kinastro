"""Process-level cache for annual SR timeline (API / scripts)."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from typing import Any

from astro.annual.models import SolarReturnTimeline
from astro.models import BirthData


def _timeline_cache_key(
    birth_data: BirthData,
    start_year: int,
    end_year: int,
    include_systems: tuple[str, ...],
    age_kind: str,
) -> str:
    payload = {
        "birth": birth_data.model_dump(),
        "start_year": start_year,
        "end_year": end_year,
        "include_systems": include_systems,
        "age_kind": age_kind,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@lru_cache(maxsize=32)
def _cached_timeline_by_key(cache_key: str, payload_json: str) -> SolarReturnTimeline:
    from astro.annual.timeline import compute_solar_return_flowyear_timeline

    payload = json.loads(payload_json)
    birth = BirthData.model_validate(payload["birth"])
    return compute_solar_return_flowyear_timeline(
        birth,
        payload["start_year"],
        payload["end_year"],
        include_systems=list(payload["include_systems"]),
        age_kind=payload.get("age_kind", "virtual"),
    )


def compute_annual_timeline_cached(
    birth_data: BirthData,
    start_year: int,
    end_year: int,
    include_systems: list[str] | None = None,
    *,
    age_kind: str = "virtual",
) -> SolarReturnTimeline:
    """LRU-cached timeline for repeated API/script queries."""
    systems = tuple(sorted(include_systems or ["western", "liuren", "ziwei", "bazi", "qizheng"]))
    key = _timeline_cache_key(birth_data, start_year, end_year, systems, age_kind)
    payload_json = json.dumps(
        {
            "birth": birth_data.model_dump(),
            "start_year": start_year,
            "end_year": end_year,
            "include_systems": systems,
            "age_kind": age_kind,
        },
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    return _cached_timeline_by_key(key, payload_json)


def clear_annual_timeline_cache() -> None:
    _cached_timeline_by_key.cache_clear()