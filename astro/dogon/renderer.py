"""Streamlit renderer for Dogon Sirius Cosmology."""

from __future__ import annotations

import json
from pathlib import Path

from astro.chart_theme import apply_chart_theme, svg_header, svg_footer, FONT_FAMILY
from astro.i18n import auto_cn, get_lang

from .calculator import DogonSiriusChart


def _load_constants_cached():
    import streamlit as st

    @st.cache_data(show_spinner=False)
    def _load() -> dict:
        p = Path(__file__).parent / "data" / "constants.json"
        return json.loads(p.read_text(encoding="utf-8"))

    return _load()


def _build_svg_fallback(chart: DogonSiriusChart, constants: dict) -> str:
    colors = constants["palette"]
    size = 640
    cx = cy = size / 2
    r0 = 190

    body_cfg = constants["bodies"]

    def pos(lon: float, radius: float) -> tuple[float, float]:
        import math

        a = math.radians((lon - 90.0) % 360)
        return cx + radius * math.cos(a), cy + radius * math.sin(a)

    lines = [
        svg_header(size, size, "Dogon Sirius Cosmology"),
        f'<defs><radialGradient id="dogonbg"><stop offset="0%" stop-color="{colors["indigo"]}"/><stop offset="100%" stop-color="{colors["black"]}"/></radialGradient></defs>',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="url(#dogonbg)"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r0}" fill="none" stroke="{colors["earth"]}" stroke-width="1.8" stroke-dasharray="3 5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r0 * 0.66}" fill="none" stroke="{colors["stardust"]}" stroke-width="1" opacity="0.55"/>',
    ]

    for body in chart.bodies:
        cfg = body_cfg[body.key]
        px, py = pos(body.longitude, r0 if body.key == "sirius_a" else (r0 * 0.66 if body.key == "sirius_b" else r0 * 0.5))
        lines.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{cfg["radius"]}" fill="{cfg["color"]}" opacity="0.95"/>'
        )
        lines.append(
            f'<text x="{px + 12:.2f}" y="{py - 10:.2f}" font-family="{FONT_FAMILY}" font-size="12" fill="{colors["stardust"]}">{body.label} · {body.dogon_name}</text>'
        )

    lines.append(
        f'<text x="18" y="{size - 34}" font-family="{FONT_FAMILY}" font-size="12" fill="{colors["stardust"]}">Sigui cycle: {chart.sigui.previous_year} → {chart.sigui.next_year}</text>'
    )
    lines.append(
        f'<text x="18" y="{size - 16}" font-family="{FONT_FAMILY}" font-size="11" fill="{colors["earth"]}">Zone: {chart.zone_result.label}</text>'
    )
    lines.append(svg_footer())
    return "".join(lines)


