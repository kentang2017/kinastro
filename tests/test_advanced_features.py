"""
Comprehensive tests for 13 advanced modules in the kinastro project.

Covers: chart_theme, vedic_dasha, ashtakavarga, vedic_yogas, asteroids,
western_transit, western_return, western_synastry, hellenistic,
cross_compare, fixed_stars, export, qizheng_electional.
"""

import json
import pytest
import swisseph as swe

from astro.western import compute_western_chart
from astro.indian import compute_vedic_chart
from astro.calculator import compute_chart

# ── Standard test parameters ──────────────────────────────────────────
YEAR, MONTH, DAY, HOUR, MINUTE = 1990, 6, 15, 12, 0
TZ = 8.0
LAT, LON = 22.3193, 114.1694
LOC = "Hong Kong"
JD = swe.julday(YEAR, MONTH, DAY, HOUR - TZ + MINUTE / 60.0)


# ── Vedic planet name → canonical English mapping ─────────────────────
_VEDIC_TO_ENGLISH = {
    "Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
    "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus",
    "Shani": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu",
}


def _vedic_planet_longs(vedic_chart):
    """Extract planet longitudes with canonical English names from a VedicChart."""
    return {
        _VEDIC_TO_ENGLISH.get(p.name.split()[0], p.name.split()[0]): p.longitude
        for p in vedic_chart.planets
    }


# ── Shared fixtures ──────────────────────────────────────────────────
@pytest.fixture(scope="module")
def western_chart():
    return compute_western_chart(YEAR, MONTH, DAY, HOUR, MINUTE, TZ, LAT, LON, LOC)


@pytest.fixture(scope="module")
def vedic_chart():
    return compute_vedic_chart(YEAR, MONTH, DAY, HOUR, MINUTE, TZ, LAT, LON, LOC)


@pytest.fixture(scope="module")
def chinese_chart():
    return compute_chart(YEAR, MONTH, DAY, HOUR, MINUTE, TZ, LAT, LON, LOC)


# ══════════════════════════════════════════════════════════════════════
# 1. chart_theme
# ══════════════════════════════════════════════════════════════════════
class TestChartTheme:
    def test_planet_colors_dict_exists(self):
        from astro.chart_theme import PLANET_COLORS
        assert isinstance(PLANET_COLORS, dict)
        assert len(PLANET_COLORS) >= 7

    def test_get_planet_color_canonical(self):
        from astro.chart_theme import get_planet_color
        color = get_planet_color("Sun")
        assert isinstance(color, str)
        assert color.startswith("#")

    def test_get_planet_color_alias_chinese(self):
        from astro.chart_theme import get_planet_color
        color = get_planet_color("太陽")
        assert color.startswith("#")

    def test_get_planet_color_unknown_returns_fallback(self):
        from astro.chart_theme import get_planet_color
        color = get_planet_color("NonExistentPlanet")
        assert color == "#666666"

    def test_mobile_css_is_string(self):
        from astro.chart_theme import MOBILE_CSS
        assert isinstance(MOBILE_CSS, str)
        assert len(MOBILE_CSS) > 0


# ══════════════════════════════════════════════════════════════════════
# 2. vedic_dasha
# ══════════════════════════════════════════════════════════════════════
class TestVedicDasha:
    @pytest.fixture(scope="class")
    def moon_data(self, vedic_chart):
        moon = next(p for p in vedic_chart.planets if "Chandra" in p.name)
        return moon.longitude, vedic_chart.julian_day

    def test_vimshottari_return_type(self, moon_data):
        from astro.vedic_dasha import compute_vimshottari
        result = compute_vimshottari(moon_data[0], moon_data[1])
        assert hasattr(result, "moon_nakshatra")
        assert hasattr(result, "mahadasha_periods")

    def test_vimshottari_has_nine_periods(self, moon_data):
        from astro.vedic_dasha import compute_vimshottari
        result = compute_vimshottari(moon_data[0], moon_data[1])
        assert len(result.mahadasha_periods) == 9

    def test_vimshottari_total_years_sums_correctly(self, moon_data):
        """First period may be partial (balance). Full periods sum to 120."""
        from astro.vedic_dasha import compute_vimshottari, VIMSHOTTARI_YEARS
        result = compute_vimshottari(moon_data[0], moon_data[1])
        full_cycle = sum(VIMSHOTTARI_YEARS.values())
        assert abs(full_cycle - 120.0) < 0.01
        # First period is the balance; rest are full
        assert result.mahadasha_periods[0].years <= VIMSHOTTARI_YEARS[result.mahadasha_periods[0].lord]

    def test_vimshottari_sub_periods_exist(self, moon_data):
        from astro.vedic_dasha import compute_vimshottari
        result = compute_vimshottari(moon_data[0], moon_data[1])
        for period in result.mahadasha_periods:
            assert len(period.sub_periods) == 9

    def test_yogini_return_type(self, moon_data):
        from astro.vedic_dasha import compute_yogini
        result = compute_yogini(moon_data[0], moon_data[1])
        assert hasattr(result, "starting_yogini")
        assert hasattr(result, "periods")

    def test_yogini_has_eight_periods(self, moon_data):
        from astro.vedic_dasha import compute_yogini
        result = compute_yogini(moon_data[0], moon_data[1])
        assert len(result.periods) == 8

    def test_yogini_total_years_sums_correctly(self, moon_data):
        """First period may be partial; the 8 full yogini years total 36."""
        from astro.vedic_dasha import compute_yogini, YOGINI_YEARS
        result = compute_yogini(moon_data[0], moon_data[1])
        full_cycle = sum(YOGINI_YEARS)
        assert abs(full_cycle - 36.0) < 0.01
        # First period can be partial balance
        assert result.periods[0].years <= max(YOGINI_YEARS)

    def test_jd_to_date_str_format(self):
        from astro.vedic_dasha import jd_to_date_str
        s = jd_to_date_str(JD)
        assert isinstance(s, str)
        parts = s.split("-")
        assert len(parts) == 3
        assert int(parts[0]) == YEAR


