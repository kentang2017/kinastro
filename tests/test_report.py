"""Focused tests for professional Ziwei PDF report generation."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from astro.interpretation import ZiweiInterpretationResult, generate_ziwei_interpretation
from astro.models import BirthData, LunarDate, ZiweiChartResult, ZiweiPalace
from astro.report import (
    ZiweiReportOptions,
    generate_pdf_report,
    render_ziwei_report_chart_png,
)


def _build_sample_chart() -> ZiweiChartResult:
    birth_data = BirthData(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8,
        latitude=22.3193,
        longitude=114.1694,
        location_name="Hong Kong",
        gender="male",
    )
    palaces = [
        ZiweiPalace(
            index=0,
            name="命宮",
            branch=4,
            branch_name="辰",
            stem=0,
            stem_name="甲",
            stars=["紫微", "天府"],
            auxiliary_stars=["左輔", "右弼"],
            brightness={"紫微": "廟", "天府": "旺"},
            sihua={"紫微": "祿"},
            da_xian="3-12",
            da_xian_start=3,
        ),
        ZiweiPalace(
            index=1,
            name="官祿",
            branch=8,
            branch_name="申",
            stem=1,
            stem_name="乙",
            stars=["武曲", "七殺"],
            auxiliary_stars=["文昌"],
            brightness={"武曲": "旺"},
            da_xian="13-22",
            da_xian_start=13,
        ),
        ZiweiPalace(
            index=2,
            name="遷移",
            branch=0,
            branch_name="子",
            stem=2,
            stem_name="丙",
            stars=["廉貞"],
            auxiliary_stars=["天魁"],
            sihua={"廉貞": "忌"},
            da_xian="23-32",
            da_xian_start=23,
        ),
        ZiweiPalace(
            index=3,
            name="財帛",
            branch=10,
            branch_name="戌",
            stem=3,
            stem_name="丁",
            stars=["太陰"],
            da_xian="33-42",
            da_xian_start=33,
        ),
    ]
    return ZiweiChartResult(
        birth_data=birth_data,
        lunar_date=LunarDate(year=1989, month=12, day=5, is_leap_month=False),
        gender="male",
        hour_branch=6,
        ming_gong_branch=4,
        shen_gong_branch=8,
        wu_xing_ju=5,
        ziwei_branch=4,
        yin_yang="陽男",
        ming_zhu="祿存",
        shen_zhu="天相",
        sihua={"紫微": "祿", "廉貞": "忌"},
        palaces=palaces,
        sanhe_groups=[[4, 8, 0]],
    )


def test_ziwei_report_chart_png_renders():
    """The printable Ziwei palace-grid preview should render as PNG bytes."""
    image_bytes = render_ziwei_report_chart_png(_build_sample_chart())
    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(image_bytes) > 5000


def test_ziwei_pdf_report_generation_contains_required_sections():
    """The PDF generator should render key structured sections into the output."""
    chart = _build_sample_chart()
    interpretation = generate_ziwei_interpretation(chart, mode="traditional")
    pdf_bytes = generate_pdf_report(
        "ziwei",
        chart=chart,
        interpretation=interpretation,
        options=ZiweiReportOptions(),
    )
    assert pdf_bytes.startswith(b"%PDF")
    reader = PdfReader(BytesIO(pdf_bytes))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "Summary /" in extracted
    assert "Ming Gong Analysis /" in extracted
    assert "Da Xian Overview /" in extracted
    assert "KinAstro" in extracted


def test_ziwei_pdf_report_uses_updated_final_text():
    """Custom final interpretation text should appear in the generated report."""
    chart = _build_sample_chart()
    interpretation = ZiweiInterpretationResult.model_validate(
        generate_ziwei_interpretation(chart, mode="traditional").model_dump()
    ).model_copy(
        update={"final_text": "## Summary\nClient-facing custom final interpretation."}
    )
    pdf_bytes = generate_pdf_report(
        "ziwei",
        chart=chart,
        interpretation=interpretation,
        options=ZiweiReportOptions(include_ai_notes=False),
    )
    reader = PdfReader(BytesIO(pdf_bytes))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "Client-facing custom final interpretation." in extracted
