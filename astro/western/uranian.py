"""
astro/western/uranian.py — 漢堡學派天王星派占星
Uranian Astrology — Alfred Witte Hamburg School (1920–1941)

Implements:
  • 8 Transneptunian Planets (TNPs) via fixed longitudes (updated annually)
  • 90° Dial (modular reduction)
  • Midpoint Tree (all pairs, sorted by orb tightness)
  • Planetary Pictures  A + B − C = D  (Witte's Regelwerk law)
  • Family / relationship cross-chart symmetry (optional)

Mathematical conventions:
  - All longitudes are absolute (0°–360°, 0° = Aries).
  - 90° Dial position = longitude mod 90°.
  - Midpoint M(A,B) = ((A + B) / 2) mod 360°, and its antiscion = (M + 180°) mod 360°.
  - Hard aspects on the 90° dial: 0°, 45°, 90°, 135°, 180° all collapse to the same
    cluster position, so only |dial_A − dial_B| ≤ orb (mod 90°) matters.
  - Planetary Picture:  A + B − C = D  →  |dial(A+B−C) − dial(D)| ≤ orb.
"""

from __future__ import annotations

import math
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================================================
# Transneptunian Planet (TNP) Mean Longitudes
# Using Witte / Sieggrün mean motions; epoch J2000.0 (JD 2451545.0)
# Rates in degrees per Julian year (365.25 days)
# ============================================================

# Approximate tropical positions at J2000.0 (2000 Jan 1.5 TT)
# Sourced from Hamburg School ephemeris tables.
TNP_EPOCH2000: Dict[str, float] = {
    "Cupido":   211.2,   # ~1° Scorpio
    "Hades":    178.0,   # ~28° Virgo
    "Zeus":     289.5,   # ~19° Capricorn
    "Kronos":   271.4,   # ~1° Capricorn
    "Apollon":  183.3,   # ~3° Virgo
    "Admetos":  273.0,   # ~3° Capricorn
    "Vulkanus": 65.2,    # ~5° Gemini
    "Poseidon": 183.6,   # ~3° Virgo
}

# Annual motion in degrees/year (Witte's original values)
TNP_RATE: Dict[str, float] = {
    "Cupido":   1.389,
    "Hades":    1.000,
    "Zeus":     1.528,
    "Kronos":   1.667,
    "Apollon":  1.528,
    "Admetos":  1.111,
    "Vulkanus": 1.750,
    "Poseidon": 1.528,
}

J2000 = 2451545.0  # Julian Day for J2000.0

TNP_SYMBOLS: Dict[str, str] = {
    "Cupido":   "♡",
    "Hades":    "☠",
    "Zeus":     "⚡",
    "Kronos":   "♚",
    "Apollon":  "✦",
    "Admetos":  "⊕",
    "Vulkanus": "🌋",
    "Poseidon": "🌊",
}

TNP_MEANINGS: Dict[str, Dict[str, str]] = {
    "Cupido": {
        "en": "Family, community, marriage, art, social bonds, collective",
        "zh": "家庭、社區、婚姻、藝術、社會紐帶",
    },
    "Hades": {
        "en": "Decay, past, karma, hidden matters, disease, depth, ancient",
        "zh": "衰敗、過去、業力、隱藏事務、疾病、古老",
    },
    "Zeus": {
        "en": "Creative power, leadership, goal, directed energy, fire, ignition",
        "zh": "創造力、領導、目標、定向能量、火力、點燃",
    },
    "Kronos": {
        "en": "Authority, elevation, mastery, highest standard, government, law",
        "zh": "權威、提升、精通、最高標準、政府、法律",
    },
    "Apollon": {
        "en": "Breadth, success, multiplicity, far-reaching, expansion, commerce",
        "zh": "廣度、成功、多元、遠大、擴展、商業",
    },
    "Admetos": {
        "en": "Endurance, obstruction, depth, raw matter, standstill, transformation",
        "zh": "持久、阻塞、深度、原材料、停滯、轉化",
    },
    "Vulkanus": {
        "en": "Force, explosion, control, eruptive power, enormous energy",
        "zh": "力量、爆發、控制、噴發力、巨大能量",
    },
    "Poseidon": {
        "en": "Spirit, enlightenment, wisdom, higher thought, truth, idealism",
        "zh": "靈性、啟蒙、智慧、高層思想、真理、理想主義",
    },
}

