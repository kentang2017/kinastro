"""Visualization and Streamlit rendering for Vietnam Tử Vi module."""

from __future__ import annotations

import math
from collections.abc import Callable

import svgwrite

from astro.vietnam.data.stars import get_star_name
from astro.vietnam.models import TuViChart


def build_12_palace_svg(chart: TuViChart, lang: str = "zh") -> str:
    """Build a simple 12-palace circular SVG with localized star names."""
    dwg = svgwrite.Drawing(size=(760, 760))
    cx, cy = 380, 380
    outer_r, inner_r = 320, 220

    dwg.add(dwg.circle(center=(cx, cy), r=outer_r, fill="#111", stroke="#DA251D", stroke_width=2))
    dwg.add(dwg.circle(center=(cx, cy), r=inner_r, fill="#1B1B1B", stroke="#444", stroke_width=1.5))

    for i, palace in enumerate(chart.base_chart.palaces):
        angle = (i * 30) - 90
        rad = angle * math.pi / 180.0
        x_outer = cx + outer_r * math.cos(rad)
        y_outer = cy + outer_r * math.sin(rad)
        dwg.add(dwg.line(start=(cx, cy), end=(x_outer, y_outer), stroke="#333", stroke_width=1))

        label_r = 265
        lx = cx + label_r * math.cos(rad + (15 * math.pi / 180.0))
        ly = cy + label_r * math.sin(rad + (15 * math.pi / 180.0))
        stars_local = ", ".join(get_star_name(s, lang) for s in palace.stars[:2]) or "-"
        dwg.add(dwg.text(
            f"{palace.name} {palace.branch_name}",
            insert=(lx, ly - 8),
            fill="#FFCD00",
            style="font-size:12px;font-weight:bold;",
            text_anchor="middle",
        ))
        dwg.add(dwg.text(
            stars_local,
            insert=(lx, ly + 10),
            fill="#DDD",
            style="font-size:10px;",
            text_anchor="middle",
        ))

    dwg.add(dwg.text(
        "Vietnam Tử Vi Đẩu Số",
        insert=(cx, cy - 8),
        fill="#FFCD00",
        style="font-size:20px;font-weight:bold;",
        text_anchor="middle",
    ))
    dwg.add(dwg.text(
        f"Mode: {chart.interpretation_mode}",
        insert=(cx, cy + 18),
        fill="#ddd",
        style="font-size:12px;",
        text_anchor="middle",
    ))

    return dwg.tostring()


def render_streamlit(
    chart: TuViChart,
    after_chart_hook: Callable[[], None] | None = None,
) -> None:
    """Render Vietnam Tu Vi chart in Streamlit."""
    import streamlit as st

    mode_label = {
        "trung_chau_tam_hop": "Trung Châu Tam Hợp",
        "traditional_cn": "Traditional CN",
    }.get(str(chart.interpretation_mode), str(chart.interpretation_mode))
    st.subheader(f"🇻🇳 Việt Nam Tử Vi Đẩu Số（{mode_label}）")
    st.caption(f"Interpret mode: {chart.interpretation_mode} · Language: {chart.language}")

    svg = chart.visual.get("svg_12_palace") or build_12_palace_svg(chart, chart.language)
    st.markdown(svg, unsafe_allow_html=True)

    if after_chart_hook:
        after_chart_hook()

    st.markdown("### 🧭 基本性格 + 格局")
    st.write(chart.interpretation.personality)
    st.write(chart.interpretation.physiology)
    st.write(chart.interpretation.self_effort)

    st.markdown("### ⏳ Đại hạn / Lưu niên")
    st.write(chart.interpretation.dai_han)
    st.write(chart.interpretation.luu_nien)

    st.markdown("### 🛠️ Remedies")
    for item in chart.remedies:
        st.markdown(f"- {item}")

    st.markdown("### 🔍 中越對照")
    for row in chart.comparison:
        st.markdown(
            f"**{row.topic}**\n\n"
            f"- 中國：{row.chinese_view}\n"
            f"- 越南：{row.vietnam_view}\n"
            f"- 差異：{row.summary_diff}"
        )
