# coding: utf-8
"""
astro/western/aspect_patterns.py - Aspect Pattern Detection

Detects classic Western astrology aspect patterns from a set of
planet positions.  Supported patterns:

  - Grand Trine (\u5927\u4e09\u89d2)
  - T-Square (T\u5f62\u76f8\u4f4d)
  - Grand Cross (\u5927\u5341\u5b57)
  - Yod / Finger of God (\u547d\u904b\u6307)
  - Kite (\u98a8\u7b4d)
  - Mystic Rectangle (\u795e\u79d8\u9577\u65b9\u5f62)
  - Grand Sextile (\u5927\u516d\u8292\u661f)
  - Stellium (\u661f\u7fa4)
  - Boomerang (\u56de\u529b\u93d6)

Each detected pattern is returned as a dict with at least:
  - "pattern"        English pattern name
  - "pattern_cn"     Chinese pattern name
  - "planets"        participating planet names
  - "element"        dominant element where applicable
  - "quality"        modality quality where applicable
  - "apex"           apex/focal planet where applicable
  - "description"    brief English description
  - "description_cn" brief Chinese description
"""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import plotly.graph_objects as go  # noqa: F401

ZODIAC_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

ZODIAC_QUALITIES = {
    "Aries": "Cardinal", "Cancer": "Cardinal",
    "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed",
    "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable",
    "Sagittarius": "Mutable", "Pisces": "Mutable",
}

ZODIAC_SIGNS_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ELEMENT_CN = {"Fire": "\u706b", "Earth": "\u571f", "Air": "\u98a8", "Water": "\u6c34"}
QUALITY_CN = {"Cardinal": "\u672c\u4f4d", "Fixed": "\u56fa\u5b9a", "Mutable": "\u8b8a\u52d5"}

_PATTERN_COLORS = {
    "Grand Trine": "#4CAF50",
    "T-Square": "#F44336",
    "Grand Cross": "#FF5722",
    "Yod": "#9C27B0",
    "Kite": "#2196F3",
    "Mystic Rectangle": "#00BCD4",
    "Grand Sextile": "#FFD700",
    "Stellium": "#FF9800",
    "Boomerang": "#E91E63",
}


def _normalize(deg):
    return deg % 360.0


def _angle_diff(a, b):
    diff = abs(_normalize(a) - _normalize(b))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _is_aspect(lon_a, lon_b, target, orb):
    return abs(_angle_diff(lon_a, lon_b) - target) <= orb


def _sign_of(longitude):
    idx = int(_normalize(longitude) / 30.0) % 12
    return ZODIAC_SIGNS_ORDER[idx]


def _dominant_element(planet_names, positions):
    counts = {}
    for name in planet_names:
        lon = positions.get(name)
        if lon is None:
            continue
        elem = ZODIAC_ELEMENTS.get(_sign_of(lon), "")
        if elem:
            counts[elem] = counts.get(elem, 0) + 1
    return max(counts, key=counts.get) if counts else ""


def _dominant_quality(planet_names, positions):
    counts = {}
    for name in planet_names:
        lon = positions.get(name)
        if lon is None:
            continue
        qual = ZODIAC_QUALITIES.get(_sign_of(lon), "")
        if qual:
            counts[qual] = counts.get(qual, 0) + 1
    return max(counts, key=counts.get) if counts else ""


