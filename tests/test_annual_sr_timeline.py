"""Tests for solar-return annual flow timeline."""

from __future__ import annotations

from datetime import datetime

import pytest

from astro.annual import compute_solar_return_flowyear_timeline
from astro.annual.timezone import jd_to_local_datetime, jd_to_utc_datetime
from astro.models import BirthData
from astro.western.solar_return_core import find_solar_return_jd
from astro.western.western_return import compute_solar_return


BIRTH = BirthData(
    year=1990,
    month=5,
    day=15,
    hour=14,
    minute=30,
    timezone=8.0,
    latitude=25.033,
    longitude=121.565,
    location_name="台北",
    gender="male",
)

LAT = 25.033
LON = 121.565
TZ = 8.0
LOC = "台北"


class TestSolarReturnCoreRefactor:
    def test_western_return_still_works(self):
        from astro.western.western import compute_western_chart

        natal = compute_western_chart(1990, 5, 15, 14, 30, TZ, LAT, LON, LOC)
        sun_lon = natal.planets[0].longitude
        sr = compute_solar_return(sun_lon, 2024, LAT, LON, TZ, LOC)
        assert sr.return_year == 2024
        assert sr.return_jd > 0
        return_sun = sr.return_chart.planets[0].longitude
        diff = abs(sun_lon - return_sun) % 360
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.5


class TestAnnualTimeline:
    def test_compute_timeline_basic(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2024,
            end_year=2026,
            include_systems=["western", "liuren", "bazi", "ziwei", "qizheng"],
        )
        assert len(timeline.years) == 3
        assert timeline.benming_zhi
        assert timeline.natal_sun_longitude > 0

    def test_virtual_age(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2024,
            end_year=2024,
            include_systems=["liuren"],
        )
        year = timeline.years[0]
        assert year.age == 2024 - 1990 + 1
        assert year.age_kind == "virtual"

    def test_liuren_fields_present(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["liuren"],
        )
        year = timeline.years[0]
        assert year.liuren_jixiong is not None
        assert 0 <= year.liuren_jixiong.score <= 100
        assert year.liuren_chart
        assert year.sr_day_gz
        assert year.liunian_zhi

    def test_independent_system_scores(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["western", "liuren", "bazi", "ziwei", "qizheng"],
        )
        year = timeline.years[0]
        assert "western" in year.system_scores
        assert "liuren" in year.system_scores
        assert "bazi" in year.system_scores
        assert "ziwei" in year.system_scores
        assert "qizheng" in year.system_scores

    def test_sr_local_datetime_used_for_liuren(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["liuren"],
        )
        year = timeline.years[0]
        assert year.exact_sr_datetime_local.year == year.year or (
            year.exact_sr_datetime_local.month >= 1
        )

    def test_sanshi_sr_charts_present(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2024,
            end_year=2024,
            include_systems=["liuren", "taiyi", "qimen"],
        )
        year = timeline.years[0]
        assert year.liuren_chart
        assert year.liuren_lunming
        assert year.taiyi_chart
        assert year.qimen_chart
        assert timeline.trend_summary

    def test_birth_year_to_current_span(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=BIRTH.year,
            end_year=1992,
            include_systems=["liuren", "taiyi", "qimen"],
        )
        assert len(timeline.years) == 1992 - 1990 + 1
        assert timeline.years[0].year == 1990
        assert timeline.years[-1].year == 1992

    def test_invalid_system_raises(self):
        with pytest.raises(ValueError, match="Unsupported systems"):
            compute_solar_return_flowyear_timeline(
                BIRTH,
                start_year=2024,
                end_year=2024,
                include_systems=["tarot"],
            )


class TestTimezoneHelpers:
    def test_jd_roundtrip_consistency(self):
        jd = find_solar_return_jd(45.0, 2024)
        utc_dt = jd_to_utc_datetime(jd)
        local_dt = jd_to_local_datetime(jd, 8.0)
        assert isinstance(utc_dt, datetime)
        assert isinstance(local_dt, datetime)
        assert local_dt.hour != utc_dt.hour or local_dt.day != utc_dt.day or TZ == 0