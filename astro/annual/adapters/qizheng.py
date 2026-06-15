"""Qizheng adapter: natal chart + dasha at solar-return year."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from astro.models import BirthData
from astro.qizheng.calculator import compute_chart
from astro.qizheng.qizheng_dasha import DashaResult, compute_dasha, EARTHLY_BRANCHES


@dataclass
class QizhengAnnualContext:
    natal_chart: Any
    dasha: DashaResult
    current_period_lord: str
    current_period_palace: str
    flow_year_branch: str
    flow_year_palace: str
    current_age: int
    resonance_hits: list[dict[str, Any]] = field(default_factory=list)
    resonance_score: float = 0.0


def _qizheng_gender(birth: BirthData) -> str:
    legacy = birth.legacy_gender or "男"
    return "male" if legacy == "男" else "female"


def compute_qizheng_natal(birth: BirthData) -> Any:
    return compute_chart(
        year=birth.year,
        month=birth.month,
        day=birth.day,
        hour=birth.hour,
        minute=birth.minute,
        timezone=birth.timezone,
        latitude=birth.latitude,
        longitude=birth.longitude,
        location_name=birth.location_name,
        gender=_qizheng_gender(birth),
    )


def _planet_longitude_map(chart: Any) -> dict[str, float]:
    return {planet.name: float(planet.longitude) for planet in getattr(chart, "planets", [])}


def _evaluate_sr_resonance(
    natal_chart: Any,
    sr_local: datetime,
    timezone: float,
) -> tuple[list[dict[str, Any]], float]:
    from astro.qizheng.financial.gann_macro_stock import (
        evaluate_qizheng_resonance,
        get_transit_longitudes,
    )

    natal_map = _planet_longitude_map(natal_chart)
    transit_map = get_transit_longitudes(sr_local, timezone=timezone)
    hits = evaluate_qizheng_resonance(natal_map, transit_map, orb=3.0)
    score = sum(hit.get("score", 0) for hit in hits[:6])
    return hits, float(score)


def compute_qizheng_annual(
    birth: BirthData,
    sr_year: int,
    natal_chart: Any | None = None,
    *,
    sr_local: datetime | None = None,
    timezone: float | None = None,
) -> QizhengAnnualContext:
    chart = natal_chart or compute_qizheng_natal(birth)
    dasha = compute_dasha(
        birth_year=birth.year,
        ming_gong_branch=chart.ming_gong_branch,
        gender=chart.gender,
        houses=chart.houses,
        current_year=sr_year,
    )
    period_lord = ""
    period_palace = ""
    if 0 <= dasha.current_period_idx < len(dasha.periods):
        period = dasha.periods[dasha.current_period_idx]
        period_lord = period.lord
        period_palace = period.palace_name

    flow_branch = ""
    if 0 <= dasha.flow_year_branch < 12:
        flow_branch = EARTHLY_BRANCHES[dasha.flow_year_branch]

    resonance_hits: list[dict[str, Any]] = []
    resonance_score = 0.0
    if sr_local is not None:
        tz = timezone if timezone is not None else birth.timezone
        resonance_hits, resonance_score = _evaluate_sr_resonance(chart, sr_local, tz)

    return QizhengAnnualContext(
        natal_chart=chart,
        dasha=dasha,
        current_period_lord=period_lord,
        current_period_palace=period_palace,
        flow_year_branch=flow_branch,
        flow_year_palace=dasha.flow_year_palace,
        current_age=dasha.current_age,
        resonance_hits=resonance_hits,
        resonance_score=resonance_score,
    )