def detect_aspect_patterns(positions, orb=8.0):
    """Detect classic aspect patterns from a dict of planet longitudes.

    Parameters
    ----------
    positions : dict[str, float]
        Mapping of planet name to ecliptic longitude (0-360 degrees).
    orb : float
        Default orb in degrees for major aspects.

    Returns
    -------
    list[dict]
        Each dict describes one detected pattern.
    """
    planets = list(positions.keys())
    n = len(planets)
    patterns = []
    seen_sets = set()

    trine_orb = orb
    square_orb = orb
    sextile_orb = max(3.0, orb * 0.5)
    quincunx_orb = max(3.0, orb * 0.5)
    opposition_orb = orb

    def _add(record):
        key = (record["pattern"], frozenset(record["planets"]))
        if key not in seen_sets:
            seen_sets.add(key)
            patterns.append(record)

    def _trine(a, b):
        return _is_aspect(positions[a], positions[b], 120, trine_orb)

    def _square(a, b):
        return _is_aspect(positions[a], positions[b], 90, square_orb)

    def _sextile(a, b):
        return _is_aspect(positions[a], positions[b], 60, sextile_orb)

    def _quincunx(a, b):
        return _is_aspect(positions[a], positions[b], 150, quincunx_orb)

    def _opposition(a, b):
        return _is_aspect(positions[a], positions[b], 180, opposition_orb)

    # Grand Trine
    for a, b, c in combinations(planets, 3):
        if _trine(a, b) and _trine(b, c) and _trine(a, c):
            elem = _dominant_element([a, b, c], positions)
            elem_cn = ELEMENT_CN.get(elem, "")
            _add({
                "pattern": "Grand Trine",
                "pattern_cn": "\u5927\u4e09\u89d2",
                "planets": [a, b, c],
                "element": elem, "element_cn": elem_cn,
                "quality": "", "quality_cn": "", "apex": "",
                "description": "A Grand Trine in " + elem + " element -- natural talent and ease, but may lack motivation without challenge.",
                "description_cn": "\u5927\u4e09\u89d2\uff08" + elem_cn + "\u8c61\uff09\u2014\u2014 \u4ee3\u8868\u5929\u8ce6\u624d\u80fd\u8207\u8f15\u9b06\u6d41\u52d5\u7684\u80fd\u91cf\u3002",
            })

    # T-Square
    for a, b in combinations(planets, 2):
        if not _opposition(a, b):
            continue
        for c in planets:
            if c == a or c == b:
                continue
            if _square(a, c) and _square(b, c):
                qual = _dominant_quality([a, b, c], positions)
                qual_cn = QUALITY_CN.get(qual, "")
                _add({
                    "pattern": "T-Square",
                    "pattern_cn": "T\u5f62\u76f8\u4f4d",
                    "planets": [a, b, c],
                    "element": "", "element_cn": "",
                    "quality": qual, "quality_cn": qual_cn, "apex": c,
                    "description": "A T-Square with apex " + c + " in " + qual + " quality -- intense pressure and drive concentrated at the apex.",
                    "description_cn": "T\u5f62\u76f8\u4f4d\uff0c\u9802\u9ede " + c + " (" + qual_cn + "\u661f\u5ea7) -- \u5f37\u5927\u5f35\u529b\u96c6\u4e2d\u5728\u9802\u9ede\u884c\u661f\u3002",
                })

    # Grand Cross
    for a, b, c, d in combinations(planets, 4):
        if (
            _opposition(a, b) and _opposition(c, d)
            and _square(a, c) and _square(a, d)
            and _square(b, c) and _square(b, d)
        ):
            qual = _dominant_quality([a, b, c, d], positions)
            qual_cn = QUALITY_CN.get(qual, "")
            _add({
                "pattern": "Grand Cross",
                "pattern_cn": "\u5927\u5341\u5b57",
                "planets": [a, b, c, d],
                "element": "", "element_cn": "",
                "quality": qual, "quality_cn": qual_cn, "apex": "",
                "description": "A Grand Cross in " + qual + " quality -- extreme tension from four directions; powerful but demanding.",
                "description_cn": "\u5927\u5341\u5b57(" + qual_cn + "\u661f\u5ea7) -- \u56db\u9762\u58d3\u529b\uff0c\u6975\u5927\u7d27\u5f35\u80fd\u91cf\u3002",
            })

    # Yod
    for a, b in combinations(planets, 2):
        if not _sextile(a, b):
            continue
        for c in planets:
            if c == a or c == b:
                continue
            if _quincunx(a, c) and _quincunx(b, c):
                _add({
                    "pattern": "Yod",
                    "pattern_cn": "\u547d\u904b\u6307\uff08\u4e0a\u5e1d\u4e4b\u6307\uff09",
                    "planets": [a, b, c],
                    "element": "", "element_cn": "",
                    "quality": "", "quality_cn": "", "apex": c,
                    "description": "A Yod pointing to " + c + " -- karmic configuration suggesting a special destiny or spiritual mission.",
                    "description_cn": "\u547d\u904b\u6307\uff0c\u6307\u5411 " + c + " -- \u696d\u529b\u683c\u5c40\uff0c\u66b4\u793a\u7279\u6b8a\u4f7f\u547d\u3002",
                })

    # Kite
    for a, b, c in combinations(planets, 3):
        if not (_trine(a, b) and _trine(b, c) and _trine(a, c)):
            continue
        for d in planets:
            if d in (a, b, c):
                continue
            for apex in (a, b, c):
                others = [p for p in (a, b, c) if p != apex]
                if _opposition(d, apex) and _sextile(d, others[0]) and _sextile(d, others[1]):
                    elem = _dominant_element([a, b, c], positions)
                    elem_cn = ELEMENT_CN.get(elem, "")
                    _add({
                        "pattern": "Kite",
                        "pattern_cn": "\u98a8\u7b4d",
                        "planets": sorted([a, b, c, d]),
                        "element": elem, "element_cn": elem_cn,
                        "quality": "", "quality_cn": "", "apex": d,
                        "description": "A Kite with focal planet " + d + " -- Grand Trine energy directed through focal point into practical achievement.",
                        "description_cn": "\u98a8\u7b4d\uff0c\u7126\u9ede\u884c\u661f " + d + " -- \u5927\u4e09\u89d2\u80fd\u91cf\u8f49\u5316\u70ba\u73fe\u5be6\u6210\u5c31\u3002",
                    })

    # Mystic Rectangle
    for a, b, c, d in combinations(planets, 4):
        if (
            _opposition(a, b) and _opposition(c, d)
            and _sextile(a, c) and _sextile(b, d)
            and _trine(a, d) and _trine(b, c)
        ):
            _add({
                "pattern": "Mystic Rectangle",
                "pattern_cn": "\u795e\u79d8\u9577\u65b9\u5f62",
                "planets": [a, b, c, d],
                "element": "", "element_cn": "",
                "quality": "", "quality_cn": "", "apex": "",
                "description": "A Mystic Rectangle -- harmonious flow of opposing energies, creativity and practical ability balanced.",
                "description_cn": "\u795e\u79d8\u9577\u65b9\u5f62 -- \u5c0d\u7acb\u80fd\u91cf\u7684\u548c\u8ae7\u6d41\u52d5\uff0c\u5275\u9020\u529b\u8207\u5be6\u8e10\u529b\u5e73\u8861\u3002",
            })

    # Grand Sextile: 6 planets at 60-degree intervals forming 3 oppositions
    if n >= 6:
        for combo in combinations(planets, 6):
            pts = list(combo)
            lons = sorted(positions[p] for p in pts)
            diffs = []
            for x in range(6):
                d = _normalize(lons[(x + 1) % 6] - lons[x])
                if d > 180:
                    d = 360 - d
                diffs.append(d)
            if not all(abs(d - 60) <= sextile_orb for d in diffs):
                continue
            if not (
                _is_aspect(lons[0], lons[3], 180, opposition_orb)
                and _is_aspect(lons[1], lons[4], 180, opposition_orb)
                and _is_aspect(lons[2], lons[5], 180, opposition_orb)
            ):
                continue
            elem = _dominant_element(pts, positions)
            elem_cn = ELEMENT_CN.get(elem, "")
            _add({
                "pattern": "Grand Sextile",
                "pattern_cn": "\u5927\u516d\u8292\u661f",
                "planets": pts,
                "element": elem, "element_cn": elem_cn,
                "quality": "", "quality_cn": "", "apex": "",
                "description": "A Grand Sextile (Star of David) -- a rare, highly harmonious configuration of great gifts and creative potential.",
                "description_cn": "\u5927\u516d\u8292\u661f\uff08\u5927\u885b\u4e4b\u661f\uff09 -- \u6975\u70ba\u7f55\u898b\u7684\u548c\u8ae7\u683c\u5c40\uff0c\u8c61\u5fb5\u8c50\u76db\u5929\u8ce6\u3002",
            })

    # Boomerang: Yod + opposition to apex
    for a, b in combinations(planets, 2):
        if not _sextile(a, b):
            continue
        for c in planets:
            if c == a or c == b:
                continue
            if not (_quincunx(a, c) and _quincunx(b, c)):
                continue
            for d in planets:
                if d in (a, b, c):
                    continue
                if _opposition(c, d):
                    _add({
                        "pattern": "Boomerang",
                        "pattern_cn": "\u56de\u529b\u93d6",
                        "planets": [a, b, c, d],
                        "element": "", "element_cn": "",
                        "quality": "", "quality_cn": "", "apex": c,
                        "description": "A Boomerang with apex " + c + " and reaction point " + d + " -- karmic Yod energy reflected through opposition.",
                        "description_cn": "\u56de\u529b\u93d6\uff0c\u9802\u9ede " + c + "\uff0c\u53cd\u5c04\u9ede " + d + " -- \u547d\u904b\u6307\u696d\u529b\u80fd\u91cf\u9001\u904e\u5c0d\u5206\u76f8\u53cd\u5c04\u3002",
                    })

    # Stellium: 3+ planets in same sign
    sign_groups = {}
    for p in planets:
        lon = positions.get(p)
        if lon is None:
            continue
        sign = _sign_of(lon)
        sign_groups.setdefault(sign, []).append(p)

    for sign, members in sign_groups.items():
        if len(members) >= 3:
            elem = ZODIAC_ELEMENTS.get(sign, "")
            qual = ZODIAC_QUALITIES.get(sign, "")
            _add({
                "pattern": "Stellium",
                "pattern_cn": "\u661f\u7fa4",
                "planets": members,
                "element": elem, "element_cn": ELEMENT_CN.get(elem, ""),
                "quality": qual, "quality_cn": QUALITY_CN.get(qual, ""),
                "apex": "",
                "description": "A Stellium in " + sign + " -- intense concentration of energy in " + sign + " themes.",
                "description_cn": sign + "\u661f\u5ea7\u661f\u7fa4 -- \u80fd\u91cf\u9ad8\u5ea6\u96c6\u4e2d\u65bc" + sign + "\u7684\u4e3b\u984c\uff0c\u662f\u4eba\u751f\u7684\u6838\u5fc3\u7126\u9ede\u3002",
            })

    return patterns