def render_dogon_sirius_chart(chart: DogonSiriusChart, after_chart_hook=None) -> None:
    import streamlit as st

    constants = _load_constants_cached()
    colors = constants["palette"]
    lang = get_lang()
    is_zh = lang in ("zh", "zh_cn")

    st.markdown(
        f"""
<div style="padding:16px 18px;border-radius:14px;border:1px solid {colors['earth']};
background:linear-gradient(135deg,{colors['black']} 0%,{colors['indigo']} 100%);margin-bottom:10px;">
  <div style="font-size:1.2rem;color:{colors['stardust']};font-weight:700;">🜂 Dogon Sirius Cosmology · Po Tolo · Nommo · Sigui</div>
  <div style="font-size:.92rem;color:{colors['earth']};margin-top:6px;">{chart.location_name} · {chart.year:04d}-{chart.month:02d}-{chart.day:02d} {chart.hour:02d}:{chart.minute:02d} (UTC{chart.timezone:+.1f})</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    fig_ok = False
    try:
        import plotly.graph_objects as go

        traces = []
        for body in chart.bodies:
            traces.append(
                go.Scatterpolar(
                    r=[1 if body.key == "sirius_a" else (0.66 if body.key == "sirius_b" else 0.5)],
                    theta=[body.longitude],
                    mode="markers+text",
                    text=[f"{body.label}<br>{body.dogon_name}"],
                    textposition="top center",
                    marker=dict(size=14 if body.key == "sirius_a" else 11, color={
                        "sirius_a": constants["bodies"]["sirius_a"]["color"],
                        "sirius_b": constants["bodies"]["sirius_b"]["color"],
                        "sirius_c": constants["bodies"]["sirius_c"]["color"],
                    }[body.key]),
                    customdata=[[body.cultural_note_zh, body.cultural_note_en]],
                    hovertemplate="%{text}<br>%{customdata[0]}<extra></extra>" if is_zh else "%{text}<br>%{customdata[1]}<extra></extra>",
                    name=body.label,
                )
            )

        timeline = list(range(chart.sigui.previous_year, chart.sigui.next_year + 1, 5))
        traces.append(
            go.Scatterpolar(
                r=[0.2 + 0.3 * ((y - chart.sigui.previous_year) / max(1, chart.sigui.cycle_years)) for y in timeline],
                theta=[(360 * ((y - chart.sigui.previous_year) / max(1, chart.sigui.cycle_years))) for y in timeline],
                mode="lines+markers",
                line=dict(color=colors["ochre"], width=1, dash="dot"),
                marker=dict(size=5, color=colors["stardust"]),
                name="Sigui timeline",
                hovertext=[str(y) for y in timeline],
                hoverinfo="text+name",
            )
        )

        fig = go.Figure(data=traces)
        fig.update_layout(
            polar=dict(
                bgcolor=f"rgba(0,0,0,0)",
                radialaxis=dict(visible=True, showticklabels=False, gridcolor="rgba(217,191,139,0.15)"),
                angularaxis=dict(direction="clockwise", rotation=90, gridcolor="rgba(217,191,139,0.12)"),
            ),
            title="Dogon Sirius Cosmology View",
            showlegend=True,
        )
        apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        fig_ok = True
    except Exception:
        pass

    if not fig_ok:
        st.markdown(_build_svg_fallback(chart, constants), unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric(auto_cn("Sirius 赤緯", "Sirius declination"), f"{chart.sirius_declination:.2f}°")
    c2.metric(auto_cn("距下次 Sigui", "To next Sigui"), f"{chart.sigui.years_until_next:.2f}y")
    c3.metric(auto_cn("星象區域", "Lore zone"), chart.zone_result.label)

    st.caption(auto_cn(chart.disclaimer_zh, chart.disclaimer_en))

    st.subheader(auto_cn("Dogon 個人影響", "Dogon Personal Influence"))
    st.info(chart.personal_influence_zh if is_zh else chart.personal_influence_en)

    st.subheader(auto_cn("文化宇宙學與教育內容", "Cultural Cosmology & Learning"))
    st.markdown(
        auto_cn(
            "- **Nommo**：祖先靈與秩序修復象徵\n"
            "- **Po Tolo**：高密度『種子星』隱喻\n"
            "- **Sigui**：約 50 年社群更新節律\n"
            "- **提示**：此頁內容以文化人類學脈絡呈現，不作自然科學定論。",
            "- **Nommo**: ancestor-spirit motif of order restoration\n"
            "- **Po Tolo**: dense 'seed-star' metaphor\n"
            "- **Sigui**: ~50-year communal renewal rhythm\n"
            "- **Note**: presented as cultural anthropology, not hard-science proof."
        )
    )

    st.subheader(auto_cn("跨文化比較（Sirius）", "Cross-cultural Sirius comparison"))
    for row in chart.cross_cultural:
        st.markdown(f"- **{row['system']}** · {(row['zh'] if is_zh else row['en'])}")

    with st.expander(auto_cn("來源與爭議說明", "Sources & contested points"), expanded=False):
        for ref in chart.references:
            st.markdown(f"- {ref}")

    report_txt = (
        chart.personal_influence_zh if is_zh else chart.personal_influence_en
    ) + "\n\n" + (chart.disclaimer_zh if is_zh else chart.disclaimer_en)
    st.download_button(
        auto_cn("⬇ 匯出 Dogon 解讀（TXT）", "⬇ Export Dogon reading (TXT)"),
        data=report_txt,
        file_name=f"dogon_sirius_{chart.year:04d}{chart.month:02d}{chart.day:02d}.txt",
        mime="text/plain",
    )

    if after_chart_hook:
        after_chart_hook()