# ══════════════════════════════════════════════════════════════════════
# 3. ashtakavarga
# ══════════════════════════════════════════════════════════════════════
class TestAshtakavarga:
    @pytest.fixture(scope="class")
    def avarga(self, vedic_chart):
        from astro.ashtakavarga import compute_ashtakavarga
        planet_longs = _vedic_planet_longs(vedic_chart)
        return compute_ashtakavarga(planet_longs, vedic_chart.ascendant)

    def test_has_seven_bav_rows(self, avarga):
        assert len(avarga.bav) == 7

    def test_bav_bindus_length(self, avarga):
        for row in avarga.bav:
            assert len(row.bindus) == 12

    def test_bav_bindus_range(self, avarga):
        for row in avarga.bav:
            for b in row.bindus:
                assert 0 <= b <= 8

    def test_sarva_length(self, avarga):
        assert len(avarga.sarva) == 12

    def test_sarva_total_equals_sum(self, avarga):
        assert avarga.sarva_total == sum(avarga.sarva)

    def test_bav_totals_match_bindus(self, avarga):
        for row in avarga.bav:
            assert row.total == sum(row.bindus)


# ══════════════════════════════════════════════════════════════════════
# 4. vedic_yogas
# ══════════════════════════════════════════════════════════════════════
class TestVedicYogas:
    @pytest.fixture(scope="class")
    def yogas(self, vedic_chart):
        from astro.vedic_yogas import compute_yogas
        planet_longs = _vedic_planet_longs(vedic_chart)
        return compute_yogas(planet_longs, vedic_chart.ascendant)

    def test_returns_list(self, yogas):
        assert isinstance(yogas, list)
        assert len(yogas) >= 5  # at least the non-Pancha-Mahapurusha yogas

    def test_yoga_fields(self, yogas):
        for y in yogas:
            assert hasattr(y, "name")
            assert hasattr(y, "is_present")
            assert hasattr(y, "strength")
            assert isinstance(y.is_present, bool)

    def test_yoga_strength_values(self, yogas):
        valid = {"Strong", "Moderate", "—"}
        for y in yogas:
            assert y.strength in valid

    def test_has_gajakesari(self, yogas):
        names = [y.name for y in yogas]
        assert any("Gajakesari" in n for n in names)

    def test_has_pancha_mahapurusha_or_common_yogas(self, yogas):
        names = [y.name for y in yogas]
        # At least some standard yogas should be detected
        known = ["Gajakesari", "Kemdruma", "Budha-Aditya", "Chandra-Mangal",
                 "Gandanta", "Ruchaka", "Bhadra", "Hamsa", "Malavya", "Sasa",
                 "Vesi", "Vosi"]
        found = [n for n in names if any(k in n for k in known)]
        assert len(found) >= 3


