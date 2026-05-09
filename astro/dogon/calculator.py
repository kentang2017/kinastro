"""Dogon Sirius Cosmology calculation engine (pure computation)."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


@dataclass
class DogonBodyPoint:
    key: str
    label: str
    dogon_name: str
    longitude: float
    declination: float
    orbit_phase: float
    cultural_note_zh: str
    cultural_note_en: str


@dataclass
class SiguiCycleInfo:
    anchor_year: int
    cycle_years: int
    previous_year: int
    next_year: int
    years_since_previous: float
    years_until_next: float


@dataclass
class DogonZoneResult:
    zone_id: Optional[str]
    label: str
    in_zone: bool
    meaning_zh: str
    meaning_en: str


@dataclass
class DogonSiriusChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    sirius_longitude: float
    sirius_declination: float
    overlay_real_position: bool
    bodies: list[DogonBodyPoint]
    zone_result: DogonZoneResult
    sigui: SiguiCycleInfo
    personal_influence_zh: str
    personal_influence_en: str
    disclaimer_zh: str
    disclaimer_en: str
    references: list[str]
    cross_cultural: list[dict[str, str]]


@lru_cache(maxsize=1)
def load_dogon_constants() -> dict[str, Any]:
    p = Path(__file__).parent / "data" / "constants.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _normalize_360(value: float) -> float:
    return value % 360.0


def _decimal_year(year: int, month: int, day: int) -> float:
    return year + (month - 1) / 12.0 + (day - 1) / 365.0


def _compute_jd(year: int, month: int, day: int, hour: int, minute: int, timezone_offset: float) -> float:
    try:
        import swisseph as swe
    except Exception:
        ut_hour = hour + minute / 60.0 - timezone_offset
        # Meeus-like approximation fallback for environments without swisseph
        a = (14 - month) // 12
        y = year + 4800 - a
        m = month + 12 * a - 3
        jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        return jdn + (ut_hour - 12.0) / 24.0
    ut_hour = hour + minute / 60.0 - timezone_offset
    return swe.julday(year, month, day, ut_hour)


def _init_swe() -> None:
    try:
        from astro.swe_init import init_swisseph

        init_swisseph()
    except Exception:
        pass


def _compute_sirius_real_position(jd: float) -> tuple[float, float]:
    """Return (ecliptic_lon, declination)."""
    try:
        import swisseph as swe

        _init_swe()
        ecl, _ = swe.fixstar2_ut("Sirius", jd)
        eq, _ = swe.fixstar2_ut("Sirius", jd, swe.FLG_EQUATORIAL)
        return _normalize_360(float(ecl[0])), float(eq[1])
    except Exception:
        # Stable fallback: approximate Sirius around tropical Cancer with southern declination
        days = jd - 2451545.0
        drift = (days / 36525.0) * 1.4
        lon = _normalize_360(104.0 + drift)
        dec = -16.7 + 0.05 * math.sin(days / 365.25)
        return lon, dec


def _sigui_info(decimal_year: float, anchor: int, cycle: int) -> SiguiCycleInfo:
    elapsed = decimal_year - anchor
    idx = math.floor(elapsed / cycle)
    prev_year = anchor + idx * cycle
    next_year = prev_year + cycle
    return SiguiCycleInfo(
        anchor_year=anchor,
        cycle_years=cycle,
        previous_year=prev_year,
        next_year=next_year,
        years_since_previous=max(0.0, decimal_year - prev_year),
        years_until_next=max(0.0, next_year - decimal_year),
    )


def _resolve_zone(declination: float, zones: list[dict[str, Any]]) -> DogonZoneResult:
    for z in zones:
        dmin = float(z["declination_min"])
        dmax = float(z["declination_max"])
        if dmin <= declination < dmax:
            return DogonZoneResult(
                zone_id=z["id"],
                label=z["label"],
                in_zone=True,
                meaning_zh=z["meaning_zh"],
                meaning_en=z["meaning_en"],
            )
    return DogonZoneResult(
        zone_id=None,
        label="Out-of-band",
        in_zone=False,
        meaning_zh="位於定義區域之外，重點看週期與儀式節律。",
        meaning_en="Outside predefined bands; emphasize cycle timing and ritual rhythm.",
    )


def _build_bodies(
    constants: dict[str, Any],
    sirius_lon: float,
    sirius_dec: float,
    decimal_year: float,
) -> list[DogonBodyPoint]:
    bodies_cfg = constants["bodies"]
    cfg_a = bodies_cfg["sirius_a"]
    cfg_b = bodies_cfg["sirius_b"]
    cfg_c = bodies_cfg["sirius_c"]

    phase_b = ((decimal_year - 1900.0) % cfg_b["period_years"]) / cfg_b["period_years"]
    phase_c = ((decimal_year - 1900.0) % cfg_c["period_years"]) / cfg_c["period_years"]

    lon_b = _normalize_360(sirius_lon + 10.0 * math.sin(2 * math.pi * phase_b))
    dec_b = sirius_dec + 3.0 * math.cos(2 * math.pi * phase_b)
    lon_c = _normalize_360(sirius_lon + 18.0 * math.sin(2 * math.pi * phase_c + 1.2))
    dec_c = sirius_dec + 5.0 * math.cos(2 * math.pi * phase_c + 0.7)

    return [
        DogonBodyPoint(
            key="sirius_a",
            label=cfg_a["label"],
            dogon_name=cfg_a["dogon_name"],
            longitude=sirius_lon,
            declination=sirius_dec,
            orbit_phase=0.0,
            cultural_note_zh=cfg_a["cultural"]["zh"],
            cultural_note_en=cfg_a["cultural"]["en"],
        ),
        DogonBodyPoint(
            key="sirius_b",
            label=cfg_b["label"],
            dogon_name=cfg_b["dogon_name"],
            longitude=lon_b,
            declination=dec_b,
            orbit_phase=phase_b,
            cultural_note_zh=cfg_b["cultural"]["zh"],
            cultural_note_en=cfg_b["cultural"]["en"],
        ),
        DogonBodyPoint(
            key="sirius_c",
            label=cfg_c["label"],
            dogon_name=cfg_c["dogon_name"],
            longitude=lon_c,
            declination=dec_c,
            orbit_phase=phase_c,
            cultural_note_zh=cfg_c["cultural"]["zh"],
            cultural_note_en=cfg_c["cultural"]["en"],
        ),
    ]


def format_dogon_sirius_for_prompt(chart: DogonSiriusChart, lang: str = "zh") -> str:
    is_zh = lang in ("zh", "zh_cn")
    zone_meaning = chart.zone_result.meaning_zh if is_zh else chart.zone_result.meaning_en
    influence = chart.personal_influence_zh if is_zh else chart.personal_influence_en
    rows = [
        f"Dogon Sirius Cosmology @ {chart.location_name}",
        f"Date: {chart.year:04d}-{chart.month:02d}-{chart.day:02d} {chart.hour:02d}:{chart.minute:02d} (UTC{chart.timezone:+.1f})",
        f"Sirius lon/dec: {chart.sirius_longitude:.2f}° / {chart.sirius_declination:.2f}°",
        f"Zone: {chart.zone_result.label} ({zone_meaning})",
        f"Sigui previous/next: {chart.sigui.previous_year} / {chart.sigui.next_year}",
        f"Years until next Sigui: {chart.sigui.years_until_next:.2f}",
        "Bodies:",
    ]
    rows.extend(
        f"- {b.label} ({b.dogon_name}): lon {b.longitude:.2f}°, dec {b.declination:.2f}°"
        for b in chart.bodies
    )
    rows.append("Interpretation:")
    rows.append(influence)
    rows.append("Disclaimer:")
    rows.append(chart.disclaimer_zh if is_zh else chart.disclaimer_en)
    return "\n".join(rows)


def compute_dogon_sirius_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    overlay_real_position: bool = True,
) -> DogonSiriusChart:
    """Compute Dogon Sirius cosmology chart for given birth data."""
    from .interpretations import build_dogon_personal_influence

    constants = load_dogon_constants()

    lat = max(-90.0, min(90.0, float(latitude)))
    lon = ((float(longitude) + 180.0) % 360.0) - 180.0

    jd = _compute_jd(year, month, day, hour, minute, timezone)
    sirius_lon, sirius_dec = _compute_sirius_real_position(jd)

    dyear = _decimal_year(year, month, day)
    cycle = int(constants["system"]["sigui_cycle_years"])
    anchor = int(constants["system"]["sigui_anchor_year"])

    zone_result = _resolve_zone(sirius_dec, constants["zones"])
    sigui = _sigui_info(dyear, anchor, cycle)
    bodies = _build_bodies(constants, sirius_lon, sirius_dec, dyear)

    influence_zh, influence_en = build_dogon_personal_influence(
        sirius_declination=sirius_dec,
        zone_result=zone_result,
        sigui=sigui,
        latitude=lat,
        longitude=lon,
    )

    cross = [
        {
            "system": row["system"],
            "zh": row["focus"]["zh"],
            "en": row["focus"]["en"],
        }
        for row in constants.get("cross_cultural", [])
    ]

    return DogonSiriusChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=lat,
        longitude=lon,
        location_name=location_name,
        julian_day=jd,
        sirius_longitude=sirius_lon if overlay_real_position else bodies[0].longitude,
        sirius_declination=sirius_dec if overlay_real_position else bodies[0].declination,
        overlay_real_position=overlay_real_position,
        bodies=bodies,
        zone_result=zone_result,
        sigui=sigui,
        personal_influence_zh=influence_zh,
        personal_influence_en=influence_en,
        disclaimer_zh=constants["system"]["disclaimer"]["zh"],
        disclaimer_en=constants["system"]["disclaimer"]["en"],
        references=constants.get("references", []),
        cross_cultural=cross,
    )