# Standard natal planets
NATAL_PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

PLANET_SYMBOLS: Dict[str, str] = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Asc": "AC",
    "MC": "MC",
    "Node": "☊",
}

# Personal points — highest weight
PERSONAL_POINTS = {"Sun", "Moon", "Asc", "MC", "Node"}


# ============================================================
# Data classes
# ============================================================

@dataclass
class PlanetPosition:
    name: str
    symbol: str
    longitude: float          # absolute, 0–360°
    dial90: float             # longitude mod 90°
    sign: str
    sign_degree: float
    is_personal: bool = False
    is_tnp: bool = False


@dataclass
class Midpoint:
    planet_a: str
    planet_b: str
    longitude: float          # midpoint absolute longitude
    dial90: float             # midpoint mod 90°
    orb_to_target: float = 0.0
    target: str = ""


@dataclass
class MidpointTreeEntry:
    focal_point: str          # e.g. "Sun/Moon"
    focal_lon: float          # absolute midpoint longitude
    focal_dial: float         # dial position
    conjunctions: List[Tuple[str, float, float]] = field(default_factory=list)
    # (planet_name, absolute_lon, orb_degrees)


@dataclass
class PlanetaryPicture:
    formula: str              # "A + B − C = D"
    planet_a: str
    planet_b: str
    planet_c: str
    planet_d: str
    computed_lon: float       # A + B − C (mod 360°)
    target_lon: float         # D actual longitude
    orb: float                # |computed − target| on 90° dial
    involves_personal: bool
    involves_tnp: bool
    meaning_en: str
    meaning_zh: str


@dataclass
class UranianChart:
    positions: List[PlanetPosition] = field(default_factory=list)
    midpoint_tree: List[MidpointTreeEntry] = field(default_factory=list)
    planetary_pictures: List[PlanetaryPicture] = field(default_factory=list)
    dial90_clusters: List[Tuple[float, List[str]]] = field(default_factory=list)
    # (dial_position, [planet names within orb])

    def get_position(self, name: str) -> Optional[PlanetPosition]:
        for p in self.positions:
            if p.name == name:
                return p
        return None


# ============================================================
# Helper functions
# ============================================================

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_CN = {
    "Aries": "白羊", "Taurus": "金牛", "Gemini": "雙子", "Cancer": "巨蟹",
    "Leo": "獅子", "Virgo": "處女", "Libra": "天秤", "Scorpio": "天蠍",
    "Sagittarius": "射手", "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "雙魚",
}


def _normalize(deg: float) -> float:
    return deg % 360.0


def _dial90(lon: float) -> float:
    return lon % 90.0


def _dial_diff(a: float, b: float) -> float:
    """Minimum distance on the 90° dial (0–45°)."""
    d = abs(a - b) % 90.0
    return min(d, 90.0 - d)


def _sign_from_lon(lon: float) -> Tuple[str, float]:
    idx = int(lon / 30.0) % 12
    deg = lon % 30.0
    return ZODIAC_SIGNS[idx], deg


def _julian_day(year: int, month: int, day: int, hour: float) -> float:
    return swe.julday(year, month, day, hour)


def _compute_tnp_position(name: str, jd: float) -> float:
    """Compute TNP longitude using linear motion from J2000.0 epoch."""
    years_from_2000 = (jd - J2000) / 365.25
    lon = TNP_EPOCH2000[name] + TNP_RATE[name] * years_from_2000
    return _normalize(lon)


def _midpoint(lon_a: float, lon_b: float) -> float:
    """Calculate the shorter-arc midpoint of two longitudes."""
    diff = _normalize(lon_b - lon_a)
    if diff > 180.0:
        mp = _normalize(lon_a - (360.0 - diff) / 2.0)
    else:
        mp = _normalize(lon_a + diff / 2.0)
    return mp


