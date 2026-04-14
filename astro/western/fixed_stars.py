"""
astro/fixed_stars.py — 固定星模組 (Fixed Stars)

Computes positions of classical fixed stars and finds conjunctions with planets.
"""
import json
import os
import swisseph as swe
from dataclasses import dataclass

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

_DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "data")


def load_star_catalog():
    path = os.path.join(_DATA_DIR, "fixed_stars.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class FixedStarPosition:
    name: str
    longitude: float
    latitude: float
    magnitude: float
    nature: str
    meaning_en: str
    meaning_cn: str
    constellation: str
    sign: str
    sign_degree: float


@dataclass
class StarConjunction:
    star_name: str
    star_longitude: float
    planet_name: str
    planet_longitude: float
    orb: float
    nature: str
    meaning_en: str
    meaning_cn: str


def compute_fixed_star_positions(jd):
    """Compute positions of all catalogued fixed stars."""
    catalog = load_star_catalog()
    results = []
    for star in catalog:
        try:
            name_result, xx = swe.fixstar_ut(star["swe_name"], jd)
            lon, lat = xx[0], xx[1]
            idx = int(lon / 30) % 12
            results.append(FixedStarPosition(
                name=star["name"], longitude=lon, latitude=lat,
                magnitude=star["magnitude"], nature=star["nature"],
                meaning_en=star["meaning_en"], meaning_cn=star["meaning_cn"],
                constellation=star["constellation"],
                sign=ZODIAC_SIGNS[idx], sign_degree=round(lon % 30, 4),
            ))
        except Exception:
            pass
    results.sort(key=lambda s: s.longitude)
    return results


def find_conjunctions(stars, planet_positions, orb=1.5):
    """Find fixed stars within orb of any planet.

    planet_positions: dict of {name: longitude}
    """
    results = []
    for star in stars:
        for p_name, p_lon in planet_positions.items():
            diff = abs(star.longitude - p_lon) % 360
            actual_orb = min(diff, 360 - diff)
            if actual_orb <= orb:
                results.append(StarConjunction(
                    star_name=star.name, star_longitude=star.longitude,
                    planet_name=p_name, planet_longitude=p_lon,
                    orb=round(actual_orb, 4),
                    nature=star.nature,
                    meaning_en=star.meaning_en, meaning_cn=star.meaning_cn,
                ))
    results.sort(key=lambda c: c.orb)
    return results