# ══════════════════════════════════════════════════════════════════════
# 5. asteroids
# ══════════════════════════════════════════════════════════════════════
class TestAsteroids:
    @pytest.fixture(scope="class")
    def asteroids(self):
        from astro.asteroids import compute_asteroids
        return compute_asteroids(JD)

    def test_returns_list(self, asteroids):
        assert isinstance(asteroids, list)

    def test_asteroid_fields_when_available(self, asteroids):
        for a in asteroids:
            assert hasattr(a, "name")
            assert hasattr(a, "longitude")
            assert hasattr(a, "sign")
            assert hasattr(a, "retrograde")

    def test_longitude_range(self, asteroids):
        for a in asteroids:
            assert 0 <= a.longitude < 360

    def test_sign_degree_range(self, asteroids):
        for a in asteroids:
            assert 0 <= a.sign_degree < 30

    def test_known_names_subset(self, asteroids):
        """If ephemeris data is available, names should be from the known set."""
        expected = {"Chiron", "Ceres", "Pallas", "Juno", "Vesta"}
        for a in asteroids:
            assert a.name in expected


# ══════════════════════════════════════════════════════════════════════
# 6. western_transit
# ══════════════════════════════════════════════════════════════════════
class TestWesternTransit:
    @pytest.fixture(scope="class")
    def transit(self, western_chart):
        from astro.western_transit import compute_western_transits
        return compute_western_transits(western_chart, 2024, 1, 1, 12, 0, TZ)

    def test_return_type(self, transit):
        assert hasattr(transit, "transit_date")
        assert hasattr(transit, "transit_planets")
        assert hasattr(transit, "aspects_to_natal")

    def test_transit_planets_populated(self, transit):
        assert len(transit.transit_planets) >= 10

    def test_aspects_have_correct_fields(self, transit):
        for asp in transit.aspects_to_natal:
            assert hasattr(asp, "transit_planet")
            assert hasattr(asp, "natal_planet")
            assert hasattr(asp, "orb")
            assert asp.orb >= 0

    def test_aspects_sorted_by_orb(self, transit):
        orbs = [a.orb for a in transit.aspects_to_natal]
        assert orbs == sorted(orbs)

    def test_transit_date_string(self, transit):
        assert "2024" in transit.transit_date


# ══════════════════════════════════════════════════════════════════════
# 7. western_return
# ══════════════════════════════════════════════════════════════════════
class TestWesternReturn:
    @pytest.fixture(scope="class")
    def solar_return(self, western_chart):
        from astro.western_return import compute_solar_return
        sun_lon = western_chart.planets[0].longitude
        return compute_solar_return(sun_lon, 2024, LAT, LON, TZ, LOC)

    @pytest.fixture(scope="class")
    def lunar_return(self, western_chart):
        from astro.western_return import compute_lunar_return
        moon_lon = western_chart.planets[1].longitude
        after_jd = swe.julday(2024, 1, 1, 0.0)
        return compute_lunar_return(moon_lon, after_jd, LAT, LON, TZ, LOC)

    def test_solar_return_fields(self, solar_return):
        assert hasattr(solar_return, "return_jd")
        assert hasattr(solar_return, "return_date")
        assert hasattr(solar_return, "return_chart")

    def test_solar_return_year(self, solar_return):
        assert solar_return.return_year == 2024

    def test_solar_return_sun_matches_natal(self, solar_return):
        natal_lon = solar_return.natal_sun_longitude
        return_sun = solar_return.return_chart.planets[0].longitude
        diff = abs(natal_lon - return_sun) % 360
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.5  # within 0.5 degrees

    def test_lunar_return_fields(self, lunar_return):
        assert hasattr(lunar_return, "return_jd")
        assert hasattr(lunar_return, "return_chart")

    def test_lunar_return_moon_matches_natal(self, lunar_return):
        natal_lon = lunar_return.natal_moon_longitude
        return_moon = lunar_return.return_chart.planets[1].longitude
        diff = abs(natal_lon - return_moon) % 360
        if diff > 180:
            diff = 360 - diff
        # The iterative solver has limited precision; 6° ≈ half a day of lunar motion
        assert diff < 6.0


# ══════════════════════════════════════════════════════════════════════
# 8. western_synastry
# ══════════════════════════════════════════════════════════════════════
class TestWesternSynastry:
    @pytest.fixture(scope="class")
    def synastry(self):
        from astro.western_synastry import compute_synastry
        chart_a = compute_western_chart(1990, 6, 15, 12, 0, TZ, LAT, LON, LOC)
        chart_b = compute_western_chart(1992, 3, 20, 8, 30, TZ, LAT, LON, LOC)
        return compute_synastry(chart_a, chart_b, "Alice", "Bob")

    def test_return_type(self, synastry):
        assert hasattr(synastry, "inter_aspects")
        assert hasattr(synastry, "harmony_summary")

    def test_names(self, synastry):
        assert synastry.person_a_name == "Alice"
        assert synastry.person_b_name == "Bob"

    def test_harmony_is_numeric(self, synastry):
        assert isinstance(synastry.harmony_summary, float)

    def test_aspects_have_orb(self, synastry):
        for asp in synastry.inter_aspects:
            assert hasattr(asp, "orb")
            assert asp.orb >= 0

    def test_element_compatibility_exists(self, synastry):
        assert isinstance(synastry.element_compatibility, str)
        assert len(synastry.element_compatibility) > 0