def _planetary_picture_lon(lon_a: float, lon_b: float, lon_c: float) -> float:
    """Compute A + B − C modulo 360°."""
    return _normalize(lon_a + lon_b - lon_c)


def _interpret_picture(a: str, b: str, c: str, d: str) -> Tuple[str, str]:
    """Generate a brief Witte-style interpretation for a planetary picture."""
    # Check for TNP involvement and personal point involvement
    tnps = set(TNP_MEANINGS.keys())
    all_four = {a, b, c, d}

    meanings_en, meanings_zh = [], []

    # Collect TNP meanings
    for planet in all_four & tnps:
        meanings_en.append(TNP_MEANINGS[planet]["en"].split(",")[0])
        meanings_zh.append(TNP_MEANINGS[planet]["zh"].split("、")[0])

    # Add personal point context
    personal = all_four & PERSONAL_POINTS
    if "Sun" in personal:
        meanings_en.insert(0, "Vitality/ego")
        meanings_zh.insert(0, "生命力/自我")
    if "Moon" in personal:
        meanings_en.insert(0, "Emotions/public")
        meanings_zh.insert(0, "情緒/公眾")
    if "MC" in personal:
        meanings_en.insert(0, "Career/status")
        meanings_zh.insert(0, "事業/地位")
    if "Asc" in personal:
        meanings_en.insert(0, "Body/environment")
        meanings_zh.insert(0, "身體/環境")
    if "Node" in personal:
        meanings_en.insert(0, "Connections/fate")
        meanings_zh.insert(0, "連結/命運")

    en = "; ".join(meanings_en[:3]) if meanings_en else "Energy confluence"
    zh = "；".join(meanings_zh[:3]) if meanings_zh else "能量匯聚"
    return en, zh


# ============================================================
# Main computation
# ============================================================

ORB_DIAL = 1.5   # degrees orb on the 90° dial (strict Witte = 1°, practical = 1.5°)
ORB_PICTURE = 1.5


