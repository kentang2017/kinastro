"""
astro/western/western_love_synastry.py — 愛情合盤 (Romantic Love Synastry)

Computes love-focused synastry between two natal charts:
 • Romantic cross-aspects (Venus/Mars/Sun/Moon)
 • House overlays (5th / 7th / 8th)
 • Multi-dimensional love scores
 • Composite core planet positions
 • Bilingual (EN/ZH) romantic summaries & advice
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from astro.interpretations import get_synastry_reading

# ============================================================
# Constants
# ============================================================

# Love-focused aspect definitions — tighter orbs for clarity
LOVE_ASPECT_TYPES = [
    {"name": "Conjunction (合)",  "symbol": "☌", "angle":   0, "orb": 8},
    {"name": "Opposition (沖)",   "symbol": "☍", "angle": 180, "orb": 6},
    {"name": "Trine (三合)",      "symbol": "△", "angle": 120, "orb": 6},
    {"name": "Square (刑)",       "symbol": "□", "angle":  90, "orb": 6},
    {"name": "Sextile (六合)",    "symbol": "⚹", "angle":  60, "orb": 4},
]

# Base harmony weight used for love-score calculation
LOVE_BASE_HARMONY = {
    "Conjunction (合)":  0.6,
    "Opposition (沖)":  -0.2,
    "Trine (三合)":      1.0,
    "Square (刑)":      -0.4,
    "Sextile (六合)":    0.7,
}

# Romantic core planets (canonical prefix → display name)
LOVE_PLANETS = {"Sun", "Moon", "Venus", "Mars", "Juno", "Lilith", "Vertex"}

# Canonical short name for house-overlay matching
_PLANET_CANON = {
    "Sun ☉": "Sun", "Moon ☽": "Moon", "Mercury ☿": "Mercury",
    "Venus ♀": "Venus", "Mars ♂": "Mars", "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn", "Uranus ♅": "Uranus", "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
}


def _canon_name(name: str) -> str:
    if name in _PLANET_CANON:
        return _PLANET_CANON[name]
    for alias, canon in _PLANET_CANON.items():
        if alias in name:
            return canon
    return name.split()[0] if name else name


def _angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _composite_lon(lon_a: float, lon_b: float) -> float:
    """Midpoint of two ecliptic longitudes (short arc)."""
    diff = (lon_b - lon_a) % 360
    if diff > 180:
        mid = (lon_a + (lon_b + 360)) / 2
    else:
        mid = (lon_a + lon_b) / 2
    return mid % 360


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ZODIAC_SIGNS_ZH = [
    "牡羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
    "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚",
]

SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


def _sign_for_lon(lon: float) -> tuple[str, str, str]:
    idx = int((lon % 360) / 30)
    return ZODIAC_SIGNS[idx], ZODIAC_SIGNS_ZH[idx], SIGN_GLYPHS[idx]


# ============================================================
# Love relevance weights per planet-pair (higher = more romantic)
# ============================================================

_PAIR_RELEVANCE: dict[frozenset, float] = {
    frozenset({"Venus", "Mars"}):   1.0,   # chemistry / passion
    frozenset({"Moon", "Venus"}):   0.9,   # emotional intimacy
    frozenset({"Sun", "Moon"}):     0.95,  # soul connection
    frozenset({"Sun", "Venus"}):    0.85,  # admiration / warmth
    frozenset({"Mars", "Moon"}):    0.8,   # desire / protection
    frozenset({"Venus", "Venus"}):  0.75,  # shared values
    frozenset({"Mars", "Mars"}):    0.6,   # shared drive
    frozenset({"Sun", "Sun"}):      0.65,  # identity bond
    frozenset({"Sun", "Mars"}):     0.55,  # vitality / initiative
    frozenset({"Moon", "Moon"}):    0.8,   # emotional resonance
    frozenset({"Juno", "Sun"}):     0.7,   # commitment signal
    frozenset({"Juno", "Moon"}):    0.7,
    frozenset({"Juno", "Venus"}):   0.75,
    frozenset({"Lilith", "Venus"}): 0.65,  # forbidden attraction
    frozenset({"Lilith", "Mars"}):  0.65,
    frozenset({"Vertex", "Venus"}): 0.7,   # destined meeting
    frozenset({"Vertex", "Sun"}):   0.6,
}


def _pair_relevance(name_a: str, name_b: str) -> float:
    ca, cb = _canon_name(name_a), _canon_name(name_b)
    key = frozenset({ca, cb})
    return _PAIR_RELEVANCE.get(key, 0.0)


# ============================================================
# House overlay meanings
# ============================================================

_HOUSE_OVERLAY_MEANINGS: dict[int, tuple[str, str]] = {
    5: (
        "5th house overlay — romance, flirtation, joy, and playful creativity. "
        "This person lights up your sense of fun and sparks playful attraction.",
        "第五宮疊加——浪漫調情、歡樂與創意。對方激活你的玩樂精神，讓愛情充滿樂趣。",
    ),
    7: (
        "7th house overlay — partnership, marriage potential, and 'the one'. "
        "You instinctively see this person as a life companion.",
        "第七宮疊加——伴侶關係與婚姻潛力。你本能地將對方視為人生伴侶，具有長期承諾的能量。",
    ),
    8: (
        "8th house overlay — deep intimacy, sexual magnetism, and transformative bonding. "
        "This relationship touches the soul at the deepest level.",
        "第八宮疊加——深度親密與性吸引力。這段關係觸碰到靈魂最深處，帶來強烈的轉化能量。",
    ),
}


# ============================================================
# Data Classes
# ============================================================

@dataclass
class LoveSynastryAspect:
    """A single cross-chart aspect, enriched with love relevance."""
    planet_a: str
    planet_b: str
    aspect_name: str
    aspect_symbol: str
    aspect_angle: float
    orb: float
    harmony_score: float
    love_relevance: float          # 0.0 – 1.0, how romantic this pair is
    interpretation_en: str
    interpretation_cn: str

    @property
    def weighted_score(self) -> float:
        """harmony_score weighted by love_relevance."""
        return round(self.harmony_score * (0.4 + 0.6 * self.love_relevance), 4)


@dataclass
class LoveHouseOverlay:
    """A planet from one chart falling into a key love house of the other."""
    planet_name: str        # e.g. "Venus ♀"
    planet_canon: str       # e.g. "Venus"
    planet_owner: str       # name of person whose planet it is
    house_number: int       # 5, 7, or 8
    house_owner: str        # name of person whose house it is
    house_sign: str
    meaning_en: str
    meaning_cn: str


@dataclass
class CompositePlanet:
    """Midpoint (composite) position of one planet."""
    name: str
    longitude: float
    sign: str
    sign_zh: str
    sign_glyph: str
    sign_degree: float


@dataclass
class LoveSynastryResult:
    """Full love synastry result between two people."""
    person_a_name: str
    person_b_name: str

    # Scored aspects (all cross-aspects involving love planets)
    key_love_aspects: list = field(default_factory=list)   # List[LoveSynastryAspect]
    # House overlays for houses 5, 7, 8
    house_overlays: list = field(default_factory=list)     # List[LoveHouseOverlay]
    # Composite core planet positions
    composite_planets: list = field(default_factory=list)  # List[CompositePlanet]

    # Scores 0–100
    scores: dict = field(default_factory=dict)
    # {
    #   "attraction":    float,
    #   "emotional":     float,
    #   "sexual":        float,
    #   "longterm":      float,
    #   "overall":       float,
    # }

    romantic_summary_en: str = ""
    romantic_summary_cn: str = ""
    love_advice_en: str = ""
    love_advice_cn: str = ""


# ============================================================
# Core computation
# ============================================================

def _find_house_number(planet_lon: float, house_cusps: list) -> int:
    """Return house number (1-based) for a given ecliptic longitude."""
    lon = planet_lon % 360
    for i in range(12):
        start = house_cusps[i] % 360
        end = house_cusps[(i + 1) % 12] % 360
        if start < end:
            if start <= lon < end:
                return i + 1
        else:  # wraps 360
            if lon >= start or lon < end:
                return i + 1
    return 1


def _house_cusps_from_chart(chart) -> list[float]:
    """Extract ordered house cusp longitudes from a WesternChart."""
    houses_sorted = sorted(chart.houses, key=lambda h: h.number)
    return [h.cusp for h in houses_sorted]



def compute_love_synastry(
    chart_a,
    chart_b,
    name_a: str = "你",
    name_b: str = "對方",
) -> LoveSynastryResult:
    """
    Compute a love-focused synastry between two WesternChart objects.

    Parameters
    ----------
    chart_a, chart_b : WesternChart
    name_a, name_b   : display names

    Returns
    -------
    LoveSynastryResult
    """
    # ── 1. Cross-aspects ────────────────────────────────────────
    love_aspects: list[LoveSynastryAspect] = []

    for pa in chart_a.planets:
        canon_a = _canon_name(pa.name)
        for pb in chart_b.planets:
            canon_b = _canon_name(pb.name)
            # Only include pairs where at least one is a love planet
            if canon_a not in LOVE_PLANETS and canon_b not in LOVE_PLANETS:
                continue
            relevance = _pair_relevance(pa.name, pb.name)
            if relevance == 0.0:
                continue  # ignore non-romantic pairs entirely

            diff = _angle_diff(pa.longitude, pb.longitude)
            for asp in LOVE_ASPECT_TYPES:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    base = LOVE_BASE_HARMONY.get(asp["name"], 0)
                    score = base * (1 - orb / asp["orb"])
                    love_aspects.append(LoveSynastryAspect(
                        planet_a=pa.name,
                        planet_b=pb.name,
                        aspect_name=asp["name"],
                        aspect_symbol=asp["symbol"],
                        aspect_angle=asp["angle"],
                        orb=round(orb, 2),
                        harmony_score=round(score, 3),
                        love_relevance=relevance,
                        interpretation_en=get_synastry_reading(pa.name, pb.name, asp["name"], "en"),
                        interpretation_cn=get_synastry_reading(pa.name, pb.name, asp["name"], "zh"),
                    ))

    love_aspects.sort(key=lambda a: (-a.love_relevance, a.orb))

    # ── 2. House overlays (5th / 7th / 8th) ─────────────────────
    overlays: list[LoveHouseOverlay] = []
    love_houses = {5, 7, 8}

    def _find_house_sign(chart, house_num: int) -> str:
        h = next((hh for hh in chart.houses if hh.number == house_num), None)
        return h.sign if h else ""

    cusps_b = _house_cusps_from_chart(chart_b)
    for pa in chart_a.planets:
        h_num = _find_house_number(pa.longitude, cusps_b)
        if h_num in love_houses:
            meaning = _HOUSE_OVERLAY_MEANINGS.get(h_num, ("", ""))
            overlays.append(LoveHouseOverlay(
                planet_name=pa.name,
                planet_canon=_canon_name(pa.name),
                planet_owner=name_a,
                house_number=h_num,
                house_owner=name_b,
                house_sign=_find_house_sign(chart_b, h_num),
                meaning_en=meaning[0],
                meaning_cn=meaning[1],
            ))

    cusps_a = _house_cusps_from_chart(chart_a)
    for pb in chart_b.planets:
        h_num = _find_house_number(pb.longitude, cusps_a)
        if h_num in love_houses:
            meaning = _HOUSE_OVERLAY_MEANINGS.get(h_num, ("", ""))
            overlays.append(LoveHouseOverlay(
                planet_name=pb.name,
                planet_canon=_canon_name(pb.name),
                planet_owner=name_b,
                house_number=h_num,
                house_owner=name_a,
                house_sign=_find_house_sign(chart_a, h_num),
                meaning_en=meaning[0],
                meaning_cn=meaning[1],
            ))

    # ── 3. Composite core planets ────────────────────────────────
    composite_targets = ["Sun", "Moon", "Venus", "Mars"]
    composite: list[CompositePlanet] = []
    for target in composite_targets:
        pa_ = next((p for p in chart_a.planets if _canon_name(p.name) == target), None)
        pb_ = next((p for p in chart_b.planets if _canon_name(p.name) == target), None)
        if pa_ and pb_:
            c_lon = _composite_lon(pa_.longitude, pb_.longitude)
            sign, sign_zh, sign_glyph = _sign_for_lon(c_lon)
            composite.append(CompositePlanet(
                name=target,
                longitude=round(c_lon, 4),
                sign=sign,
                sign_zh=sign_zh,
                sign_glyph=sign_glyph,
                sign_degree=round(c_lon % 30, 2),
            ))

    # ── 4. Love scores (0–100) ───────────────────────────────────
    scores = _compute_love_scores(love_aspects, overlays)

    # ── 5. Summaries & advice ────────────────────────────────────
    summary_en, summary_cn, advice_en, advice_cn = _build_narratives(
        name_a, name_b, scores, love_aspects, overlays
    )

    return LoveSynastryResult(
        person_a_name=name_a,
        person_b_name=name_b,
        key_love_aspects=love_aspects,
        house_overlays=overlays,
        composite_planets=composite,
        scores=scores,
        romantic_summary_en=summary_en,
        romantic_summary_cn=summary_cn,
        love_advice_en=advice_en,
        love_advice_cn=advice_cn,
    )


# ============================================================
# Score helpers
# ============================================================

def _score_from_aspects(aspects: list[LoveSynastryAspect], pair_set: set[frozenset]) -> float:
    """Return 0-100 score for aspects matching any of the given planet pairs."""
    relevant = [a for a in aspects if frozenset({_canon_name(a.planet_a), _canon_name(a.planet_b)}) in pair_set]
    if not relevant:
        return 50.0  # neutral baseline
    raw = sum(a.weighted_score for a in relevant)
    # Normalise: raw range roughly [-0.6*n, 1.0*n]; map to 0-100
    n = len(relevant)
    clamped = max(-n * 0.6, min(n * 1.0, raw))
    return round(50 + (clamped / max(n * 0.8, 0.01)) * 35, 1)


def _overlay_bonus(overlays: list[LoveHouseOverlay], house_nums: set[int], love_planets: set[str]) -> float:
    """Return 0-10 bonus points for romantic house overlays."""
    matches = [o for o in overlays if o.house_number in house_nums and o.planet_canon in love_planets]
    return min(10.0, len(matches) * 2.5)


def _compute_love_scores(
    aspects: list[LoveSynastryAspect],
    overlays: list[LoveHouseOverlay],
) -> dict[str, float]:

    # Attraction & Chemistry — Venus/Mars
    attraction_pairs = {frozenset({"Venus", "Mars"}), frozenset({"Mars", "Venus"}),
                        frozenset({"Sun", "Venus"}), frozenset({"Venus", "Venus"})}
    attraction = _score_from_aspects(aspects, attraction_pairs)
    attraction += _overlay_bonus(overlays, {5, 7}, {"Venus", "Mars"})
    attraction = min(100, attraction)

    # Emotional Bond — Moon/Venus, Moon/Moon, Sun/Moon
    emotional_pairs = {frozenset({"Moon", "Venus"}), frozenset({"Moon", "Moon"}),
                       frozenset({"Sun", "Moon"}), frozenset({"Moon", "Sun"})}
    emotional = _score_from_aspects(aspects, emotional_pairs)
    emotional += _overlay_bonus(overlays, {4, 7}, {"Moon", "Venus"})
    emotional = min(100, emotional)

    # Sexual Chemistry — Mars/Moon, Venus/Mars (tense), Mars/Mars
    sexual_pairs = {frozenset({"Mars", "Moon"}), frozenset({"Venus", "Mars"}),
                    frozenset({"Mars", "Mars"}), frozenset({"Mars", "Venus"})}
    sexual = _score_from_aspects(aspects, sexual_pairs)
    sexual += _overlay_bonus(overlays, {8}, {"Mars", "Venus", "Lilith"})
    sexual = min(100, sexual)

    # Long-term Potential — Sun/Sun, Sun/Moon, Juno
    longterm_pairs = {frozenset({"Sun", "Sun"}), frozenset({"Sun", "Moon"}),
                      frozenset({"Juno", "Sun"}), frozenset({"Juno", "Moon"}),
                      frozenset({"Juno", "Venus"}), frozenset({"Venus", "Saturn"})}
    longterm = _score_from_aspects(aspects, longterm_pairs)
    longterm += _overlay_bonus(overlays, {7}, {"Sun", "Moon", "Juno"})
    longterm = min(100, longterm)

    overall = round((attraction * 0.25 + emotional * 0.30 + sexual * 0.20 + longterm * 0.25), 1)

    return {
        "attraction": round(attraction, 1),
        "emotional":  round(emotional, 1),
        "sexual":     round(sexual, 1),
        "longterm":   round(longterm, 1),
        "overall":    overall,
    }


# ============================================================
# Narrative builders
# ============================================================

_OVERALL_BANDS = [
    (80, (
        "A deeply romantic and fated connection — your stars align beautifully in love.",
        "這是一段深情而命定的緣分——你們的星盤在愛情中完美共鳴，如詩如畫。",
        "Cherish this rare bond. Nurture open communication and keep the romance alive.",
        "珍惜這難得的緣分，保持開誠布公的溝通，讓浪漫持續燃燒。",
    )),
    (65, (
        "A warm and promising love story with strong mutual attraction.",
        "這是一段充滿溫度與希望的愛情故事，彼此吸引力強烈。",
        "Build on your emotional connection; invest in shared experiences and honest dialogue.",
        "以情感連結為基礎，投入共同體驗與真誠對話，讓關係持續深化。",
    )),
    (50, (
        "A connection with real potential — with care and effort love can blossom fully.",
        "這段關係具有真實潛力，只要用心耕耘，愛情之花必將盛放。",
        "Focus on understanding each other's emotional needs and celebrate your differences.",
        "專注於理解彼此的情感需求，用包容轉化差異為成長的養分。",
    )),
    (35, (
        "An intriguing mix of attraction and challenge — growth through honest connection.",
        "吸引力與挑戰並存，在真誠的連結中共同成長。",
        "Give space for individual needs, and approach conflicts as opportunities to deepen trust.",
        "尊重彼此的個人空間，將衝突視為深化信任的機會而非障礙。",
    )),
    (0, (
        "A complex dynamic requiring patience and intentional care to thrive.",
        "這段動態較為複雜，需要耐心與有意識的付出方能開花結果。",
        "Seek mutual understanding first; professional guidance may help navigate tensions.",
        "首先尋求相互理解，必要時可尋求專業引導來化解張力。",
    )),
]


def _build_narratives(
    name_a: str,
    name_b: str,
    scores: dict[str, float],
    aspects: list[LoveSynastryAspect],
    overlays: list[LoveHouseOverlay],
) -> tuple[str, str, str, str]:
    overall = scores.get("overall", 50)

    # Pick band
    for threshold, texts in _OVERALL_BANDS:
        if overall >= threshold:
            sum_en, sum_cn, adv_en, adv_cn = texts
            break
    else:
        sum_en, sum_cn, adv_en, adv_cn = _OVERALL_BANDS[-1][1]

    # Add overlay highlights
    h7 = [o for o in overlays if o.house_number == 7]
    h8 = [o for o in overlays if o.house_number == 8]
    if h7:
        owners = " & ".join({o.planet_owner for o in h7[:2]})
        sum_en += f" The 7th house overlays ({owners}) suggest a natural sense of partnership."
        sum_cn += f"第七宮疊加（{owners}）暗示你們天生就有伴侶的默契。"
    if h8:
        sum_en += " 8th house overlays point to deep soulful intimacy."
        sum_cn += "第八宮疊加指向深層的靈魂親密感。"

    # Top aspect highlights
    top = [a for a in aspects if a.love_relevance >= 0.75][:3]
    if top:
        symbols = ", ".join(f"{a.planet_a} {a.aspect_symbol} {a.planet_b}" for a in top)
        sum_en += f" Highlighted aspects: {symbols}."
        sum_cn += f"亮點相位：{symbols}。"

    return sum_en, sum_cn, adv_en, adv_cn
