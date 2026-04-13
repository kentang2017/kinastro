"""
astro/hellenistic.py — 希臘占星 (Hellenistic Astrology)

Lots, Egyptian Bounds, Annual Profections, Zodiacal Releasing,
Planetary Condition scoring, Sect analysis.
"""
import swisseph as swe
from dataclasses import dataclass, field

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_CN = {
    "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "雙子座", "Cancer": "巨蟹座",
    "Leo": "獅子座", "Virgo": "處女座", "Libra": "天秤座", "Scorpio": "天蠍座",
    "Sagittarius": "射手座", "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Minor years for Zodiacal Releasing
SIGN_YEARS = {
    "Aries": 15, "Taurus": 8, "Gemini": 20, "Cancer": 25,
    "Leo": 19, "Virgo": 20, "Libra": 8, "Scorpio": 15,
    "Sagittarius": 12, "Capricorn": 27, "Aquarius": 30, "Pisces": 12,
}

# Egyptian Bounds (Ptolemaic)
EGYPTIAN_BOUNDS = {
    0: [("Jupiter",0,6),("Venus",6,12),("Mercury",12,20),("Mars",20,25),("Saturn",25,30)],
    1: [("Venus",0,8),("Mercury",8,14),("Jupiter",14,22),("Saturn",22,27),("Mars",27,30)],
    2: [("Mercury",0,6),("Jupiter",6,12),("Venus",12,17),("Mars",17,24),("Saturn",24,30)],
    3: [("Mars",0,7),("Venus",7,13),("Mercury",13,19),("Jupiter",19,26),("Saturn",26,30)],
    4: [("Jupiter",0,6),("Venus",6,11),("Saturn",11,18),("Mercury",18,24),("Mars",24,30)],
    5: [("Mercury",0,7),("Venus",7,17),("Jupiter",17,21),("Mars",21,28),("Saturn",28,30)],
    6: [("Saturn",0,6),("Mercury",6,14),("Jupiter",14,21),("Venus",21,28),("Mars",28,30)],
    7: [("Mars",0,7),("Venus",7,11),("Mercury",11,19),("Jupiter",19,24),("Saturn",24,30)],
    8: [("Jupiter",0,12),("Venus",12,17),("Mercury",17,21),("Mars",21,26),("Saturn",26,30)],
    9: [("Mercury",0,7),("Jupiter",7,14),("Venus",14,22),("Saturn",22,26),("Mars",26,30)],
    10:[("Mercury",0,7),("Venus",7,13),("Jupiter",13,20),("Mars",20,25),("Saturn",25,30)],
    11:[("Venus",0,12),("Jupiter",12,16),("Mercury",16,19),("Mars",19,28),("Saturn",28,30)],
}

# Dignity tables
DOMICILE = {"Sun": [4], "Moon": [3], "Mars": [0,7], "Mercury": [2,5],
            "Jupiter": [8,11], "Venus": [1,6], "Saturn": [9,10]}
EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
              "Jupiter": 3, "Venus": 11, "Saturn": 6}
DETRIMENT = {"Sun": [10], "Moon": [9], "Mars": [1,6], "Mercury": [8,11],
             "Jupiter": [2,5], "Venus": [0,7], "Saturn": [3,4]}
FALL = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
        "Jupiter": 9, "Venus": 5, "Saturn": 0}


def _sign_idx(lon): return int(lon / 30) % 12
def _sign_deg(lon): return lon % 30
def _normalize(deg): return deg % 360


@dataclass
class Lot:
    name: str
    name_cn: str
    longitude: float
    sign: str
    sign_degree: float
    house: int
    formula_en: str
    meaning_en: str
    meaning_cn: str


@dataclass
class BoundsEntry:
    sign: str
    planet: str
    start_degree: float
    end_degree: float


@dataclass
class ProfectionResult:
    current_age: int
    profected_sign: str
    profected_sign_cn: str
    time_lord: str
    time_lord_cn: str
    house_from_asc: int


