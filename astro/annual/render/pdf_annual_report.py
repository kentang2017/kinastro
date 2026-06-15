"""PDF report generation for solar-return annual timeline."""

from __future__ import annotations

from datetime import datetime
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from astro.annual.models import AnnualFlowYear, SolarReturnTimeline

_CJK_FONT = "STSong-Light"


def _ensure_font() -> None:
    try:
        pdfmetrics.getFont(_CJK_FONT)
    except KeyError:
        pdfmetrics.registerFont(UnicodeCIDFont(_CJK_FONT))


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def generate_annual_sr_pdf(
    timeline: SolarReturnTimeline,
    year: AnnualFlowYear,
    *,
    generated_at: datetime | None = None,
) -> bytes:
    """Generate a single-year SR annual PDF report."""
    _ensure_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AnnualTitle",
        parent=styles["Title"],
        fontName=_CJK_FONT,
        fontSize=16,
        leading=20,
    )
    body_style = ParagraphStyle(
        "AnnualBody",
        parent=styles["Normal"],
        fontName=_CJK_FONT,
        fontSize=10,
        leading=14,
    )
    header_style = ParagraphStyle(
        "AnnualHeader",
        parent=styles["Heading2"],
        fontName=_CJK_FONT,
        fontSize=12,
        leading=16,
    )

    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"KinAstro SR Annual {year.year}",
    )

    birth = timeline.natal_birth_data
    lr = year.liuren_jixiong
    story = [
        _p("堅占星 KinAstro — 太陽回歸流年報告", title_style),
        Spacer(1, 6 * mm),
        _p(
            f"本命：{birth.year}-{birth.month:02d}-{birth.day:02d} "
            f"{birth.hour:02d}:{birth.minute:02d} @ {birth.location_name}",
            body_style,
        ),
        _p(f"虛歲 {year.age}｜SR {year.year}｜{year.exact_sr_datetime_local}", body_style),
        Spacer(1, 4 * mm),
        _p("各體系獨立評分", header_style),
    ]

    score_rows = [["體系", "分數", "等級"]]
    if lr:
        score_rows.append(["大六壬", f"{lr.score:.0f}", lr.level.value])
    for key, snap in year.other_chinese_systems.items():
        score_rows.append([key, f"{snap.score:.0f}", snap.level.value])
    if year.western_sr:
        score_rows.append(["西洋SR", f"{year.western_sr.score:.0f}", year.western_sr.level.value])

    table = Table(score_rows, colWidths=[50 * mm, 25 * mm, 25 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), _CJK_FONT, 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.extend([table, Spacer(1, 5 * mm)])

    if lr:
        story.extend(
            [
                _p("大六壬核心", header_style),
                _p(lr.affair_summary, body_style),
                _p(f"三傳：{lr.san_chuan_summary}", body_style),
                _p(f"太歲影響：{lr.taisui_impact or '—'}", body_style),
                Spacer(1, 3 * mm),
            ]
        )
        if year.liuren_chart:
            try:
                from astro.annual.render.liuren_board_png import render_liuren_board_png

                board_png = render_liuren_board_png(
                    year.liuren_chart,
                    benming_zhi=timeline.benming_zhi,
                )
                story.append(RLImage(BytesIO(board_png), width=150 * mm, height=150 * mm))
                story.append(Spacer(1, 4 * mm))
            except Exception:
                pass

    for key, snap in year.other_chinese_systems.items():
        story.extend([_p(f"{key}", header_style), _p(snap.summary, body_style), Spacer(1, 2 * mm)])

    if year.western_sr:
        story.extend([_p("西洋太陽回歸", header_style), _p(year.western_sr.summary, body_style)])

    story.append(Spacer(1, 4 * mm))
    story.append(_p(f"生成時間：{(generated_at or datetime.now()).strftime('%Y-%m-%d %H:%M')}", body_style))
    doc.build(story)
    return output.getvalue()