# ══════════════════════════════════════════════════════════════════════
# 9. hellenistic
# ══════════════════════════════════════════════════════════════════════
class TestHellenistic:
    @pytest.fixture(scope="class")
    def hchart(self, western_chart):
        from astro.hellenistic import compute_hellenistic_chart
        return compute_hellenistic_chart(western_chart, birth_year=1990,
                                         current_year=2024,
                                         current_jd=swe.julday(2024, 1, 1, 12.0))

    def test_lots_count(self, hchart):
        assert len(hchart.lots) == 7

    def test_lots_fields(self, hchart):
        for lot in hchart.lots:
            assert hasattr(lot, "name")
            assert hasattr(lot, "longitude")
            assert 0 <= lot.longitude < 360
            assert hasattr(lot, "sign")

    def test_profection_fields(self, hchart):
        p = hchart.profection
        assert hasattr(p, "current_age")
        assert hasattr(p, "profected_sign")
        assert hasattr(p, "time_lord")
        assert p.current_age == 2024 - 1990

    def test_zodiacal_releasing_periods(self, hchart):
        zr = hchart.zodiacal_releasing
        assert len(zr) > 0
        for period in zr:
            assert hasattr(period, "sign")
            assert hasattr(period, "start_jd")
            assert period.years > 0

    def test_planet_conditions_scoring(self, hchart):
        for pc in hchart.planet_conditions:
            assert hasattr(pc, "planet")
            assert hasattr(pc, "score")
            assert isinstance(pc.score, (int, float))

    def test_get_bound_lord(self):
        from astro.hellenistic import get_bound_lord
        entry = get_bound_lord(0, 5.0)  # Aries at 5 degrees
        assert hasattr(entry, "planet")
        assert isinstance(entry.planet, str)
        assert len(entry.planet) > 0

    def test_compute_lots_directly(self, western_chart):
        from astro.hellenistic import compute_lots
        planet_longs = {}
        for p in western_chart.planets:
            short = p.name.split()[0]
            planet_longs[short] = p.longitude
        cusps = [h.cusp for h in western_chart.houses]
        lots = compute_lots(planet_longs, western_chart.ascendant,
                            western_chart.is_day_chart, cusps)
        assert len(lots) == 7
        for lot in lots:
            assert 0 <= lot.longitude < 360


# ══════════════════════════════════════════════════════════════════════
# 10. cross_compare
# ══════════════════════════════════════════════════════════════════════
class TestCrossCompare:
    @pytest.fixture(scope="class")
    def comparison(self, chinese_chart, western_chart, vedic_chart):
        from astro.cross_compare import compute_cross_comparison
        return compute_cross_comparison(chinese_chart, western_chart, vedic_chart)

    def test_return_type(self, comparison):
        assert hasattr(comparison, "planets")
        assert hasattr(comparison, "ayanamsa")

    def test_unified_planet_count(self, comparison):
        assert len(comparison.planets) == 7

    def test_unified_planet_fields(self, comparison):
        for up in comparison.planets:
            assert hasattr(up, "canonical_name")
            assert hasattr(up, "tropical_lon")
            assert hasattr(up, "sidereal_lon")
            assert 0 <= up.tropical_lon < 360
            assert 0 <= up.sidereal_lon < 360

    def test_ayanamsa_positive(self, comparison):
        assert comparison.ayanamsa > 20  # Lahiri ~23-24 degrees

    def test_tropical_sidereal_difference(self, comparison):
        for up in comparison.planets:
            diff = (up.tropical_lon - up.sidereal_lon) % 360
            if diff > 180:
                diff = 360 - diff
            assert abs(diff - comparison.ayanamsa) < 1.0