def build_aspect_pattern_figure(positions, patterns, title="Aspect Patterns"):
    """Build a Plotly polar figure showing planet positions and pattern lines."""
    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[1.0] * 361,
        theta=list(range(361)),
        mode="lines",
        line=dict(color="rgba(150,150,150,0.3)", width=1),
        showlegend=False,
        hoverinfo="skip",
    ))

    _PLANET_COLORS_LOCAL = {
        "Sun": "#FF8C00", "Moon": "#C0C0C0", "Mercury": "#4169E1",
        "Venus": "#FF69B4", "Mars": "#DC143C", "Jupiter": "#228B22",
        "Saturn": "#8B4513", "Uranus": "#00CED1", "Neptune": "#7B68EE",
        "Pluto": "#800080", "North": "#888888",
    }

    def _p_color(name):
        for k, v in _PLANET_COLORS_LOCAL.items():
            if k in name:
                return v
        return "#c8c8c8"

    pattern_in_legend = set()
    drawn_pairs = set()
    for pat in patterns:
        color = _PATTERN_COLORS.get(pat["pattern"], "#ffffff")
        p_names = pat["planets"]
        for idx_a in range(len(p_names)):
            for idx_b in range(idx_a + 1, len(p_names)):
                na, nb = p_names[idx_a], p_names[idx_b]
                if na not in positions or nb not in positions:
                    continue
                pair_key = frozenset({na, nb, pat["pattern"]})
                if pair_key in drawn_pairs:
                    continue
                drawn_pairs.add(pair_key)
                la, lb = positions[na], positions[nb]
                show_legend = (
                    pat["pattern"] not in pattern_in_legend
                    and idx_a == 0
                    and idx_b == 1
                )
                if show_legend:
                    pattern_in_legend.add(pat["pattern"])
                fig.add_trace(go.Scatterpolar(
                    r=[1.0, 1.0],
                    theta=[la, lb],
                    mode="lines",
                    line=dict(color=color, width=2),
                    name=pat["pattern"],
                    legendgroup=pat["pattern"],
                    showlegend=show_legend,
                    hoverinfo="name",
                ))

    for name, lon in positions.items():
        short = name.split(" ")[0]
        color = _p_color(name)
        fig.add_trace(go.Scatterpolar(
            r=[1.05],
            theta=[lon],
            mode="markers+text",
            marker=dict(size=10, color=color),
            text=[short],
            textposition="top center",
            textfont=dict(size=9, color=color),
            name=name,
            showlegend=False,
            hovertemplate=name + "<br>" + str(round(lon, 2)) + "deg<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=14)),
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.3]),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickmode="array",
                tickvals=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
                ticktext=["\u2648", "\u2649", "\u264a", "\u264b", "\u264c", "\u264d",
                          "\u264e", "\u264f", "\u2650", "\u2651", "\u2652", "\u2653"],
                tickfont=dict(size=14),
                showgrid=True,
                gridcolor="rgba(100,100,100,0.2)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=11)),
        height=500,
        margin=dict(l=20, r=20, t=50, b=60),
    )

    return fig


