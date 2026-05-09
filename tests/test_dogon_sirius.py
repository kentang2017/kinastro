"""Tests for Dogon Sirius module."""

from astro.dogon.calculator import (
    compute_dogon_sirius_chart,
    format_dogon_sirius_for_prompt,
    load_dogon_constants,
)


def test_constants_load():
    data = load_dogon_constants()
    assert data["system"]["name_short"] == "dogon_sirius"
    assert data["system"]["sigui_cycle_years"] == 50
    assert len(data["zones"]) >= 3


def test_compute_chart_basic_ranges():
    chart = compute_dogon_sirius_chart(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=0.0,
        latitude=0.0,
        longitude=0.0,
        location_name="Test",
    )
    assert 0.0 <= chart.sirius_longitude < 360.0
    assert -90.0 <= chart.sirius_declination <= 90.0
    assert chart.sigui.next_year - chart.sigui.previous_year == 50
    assert len(chart.bodies) == 3


def test_prompt_contains_sigui_and_zone():
    chart = compute_dogon_sirius_chart(
        year=2000,
        month=6,
        day=20,
        hour=8,
        minute=30,
        timezone=0.0,
        latitude=12.0,
        longitude=-8.0,
        location_name="Mali",
    )
    prompt = format_dogon_sirius_for_prompt(chart, lang="en")
    assert "Sigui" in prompt
    assert "Zone:" in prompt
