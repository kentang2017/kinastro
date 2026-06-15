"""Natal context helpers for annual solar-return timelines."""

from __future__ import annotations

from astro.bazi.calculator import _get_liunian_gz
from astro.models import BirthData
from astro.western.western import compute_western_chart

DIZHI = list("子丑寅卯辰巳午未申酉戌亥")


def year_branch_from_birth(birth: BirthData) -> str:
    import sxtwl

    lunar = sxtwl.fromSolar(birth.year, birth.month, birth.day)
    return DIZHI[lunar.getYearGZ().dz]


def liunian_branch_for_year(calendar_year: int) -> str:
    gz = _get_liunian_gz(calendar_year)
    return gz[1] if len(gz) >= 2 else ""


def liunian_ganzhi_for_year(calendar_year: int) -> str:
    return _get_liunian_gz(calendar_year)


def virtual_age(birth_year: int, sr_year: int) -> int:
    return sr_year - birth_year + 1


def western_age(birth_year: int, sr_year: int) -> int:
    return sr_year - birth_year


def natal_sun_longitude(birth: BirthData) -> float:
    chart = compute_western_chart(**birth.to_compute_kwargs())
    if chart.planets:
        return float(chart.planets[0].longitude)
    raise ValueError("Unable to determine natal Sun longitude")