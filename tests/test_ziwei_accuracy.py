"""Astronomical Ziwei accuracy tests driven by verified fixtures."""
# pylint: disable=wrong-import-position

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("swisseph")
pytest.importorskip("streamlit")

import astro
from astro.models import BirthData, ZiweiChartResult
from astro.ziwei import EARTHLY_BRANCHES, compute_ziwei_chart


_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "verified_ziwei_charts.json"


def _load_fixtures() -> list[dict]:
    with _FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def _star_to_branch_map(result: ZiweiChartResult) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for palace in result.palaces:
        for star in palace.stars:
            mapping[star] = palace.branch_name
    return mapping


@pytest.mark.parametrize(
    "fixture",
    _load_fixtures(),
    ids=lambda fixture: fixture["id"],
)
def test_verified_ziwei_fixtures_match_astronomical_model(fixture: dict) -> None:
    """The astronomical Ziwei model path should match verified fixture data."""
    birth_data = BirthData(**fixture["input"])

    result = astro.compute_chart("ziwei", birth_data)

    assert isinstance(result, ZiweiChartResult)
    expected = fixture["expected"]
    assert result.lunar_date.year == expected["lunar_year"]
    assert result.lunar_date.month == expected["lunar_month"]
    assert result.lunar_date.day == expected["lunar_day"]
    assert result.lunar_date.is_leap_month is expected["is_leap_month"]
    assert EARTHLY_BRANCHES[result.hour_branch] == expected["hour_branch"]
    assert EARTHLY_BRANCHES[result.ming_gong_branch] == expected["ming_gong_branch"]
    assert result.wu_xing_ju == expected["wu_xing_ju"]
    assert EARTHLY_BRANCHES[result.ziwei_branch] == expected["ziwei_branch"]

    star_map = _star_to_branch_map(result)
    for star_name, branch_name in expected["major_stars"].items():
        assert star_map[star_name] == branch_name

    assert result.metadata["lunar_conversion_method"] == "astronomical_jieqi"


def test_legacy_ziwei_path_still_returns_dataclass() -> None:
    """Default Ziwei compute path should remain backward compatible."""
    chart = compute_ziwei_chart(
        year=2023,
        month=3,
        day=31,
        hour=8,
        minute=0,
        timezone=8,
        latitude=39.9042,
        longitude=116.4074,
        location_name="Beijing",
        gender="男",
    )

    assert chart.__class__.__name__ == "ZiweiChart"
    assert hasattr(chart, "palaces")