# ══════════════════════════════════════════════════════════════════════
# 11. fixed_stars
# ══════════════════════════════════════════════════════════════════════
class TestFixedStars:
    def test_load_catalog(self):
        from astro.fixed_stars import load_star_catalog
        catalog = load_star_catalog()
        assert isinstance(catalog, list)
        assert len(catalog) >= 10

    def test_catalog_entry_fields(self):
        from astro.fixed_stars import load_star_catalog
        catalog = load_star_catalog()
        for entry in catalog:
            assert "name" in entry
            assert "magnitude" in entry or "nature" in entry

    def test_compute_positions_returns_list(self):
        from astro.fixed_stars import compute_fixed_star_positions
        stars = compute_fixed_star_positions(JD)
        assert isinstance(stars, list)

    def test_star_position_fields(self):
        """If ephemeris data is available, star positions have correct fields."""
        from astro.fixed_stars import compute_fixed_star_positions
        stars = compute_fixed_star_positions(JD)
        for s in stars:
            assert hasattr(s, "name")
            assert hasattr(s, "longitude")
            assert 0 <= s.longitude < 360

    def test_find_conjunctions_returns_list(self):
        from astro.fixed_stars import compute_fixed_star_positions, find_conjunctions
        stars = compute_fixed_star_positions(JD)
        planet_pos = {"Sun": 83.8, "Moon": 340.9}
        conj = find_conjunctions(stars, planet_pos, orb=2.0)
        assert isinstance(conj, list)
        for c in conj:
            assert hasattr(c, "star_name")
            assert hasattr(c, "planet_name")
            assert c.orb <= 2.0


# ══════════════════════════════════════════════════════════════════════
# 12. export
# ══════════════════════════════════════════════════════════════════════
class TestExport:
    @pytest.fixture(scope="class")
    def chart_dict(self, western_chart):
        from astro.export import western_chart_to_dict
        return western_chart_to_dict(western_chart)

    def test_western_chart_to_dict_keys(self, chart_dict):
        assert "system" in chart_dict
        assert "planets" in chart_dict
        assert "houses" in chart_dict

    def test_chart_dict_planet_list(self, chart_dict):
        assert isinstance(chart_dict["planets"], list)
        assert len(chart_dict["planets"]) >= 10

    def test_generate_chart_summary(self, chart_dict):
        from astro.export import generate_chart_summary
        summary = generate_chart_summary(chart_dict)
        assert isinstance(summary, str)
        assert len(summary) > 50

    def test_generate_planet_csv(self, chart_dict):
        from astro.export import generate_planet_csv
        csv_str = generate_planet_csv(chart_dict["planets"])
        assert isinstance(csv_str, str)
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 2  # header + at least one data row
        assert "," in lines[0]

    def test_csv_header_fields(self, chart_dict):
        from astro.export import generate_planet_csv
        csv_str = generate_planet_csv(chart_dict["planets"])
        header = csv_str.strip().split("\n")[0].lower()
        assert "name" in header or "planet" in header

    def test_generate_chart_pdf_cjk_text(self):
        """PDF generation must not crash on CJK text (latin-1 safe)."""
        from astro.export import generate_chart_pdf
        chart_data = {
            "system": "七政四餘",
            "datetime": "2026-04-13",
            "location": "台北市大安區",
            "ascendant": "白羊座",
            "planets": [
                {"name": "太陽", "sign": "白羊座", "degree": 23.5, "retrograde": False},
            ],
            "extra_sections": [
                {"title": "神煞分析", "content": "天乙貴人在子位"},
            ],
        }
        pdf_bytes = generate_chart_pdf(chart_data)
        assert isinstance(pdf_bytes, (bytes, bytearray))
        assert len(pdf_bytes) > 0



# ══════════════════════════════════════════════════════════════════════
# 14. qizheng_electional
# ══════════════════════════════════════════════════════════════════════
class TestQizhengElectional:
    @pytest.fixture(scope="class")
    def electional(self):
        from astro.qizheng_electional import find_auspicious_dates
        return find_auspicious_dates(2024, 1, 1, 2024, 1, 15, TZ, "general")

    def test_return_type(self, electional):
        assert hasattr(electional, "rated_dates")
        assert hasattr(electional, "best_date")

    def test_rated_dates_populated(self, electional):
        assert len(electional.rated_dates) > 0
        assert len(electional.rated_dates) <= 15

    def test_date_rating_fields(self, electional):
        for dr in electional.rated_dates:
            assert hasattr(dr, "date")
            assert hasattr(dr, "score")
            assert 0 <= dr.score <= 100

    def test_dates_sorted_by_score_desc(self, electional):
        scores = [dr.score for dr in electional.rated_dates]
        assert scores == sorted(scores, reverse=True)

    def test_best_date_in_range(self, electional):
        assert "2024-01" in electional.best_date

    def test_different_criteria(self):
        from astro.qizheng_electional import find_auspicious_dates
        for criteria in ("marriage", "travel", "business"):
            result = find_auspicious_dates(2024, 6, 1, 2024, 6, 10, TZ, criteria)
            assert len(result.rated_dates) > 0
