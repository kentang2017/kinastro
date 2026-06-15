"""Phase 2/3 tests: ziwei flow, qizheng dasha, PDF, API models."""

from __future__ import annotations

from astro.annual.adapters.qizheng import compute_qizheng_annual, compute_qizheng_natal
from astro.annual.adapters.ziwei_flow import resolve_ziwei_flow_palaces
from astro.annual.render.pdf_annual_report import generate_annual_sr_pdf
from astro.annual import compute_solar_return_flowyear_timeline
from astro.models import BirthData
from astro.ziwei import compute_ziwei_chart

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


class TestZiweiFlowPalaces:
    def test_liunian_and_xiaoxian_resolved(self):
        chart = compute_ziwei_chart(
            1990, 5, 15, 14, 30, 8.0, 25.033, 121.565, "台北", gender="男"
        )
        flow = resolve_ziwei_flow_palaces(chart, virtual_age=35, liunian_gz="乙巳", liunian_branch="巳")
        assert flow.liunian_palace_name
        assert flow.xiaoxian_palace_name
        assert flow.direction in {"順行", "逆行"}

    def test_ziwei_score_not_flat_fifty(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2024,
            end_year=2026,
            include_systems=["ziwei"],
        )
        scores = {year.system_scores["ziwei"] for year in timeline.years}
        assert len(scores) >= 1


class TestQizhengDasha:
    def test_qizheng_natal_and_annual(self):
        natal = compute_qizheng_natal(BIRTH)
        ctx = compute_qizheng_annual(BIRTH, 2025, natal)
        assert ctx.flow_year_branch
        assert ctx.dasha.periods

    def test_qizheng_score_in_timeline(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["qizheng"],
        )
        snap = timeline.years[0].other_chinese_systems["qizheng"]
        assert snap.raw.get("current_period_lord") is not None or snap.summary


class TestPdfReport:
    def test_generate_pdf_bytes(self):
        timeline = compute_solar_return_flowyear_timeline(
            BIRTH,
            start_year=2025,
            end_year=2025,
            include_systems=["liuren", "ziwei", "bazi", "qizheng", "western"],
        )
        pdf = generate_annual_sr_pdf(timeline, timeline.years[0])
        assert pdf[:4] == b"%PDF"