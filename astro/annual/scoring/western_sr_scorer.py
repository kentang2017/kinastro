"""Western solar-return auxiliary scoring."""

from __future__ import annotations

from typing import Any

from astro.annual.models import WesternSRSummary
from astro.annual.scoring.levels import clamp_score, score_to_level


def _planet_house(chart: Any, names: set[str]) -> int | None:
    for planet in getattr(chart, "planets", []):
        if getattr(planet, "name", "") in names:
            return getattr(planet, "house", None)
    return None


def score_western_sr(sr_chart: Any, natal_chart: Any | None = None) -> WesternSRSummary:
    base = 50.0
    asc_sign = getattr(sr_chart, "asc_sign", "")
    asc_degree = float(getattr(sr_chart, "ascendant", 0.0) % 30)
    sun_house = _planet_house(sr_chart, {"Sun", "太陽"})
    moon_house = _planet_house(sr_chart, {"Moon", "月亮"})

    angular: list[str] = []
    for planet in getattr(sr_chart, "planets", []):
        house = getattr(planet, "house", None)
        if house in {1, 4, 7, 10}:
            angular.append(getattr(planet, "name", ""))
            base += 3

    natal_aspects: list[str] = []
    if natal_chart is not None:
        sr_map = {getattr(p, "name", ""): getattr(p, "longitude", 0.0) for p in sr_chart.planets}
        natal_map = {getattr(p, "name", ""): getattr(p, "longitude", 0.0) for p in natal_chart.planets}
        for name, sr_lon in sr_map.items():
            natal_lon = natal_map.get(name)
            if natal_lon is None:
                continue
            diff = abs(sr_lon - natal_lon) % 360
            if diff > 180:
                diff = 360 - diff
            if diff <= 8:
                natal_aspects.append(f"SR {name} 合本命 {name}")
                base += 4
            elif abs(diff - 180) <= 8:
                natal_aspects.append(f"SR {name} 衝本命 {name}")
                base -= 4

    if sun_house in {1, 10}:
        base += 6
    if moon_house in {4, 10}:
        base += 4
    if sun_house in {6, 8, 12}:
        base -= 4

    score = clamp_score(base)
    summary = (
        f"SR ASC {asc_sign}，太陽在{sun_house or '—'}宮，月亮在{moon_house or '—'}宮。"
        f"角宮行星：{', '.join(angular) or '無'}。"
    )
    return WesternSRSummary(
        score=score,
        level=score_to_level(score),
        asc_sign=asc_sign,
        asc_degree=asc_degree,
        sr_sun_house=sun_house,
        sr_moon_house=moon_house,
        angular_planets=angular,
        natal_aspects=natal_aspects[:8],
        summary=summary,
    )