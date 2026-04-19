"""
astro/cross_compare.py — 跨體系比較 (Cross-System Comparison)

Unified planet positions across Western, Vedic, and Chinese systems.
"""
from dataclasses import dataclass, field

PLANET_NAME_MAP = {
    "Sun": ("太陽", "Sun ☉", "Surya (太陽)"),
    "Moon": ("太陰", "Moon ☽", "Chandra (月亮)"),
    "Mercury": ("水星", "Mercury ☿", "Budha (水星)"),
    "Venus": ("金星", "Venus ♀", "Shukra (金星)"),
    "Mars": ("火星", "Mars ♂", "Mangal (火星)"),
    "Jupiter": ("木星", "Jupiter ♃", "Guru (木星)"),
    "Saturn": ("土星", "Saturn ♄", "Shani (土星)"),
}

WESTERN_SIGNS_CN = {
    "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "雙子座",
    "Cancer": "巨蟹座", "Leo": "獅子座", "Virgo": "處女座",
    "Libra": "天秤座", "Scorpio": "天蠍座", "Sagittarius": "射手座",
    "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}


@dataclass
class UnifiedPlanetPosition:
    canonical_name: str
    canonical_cn: str
    tropical_lon: float = 0.0
    sidereal_lon: float = 0.0
    western_sign: str = ""
    western_sign_cn: str = ""
    western_degree: float = 0.0
    vedic_rashi: str = ""
    vedic_rashi_cn: str = ""
    nakshatra: str = ""
    chinese_sign: str = ""
    mansion_chinese: str = ""


@dataclass
class CrossCompareResult:
    planets: list = field(default_factory=list)
    ayanamsa: float = 0.0
    tropical_asc: str = ""
    sidereal_asc: str = ""
    chinese_ming: str = ""
    summary_en: str = ""
    summary_cn: str = ""


def _find_planet(planets, target_names):
    """Find planet by name substring matching."""
    for p in planets:
        for t in target_names:
            if t in p.name:
                return p
    return None


def compute_cross_comparison(chinese_chart, western_chart, vedic_chart):
    """Unify planet positions across three chart systems."""
    results = []

    for canonical, (cn_name, w_name, v_name) in PLANET_NAME_MAP.items():
        w_planet = _find_planet(western_chart.planets, [w_name, canonical])
        v_planet = _find_planet(vedic_chart.planets, [v_name, canonical])
        c_planet = _find_planet(chinese_chart.planets, [cn_name])

        up = UnifiedPlanetPosition(
            canonical_name=canonical, canonical_cn=cn_name,
        )
        if w_planet:
            up.tropical_lon = round(w_planet.longitude, 4)
            up.western_sign = getattr(w_planet, 'sign', '')
            up.western_sign_cn = WESTERN_SIGNS_CN.get(up.western_sign, '')
            up.western_degree = round(w_planet.longitude % 30, 2)
        if v_planet:
            up.sidereal_lon = round(v_planet.longitude, 4)
            up.vedic_rashi = getattr(v_planet, 'rashi', '')
            up.nakshatra = getattr(v_planet, 'nakshatra', '')
        if c_planet:
            up.chinese_sign = getattr(c_planet, 'sign_chinese', '')
            up.mansion_chinese = getattr(c_planet, 'mansion', '')

        results.append(up)

    ayanamsa = getattr(vedic_chart, 'ayanamsa', 0.0)

    return CrossCompareResult(
        planets=results, ayanamsa=round(ayanamsa, 4),
        tropical_asc=getattr(western_chart, 'asc_sign', ''),
        sidereal_asc=getattr(vedic_chart, 'asc_rashi', ''),
        chinese_ming="",
        summary_en=f"Comparing {len(results)} planets across 3 systems (ayanamsa={ayanamsa:.2f}°)",
        summary_cn=f"跨3個體系比較 {len(results)} 顆行星（歲差={ayanamsa:.2f}°）",
    )


def render_cross_comparison(result):
    """Render cross-comparison in Streamlit."""
    import streamlit as st

    st.subheader("🔀 Cross-System Comparison / 跨體系比較")
    st.info(result.summary_cn if st.session_state.get("lang") == "zh" else result.summary_en)

    data = []
    for p in result.planets:
        data.append({
            "Planet": f"{p.canonical_name} ({p.canonical_cn})",
            "Western": f"{p.western_sign} {p.western_degree:.1f}°" if p.western_sign else "—",
            "Vedic": p.vedic_rashi or "—",
            "Nakshatra": p.nakshatra or "—",
            "Chinese": p.chinese_sign or "—",
        })
    if data:
        st.dataframe(data, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ayanamsa", f"{result.ayanamsa:.4f}°")
    with col2:
        st.metric("Western Asc", result.tropical_asc)


# ============================================================
# Babylonian cross-comparison helper
# ============================================================
BABYLONIAN_AKKADIAN_SIGNS = [
    "LU.HUN.GA", "GU4.AN.NA", "MAŠ.TAB.BA.GAL.GAL", "ALLA",
    "UR.GU.LA", "AB.SIN", "ZI.BA.AN.NA", "GIR.TAB",
    "PA.BIL.SAG", "SUḪUR.MAŠ", "GU", "ZIB.ME",
]

BABYLONIAN_PLANET_GODS_MAP = {
    "Sun": "Shamash", "Moon": "Sin", "Mercury": "Nabu",
    "Venus": "Ishtar", "Mars": "Nergal", "Jupiter": "Marduk",
    "Saturn": "Ninurta",
}


def add_babylonian_to_comparison(result, babylonian_chart):
    """Augment a CrossCompareResult with Babylonian sidereal positions.

    Parameters
    ----------
    result : CrossCompareResult
    babylonian_chart : BabylonianChart (from astro.babylonian)

    Returns
    -------
    CrossCompareResult — same object, with Babylonian columns added to each
    UnifiedPlanetPosition (attributes: ``babylonian_akkadian``,
    ``babylonian_degree``, ``babylonian_god``).
    """
    if babylonian_chart is None:
        return result

    planet_map = {}
    for pos in getattr(babylonian_chart, "positions", []):
        planet_map[pos.name] = pos

    for up in result.planets:
        bpos = planet_map.get(up.canonical_name)
        if bpos:
            up.babylonian_akkadian = bpos.sign_akkadian
            up.babylonian_degree = bpos.sign_degree
            up.babylonian_god = BABYLONIAN_PLANET_GODS_MAP.get(
                up.canonical_name, "")
        else:
            up.babylonian_akkadian = ""
            up.babylonian_degree = 0.0
            up.babylonian_god = ""

    bab_asc_idx = int(getattr(babylonian_chart, "ascendant", 0) / 30) % 12
    result.babylonian_asc = BABYLONIAN_AKKADIAN_SIGNS[bab_asc_idx]
    return result
