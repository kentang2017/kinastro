"""
astro/asteroids.py — 小行星位置計算 (Asteroid Positions)

Chiron, Ceres, Pallas, Juno, Vesta.
"""
import swisseph as swe
from dataclasses import dataclass

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

ASTEROIDS = {
    "Chiron":  {"number": swe.CHIRON if hasattr(swe, 'CHIRON') else 15, "symbol": "⚷", "cn": "凱龍星",
                "meaning_en": "Healing, wound, teaching", "meaning_cn": "療癒、傷口、教導"},
    "Ceres":   {"number": swe.AST_OFFSET + 1, "symbol": "⚳", "cn": "穀神星",
                "meaning_en": "Nurturing, harvest", "meaning_cn": "養育、收穫"},
    "Pallas":  {"number": swe.AST_OFFSET + 2, "symbol": "⚴", "cn": "智神星",
                "meaning_en": "Wisdom, strategy", "meaning_cn": "智慧、策略"},
    "Juno":    {"number": swe.AST_OFFSET + 3, "symbol": "⚵", "cn": "婚神星",
                "meaning_en": "Partnership, commitment", "meaning_cn": "合夥、承諾"},
    "Vesta":   {"number": swe.AST_OFFSET + 4, "symbol": "⚶", "cn": "灶神星",
                "meaning_en": "Devotion, focus", "meaning_cn": "奉獻、專注"},
}


@dataclass
class AsteroidPosition:
    name: str
    name_cn: str
    symbol: str
    longitude: float
    latitude: float
    sign: str
    sign_degree: float
    retrograde: bool
    meaning_en: str
    meaning_cn: str


def compute_asteroids(jd: float) -> list:
    """Compute positions of main asteroids for given Julian Day."""
    results = []
    for name, info in ASTEROIDS.items():
        try:
            xx, _ = swe.calc_ut(jd, info["number"])
            lon = xx[0]
            lat = xx[1]
            speed = xx[3] if len(xx) > 3 else 0
            sign_idx = int(lon / 30) % 12
            results.append(AsteroidPosition(
                name=name, name_cn=info["cn"], symbol=info["symbol"],
                longitude=lon, latitude=lat,
                sign=ZODIAC_SIGNS[sign_idx], sign_degree=round(lon % 30, 4),
                retrograde=speed < 0,
                meaning_en=info["meaning_en"], meaning_cn=info["meaning_cn"],
            ))
        except Exception:
            pass
    return results
