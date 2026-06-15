"""Phase 4: cache, resonance, PDF board, edge cases."""

from __future__ import annotations

from astro.annual.cache import (
    _cached_timeline_by_key,
    clear_annual_timeline_cache,
    compute_annual_timeline_cached,
)
from astro.annual import compute_solar_return_flowyear_timeline
from astro.annual.render.liuren_board_png import render_liuren_board_png
from astro.annual.render.pdf_annual_report import generate_annual_sr_pdf
from astro.models import BirthData

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

FEMALE_BIRTH = BirthData(
    year=1985,
    month=8,
    day=26,
    hour=2,
    minute=55,
    timezone=8.0,
    latitude=22.319,
    longitude=114.169,
    location_name="香港",
    gender="female",
)


class TestAnnualCache:
    def test_lru_cache_returns_same_result(self):
        clear_annual_timeline_cache()
        t1 = compute_annual_timeline_cached(BIRTH, 2025, 2025, ["liuren"])
        t2 = compute_annual_timeline_cached(BIRTH, 2025, 2025, ["liuren"])
        assert t1.benming_zhi == t2.benming_zhi
        assert len(t1.years) == len(t2.years)

    def test_clear_cache(self):
        compute_annual_timeline_cached(BIRTH, 2024, 2024, ["liuren"])
        clear_annual_timeline_cache()
        assert _cached_timeline_by_key.cache_info().currsize == 0


class TestQizhengResonance:
    def test_resonance_hits_populated(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["qizheng"],
        )
        qz = timeline.years[0].other_chinese_systems["qizheng"]
        assert "resonance_hits" in qz.raw


class TestLiurenBoardPng:
    def test_board_png_bytes(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["liuren"],
        )
        year = timeline.years[0]
        png = render_liuren_board_png(year.liuren_chart, benming_zhi=timeline.benming_zhi)
        assert png[:8] == b"\x89PNG\r\n\x1a\n"

    def test_pdf_includes_board_attempt(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["liuren"],
        )
        pdf = generate_annual_sr_pdf(timeline, timeline.years[0])
        assert len(pdf) > 2000


class TestEdgeCases:
    def test_first_sr_year_after_birth(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=1991,
            end_year=1991,
            include_systems=["liuren"],
        )
        assert timeline.years[0].age == 2

    def test_female_qizheng_dasha(self):
        timeline = compute_solar_return_flowyear_timeline(
            FEMALE_BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["qizheng"],
        )
        assert timeline.years[0].other_chinese_systems["qizheng"].score >= 0

    def test_single_year_range(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2030,
            end_year=2030,
            include_systems=["western", "liuren", "ziwei", "bazi", "qizheng"],
        )
        assert len(timeline.years) == 1
        assert len(timeline.years[0].system_scores) == 5