@dataclass
class ZodiacalReleasingPeriod:
    level: str
    sign: str
    sign_cn: str
    ruler: str
    start_jd: float
    end_jd: float
    start_date: str
    end_date: str
    years: float


@dataclass
class PlanetCondition:
    planet: str
    score: int
    details: list  # list of (factor, points, description)


@dataclass
class HellenisticChart:
    ascendant: float
    midheaven: float
    is_day_chart: bool
    planet_longitudes: dict
    planet_houses: dict
    house_cusps: list
    lots: list = field(default_factory=list)
    bounds: list = field(default_factory=list)
    profection: object = None
    zodiacal_releasing: list = field(default_factory=list)
    planet_conditions: list = field(default_factory=list)
    sect_analysis: dict = field(default_factory=dict)


GRAHA_CN = {"Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
            "Mars": "火星", "Jupiter": "木星", "Saturn": "土星"}


def _jd_to_date(jd):
    y, m, d, h = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{int(d):02d}"


def _find_house(lon, cusps):
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 1


def compute_lots(planet_longs, ascendant, is_day, cusps):
    """Compute 7 Greek Lots."""
    sun = planet_longs.get("Sun", 0)
    moon = planet_longs.get("Moon", 0)
    venus = planet_longs.get("Venus", 0)
    mars = planet_longs.get("Mars", 0)
    mercury = planet_longs.get("Mercury", 0)
    jupiter = planet_longs.get("Jupiter", 0)
    saturn = planet_longs.get("Saturn", 0)

    if is_day:
        fortune = _normalize(ascendant + moon - sun)
        spirit = _normalize(ascendant + sun - moon)
    else:
        fortune = _normalize(ascendant + sun - moon)
        spirit = _normalize(ascendant + moon - sun)

    defs = [
        ("Lot of Fortune", "福點", fortune, "Asc+Moon-Sun (day)", "Body, health, fortune", "身體、健康、財運"),
        ("Lot of Spirit", "靈點", spirit, "Asc+Sun-Moon (day)", "Mind, career, purpose", "心靈、事業、目的"),
        ("Lot of Eros", "愛神點", _normalize(ascendant + venus - spirit), "Asc+Venus-Spirit", "Love, desire", "愛情、慾望"),
        ("Lot of Necessity", "命運點", _normalize(ascendant + fortune - mercury), "Asc+Fortune-Mercury", "Fate, obligations", "命運、義務"),
        ("Lot of Courage", "勇氣點", _normalize(ascendant + fortune - mars), "Asc+Fortune-Mars", "Boldness, conflict", "勇敢、衝突"),
        ("Lot of Victory", "勝利點", _normalize(ascendant + jupiter - spirit), "Asc+Jupiter-Spirit", "Success, abundance", "成功、豐盛"),
        ("Lot of Nemesis", "報應點", _normalize(ascendant + fortune - saturn), "Asc+Fortune-Saturn", "Hidden enemies, karma", "隱敵、業力"),
    ]
    lots = []
    for name, cn, lon, formula, m_en, m_cn in defs:
        idx = _sign_idx(lon)
        lots.append(Lot(
            name=name, name_cn=cn, longitude=lon,
            sign=ZODIAC_SIGNS[idx], sign_degree=round(_sign_deg(lon), 2),
            house=_find_house(lon, cusps),
            formula_en=formula, meaning_en=m_en, meaning_cn=m_cn,
        ))
    return lots


def get_bound_lord(sign_idx, degree):
    for planet, start, end in EGYPTIAN_BOUNDS.get(sign_idx, []):
        if start <= degree < end:
            return BoundsEntry(
                sign=ZODIAC_SIGNS[sign_idx], planet=planet,
                start_degree=start, end_degree=end,
            )
    return None