def render_aspect_patterns(patterns, positions, lang="zh"):
    """Render detected aspect patterns in Streamlit with Plotly chart."""
    import streamlit as st

    is_zh = lang in ("zh", "zh_cn")
    header = "\u7684\u76f8\u4f4d\u5716\u6848 / Aspect Patterns"
    st.subheader(header)

    if not patterns:
        msg = "\u672a\u5075\u6e2c\u5230\u7279\u6b8a\u76f8\u4f4d\u5716\u6848\u3002" if is_zh else "No significant aspect patterns detected."
        st.info(msg)
        return

    rows = []
    for pat in patterns:
        rows.append({
            ("\u5716\u6848" if is_zh else "Pattern"): (
                pat["pattern_cn"] + " (" + pat["pattern"] + ")" if is_zh else pat["pattern"]
            ),
            ("\u884c\u661f" if is_zh else "Planets"): ", ".join(pat["planets"]),
            ("\u9802\u9ede" if is_zh else "Apex"): pat.get("apex") or "\u2014",
            ("\u5143\u7d20" if is_zh else "Element"): (
                pat.get("element_cn", "") + " (" + pat.get("element", "") + ")"
                if pat.get("element") else "\u2014"
            ),
            ("\u54c1\u8cea" if is_zh else "Quality"): (
                pat.get("quality_cn", "") + " (" + pat.get("quality", "") + ")"
                if pat.get("quality") else "\u2014"
            ),
        })
    st.dataframe(rows, width="stretch")

    title = "\u76f8\u4f4d\u5716\u6848\u8f2a\u76e4" if is_zh else "Aspect Pattern Wheel"
    fig = build_aspect_pattern_figure(positions, patterns, title=title)
    st.plotly_chart(fig, use_container_width=True)

    for pat in patterns:
        pname = pat["pattern_cn"] + " (" + pat["pattern"] + ")" if is_zh else pat["pattern"]
        desc = pat.get("description_cn", "") if is_zh else pat.get("description", "")
        color = _PATTERN_COLORS.get(pat["pattern"], "#888")
        planets_str = ", ".join(pat["planets"])
        apex = pat.get("apex", "")
        apex_str = (" \u2014 \u9802\u9ede: " + apex if is_zh else " -- Apex: " + apex) if apex else ""
        st.markdown(
            '<div style="border-left: 4px solid ' + color + '; padding: 8px 12px; '
            'margin: 6px 0; background: rgba(0,0,0,0.2); border-radius: 4px;">'
            '<b style="color:' + color + '">' + pname + '</b>' + apex_str + '<br>'
            '<span style="color:#aaa;font-size:0.9em">' + planets_str + '</span><br>'
            '<span style="font-size:0.9em">' + desc + '</span>'
            '</div>',
            unsafe_allow_html=True,
        )


def format_patterns_for_prompt(patterns):
    """Format detected patterns as a text block for AI prompts."""
    if not patterns:
        return "No significant aspect patterns detected."
    lines = ["[Aspect Patterns]"]
    for pat in patterns:
        planets_str = ", ".join(pat["planets"])
        apex = ("  Apex: " + pat["apex"]) if pat.get("apex") else ""
        qual = ("  Quality: " + pat["quality"]) if pat.get("quality") else ""
        elem = ("  Element: " + pat["element"]) if pat.get("element") else ""
        lines.append("- " + pat["pattern"] + " (" + pat["pattern_cn"] + "): " + planets_str + apex + elem + qual)
        lines.append("  -> " + pat.get("description", ""))
    return "\n".join(lines)
