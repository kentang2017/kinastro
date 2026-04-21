"""
astro/western/aspect_patterns.py — Aspect Pattern Detection

Detects classic Western astrology aspect patterns from a set of
planet positions.  Supported patterns:

  - Grand Trine (大三角)
  - T-Square (T形相位 / T-方格)
  - Grand Cross (大十字)
  - Yod / Finger of God (命運指 / 上帝之指)
  - Kite (風箏)
  - Mystic Rectangle (神秘長方形)
  - Grand Sextile (大六芒星)
  - Stellium (星群)
  - Boomerang (回力鏢)

Each detected pattern is returned as a ``dict`` with at least:
  - ``"pattern"``   (str) English pattern name
  - ``"pattern_cn"`` (str) Chinese pattern name
  - ``"planets"``   (list[str]) participating planet names
  - ``"element"``   (str) dominant element where applicable
  - ``"quality"``   (str) modality quality where applicable
  - ``"apex"``      (str) apex/focal planet where applicable
  - ``"description"`` (str) brief English description
  - ``"description_cn"`` (str) brief Chinese description
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────

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

ELEMENT_CN = {"Fire": "火", "Earth": "土", "Air": "風", "Water": "水"}
QUALITY_CN = {"Cardinal": "本位", "Fixed": "固定", "Mutable": "變動"}

# ─────────────────────────────────────────────────────────────────
# Angle helpers
# ─────────────────────────────────────────────────────────────────

def _normalize(deg: float) -> float:
    return deg % 360.0


def _angle_diff(a: float, b: float) -> float:
    """Smallest arc between two longitudes (0–180°)."""
    diff = abs(_normalize(a) - _normalize(b))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _is_aspect(lon_a: float, lon_b: float, target: float, orb: float) -> bool:
    return abs(_angle_diff(lon_a, lon_b) - target) <= orb


def _sign_of(longitude: float) -> str:
    idx = int(_normalize(longitude) / 30.0) % 12
    return ZODIAC_SIGNS_ORDER[idx]


def _dominant_element(planet_names: list[str], positions: dict[str, float]) -> str:
    counts: dict[str, int] = {}
    for name in planet_names:
        lon = positions.get(name)
        if lon is None:
            continue
        elem = ZODIAC_ELEMENTS.get(_sign_of(lon), "")
        if elem:
            counts[elem] = counts.get(elem, 0) + 1
    return max(counts, key=counts.get) if counts else ""


def _dominant_quality(planet_names: list[str], positions: dict[str, float]) -> str:
    counts: dict[str, int] = {}
    for name in planet_names:
        lon = positions.get(name)
        if lon is None:
            continue
        qual = ZODIAC_QUALITIES.get(_sign_of(lon), "")
        if qual:
            counts[qual] = counts.get(qual, 0) + 1
    return max(counts, key=counts.get) if counts else ""


# ─────────────────────────────────────────────────────────────────
# Main detection function
# ─────────────────────────────────────────────────────────────────

def detect_aspect_patterns(
    positions: dict[str, float],
    orb: float = 8.0,
) -> list[dict]:
    """Detect classic aspect patterns from a dict of planet longitudes.

    Parameters
    ----------
    positions : dict[str, float]
        Mapping of planet name → ecliptic longitude (0–360°).
    orb : float
        Default orb in degrees for major aspects.  Minor-aspect orbs are
        derived proportionally.

    Returns
    -------
    list[dict]
        Each dict describes one detected pattern.
    """
    planets = list(positions.keys())
    n = len(planets)
    patterns: list[dict] = []
    seen_sets: set[frozenset] = set()  # deduplicate

    trine_orb = orb
    square_orb = orb
    sextile_orb = max(3.0, orb * 0.5)
    quincunx_orb = max(3.0, orb * 0.5)
    opposition_orb = orb

    def _add(record: dict) -> None:
        key = frozenset(record["planets"])
        # Allow the same planet-set to appear for different pattern types
        pat_key = (record["pattern"], key)
        if pat_key not in seen_sets:
            seen_sets.add(pat_key)
            patterns.append(record)

    def _trine(a, b): return _is_aspect(positions[a], positions[b], 120, trine_orb)
    def _square(a, b): return _is_aspect(positions[a], positions[b], 90, square_orb)
    def _sextile(a, b): return _is_aspect(positions[a], positions[b], 60, sextile_orb)
    def _quincunx(a, b): return _is_aspect(positions[a], positions[b], 150, quincunx_orb)
    def _opposition(a, b): return _is_aspect(positions[a], positions[b], 180, opposition_orb)
    def _conjunction(a, b): return _is_aspect(positions[a], positions[b], 0, orb)

    # ── Grand Trine ────────────────────────────────────────────
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                a, b, c = planets[i], planets[j], planets[k]
                if _trine(a, b) and _trine(b, c) and _trine(a, c):
                    elem = _dominant_element([a, b, c], positions)
                    _add({
                        "pattern": "Grand Trine",
                        "pattern_cn": "大三角",
                        "planets": [a, b, c],
                        "element": elem,
                        "element_cn": ELEMENT_CN.get(elem, ""),
                        "quality": "",
                        "quality_cn": "",
                        "apex": "",
                        "description": (
                            f"A Grand Trine in {elem} element — natural talent and ease, "
                            "but may lack motivation without challenge."
                        ),
                        "description_cn": (
                            f"大三角（{ELEMENT_CN.get(elem, '')}象）— "
                            "代表天賦才能與輕鬆流動的能量，但可能缺乏動力與挑戰。"
                        ),
                    })

    # ── T-Square ──────────────────────────────────────────────
    for i in range(n):
        for j in range(i + 1, n):
            if not _opposition(planets[i], planets[j]):
                continue
            for k in range(n):
                if k == i or k == j:
                    continue
                a, b, c = planets[i], planets[j], planets[k]
                if _square(a, c) and _square(b, c):
                    qual = _dominant_quality([a, b, c], positions)
                    _add({
                        "pattern": "T-Square",
                        "pattern_cn": "T形相位",
                        "planets": [a, b, c],
                        "element": "",
                        "element_cn": "",
                        "quality": qual,
                        "quality_cn": QUALITY_CN.get(qual, ""),
                        "apex": c,
                        "description": (
                            f"A T-Square with apex {c} in {qual} quality — "
                            "intense pressure, drive, and ambition concentrated at the apex."
                        ),
                        "description_cn": (
                            f"T形相位，頂點為 {c}（{QUALITY_CN.get(qual, '')}星座）— "
                            "強大的張力與驅動力集中在頂點行星，需要主動化解。"
                        ),
                    })

    # ── Grand Cross ───────────────────────────────────────────
    for i in range(n):
        for j in range(i + 1, n):
            if not _opposition(planets[i], planets[j]):
                continue
            for k in range(j + 1, n):
                if k == i:
                    continue
                for l in range(k + 1, n):
                    if l == i or l == j:
                        continue
                    a, b, c, d = planets[i], planets[j], planets[k], planets[l]
                    if (
                        _opposition(c, d)
                        and _square(a, c) and _square(a, d)
                        and _square(b, c) and _square(b, d)
                    ):
                        qual = _dominant_quality([a, b, c, d], positions)
                        _add({
                            "pattern": "Grand Cross",
                            "pattern_cn": "大十字",
                            "planets": [a, b, c, d],
                            "element": "",
                            "element_cn": "",
                            "quality": qual,
                            "quality_cn": QUALITY_CN.get(qual, ""),
                            "apex": "",
                            "description": (
                                f"A Grand Cross in {qual} quality — "
                                "extreme tension from four directions; powerful but demanding."
                            ),
                            "description_cn": (
                                f"大十字（{QUALITY_CN.get(qual, '')}星座）— "
                                "四面壓力，極大的緊張能量，需要強大意志力才能整合。"
                            ),
                        })

    # ── Yod (Finger of God) ───────────────────────────────────
    for i in range(n):
        for j in range(i + 1, n):
            if not _sextile(planets[i], planets[j]):
                continue
            for k in range(n):
                if k == i or k == j:
                    continue
                a, b, c = planets[i], planets[j], planets[k]
                if _quincunx(a, c) and _quincunx(b, c):
                    _add({
                        "pattern": "Yod",
                        "pattern_cn": "命運指（上帝之指）",
                        "planets": [a, b, c],
                        "element": "",
                        "element_cn": "",
                        "quality": "",
                        "quality_cn": "",
                        "apex": c,
                        "description": (
                            f"A Yod pointing to {c} — a karmic configuration suggesting "
                            "a special destiny or spiritual mission requiring adjustment."
                        ),
                        "description_cn": (
                            f"命運指，指向 {c} — 業力格局，暗示特殊使命或靈性方向，"
                            "需要持續調整與適應。"
                        ),
                    })

    # ── Kite ──────────────────────────────────────────────────
    # Grand Trine + one planet opposing one of the three and sextile the other two
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                a, b, c = planets[i], planets[j], planets[k]
                if not (_trine(a, b) and _trine(b, c) and _trine(a, c)):
                    continue
                # look for a fourth planet opposing one vertex and sextile the other two
                for l in range(n):
                    if l in (i, j, k):
                        continue
                    d = planets[l]
                    for apex in (a, b, c):
                        others = [p for p in (a, b, c) if p != apex]
                        if (
                            _opposition(d, apex)
                            and _sextile(d, others[0])
                            and _sextile(d, others[1])
                        ):
                            elem = _dominant_element([a, b, c], positions)
                            _add({
                                "pattern": "Kite",
                                "pattern_cn": "風箏",
                                "planets": [a, b, c, d],
                                "element": elem,
                                "element_cn": ELEMENT_CN.get(elem, ""),
                                "quality": "",
                                "quality_cn": "",
                                "apex": d,
                                "description": (
                                    f"A Kite with focal planet {d} — Grand Trine energy "
                                    "directed through the focal point into practical achievement."
                                ),
                                "description_cn": (
                                    f"風箏，焦點行星為 {d} — 大三角的能量透過焦點行星"
                                    "轉化為現實成就，是較為幸運的格局。"
                                ),
                            })

    # ── Mystic Rectangle ──────────────────────────────────────
    # 4 planets: 2 oppositions + 4 sextiles (or trines crossing)
    for i in range(n):
        for j in range(i + 1, n):
            if not _opposition(planets[i], planets[j]):
                continue
            for k in range(j + 1, n):
                if k in (i, j):
                    continue
                for l in range(k + 1, n):
                    if l in (i, j, k):
                        continue
                    a, b, c, d = planets[i], planets[j], planets[k], planets[l]
                    if (
                        _opposition(c, d)
                        and _sextile(a, c) and _sextile(a, d)
                        and _sextile(b, c) and _sextile(b, d)
                    ):
                        _add({
                            "pattern": "Mystic Rectangle",
                            "pattern_cn": "神秘長方形",
                            "planets": [a, b, c, d],
                            "element": "",
                            "element_cn": "",
                            "quality": "",
                            "quality_cn": "",
                            "apex": "",
                            "description": (
                                "A Mystic Rectangle — harmonious flow of opposing energies, "
                                "creativity and practical ability balanced."
                            ),
                            "description_cn": (
                                "神秘長方形 — 對立能量的和諧流動，"
                                "創造力與實踐能力相互平衡，是較為祥和的格局。"
                            ),
                        })

    # ── Grand Sextile (Star of David) ─────────────────────────
    # 6 planets each 60° apart (or 3 oppositions + 6 sextiles)
    if n >= 6:
        for combo in _combinations(range(n), 6):
            pts = [planets[idx] for idx in combo]
            lons = sorted(positions[p] for p in pts)
            # Check all pairs are either 60° or 120° apart
            all_sextile_or_trine = True
            for x in range(6):
                for y in range(x + 1, 6):
                    diff = _angle_diff(lons[x], lons[y])
                    if not (
                        abs(diff - 60) <= sextile_orb
                        or abs(diff - 120) <= trine_orb
                        or abs(diff - 180) <= opposition_orb
                    ):
                        all_sextile_or_trine = False
                        break
                if not all_sextile_or_trine:
                    break
            # Also require roughly equal 60° spacing
            diffs = []
            for x in range(6):
                d = _normalize(lons[(x + 1) % 6] - lons[x])
                if d > 180:
                    d = 360 - d
                diffs.append(d)
            spacing_ok = all(abs(d - 60) <= sextile_orb for d in diffs)
            if all_sextile_or_trine and spacing_ok:
                elem = _dominant_element(pts, positions)
                _add({
                    "pattern": "Grand Sextile",
                    "pattern_cn": "大六芒星",
                    "planets": pts,
                    "element": elem,
                    "element_cn": ELEMENT_CN.get(elem, ""),
                    "quality": "",
                    "quality_cn": "",
                    "apex": "",
                    "description": (
                        "A Grand Sextile (Star of David) — a rare, highly harmonious "
                        "configuration of great gifts and creative potential."
                    ),
                    "description_cn": (
                        "大六芒星（大衛之星）— 極為罕見的和諧格局，"
                        "象徵豐盛天賦與強大創造潛力。"
                    ),
                })

    # ── Boomerang (Yod + opposition to apex) ──────────────────
    for i in range(n):
        for j in range(i + 1, n):
            if not _sextile(planets[i], planets[j]):
                continue
            for k in range(n):
                if k == i or k == j:
                    continue
                a, b, c = planets[i], planets[j], planets[k]
                if not (_quincunx(a, c) and _quincunx(b, c)):
                    continue
                for l in range(n):
                    if l in (i, j, k):
                        continue
                    d = planets[l]
                    if _opposition(c, d):
                        _add({
                            "pattern": "Boomerang",
                            "pattern_cn": "回力鏢",
                            "planets": [a, b, c, d],
                            "element": "",
                            "element_cn": "",
                            "quality": "",
                            "quality_cn": "",
                            "apex": c,
                            "description": (
                                f"A Boomerang with apex {c} and reaction point {d} — "
                                "karmic Yod energy reflected back through opposition."
                            ),
                            "description_cn": (
                                f"回力鏢，頂點 {c}，反射點 {d} — "
                                "命運指的業力能量透過對分相反射，帶來強烈的轉化壓力。"
                            ),
                        })

    # ── Stellium (3+ planets in same sign or consecutive signs) ─
    sign_groups: dict[str, list[str]] = {}
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
                "pattern_cn": "星群",
                "planets": members,
                "element": elem,
                "element_cn": ELEMENT_CN.get(elem, ""),
                "quality": qual,
                "quality_cn": QUALITY_CN.get(qual, ""),
                "apex": "",
                "description": (
                    f"A Stellium in {sign} — intense concentration of energy and focus "
                    f"in {sign} themes; dominant life area."
                ),
                "description_cn": (
                    f"{sign}星座星群 — 能量高度集中於{sign}的主題，"
                    "是人生的核心焦點，既是天賦也是執念。"
                ),
            })

    return patterns


def _combinations(iterable, r):
    """Minimal itertools.combinations replacement (avoids import overhead)."""
    pool = list(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)


# ─────────────────────────────────────────────────────────────────
# Plotly visualization helper
# ─────────────────────────────────────────────────────────────────

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


def build_aspect_pattern_figure(
    positions: dict[str, float],
    patterns: list[dict],
    *,
    title: str = "Aspect Patterns",
) -> "plotly.graph_objects.Figure":  # type: ignore[name-defined]
    """Build a Plotly polar figure showing planet positions and pattern lines.

    Parameters
    ----------
    positions : dict[str, float]
        Planet name → ecliptic longitude (0–360°).
    patterns : list[dict]
        Output of :func:`detect_aspect_patterns`.
    title : str
        Figure title.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    import math
    import plotly.graph_objects as go

    # Convert longitude to x,y on unit circle
    # 0° Aries at top (90° from standard), going counter-clockwise
    def _xy(lon: float):
        angle_rad = math.radians(90.0 - lon)
        return math.cos(angle_rad), math.sin(angle_rad)

    fig = go.Figure()

    # Draw zodiac circle background
    theta = list(range(0, 361))
    fig.add_trace(go.Scatterpolar(
        r=[1.0] * len(theta),
        theta=theta,
        mode="lines",
        line=dict(color="rgba(150,150,150,0.3)", width=1),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Planet color map (simple fallback)
    _PLANET_COLORS = {
        "Sun": "#FF8C00", "Moon": "#C0C0C0", "Mercury": "#4169E1",
        "Venus": "#FF69B4", "Mars": "#DC143C", "Jupiter": "#228B22",
        "Saturn": "#8B4513", "Uranus": "#00CED1", "Neptune": "#7B68EE",
        "Pluto": "#800080", "North Node": "#888888",
    }

    def _p_color(name: str) -> str:
        for k, v in _PLANET_COLORS.items():
            if k in name:
                return v
        return "#c8c8c8"

    # Draw pattern lines
    already_drawn: set[tuple] = set()
    for pat in patterns:
        color = _PATTERN_COLORS.get(pat["pattern"], "#ffffff")
        p_names = pat["planets"]
        for idx_a in range(len(p_names)):
            for idx_b in range(idx_a + 1, len(p_names)):
                na, nb = p_names[idx_a], p_names[idx_b]
                if na not in positions or nb not in positions:
                    continue
                pair_key = (min(na, nb), max(na, nb))
                if pair_key in already_drawn:
                    continue
                already_drawn.add(pair_key)
                la, lb = positions[na], positions[nb]
                fig.add_trace(go.Scatterpolar(
                    r=[1.0, 1.0],
                    theta=[la, lb],
                    mode="lines",
                    line=dict(color=color, width=2, dash="solid"),
                    name=pat["pattern"],
                    legendgroup=pat["pattern"],
                    showlegend=pair_key == (min(p_names[0], p_names[1]), max(p_names[0], p_names[1])),
                    hoverinfo="name",
                ))

    # Draw planet markers
    for name, lon in positions.items():
        short = name.split(" ")[0]
        color = _p_color(name)
        fig.add_trace(go.Scatterpolar(
            r=[1.05],
            theta=[lon],
            mode="markers+text",
            marker=dict(size=10, color=color, symbol="circle"),
            text=[short],
            textposition="top center",
            textfont=dict(size=9, color=color),
            name=name,
            showlegend=False,
            hovertemplate=f"{name}<br>{lon:.2f}°<extra></extra>",
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
                ticktext=["♈", "♉", "♊", "♋", "♌", "♍",
                          "♎", "♏", "♐", "♑", "♒", "♓"],
                tickfont=dict(size=14),
                showgrid=True,
                gridcolor="rgba(100,100,100,0.2)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        height=500,
        margin=dict(l=20, r=20, t=50, b=60),
    )

    return fig


def render_aspect_patterns(patterns: list[dict], positions: dict[str, float], lang: str = "zh") -> None:
    """Render detected aspect patterns in Streamlit with Plotly chart.

    Parameters
    ----------
    patterns : list[dict]
        Output of :func:`detect_aspect_patterns`.
    positions : dict[str, float]
        Planet name → longitude (for Plotly visualization).
    lang : str
        ``"zh"`` or ``"en"``.
    """
    import streamlit as st

    is_zh = lang in ("zh", "zh_cn")
    header = "🔷 相位圖案 / Aspect Patterns"
    st.subheader(header)

    if not patterns:
        msg = "未偵測到特殊相位圖案。" if is_zh else "No significant aspect patterns detected."
        st.info(msg)
        return

    # Summary table
    rows = []
    for pat in patterns:
        rows.append({
            ("圖案" if is_zh else "Pattern"): (
                f"{pat['pattern_cn']} ({pat['pattern']})" if is_zh else pat["pattern"]
            ),
            ("行星" if is_zh else "Planets"): ", ".join(pat["planets"]),
            ("頂點" if is_zh else "Apex"): pat.get("apex") or "—",
            ("元素" if is_zh else "Element"): (
                f"{pat.get('element_cn', '')} ({pat.get('element', '')})"
                if pat.get("element") else "—"
            ),
            ("品質" if is_zh else "Quality"): (
                f"{pat.get('quality_cn', '')} ({pat.get('quality', '')})"
                if pat.get("quality") else "—"
            ),
        })
    st.dataframe(rows, width="stretch")

    # Plotly wheel
    title = "相位圖案輪盤" if is_zh else "Aspect Pattern Wheel"
    fig = build_aspect_pattern_figure(positions, patterns, title=title)
    st.plotly_chart(fig, use_container_width=True)

    # Pattern detail cards
    for pat in patterns:
        pname = f"{pat['pattern_cn']} ({pat['pattern']})" if is_zh else pat["pattern"]
        desc = pat.get("description_cn", "") if is_zh else pat.get("description", "")
        color = _PATTERN_COLORS.get(pat["pattern"], "#888")
        planets_str = ", ".join(pat["planets"])
        apex_str = f" — 頂點: {pat['apex']}" if is_zh and pat.get("apex") else (
            f" — Apex: {pat['apex']}" if pat.get("apex") else ""
        )
        st.markdown(
            f'<div style="border-left: 4px solid {color}; padding: 8px 12px; '
            f'margin: 6px 0; background: rgba(0,0,0,0.2); border-radius: 4px;">'
            f'<b style="color:{color}">{pname}</b>{apex_str}<br>'
            f'<span style="color:#aaa;font-size:0.9em">{planets_str}</span><br>'
            f'<span style="font-size:0.9em">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def format_patterns_for_prompt(patterns: list[dict]) -> str:
    """Format detected patterns as a text block for AI prompts."""
    if not patterns:
        return "No significant aspect patterns detected."
    lines = ["【相位圖案 Aspect Patterns】"]
    for pat in patterns:
        planets_str = ", ".join(pat["planets"])
        apex = f"  Apex: {pat['apex']}" if pat.get("apex") else ""
        qual = f"  Quality: {pat['quality']}" if pat.get("quality") else ""
        elem = f"  Element: {pat['element']}" if pat.get("element") else ""
        lines.append(
            f"- {pat['pattern']} ({pat['pattern_cn']}): {planets_str}{apex}{elem}{qual}"
        )
        lines.append(f"  → {pat['description']}")
    return "\n".join(lines)