def compute_profections(ascendant_lon, birth_year, current_year):
    if current_year is None:
        return None
    age = current_year - birth_year
    asc_idx = _sign_idx(ascendant_lon)
    prof_idx = (asc_idx + age) % 12
    sign = ZODIAC_SIGNS[prof_idx]
    ruler = SIGN_RULERS[sign]
    return ProfectionResult(
        current_age=age, profected_sign=sign,
        profected_sign_cn=SIGN_CN[sign], time_lord=ruler,
        time_lord_cn=GRAHA_CN.get(ruler, ruler),
        house_from_asc=(prof_idx - asc_idx) % 12 + 1,
    )


def compute_zodiacal_releasing(fortune_lon, birth_jd, target_jd):
    """L1 periods from Lot of Fortune."""
    start_idx = _sign_idx(fortune_lon)
    periods = []
    cur_jd = birth_jd
    for i in range(20):  # ~20 L1 periods to cover most lifetimes
        idx = (start_idx + i) % 12
        sign = ZODIAC_SIGNS[idx]
        yrs = SIGN_YEARS[sign]
        end_jd = cur_jd + yrs * 365.25
        periods.append(ZodiacalReleasingPeriod(
            level="L1", sign=sign, sign_cn=SIGN_CN[sign],
            ruler=SIGN_RULERS[sign],
            start_jd=cur_jd, end_jd=end_jd,
            start_date=_jd_to_date(cur_jd), end_date=_jd_to_date(end_jd),
            years=yrs,
        ))
        if end_jd > target_jd and i > 2:
            break
        cur_jd = end_jd
    return periods


def compute_planet_conditions(planet_longs, planet_houses, is_day, asc_lon):
    results = []
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        if planet not in planet_longs:
            continue
        lon = planet_longs[planet]
        idx = _sign_idx(lon)
        house = planet_houses.get(planet, 0)
        score = 0
        details = []

        # Sect
        day_planets = {"Sun", "Jupiter", "Saturn"}
        night_planets = {"Moon", "Venus", "Mars"}
        if is_day and planet in day_planets:
            score += 3; details.append(("Sect", 3, "In preferred sect"))
        elif not is_day and planet in night_planets:
            score += 3; details.append(("Sect", 3, "In preferred sect"))
        elif planet in day_planets or planet in night_planets:
            score -= 3; details.append(("Sect", -3, "Against sect"))

        # Domicile
        if idx in DOMICILE.get(planet, []):
            score += 5; details.append(("Domicile", 5, f"In own sign {ZODIAC_SIGNS[idx]}"))
        # Exaltation
        if EXALTATION.get(planet) == idx:
            score += 4; details.append(("Exaltation", 4, f"Exalted in {ZODIAC_SIGNS[idx]}"))
        # Detriment
        if idx in DETRIMENT.get(planet, []):
            score -= 5; details.append(("Detriment", -5, f"In detriment"))
        # Fall
        if FALL.get(planet) == idx:
            score -= 4; details.append(("Fall", -4, f"In fall"))

        # House (angular/succedent/cadent)
        if house in (1, 4, 7, 10):
            score += 3; details.append(("Angular", 3, f"House {house}"))
        elif house in (2, 5, 8, 11):
            score += 1; details.append(("Succedent", 1, f"House {house}"))
        elif house in (3, 6, 9, 12):
            score -= 1; details.append(("Cadent", -1, f"House {house}"))

        results.append(PlanetCondition(planet=planet, score=score, details=details))
    return results


def _compute_sect(planet_longs, planet_houses, is_day):
    sect = "Day" if is_day else "Night"
    day_benefic = "Jupiter"
    night_benefic = "Venus"
    return {
        "sect": sect,
        "sect_light": "Sun" if is_day else "Moon",
        "benefic_of_sect": day_benefic if is_day else night_benefic,
        "malefic_of_sect": "Saturn" if is_day else "Mars",
    }