def compute_uranian_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
    **_kwargs,
) -> UranianChart:
    """Compute a full Uranian (Hamburg School) chart."""

    ut_hour = hour + minute / 60.0 - timezone
    jd = _julian_day(year, month, day, ut_hour)

    # ── 1. Compute house cusps (Placidus) for Asc and MC
    houses, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]

    # ── 2. Compute natal planet positions
    positions: List[PlanetPosition] = []

    for name, pid in NATAL_PLANETS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, pid, flags)
        lon = _normalize(result[0])
        sign, sdeg = _sign_from_lon(lon)
        sym = PLANET_SYMBOLS.get(name, name[:2])
        positions.append(PlanetPosition(
            name=name, symbol=sym, longitude=lon,
            dial90=_dial90(lon),
            sign=sign, sign_degree=sdeg,
            is_personal=(name in PERSONAL_POINTS),
            is_tnp=False,
        ))

    # Ascendant
    sign, sdeg = _sign_from_lon(asc_lon)
    positions.append(PlanetPosition(
        name="Asc", symbol="AC", longitude=_normalize(asc_lon),
        dial90=_dial90(asc_lon),
        sign=sign, sign_degree=sdeg,
        is_personal=True, is_tnp=False,
    ))
    # MC
    sign, sdeg = _sign_from_lon(mc_lon)
    positions.append(PlanetPosition(
        name="MC", symbol="MC", longitude=_normalize(mc_lon),
        dial90=_dial90(mc_lon),
        sign=sign, sign_degree=sdeg,
        is_personal=True, is_tnp=False,
    ))
    # North Node
    result_node, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH)
    node_lon = _normalize(result_node[0])
    sign, sdeg = _sign_from_lon(node_lon)
    positions.append(PlanetPosition(
        name="Node", symbol="☊", longitude=node_lon,
        dial90=_dial90(node_lon),
        sign=sign, sign_degree=sdeg,
        is_personal=True, is_tnp=False,
    ))

    # ── 3. Transneptunian planets
    for tnp_name in TNP_EPOCH2000:
        tnp_lon = _compute_tnp_position(tnp_name, jd)
        sign, sdeg = _sign_from_lon(tnp_lon)
        sym = TNP_SYMBOLS.get(tnp_name, tnp_name[:2])
        positions.append(PlanetPosition(
            name=tnp_name, symbol=sym, longitude=tnp_lon,
            dial90=_dial90(tnp_lon),
            sign=sign, sign_degree=sdeg,
            is_personal=False, is_tnp=True,
        ))

    # ── 4. Build position map
    pos_map: Dict[str, float] = {p.name: p.longitude for p in positions}

    # ── 5. 90° Dial clusters
    dial_positions = [(p.name, p.dial90) for p in positions]
    dial_positions.sort(key=lambda x: x[1])

    clusters: List[Tuple[float, List[str]]] = []
    used = set()
    for i, (name_i, dial_i) in enumerate(dial_positions):
        if name_i in used:
            continue
        cluster = [name_i]
        for j, (name_j, dial_j) in enumerate(dial_positions):
            if i == j or name_j in used:
                continue
            if _dial_diff(dial_i, dial_j) <= ORB_DIAL:
                cluster.append(name_j)
                used.add(name_j)
        if len(cluster) > 1:
            avg_dial = sum(_dial90(pos_map[n]) for n in cluster) / len(cluster)
            clusters.append((avg_dial, cluster))
        used.add(name_i)

    # ── 6. Midpoint Tree
    all_names = list(pos_map.keys())
    midpoint_entries: List[MidpointTreeEntry] = []

    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)):
            na, nb = all_names[i], all_names[j]
            mp_lon = _midpoint(pos_map[na], pos_map[nb])
            mp_dial = _dial90(mp_lon)
            focal_label = f"{na}/{nb}"

            conjunctions: List[Tuple[str, float, float]] = []
            for nc in all_names:
                if nc in (na, nb):
                    continue
                orb = _dial_diff(mp_dial, _dial90(pos_map[nc]))
                if orb <= ORB_DIAL:
                    conjunctions.append((nc, pos_map[nc], orb))

            if conjunctions:
                conjunctions.sort(key=lambda x: x[2])
                midpoint_entries.append(MidpointTreeEntry(
                    focal_point=focal_label,
                    focal_lon=mp_lon,
                    focal_dial=mp_dial,
                    conjunctions=conjunctions,
                ))

    # Sort by: personal point involved first, then by tightest orb
    def _mp_priority(entry: MidpointTreeEntry) -> Tuple[int, float]:
        parts = entry.focal_point.split("/")
        has_personal = any(p in PERSONAL_POINTS for p in parts) or \
                       any(c[0] in PERSONAL_POINTS for c in entry.conjunctions)
        has_tnp = any(p in TNP_MEANINGS for p in parts) or \
                  any(c[0] in TNP_MEANINGS for c in entry.conjunctions)
        min_orb = entry.conjunctions[0][2] if entry.conjunctions else 99.0
        return (0 if has_personal else (1 if has_tnp else 2), min_orb)

    midpoint_entries.sort(key=_mp_priority)

    # ── 7. Planetary Pictures (A + B − C = D)
    pictures: List[PlanetaryPicture] = []

    # Only consider combinations where at least one personal point or TNP is involved
    important_names = [
        n for n in all_names
        if n in PERSONAL_POINTS or n in TNP_MEANINGS
    ]
    all_planet_names = all_names  # include everything as D

    # Build pictures: iterate personal/TNP as A or B, vary C and D
    seen_formulas: set = set()

    for na in important_names:
        for nb in all_names:
            if na == nb:
                continue
            computed = _planetary_picture_lon(pos_map[na], pos_map[nb], 0.0)
            # A + B − C = D: vary C from all planets
            for nc in all_names:
                if nc in (na, nb):
                    continue
                pic_lon = _planetary_picture_lon(pos_map[na], pos_map[nb], pos_map[nc])
                pic_dial = _dial90(pic_lon)

                for nd in all_planet_names:
                    if nd in (na, nb, nc):
                        continue
                    orb = _dial_diff(pic_dial, _dial90(pos_map[nd]))
                    if orb > ORB_PICTURE:
                        continue

                    # Normalize formula key to avoid A+B-C=D and B+A-C=D duplicates
                    key_parts = tuple(sorted([na, nb])) + (nc, nd)
                    if key_parts in seen_formulas:
                        continue
                    seen_formulas.add(key_parts)

                    involves_personal = any(
                        p in PERSONAL_POINTS for p in [na, nb, nc, nd]
                    )
                    involves_tnp = any(
                        p in TNP_MEANINGS for p in [na, nb, nc, nd]
                    )

                    meaning_en, meaning_zh = _interpret_picture(na, nb, nc, nd)
                    formula_str = f"{na} + {nb} − {nc} = {nd} (orb {orb:.2f}°)"

                    pictures.append(PlanetaryPicture(
                        formula=formula_str,
                        planet_a=na, planet_b=nb, planet_c=nc, planet_d=nd,
                        computed_lon=pic_lon, target_lon=pos_map[nd],
                        orb=orb,
                        involves_personal=involves_personal,
                        involves_tnp=involves_tnp,
                        meaning_en=meaning_en,
                        meaning_zh=meaning_zh,
                    ))

    # Sort: personal+TNP first, then by orb
    def _pic_priority(p: PlanetaryPicture) -> Tuple[int, int, float]:
        return (
            0 if p.involves_personal else 1,
            0 if p.involves_tnp else 1,
            p.orb,
        )

    pictures.sort(key=_pic_priority)
    # Limit to top 30 most significant
    pictures = pictures[:30]

    return UranianChart(
        positions=positions,
        midpoint_tree=midpoint_entries,
        planetary_pictures=pictures,
        dial90_clusters=clusters,
    )


