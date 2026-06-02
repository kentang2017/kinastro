"""Plotly renderer helpers for Malay Ilmu Nujum visuals."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from astro.chart_theme import apply_chart_theme


def render_mata_angin_wheel(
    result: dict[str, object],
    *,
    chart_key: str = "malay_nujum_mata_angin_wheel",
) -> None:
    """Render a manuscript-inspired 8-direction wheel for Mata Angin Lapan."""
    sectors = result.get("sectors", []) if isinstance(result, dict) else []
    if not isinstance(sectors, list) or not sectors:
        st.info("No sector data available.")
        return

    theta = [float(item.get("angle_deg", 0.0)) for item in sectors if isinstance(item, dict)]
    width = [45.0] * len(theta)
    r = [1.0] * len(theta)
    colors = []
    labels = []
    hovers = []
    for item in sectors:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "neutral"))
        if status == "auspicious":
            colors.append("rgba(67, 160, 71, 0.84)")
        elif status == "inauspicious":
            colors.append("rgba(198, 40, 40, 0.80)")
        else:
            colors.append("rgba(214, 185, 123, 0.78)")
        labels.append(f"{item.get('direction_zh', '')} {item.get('animal_zh', '')}")
        hovers.append(
            "<br>".join(
                [
                    f"{item.get('direction_en', '')} / {item.get('direction_ms', '')}",
                    f"{item.get('animal_en', '')}",
                    f"{item.get('status_zh', '')} | score={item.get('score', 0)}",
                    str(item.get("reason_en", "")),
                ]
            )
        )

    fig = go.Figure(
        data=[
            go.Barpolar(
                r=r,
                theta=theta,
                width=width,
                marker=dict(color=colors, line=dict(color="#f5e6bf", width=2)),
                text=labels,
                hovertext=hovers,
                hovertemplate="%{hovertext}<extra></extra>",
                opacity=0.95,
            )
        ]
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.25]),
            angularaxis=dict(direction="clockwise", rotation=90, showgrid=False, ticks=""),
            bgcolor="rgba(248,239,220,0.36)",
        ),
        margin=dict(l=16, r=16, t=28, b=16),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        text="✶<br>Mata Angin Lapan",
        font=dict(size=18, color="#5D4037"),
    )
    apply_chart_theme(fig)
    st.plotly_chart(fig, width="stretch", key=chart_key)


__all__ = ["render_mata_angin_wheel"]
