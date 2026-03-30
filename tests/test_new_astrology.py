"""
Tests for Western, Indian (Vedic), Thai, and Arabic astrology calculator modules.
"""

import pytest

from astro.western import (
    compute_western_chart,
    _normalize,
    _sign_index,
    _sign_degree,
    ZODIAC_SIGNS,
)
from astro.indian import (
    compute_vedic_chart,
    _nakshatra_info,
    RASHIS,
    NAKSHATRAS,
)
from astro.thai import (
    compute_thai_chart,
    THAI_RASHIS,
    THAI_DAY_PLANETS,
)
from astro.arabic import (
    compute_arabic_chart,
    ARABIC_PARTS,
    ZODIAC_SIGNS as ARABIC_ZODIAC_SIGNS,
    _get_dignity,
    _is_day_chart,
)


# ============================================================
# Western Astrology Tests
# ============================================================

class TestWesternChart:
    """西洋占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_western_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "北京"

    def test_has_eleven_planets(self, sample_chart):
        """10 planets + North Node = 11"""
        assert len(sample_chart.planets) == 11

    def test_planet_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert "Sun ☉" in names
        assert "Moon ☽" in names
        assert "Uranus ♅" in names
        assert "Neptune ♆" in names
        assert "Pluto ♇" in names
        assert "North Node ☊" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_planet_sign_degrees_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sign_degree < 30

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12

    def test_sun_in_capricorn_for_jan1(self, sample_chart):
        sun = sample_chart.planets[0]
        assert sun.sign == "Capricorn"

    def test_ascendant_and_mc(self, sample_chart):
        assert 0 <= sample_chart.ascendant < 360
        assert 0 <= sample_chart.midheaven < 360
        assert sample_chart.asc_sign in [s[0] for s in ZODIAC_SIGNS]
        assert sample_chart.mc_sign in [s[0] for s in ZODIAC_SIGNS]

    def test_different_dates_produce_different_results(self):
        c1 = compute_western_chart(2000, 6, 15, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_western_chart(2020, 12, 25, 8, 30, 8.0, 39.9, 116.4)
        sun1 = c1.planets[0].longitude
        sun2 = c2.planets[0].longitude
        assert abs(sun1 - sun2) > 1.0


# ============================================================
# Indian (Vedic) Astrology Tests
# ============================================================

class TestVedicChart:
    """印度占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_vedic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "北京"

    def test_has_nine_planets(self, sample_chart):
        """7 planets + Rahu + Ketu = 9"""
        assert len(sample_chart.planets) == 9

    def test_planet_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert "Surya (太陽)" in names
        assert "Chandra (月亮)" in names
        assert "Rahu (羅睺)" in names
        assert "Ketu (計都)" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_ayanamsa_positive(self, sample_chart):
        assert sample_chart.ayanamsa > 20  # Lahiri ayanamsa ~23-24°

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_nakshatra_assigned(self, sample_chart):
        for p in sample_chart.planets:
            assert p.nakshatra in [n[0] for n in NAKSHATRAS]
            assert 1 <= p.nakshatra_pada <= 4

    def test_rashi_assigned(self, sample_chart):
        for p in sample_chart.planets:
            assert p.rashi in [r[0] for r in RASHIS]

    def test_ketu_opposite_rahu(self, sample_chart):
        rahu = next(p for p in sample_chart.planets if "Rahu" in p.name)
        ketu = next(p for p in sample_chart.planets if "Ketu" in p.name)
        diff = abs(rahu.longitude - ketu.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ascendant_rashi(self, sample_chart):
        assert sample_chart.asc_rashi in [r[0] for r in RASHIS]

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12


class TestNakshatraInfo:
    """Nakshatra calculation tests"""

    def test_first_nakshatra(self):
        idx, pada = _nakshatra_info(0.0)
        assert idx == 0
        assert pada == 1

    def test_last_nakshatra(self):
        idx, pada = _nakshatra_info(359.0)
        assert idx == 26
        assert pada >= 1

    def test_pada_range(self):
        for deg in range(0, 360, 10):
            _, pada = _nakshatra_info(float(deg))
            assert 1 <= pada <= 4


# ============================================================
# Thai Astrology Tests
# ============================================================

class TestThaiChart:
    """泰國占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_thai_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=7.0, latitude=13.7563, longitude=100.5018,
            location_name="Bangkok",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "Bangkok"

    def test_has_nine_planets(self, sample_chart):
        """7 planets + Rahu + Ketu = 9"""
        assert len(sample_chart.planets) == 9

    def test_planet_names_thai(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert any("พระอาทิตย์" in n for n in names)
        assert any("ราหู" in n for n in names)
        assert any("เกตุ" in n for n in names)

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_day_planet_assigned(self, sample_chart):
        # Jan 1 1990 is Monday
        assert sample_chart.day_of_week == 1
        assert sample_chart.day_planet == "พระจันทร์"

    def test_rashi_thai_names(self, sample_chart):
        for p in sample_chart.planets:
            assert p.rashi in [r[0] for r in THAI_RASHIS]

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12

    def test_ketu_opposite_rahu(self, sample_chart):
        rahu = next(p for p in sample_chart.planets if "ราหู" in p.name)
        ketu = next(p for p in sample_chart.planets if "เกตุ" in p.name)
        diff = abs(rahu.longitude - ketu.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ayanamsa_positive(self, sample_chart):
        assert sample_chart.ayanamsa > 20

    def test_sunday_is_sun(self):
        """Sunday should map to Sun planet"""
        # 1990-01-07 is Sunday
        chart = compute_thai_chart(1990, 1, 7, 12, 0, 7.0, 13.7563, 100.5018)
        assert chart.day_of_week == 0
        assert chart.day_planet == "พระอาทิตย์"


# ============================================================
# Arabic Astrology Tests
# ============================================================

class TestArabicChart:
    """阿拉伯占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_arabic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "北京"

    def test_has_eight_planets(self, sample_chart):
        """7 classical planets + North Node = 8"""
        assert len(sample_chart.planets) == 8

    def test_planet_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert "Sun ☉ (太陽)" in names
        assert "Moon ☽ (月亮)" in names
        assert "Mars ♂ (火星)" in names
        assert "Saturn ♄ (土星)" in names
        assert "North Node ☊ (北交點)" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_planet_sign_degrees_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sign_degree < 30

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12

    def test_sun_in_capricorn_for_jan1(self, sample_chart):
        sun = next(p for p in sample_chart.planets if "Sun" in p.name)
        assert sun.sign == "Capricorn"

    def test_ascendant_and_mc(self, sample_chart):
        assert 0 <= sample_chart.ascendant < 360
        assert 0 <= sample_chart.midheaven < 360
        assert sample_chart.asc_sign in [s[0] for s in ARABIC_ZODIAC_SIGNS]
        assert sample_chart.mc_sign in [s[0] for s in ARABIC_ZODIAC_SIGNS]

    def test_is_day_chart_boolean(self, sample_chart):
        assert isinstance(sample_chart.is_day_chart, bool)

    def test_arabic_parts_count(self, sample_chart):
        """Should have as many parts as defined in ARABIC_PARTS"""
        assert len(sample_chart.arabic_parts) == len(ARABIC_PARTS)

    def test_arabic_parts_longitudes_in_range(self, sample_chart):
        for part in sample_chart.arabic_parts:
            assert 0 <= part.longitude < 360

    def test_arabic_parts_sign_degrees_in_range(self, sample_chart):
        for part in sample_chart.arabic_parts:
            assert 0 <= part.sign_degree < 30

    def test_arabic_parts_have_house(self, sample_chart):
        for part in sample_chart.arabic_parts:
            assert 1 <= part.house <= 12

    def test_part_of_fortune_present(self, sample_chart):
        names = [part.english_name for part in sample_chart.arabic_parts]
        assert "Part of Fortune" in names

    def test_part_of_spirit_present(self, sample_chart):
        names = [part.english_name for part in sample_chart.arabic_parts]
        assert "Part of Spirit" in names

    def test_arabic_sign_names_populated(self, sample_chart):
        for p in sample_chart.planets:
            assert p.arabic_sign != ""

    def test_dignity_is_string(self, sample_chart):
        for p in sample_chart.planets:
            assert isinstance(p.dignity, str)

    def test_different_dates_produce_different_results(self):
        c1 = compute_arabic_chart(2000, 6, 15, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_arabic_chart(2020, 12, 25, 8, 30, 8.0, 39.9, 116.4)
        sun1 = next(p for p in c1.planets if "Sun" in p.name).longitude
        sun2 = next(p for p in c2.planets if "Sun" in p.name).longitude
        assert abs(sun1 - sun2) > 1.0


class TestArabicDignity:
    """Essential dignity calculation tests"""

    def test_sun_domicile_in_leo(self):
        # Leo is sign index 4, Sun domicile
        assert "入廟" in _get_dignity("Sun ☉ (太陽)", 4)

    def test_sun_exaltation_in_aries(self):
        # Aries is sign index 0, Sun exaltation
        assert "入旺" in _get_dignity("Sun ☉ (太陽)", 0)

    def test_sun_detriment_in_aquarius(self):
        # Aquarius (index 10) is opposite Leo (domicile)
        assert "落陷" in _get_dignity("Sun ☉ (太陽)", 10)

    def test_sun_fall_in_libra(self):
        # Libra (index 6) is opposite Aries (exaltation)
        assert "入弱" in _get_dignity("Sun ☉ (太陽)", 6)

    def test_no_dignity(self):
        # Jupiter in Aries has no special dignity
        result = _get_dignity("Jupiter ♃ (木星)", 0)
        assert result == "—"