# ============================================================
# Streamlit render functions
# ============================================================

def _lon_to_str(lon: float) -> str:
    sign, sdeg = _sign_from_lon(lon)
    return f"{sdeg:05.2f}° {sign} ({SIGN_CN.get(sign, sign)}) [abs {lon:.2f}°]"


def _dial90_str(dial: float) -> str:
    return f"{dial:.2f}°"


def render_uranian_chart(chart: UranianChart) -> None:
    """Render the full Uranian Astrology analysis in Streamlit."""

    st.markdown(
        "## Uranian Astrology — Alfred Witte 漢堡學派\n"
        "*Hamburg School · Regelwerk für Planetenbilder · 90° Dial*"
    )

    # ── Tab layout
    tab_dial, tab_tree, tab_pictures, tab_tnp = st.tabs([
        "🔵 90° Dial",
        "🌿 Midpoint Tree",
        "🔢 Planetary Pictures",
        "🪐 Transneptunian Planets",
    ])

    # ── TAB 1: 90° Dial summary
    with tab_dial:
        st.subheader("90° Dial — Planet Positions")
        st.caption(
            "All hard aspects (0°, 45°, 90°, 135°, 180°) collapse to conjunctions "
            "on the 90° Dial. Position = longitude mod 90°."
        )

        # Planet position table
        rows = []
        for p in sorted(chart.positions, key=lambda x: x.dial90):
            tag = ""
            if p.is_personal:
                tag = "⭐"
            elif p.is_tnp:
                tag = "🪐"
            rows.append({
                "": tag,
                "Planet / Point": f"{p.symbol} {p.name}",
                "Abs. Longitude": f"{p.longitude:.4f}°",
                "Sign": f"{p.sign} {SIGN_CN.get(p.sign, '')} {p.sign_degree:.2f}°",
                "90° Dial": f"{p.dial90:.4f}°",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

        # Dial clusters
        if chart.dial90_clusters:
            st.subheader("📍 90° Dial Clusters (within orb)")
            st.caption(f"Orb threshold: ±{ORB_DIAL}°")
            for dial_pos, members in sorted(chart.dial90_clusters, key=lambda x: x[0]):
                member_labels = []
                for m in members:
                    p = chart.get_position(m)
                    sym = p.symbol if p else m
                    member_labels.append(f"**{sym} {m}**")
                st.markdown(
                    f"• `{dial_pos:.2f}°` on dial → {', '.join(member_labels)}"
                )

        # SVG 90° dial visualization
        _svg = _build_dial_svg(chart)
        st.markdown(_svg, unsafe_allow_html=True)

    # ── TAB 2: Midpoint Tree
    with tab_tree:
        st.subheader("Midpoint Tree — Top Entries")
        st.caption(
            "Formula: M(A/B) = (A + B) / 2. "
            "Listed entries have at least one planet within orb on the 90° Dial."
        )
        if not chart.midpoint_tree:
            st.info("No midpoints within orb found.")
        else:
            _top_n = min(15, len(chart.midpoint_tree))
            for entry in chart.midpoint_tree[:_top_n]:
                parts = entry.focal_point.split("/")
                has_p = any(p in PERSONAL_POINTS for p in parts)
                label_color = "🔴" if has_p else "🔵"
                conj_strs = []
                for (cname, clon, corb) in entry.conjunctions:
                    cp = chart.get_position(cname)
                    csym = cp.symbol if cp else cname
                    conj_strs.append(f"{csym} **{cname}** (orb {corb:.2f}°)")
                st.markdown(
                    f"{label_color} **{entry.focal_point}** = "
                    f"`{entry.focal_lon:.2f}°` (dial `{entry.focal_dial:.2f}°`) "
                    f"→ {', '.join(conj_strs)}"
                )

    # ── TAB 3: Planetary Pictures
    with tab_pictures:
        st.subheader("Planetary Pictures — A + B − C = D")
        st.caption(
            "Witte's mathematical law: A + B − C = D on the 90° Dial. "
            "All hard aspects treated as conjunctions."
        )
        if not chart.planetary_pictures:
            st.info("No significant Planetary Pictures found within orb.")
        else:
            for pic in chart.planetary_pictures:
                pa = chart.get_position(pic.planet_a)
                pb = chart.get_position(pic.planet_b)
                pc = chart.get_position(pic.planet_c)
                pd = chart.get_position(pic.planet_d)
                sym_a = pa.symbol if pa else pic.planet_a
                sym_b = pb.symbol if pb else pic.planet_b
                sym_c = pc.symbol if pc else pic.planet_c
                sym_d = pd.symbol if pd else pic.planet_d

                flags = []
                if pic.involves_personal:
                    flags.append("⭐ Personal")
                if pic.involves_tnp:
                    flags.append("🪐 TNP")
                flag_str = " · ".join(flags)

                with st.expander(
                    f"{sym_a}{pic.planet_a} + {sym_b}{pic.planet_b} − "
                    f"{sym_c}{pic.planet_c} = {sym_d}{pic.planet_d} "
                    f"[orb {pic.orb:.2f}°] {flag_str}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Formula:** `{pic.formula}`")
                        st.markdown(f"**Computed lon:** `{pic.computed_lon:.2f}°`")
                        st.markdown(f"**{pic.planet_d} lon:** `{pic.target_lon:.2f}°`")
                        st.markdown(f"**Orb:** `{pic.orb:.2f}°`")
                    with col2:
                        st.markdown(f"**Meaning (EN):** {pic.meaning_en}")
                        st.markdown(f"**Meaning (ZH):** {pic.meaning_zh}")

    # ── TAB 4: Transneptunian Planets
    with tab_tnp:
        st.subheader("🪐 8 Transneptunian Planets (TNPs)")
        st.caption(
            "Alfred Witte's hypothetical planets. "
            "Positions computed via Hamburg School linear ephemeris."
        )
        tnp_rows = []
        for p in chart.positions:
            if not p.is_tnp:
                continue
            meanings = TNP_MEANINGS.get(p.name, {})
            tnp_rows.append({
                "Symbol": TNP_SYMBOLS.get(p.name, ""),
                "Name": p.name,
                "Longitude": f"{p.longitude:.4f}°",
                "Sign": f"{p.sign} ({SIGN_CN.get(p.sign, '')}) {p.sign_degree:.2f}°",
                "90° Dial": f"{p.dial90:.4f}°",
                "Meaning (EN)": meanings.get("en", ""),
                "Meaning (ZH)": meanings.get("zh", ""),
            })
        st.dataframe(tnp_rows, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### TNP Keyword Reference")
        for tnp_name, syms in TNP_SYMBOLS.items():
            meanings = TNP_MEANINGS.get(tnp_name, {})
            st.markdown(
                f"**{syms} {tnp_name}** — "
                f"{meanings.get('en', '')} · {meanings.get('zh', '')}"
            )


# ============================================================
# SVG 90° Dial visualization
# ============================================================

def _build_dial_svg(chart: UranianChart) -> str:
    """Build a circular 90° Dial SVG showing all planet positions."""
    W = 480
    CX, CY, R = W // 2, W // 2, 190

    # Background and circle
    lines = [
        f'<svg width="{W}" height="{W}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#0d1117; border-radius:50%; display:block; margin:auto;">',
        # Outer ring
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#30363d" stroke-width="2"/>',
        # Inner ring
        f'<circle cx="{CX}" cy="{CY}" r="{R - 20}" fill="none" stroke="#21262d" stroke-width="1"/>',
        # Center dot
        f'<circle cx="{CX}" cy="{CY}" r="4" fill="#58a6ff"/>',
    ]

    # Degree marks (every 5° on 90° dial)
    for deg_mark in range(0, 90, 5):
        angle_rad = math.radians(deg_mark * 4 - 90)  # *4 to map 90° → 360°
        is_major = (deg_mark % 15 == 0)
        tick_len = 12 if is_major else 6
        x1 = CX + (R - 2) * math.cos(angle_rad)
        y1 = CY + (R - 2) * math.sin(angle_rad)
        x2 = CX + (R - 2 - tick_len) * math.cos(angle_rad)
        y2 = CY + (R - 2 - tick_len) * math.sin(angle_rad)
        color = "#58a6ff" if is_major else "#30363d"
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{color}" stroke-width="1"/>')
        if is_major:
            label_r = R + 12
            lx = CX + label_r * math.cos(angle_rad)
            ly = CY + label_r * math.sin(angle_rad)
            lines.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#8b949e" '
                          f'font-size="9" text-anchor="middle" dominant-baseline="middle">'
                          f'{deg_mark}°</text>')

    # Planet markers
    colors = {
        "personal": "#f85149",   # red for personal points
        "tnp": "#d2a8ff",        # purple for TNPs
        "planet": "#79c0ff",     # blue for regular planets
    }

    for p in chart.positions:
        angle_rad = math.radians(p.dial90 * 4 - 90)  # map 0–90° → 0–360°
        marker_r = R - 30
        mx = CX + marker_r * math.cos(angle_rad)
        my = CY + marker_r * math.sin(angle_rad)

        if p.is_personal:
            col = colors["personal"]
        elif p.is_tnp:
            col = colors["tnp"]
        else:
            col = colors["planet"]

        # Spoke line
        spoke_r1 = R - 22
        spoke_r2 = R - 42
        sx1 = CX + spoke_r1 * math.cos(angle_rad)
        sy1 = CY + spoke_r1 * math.sin(angle_rad)
        sx2 = CX + spoke_r2 * math.cos(angle_rad)
        sy2 = CY + spoke_r2 * math.sin(angle_rad)
        lines.append(f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" '
                      f'stroke="{col}" stroke-width="1.5" opacity="0.7"/>')

        # Symbol text
        sym = p.symbol if len(p.symbol) <= 2 else p.name[:2]
        lines.append(f'<text x="{mx:.1f}" y="{my:.1f}" fill="{col}" '
                      f'font-size="10" text-anchor="middle" dominant-baseline="middle" '
                      f'font-weight="bold">{sym}</text>')

    lines.append("</svg>")
    return "\n".join(lines)
