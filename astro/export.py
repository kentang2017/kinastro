"""
astro/export.py — 匯出功能 (Chart Export)

Text summary, CSV, and PDF export for chart data.
"""
import csv
import io
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


def generate_chart_pdf(chart_data):
    """Generate PDF bytes from chart data. Requires fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        raise RuntimeError("fpdf2 not installed. Run: pip install fpdf2")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    title = chart_data.get("system", "Astrology Chart")
    pdf.cell(0, 10, _safe_latin1(title), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _safe_latin1(f"Date: {chart_data.get('datetime', '')}"), ln=True)
    pdf.cell(0, 6, _safe_latin1(f"Location: {chart_data.get('location', '')}"), ln=True)
    if chart_data.get("ascendant"):
        pdf.cell(0, 6, _safe_latin1(f"Ascendant: {chart_data['ascendant']}"), ln=True)
    pdf.ln(4)

    # Planet table
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, "Planet", border=1)
    pdf.cell(40, 7, "Sign", border=1)
    pdf.cell(30, 7, "Degree", border=1)
    pdf.cell(20, 7, "R", border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for p in chart_data.get("planets", []):
        pdf.cell(50, 6, _safe_latin1(p.get("name", "")), border=1)
        pdf.cell(40, 6, _safe_latin1(p.get("sign", "")), border=1)
        pdf.cell(30, 6, f"{p.get('degree', 0):.2f}", border=1)
        pdf.cell(20, 6, "R" if p.get("retrograde") else "", border=1)
        pdf.ln()

    for sec in chart_data.get("extra_sections", []):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, _safe_latin1(sec.get("title", "")), ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, _safe_latin1(sec.get("content", "")))

    return pdf.output()


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


def render_download_buttons(chart_data, key_prefix=""):
    """Render download buttons in Streamlit."""
    import streamlit as st

    cols = st.columns(3)
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
        except RuntimeError:
            st.caption("PDF export requires fpdf2")
