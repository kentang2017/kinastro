"""Professional PDF report generation for KinAstro.

Example:
    >>> from astro.report import ZiweiReportOptions, generate_pdf_report
    >>> pdf_bytes = generate_pdf_report(
    ...     "ziwei",
    ...     chart=ziwei_chart_result,
    ...     interpretation=ziwei_interpretation_result,
    ...     options=ZiweiReportOptions(),
    ... )
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from astro.interpretation.ziwei import ZiweiInterpretationResult
from astro.models import ZiweiChartResult

from .templates.ziwei import (
    ZiweiReportOptions,
    build_ziwei_report_sections,
    render_ziwei_report_chart_png,
)

_CJK_FONT_NAME = "NotoSansCJKtc"
_CJK_FONT_FALLBACK = "STSong-Light"
_FONT_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "fonts" / "NotoSansCJKtc-Regular.otf"
)
_REGISTERED_FONT_NAME: str | None = None


def generate_pdf_report(
    system: str,
    *,
    chart: Any,
    interpretation: Any,
    options: ZiweiReportOptions | None = None,
    chart_image_bytes: bytes | None = None,
    generated_at: datetime | None = None,
) -> bytes:
    """Generate a professional PDF report for the selected astrology system."""
    # pylint: disable=too-many-arguments
    if system != "ziwei":
        raise ValueError(f"Unsupported report system: {system}")
    if not isinstance(chart, ZiweiChartResult):
        raise TypeError("Ziwei PDF reports require a ZiweiChartResult chart.")
    if not isinstance(interpretation, ZiweiInterpretationResult):
        raise TypeError(
            "Ziwei PDF reports require a ZiweiInterpretationResult interpretation."
        )
    return generate_ziwei_pdf_report(
        chart,
        interpretation,
        options=options or ZiweiReportOptions(),
        chart_image_bytes=chart_image_bytes,
        generated_at=generated_at,
    )


def generate_ziwei_pdf_report(
    chart: ZiweiChartResult,
    interpretation: ZiweiInterpretationResult,
    *,
    options: ZiweiReportOptions,
    chart_image_bytes: bytes | None = None,
    generated_at: datetime | None = None,
) -> bytes:
    """Generate a professional printable Ziwei PDF report."""
    # pylint: disable=too-many-arguments
    active_generated_at = generated_at or datetime.now()
    resolved_chart_image = chart_image_bytes
    if resolved_chart_image is None and options.include_chart_visual:
        resolved_chart_image = render_ziwei_report_chart_png(chart, theme=options.theme)

    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title=options.title,
        author=options.branding,
        subject="Ziwei professional report",
        pageCompression=0,
    )
    styles = _build_styles(options)
    story = _build_ziwei_story(
        chart,
        interpretation,
        options=options,
        styles=styles,
        chart_image_bytes=resolved_chart_image,
        generated_at=active_generated_at,
    )
    document.build(
        story,
        onFirstPage=lambda canvas, doc: _draw_page_chrome(
            canvas, doc, options=options, generated_at=active_generated_at
        ),
        onLaterPages=lambda canvas, doc: _draw_page_chrome(
            canvas, doc, options=options, generated_at=active_generated_at
        ),
    )
    return output.getvalue()


def _build_ziwei_story(
    chart: ZiweiChartResult,
    interpretation: ZiweiInterpretationResult,
    *,
    options: ZiweiReportOptions,
    styles: dict[str, ParagraphStyle],
    chart_image_bytes: bytes | None,
    generated_at: datetime,
) -> list:
    # pylint: disable=too-many-arguments
    story: list = [
        Paragraph(_escape(options.title), styles["report_title"]),
        Spacer(1, 5 * mm),
        Paragraph(_escape(options.subtitle), styles["report_subtitle"]),
        Spacer(1, 7 * mm),
        _build_birth_info_table(chart, generated_at, options, styles),
        Spacer(1, 6 * mm),
    ]
    if chart_image_bytes is not None:
        story.extend(_build_visual_block(chart_image_bytes, styles))
    for title, content in build_ziwei_report_sections(
        interpretation,
        include_ai_notes=options.include_ai_notes,
        include_final_text=options.include_final_text,
    ):
        story.extend(_build_section_block(title, content, styles))
    if options.include_warnings and interpretation.warnings:
        story.extend(_build_section_block("Warnings / 注意事項", interpretation.warnings, styles))
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", color=colors.HexColor(options.theme.panel_border)))
    story.append(Spacer(1, 4 * mm))
    for disclaimer in options.disclaimer_lines:
        story.append(Paragraph(_escape(disclaimer), styles["disclaimer"]))
    return story


def _build_birth_info_table(
    chart: ZiweiChartResult,
    generated_at: datetime,
    options: ZiweiReportOptions,
    styles: dict[str, ParagraphStyle],
) -> Table:
    birth = chart.birth_data
    lunar = chart.lunar_date
    leap_flag = " (Leap / 閏月)" if lunar.is_leap_month else ""
    info_rows = [
        [
            Paragraph("<b>Birth Date / 出生日期</b>", styles["table_label"]),
            Paragraph(
                _escape(
                    f"{birth.year:04d}-{birth.month:02d}-{birth.day:02d} "
                    f"{birth.hour:02d}:{birth.minute:02d} UTC{birth.timezone:+.1f}"
                ),
                styles["table_value"],
            ),
            Paragraph("<b>Location / 地點</b>", styles["table_label"]),
            Paragraph(_escape(birth.location_name or "—"), styles["table_value"]),
        ],
        [
            Paragraph("<b>Lunar Date / 農曆</b>", styles["table_label"]),
            Paragraph(
                _escape(f"{lunar.year}年 {lunar.month}月 {lunar.day}日{leap_flag}"),
                styles["table_value"],
            ),
            Paragraph("<b>Core Markers / 命身主軸</b>", styles["table_label"]),
            Paragraph(
                _escape(
                    f"命宮 {chart.ming_gong_branch} · 身宮 {chart.shen_gong_branch} · "
                    f"{chart.ming_zhu} / {chart.shen_zhu}"
                ),
                styles["table_value"],
            ),
        ],
        [
            Paragraph(f"<b>{_escape(options.generated_label)}</b>", styles["table_label"]),
            Paragraph(
                _escape(generated_at.strftime("%Y-%m-%d %H:%M:%S")),
                styles["table_value"],
            ),
            Paragraph("<b>Si Hua / 四化</b>", styles["table_label"]),
            Paragraph(
                _escape("、".join(f"{star}化{transform}" for star, transform in chart.sihua.items())),
                styles["table_value"],
            ),
        ],
    ]
    table = Table(info_rows, colWidths=[30 * mm, 58 * mm, 34 * mm, 55 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBF8F1")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(options.theme.panel_border)),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5D7BC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _build_visual_block(
    chart_image_bytes: bytes,
    styles: dict[str, ParagraphStyle],
) -> list:
    image = Image(BytesIO(chart_image_bytes), width=160 * mm, height=160 * mm)
    return [
        KeepTogether(
            [
                Paragraph("Chart Visual / 命盤圖像", styles["section_title"]),
                Spacer(1, 3 * mm),
                image,
                Spacer(1, 5 * mm),
            ]
        )
    ]


def _build_section_block(
    title: str,
    content: str | list[str],
    styles: dict[str, ParagraphStyle],
) -> list:
    flowables: list = [Paragraph(_escape(title), styles["section_title"]), Spacer(1, 2.5 * mm)]
    if isinstance(content, list):
        for item in content:
            flowables.append(Paragraph("• " + _escape(item), styles["body"]))
            flowables.append(Spacer(1, 1.5 * mm))
    else:
        flowables.extend(_build_rich_paragraphs(content, styles))
    flowables.append(Spacer(1, 4 * mm))
    return flowables


def _build_rich_paragraphs(
    text: str,
    styles: dict[str, ParagraphStyle],
) -> list:
    flowables: list = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flowables.append(Spacer(1, 1.5 * mm))
            continue
        if line.startswith("## "):
            flowables.append(Paragraph(_escape(line[3:]), styles["subheading"]))
        elif line.startswith("- "):
            flowables.append(Paragraph("• " + _escape(line[2:]), styles["body"]))
        else:
            flowables.append(Paragraph(_escape(line), styles["body"]))
    return flowables


def _build_styles(options: ZiweiReportOptions) -> dict[str, ParagraphStyle]:
    font_name = _register_report_font()
    sample = getSampleStyleSheet()
    return {
        "report_title": ParagraphStyle(
            "ReportTitle",
            parent=sample["Title"],
            fontName=font_name,
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor(options.theme.accent_color),
            spaceAfter=2,
        ),
        "report_subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=9.5,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor(options.theme.text_muted),
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=sample["Heading2"],
            fontName=font_name,
            fontSize=13.5,
            leading=18,
            textColor=colors.HexColor(options.theme.accent_color),
            borderPadding=0,
            spaceAfter=2,
        ),
        "subheading": ParagraphStyle(
            "Subheading",
            parent=sample["Heading3"],
            fontName=font_name,
            fontSize=11.5,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor(options.theme.text_primary),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=10.3,
            leading=15.5,
            alignment=TA_LEFT,
            textColor=colors.HexColor(options.theme.text_primary),
        ),
        "table_label": ParagraphStyle(
            "TableLabel",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=9.6,
            leading=12,
            textColor=colors.HexColor(options.theme.accent_color),
        ),
        "table_value": ParagraphStyle(
            "TableValue",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=9.6,
            leading=12,
            textColor=colors.HexColor(options.theme.text_primary),
        ),
        "disclaimer": ParagraphStyle(
            "Disclaimer",
            parent=sample["BodyText"],
            fontName=font_name,
            fontSize=8.6,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor(options.theme.footer_text),
        ),
    }


def _draw_page_chrome(canvas, doc, *, options: ZiweiReportOptions, generated_at: datetime) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor(options.theme.header_background))
    canvas.rect(0, height - (18 * mm), width, 18 * mm, stroke=0, fill=1)
    canvas.setFont(_register_report_font(), 10)
    canvas.setFillColor(colors.HexColor(options.theme.title_color))
    canvas.drawString(18 * mm, height - (11.5 * mm), options.branding)
    canvas.setFillColor(colors.HexColor(options.theme.footer_text))
    canvas.setFont(_register_report_font(), 8.5)
    canvas.drawCentredString(
        width / 2,
        8 * mm,
        (
            f"{options.branding} · {generated_at.strftime('%Y-%m-%d %H:%M')} · "
            f"Page {doc.page}"
        ),
    )
    canvas.restoreState()


def _register_report_font() -> str:
    global _REGISTERED_FONT_NAME  # pylint: disable=global-statement
    if _REGISTERED_FONT_NAME is not None:
        return _REGISTERED_FONT_NAME
    try:
        pdfmetrics.registerFont(UnicodeCIDFont(_CJK_FONT_FALLBACK))
        _REGISTERED_FONT_NAME = _CJK_FONT_FALLBACK
    except (KeyError, TypeError, ValueError):  # pragma: no cover - rare runtime
        _REGISTERED_FONT_NAME = "Helvetica"
    if _FONT_PATH.exists():
        try:
            pdfmetrics.registerFont(TTFont(_CJK_FONT_NAME, str(_FONT_PATH)))
            _REGISTERED_FONT_NAME = _CJK_FONT_NAME
        except (OSError, TTFError, ValueError):
            pass
    return _REGISTERED_FONT_NAME


def _escape(text: str) -> str:
    return escape(text).replace("\n", "<br/>")


__all__ = [
    "generate_pdf_report",
    "generate_ziwei_pdf_report",
]