def compute_hellenistic_chart(western_chart, birth_year=None,
                              current_year=None, current_jd=None):
    """Derive Hellenistic techniques from a WesternChart."""
    p_longs = {p.name.split()[0]: p.longitude for p in western_chart.planets}
    p_houses = {p.name.split()[0]: p.house for p in western_chart.planets}
    cusps = [h.cusp for h in western_chart.houses]
    asc = western_chart.ascendant
    is_day = western_chart.is_day_chart

    lots = compute_lots(p_longs, asc, is_day, cusps)
    asc_idx = _sign_idx(asc)
    bound = get_bound_lord(asc_idx, _sign_deg(asc))
    profection = compute_profections(asc, birth_year or western_chart.year,
                                     current_year)

    fortune_lon = lots[0].longitude if lots else 0.0
    birth_jd = western_chart.julian_day
    zr = compute_zodiacal_releasing(fortune_lon, birth_jd,
                                     current_jd or birth_jd + 36525)
    conditions = compute_planet_conditions(p_longs, p_houses, is_day, asc)
    sect = _compute_sect(p_longs, p_houses, is_day)

    return HellenisticChart(
        ascendant=asc, midheaven=western_chart.midheaven,
        is_day_chart=is_day, planet_longitudes=p_longs,
        planet_houses=p_houses, house_cusps=cusps,
        lots=lots, bounds=[bound] if bound else [],
        profection=profection, zodiacal_releasing=zr,
        planet_conditions=conditions, sect_analysis=sect,
    )


def render_hellenistic_chart(chart):
    """Render Hellenistic chart in Streamlit."""
    import streamlit as st

    st.subheader("☿ Hellenistic Astrology / 希臘占星")
    sect = chart.sect_analysis
    st.info(f"**Sect**: {sect.get('sect', '—')} chart | "
            f"Benefic of sect: {sect.get('benefic_of_sect', '—')} | "
            f"Malefic of sect: {sect.get('malefic_of_sect', '—')}")

    # Lots
    st.markdown("#### Lots / 希臘點")
    lot_data = []
    for lot in chart.lots:
        lot_data.append({
            "Name": f"{lot.name} ({lot.name_cn})",
            "Sign": lot.sign,
            "Degree": f"{lot.sign_degree:.2f}°",
            "House": lot.house,
            "Meaning": lot.meaning_cn,
        })
    if lot_data:
        st.dataframe(lot_data, use_container_width=True)

    # Bounds
    if chart.bounds:
        b = chart.bounds[0]
        st.markdown(f"#### Ascendant Bound Lord / 上升界主: **{b.planet}** "
                    f"({b.sign} {b.start_degree}°–{b.end_degree}°)")

    # Profection
    if chart.profection:
        pf = chart.profection
        st.markdown(f"#### Annual Profection / 年限推進")
        st.write(f"Age {pf.current_age} → **{pf.profected_sign}** ({pf.profected_sign_cn}) | "
                 f"Time Lord: **{pf.time_lord}** ({pf.time_lord_cn}) | "
                 f"House {pf.house_from_asc}")

    # Zodiacal Releasing
    if chart.zodiacal_releasing:
        st.markdown("#### Zodiacal Releasing / 黃道釋放 (L1)")
        zr_data = [{"Sign": p.sign, "Sign (CN)": p.sign_cn,
                     "Ruler": p.ruler, "Years": p.years,
                     "Start": p.start_date, "End": p.end_date}
                    for p in chart.zodiacal_releasing]
        st.dataframe(zr_data, use_container_width=True)

    # Planet Conditions
    if chart.planet_conditions:
        st.markdown("#### Planetary Condition / 行星狀態評分")
        cond_data = []
        for pc in chart.planet_conditions:
            detail_str = "; ".join(f"{f}: {p:+d}" for f, p, _ in pc.details)
            cond_data.append({"Planet": pc.planet, "Score": pc.score,
                              "Details": detail_str})
        st.dataframe(cond_data, use_container_width=True)
