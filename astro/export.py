"""
astro/export.py — 匯出功能 (Chart Export)

Text summary, CSV, PDF (with CJK support), and SVG→PNG export for chart data.
"""
import csv
import io
import os
from dataclasses import asdict


def generate_chart_summary(chart_data):
    """Generate text summary from a standardized chart dict.

    chart_data: {system, datetime, location, planets, houses, ascendant, extra_sections}
    """
    lines = []
    lines.append(f"=== {chart_data.get('system', 'Chart')} ===")
    lines.append(f"Date/Time: {chart_data.get('datetime', '—')}")
    lines.append(f"Location: {chart_data.get('location', '—')}")
    if chart_data.get('ascendant'):
        lines.append(f"Ascendant: {chart_data['ascendant']}")
    lines.append("")
    lines.append("--- Planets ---")
    for p in chart_data.get("planets", []):
        retro = " (R)" if p.get("retrograde") else ""
        lines.append(f"  {p['name']:20s} {p.get('sign',''):14s} {p.get('degree', 0):7.2f}°{retro}")
    if chart_data.get("houses"):
        lines.append("")
        lines.append("--- Houses ---")
        for h in chart_data["houses"]:
            lines.append(f"  House {h.get('number', '?'):2s}  {h.get('sign', ''):14s}  {h.get('cusp', 0):7.2f}°")
    for sec in chart_data.get("extra_sections", []):
        lines.append("")
        lines.append(f"--- {sec['title']} ---")
        lines.append(sec["content"])
    return "\n".join(lines)


def generate_planet_csv(planets):
    """Generate CSV string from list of planet dicts."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Name", "Longitude", "Sign", "Degree", "Retrograde"])
    for p in planets:
        writer.writerow([p.get("name",""), f"{p.get('longitude',0):.4f}",
                         p.get("sign",""), f"{p.get('degree',0):.2f}",
                         p.get("retrograde", False)])
    return out.getvalue()


def _safe_latin1(text):
    """Encode text to latin-1 safely, replacing unsupported characters."""
    if not isinstance(text, str):
        text = str(text)
    return text.encode("latin-1", "replace").decode("latin-1")


def _find_cjk_font():
    """Search for an available CJK font on the system."""
    candidates = [
        # Linux — Noto CJK
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        # Windows
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msjh.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def generate_chart_pdf(chart_data):
    """Generate PDF bytes from chart data. Supports CJK when fonts are available."""
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
    except ImportError:
        raise RuntimeError("fpdf2 not installed. Run: pip install fpdf2")

    pdf = FPDF()
    pdf.add_page()

    # Try to load CJK font for proper Chinese character rendering
    cjk_font = _find_cjk_font()
    if cjk_font:
        try:
            pdf.add_font("CJK", "", cjk_font, uni=True)
            pdf.set_font("CJK", "", 16)
        except Exception:
            pdf.set_font("Helvetica", "B", 16)
            cjk_font = None
    else:
        pdf.set_font("Helvetica", "B", 16)

    _text = (lambda s: s) if cjk_font else _safe_latin1

    title = chart_data.get("system", "Astrology Chart")
    pdf.cell(0, 10, _text(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    if cjk_font:
        pdf.set_font("CJK", "", 10)
    else:
        pdf.set_font("Helvetica", "", 10)

    pdf.cell(0, 6, _text(f"Date: {chart_data.get('datetime', '')}"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, _text(f"Location: {chart_data.get('location', '')}"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if chart_data.get("ascendant"):
        pdf.cell(0, 6, _text(f"Ascendant: {chart_data['ascendant']}"),
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Planet table
    if cjk_font:
        pdf.set_font("CJK", "", 10)
    else:
        pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, "Planet", border=1)
    pdf.cell(40, 7, "Sign", border=1)
    pdf.cell(30, 7, "Degree", border=1)
    pdf.cell(20, 7, "R", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if cjk_font:
        pdf.set_font("CJK", "", 9)
    else:
        pdf.set_font("Helvetica", "", 9)
    for p in chart_data.get("planets", []):
        pdf.cell(50, 6, _text(p.get("name", "")), border=1)
        pdf.cell(40, 6, _text(p.get("sign", "")), border=1)
        pdf.cell(30, 6, f"{p.get('degree', 0):.2f}", border=1)
        pdf.cell(20, 6, "R" if p.get("retrograde") else "", border=1,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    for sec in chart_data.get("extra_sections", []):
        pdf.ln(4)
        if cjk_font:
            pdf.set_font("CJK", "", 10)
        else:
            pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, _text(sec.get("title", "")),
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if cjk_font:
            pdf.set_font("CJK", "", 9)
        else:
            pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, _text(sec.get("content", "")))

    return pdf.output()


def svg_to_png(svg_string: str, width: int = 800) -> bytes | None:
    """Convert SVG string to PNG bytes. Returns None if cairosvg is unavailable."""
    try:
        import cairosvg
        return cairosvg.svg2png(
            bytestring=svg_string.encode("utf-8"),
            output_width=width,
        )
    except ImportError:
        return None
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("SVG to PNG conversion failed: %s", exc)
        return None


def western_chart_to_dict(chart):
    """Convert WesternChart to standardized dict."""
    planets = [{"name": p.name, "longitude": p.longitude, "sign": p.sign,
                "degree": p.sign_degree, "retrograde": p.retrograde}
               for p in chart.planets]
    houses = [{"number": str(h.number), "sign": h.sign, "cusp": h.cusp}
              for h in chart.houses]
    return {"system": "Western Astrology", "datetime": f"{chart.year}-{chart.month:02d}-{chart.day:02d}",
            "location": chart.location_name, "ascendant": chart.asc_sign,
            "planets": planets, "houses": houses}


def vedic_chart_to_dict(chart):
    planets = [{"name": p.name, "longitude": p.longitude, "sign": p.rashi,
                "degree": round(p.longitude % 30, 2), "retrograde": p.retrograde}
               for p in chart.planets]
    return {"system": "Vedic Astrology", "datetime": f"{chart.year}-{chart.month:02d}-{chart.day:02d}",
            "location": chart.location_name, "ascendant": getattr(chart, 'asc_rashi', ''),
            "planets": planets, "houses": []}


def chinese_chart_to_dict(chart):
    planets = [{"name": p.name, "longitude": p.longitude,
                "sign": getattr(p, 'sign_chinese', ''),
                "degree": round(p.longitude % 30, 2), "retrograde": False}
               for p in chart.planets]
    return {"system": "Chinese Astrology (七政四餘)", "datetime": f"{chart.year}-{chart.month:02d}-{chart.day:02d}",
            "location": chart.location_name, "ascendant": "",
            "planets": planets, "houses": []}


def render_download_buttons(chart_data, svg_string=None, key_prefix=""):
    """Render download buttons in Streamlit (TXT, CSV, PDF, optional PNG)."""
    import streamlit as st

    n_cols = 4 if svg_string else 3
    cols = st.columns(n_cols)
    with cols[0]:
        txt = generate_chart_summary(chart_data)
        st.download_button("📄 Text Summary", data=txt,
                          file_name="chart_summary.txt",
                          mime="text/plain", key=f"{key_prefix}_txt")
    with cols[1]:
        csv_str = generate_planet_csv(chart_data.get("planets", []))
        st.download_button("📊 Planet CSV", data=csv_str,
                          file_name="planet_data.csv",
                          mime="text/csv", key=f"{key_prefix}_csv")
    with cols[2]:
        try:
            pdf_bytes = generate_chart_pdf(chart_data)
            st.download_button("📑 PDF Report", data=pdf_bytes,
                              file_name="chart_report.pdf",
                              mime="application/pdf", key=f"{key_prefix}_pdf")
        except Exception:
            st.caption("PDF export unavailable (fpdf2 missing or error)")
    if svg_string and n_cols == 4:
        with cols[3]:
            png_bytes = svg_to_png(svg_string)
            if png_bytes:
                st.download_button("🖼️ PNG Image", data=png_bytes,
                                  file_name="chart_image.png",
                                  mime="image/png", key=f"{key_prefix}_png")
            else:
                st.caption("PNG export unavailable")
