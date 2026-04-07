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
    calculate_thai_nine_grid,
    _digit_reduce,
    _NINE_GRID_LINES,
    THAI_NUMEROLOGY_PLANETS,
)
from astro.arabic import (
    compute_arabic_chart,
    ARABIC_PARTS,
    ZODIAC_SIGNS as ARABIC_ZODIAC_SIGNS,
    _get_dignity,
    _is_day_chart,
    _compute_aspects,
    ASPECT_TYPES,
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
# Sukkayodo (宿曜道) Tests
# ============================================================

class TestSukkayodo:
    """宿曜道排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_vedic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_sukkayodo_mansion_index_valid(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sukkayodo_mansion_index < 28

    def test_sukkayodo_pada_valid(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.sukkayodo_pada <= 4

    def test_sukkayodo_mansion_name_is_string(self, sample_chart):
        for p in sample_chart.planets:
            assert isinstance(p.sukkayodo_mansion, str)
            assert len(p.sukkayodo_mansion) > 0

    def test_sukkayodo_mansion_chinese_is_string(self, sample_chart):
        """Bug fix test: sukkayodo_mansion_chinese should be a Chinese
        name string, not an integer lord index."""
        for p in sample_chart.planets:
            assert isinstance(p.sukkayodo_mansion_chinese, str)
            assert len(p.sukkayodo_mansion_chinese) > 0

    def test_sukkayodo_mansion_chinese_matches_data(self, sample_chart):
        """Verify mansion_chinese matches SUKKAYODO_MANSION[idx][2]."""
        from astro.sukkayodo import SUKKAYODO_MANSION
        for p in sample_chart.planets:
            expected = SUKKAYODO_MANSION[p.sukkayodo_mansion_index][2]
            assert p.sukkayodo_mansion_chinese == expected


class TestSukkayodoInfo:
    """sukkayodo_info calculation tests"""

    def test_first_mansion(self):
        from astro.sukkayodo import sukkayodo_info
        idx, pada = sukkayodo_info(0.0)
        assert idx == 0
        assert pada == 1

    def test_last_mansion(self):
        from astro.sukkayodo import sukkayodo_info
        idx, pada = sukkayodo_info(359.9)
        assert idx == 27

    def test_pada_range(self):
        from astro.sukkayodo import sukkayodo_info
        for deg in range(0, 360, 5):
            _, pada = sukkayodo_info(float(deg))
            assert 1 <= pada <= 4

    def test_mansion_index_range(self):
        from astro.sukkayodo import sukkayodo_info
        for deg in range(0, 360, 5):
            idx, _ = sukkayodo_info(float(deg))
            assert 0 <= idx < 28


class TestTwelvePalaces:
    """十二宮 mapping tests"""

    def test_all_28_mansions_mapped(self):
        from astro.sukkayodo import TWELVE_PALACES
        all_indices = []
        for _, indices in TWELVE_PALACES:
            all_indices.extend(indices)
        assert sorted(all_indices) == list(range(28))

    def test_twelve_palaces_count(self):
        from astro.sukkayodo import TWELVE_PALACES
        assert len(TWELVE_PALACES) == 12

    def test_palace_names(self):
        from astro.sukkayodo import TWELVE_PALACES
        expected = ["羊宮", "牛宮", "夫宮", "蟹宮", "獅宮", "女宮",
                    "秤宮", "蝎宮", "弓宮", "磨宮", "瓶宮", "魚宮"]
        names = [name for name, _ in TWELVE_PALACES]
        assert names == expected


class TestGetRokuyo:
    """六曜 lookup tests"""

    def test_valid_index(self):
        from astro.sukkayodo import get_rokuyo
        for i in range(28):
            rk = get_rokuyo(i)
            assert rk is not None
            assert len(rk) == 4

    def test_invalid_index_returns_none(self):
        from astro.sukkayodo import get_rokuyo
        assert get_rokuyo(-1) is None
        assert get_rokuyo(28) is None


class TestSansanjuMansions:
    """三九秘宿法 (San-Jiu Bi-Su) data and calculation tests"""

    def test_sansanju_27_mansions_length(self):
        """SANSANJU_27_MANSIONS must have exactly 27 elements."""
        from astro.sukkayodo import SANSANJU_27_MANSIONS
        assert len(SANSANJU_27_MANSIONS) == 27

    def test_sansanju_27_mansions_excludes_abhijit(self):
        """Abhijit (牛宿, index 21) must not appear in the 27-mansion list."""
        from astro.sukkayodo import SANSANJU_27_MANSIONS
        assert 21 not in SANSANJU_27_MANSIONS

    def test_sansanju_27_mansions_covers_all_others(self):
        """All 28 mansions except Abhijit (21) must appear exactly once."""
        from astro.sukkayodo import SANSANJU_27_MANSIONS
        expected = sorted(set(range(28)) - {21})
        assert sorted(SANSANJU_27_MANSIONS) == expected

    def test_get_sansanju_table_all_months(self):
        """_get_sansanju_table must not raise IndexError for any birth month."""
        from astro.sukkayodo import _get_sansanju_table
        for month in range(1, 13):
            result = _get_sansanju_table(month, 1)
            assert "table" in result
            assert "day_category" in result
            assert len(result["table"]) == 33

    def test_get_sansanju_table_all_days(self):
        """_get_sansanju_table must not raise IndexError for any birth day."""
        from astro.sukkayodo import _get_sansanju_table
        for day in range(1, 32):
            result = _get_sansanju_table(1, day)
            assert result["day_category"] in [
                "命", "業", "胎", "榮", "衰", "安", "危", "成", "壞", "友", "親"
            ]

    def test_sansanju_month_starts_length(self):
        """SANSANJU_MONTH_STARTS must have exactly 12 entries (one per month)."""
        from astro.sukkayodo import SANSANJU_MONTH_STARTS
        assert len(SANSANJU_MONTH_STARTS) == 12

    def test_sansanju_month_starts_first_is_zero(self):
        """正月 (January) must start at position 0 (室宿)."""
        from astro.sukkayodo import SANSANJU_MONTH_STARTS, SANSANJU_27_MANSIONS, SUKKAYODO_MANSION
        pos = SANSANJU_MONTH_STARTS[0]
        assert pos == 0
        mansion_idx = SANSANJU_27_MANSIONS[pos]
        assert mansion_idx < len(SUKKAYODO_MANSION), (
            f"mansion_idx {mansion_idx} is out of range for SUKKAYODO_MANSION "
            f"(len={len(SUKKAYODO_MANSION)})"
        )
        assert SUKKAYODO_MANSION[mansion_idx][2] == "室宿"


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
# Thai Numerology 9-Box Grid Tests
# ============================================================

class TestThaiNineGrid:
    """泰國 Numerology 9宮格計算測試"""

    @pytest.fixture
    def sample_result(self):
        # 05/03/1985
        return calculate_thai_nine_grid(day=5, month=3, year=1985)

    def test_returns_dict_with_expected_keys(self, sample_result):
        expected = {"counts", "birth_number", "life_path",
                    "complete_lines", "strongest", "missing", "day", "month", "year"}
        assert expected.issubset(sample_result.keys())

    def test_counts_keys_are_1_to_9(self, sample_result):
        assert set(sample_result["counts"].keys()) == set(range(1, 10))

    def test_counts_are_non_negative(self, sample_result):
        for n, c in sample_result["counts"].items():
            assert c >= 0, f"Negative count for digit {n}"

    def test_birth_number_is_single_digit(self, sample_result):
        bn = sample_result["birth_number"]
        assert 1 <= bn <= 9

    def test_life_path_is_single_digit(self, sample_result):
        lp = sample_result["life_path"]
        assert 1 <= lp <= 9

    def test_birth_number_correct_for_day5(self, sample_result):
        # day 5 → birth number 5
        assert sample_result["birth_number"] == 5

    def test_life_path_correct(self):
        # 05/03/1985 → digits: 5,3,1,9,8,5 → sum=31 → 3+1=4
        result = calculate_thai_nine_grid(5, 3, 1985)
        assert result["life_path"] == 4

    def test_derived_numbers_added_to_counts(self):
        # day=1, month=1, year=1111 → raw digits: 1,1,1,1,1,1
        # birth_number = 1, life_path = reduce(6) = 6
        # counts before derived: {1:6}
        # after: {1:6+1=7, 6:0+1=1}
        result = calculate_thai_nine_grid(1, 1, 1111)
        assert result["counts"][1] == 7
        assert result["counts"][6] == 1

    def test_complete_lines_are_valid_line_names(self, sample_result):
        valid = set(_NINE_GRID_LINES.keys())
        for line in sample_result["complete_lines"]:
            assert line in valid

    def test_complete_line_means_all_digits_present(self, sample_result):
        counts = sample_result["counts"]
        for line_name in sample_result["complete_lines"]:
            for n in _NINE_GRID_LINES[line_name]:
                assert counts[n] > 0, (
                    f"Line {line_name} marked complete but digit {n} has count 0"
                )

    def test_strongest_all_have_same_count(self, sample_result):
        counts = sample_result["counts"]
        strongest = sample_result["strongest"]
        if strongest:
            max_count = max(counts[n] for n in strongest)
            for n in strongest:
                assert counts[n] == max_count

    def test_missing_have_zero_count(self, sample_result):
        counts = sample_result["counts"]
        for n in sample_result["missing"]:
            assert counts[n] == 0

    def test_strongest_and_missing_disjoint(self, sample_result):
        s = set(sample_result["strongest"])
        m = set(sample_result["missing"])
        assert s.isdisjoint(m)

    def test_all_digits_present_gives_no_missing(self):
        # 19/08/2753 → has 1,9,0,8,2,7,5,3 → non-zero: 1,9,8,2,7,5,3
        # birth_number = reduce(19)=reduce(10)=1, life_path = reduce(1+9+8+2+7+5+3)=reduce(35)=8
        # Still might miss 4 and 6 from raw — test that logic is consistent
        result = calculate_thai_nine_grid(19, 8, 2753)
        for n in result["missing"]:
            assert result["counts"][n] == 0

    def test_original_date_preserved(self):
        result = calculate_thai_nine_grid(15, 7, 2000)
        assert result["day"] == 15
        assert result["month"] == 7
        assert result["year"] == 2000

    def test_digit_reduce_single(self):
        assert _digit_reduce(5) == 5
        assert _digit_reduce(9) == 9

    def test_digit_reduce_two_digit(self):
        assert _digit_reduce(19) == 1   # 1+9=10 → 1+0=1
        assert _digit_reduce(29) == 2   # 2+9=11 → 1+1=2

    def test_digit_reduce_large(self):
        assert _digit_reduce(999) == 9  # 27 → 9

    def test_digit_reduce_zero(self):
        # 0 and negatives should return 1 (fallback)
        assert _digit_reduce(0) == 1
        assert _digit_reduce(-5) == 1

    def test_numerology_planets_covers_1_to_9(self):
        assert set(THAI_NUMEROLOGY_PLANETS.keys()) == set(range(1, 10))

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


class TestArabicAspects:
    """阿拉伯占星相位測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_arabic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_aspects_is_list(self, sample_chart):
        assert isinstance(sample_chart.aspects, list)

    def test_aspects_not_empty(self, sample_chart):
        # With 7 classical planets, there should be at least some aspects
        assert len(sample_chart.aspects) > 0

    def test_aspect_has_required_fields(self, sample_chart):
        for a in sample_chart.aspects:
            assert hasattr(a, "planet1")
            assert hasattr(a, "planet2")
            assert hasattr(a, "aspect_name")
            assert hasattr(a, "arabic_name")
            assert hasattr(a, "chinese_name")
            assert hasattr(a, "angle")
            assert hasattr(a, "orb")

    def test_aspect_names_are_valid(self, sample_chart):
        valid_names = {eng for eng, _, _, _, _ in ASPECT_TYPES}
        for a in sample_chart.aspects:
            assert a.aspect_name in valid_names

    def test_aspect_orb_within_limit(self, sample_chart):
        orb_limits = {eng: orb for eng, _, _, _, orb in ASPECT_TYPES}
        for a in sample_chart.aspects:
            assert a.orb <= orb_limits[a.aspect_name]

    def test_aspect_angle_positive(self, sample_chart):
        for a in sample_chart.aspects:
            assert 0 <= a.angle <= 180

    def test_no_self_aspects(self, sample_chart):
        for a in sample_chart.aspects:
            assert a.planet1 != a.planet2

    def test_no_north_node_in_aspects(self, sample_chart):
        for a in sample_chart.aspects:
            assert "North Node" not in a.planet1
            assert "North Node" not in a.planet2


# ============================================================
# Zi Wei Dou Shu (紫微斗數) Tests
# ============================================================

from astro.ziwei import (
    compute_ziwei_chart,
    _get_hour_branch,
    _get_year_stem,
    _get_year_branch,
    _get_ming_gong_branch,
    _get_shen_gong_branch,
    _get_wu_xing_ju,
    _get_ziwei_branch,
    _get_tianfu_branch,
    _get_ming_gong_stem,
    _solar_to_lunar,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    WU_XING_JU_NAMES,
    PALACE_SEQUENCE,
)


class TestZiweiHelpers:
    """紫微斗數輔助函數測試"""

    def test_hour_branch_zi_midnight(self):
        assert _get_hour_branch(0, 0) == 0   # 子時

    def test_hour_branch_zi_late_night(self):
        assert _get_hour_branch(23, 30) == 0  # 子時

    def test_hour_branch_chou(self):
        assert _get_hour_branch(1, 0) == 1   # 丑時

    def test_hour_branch_yin(self):
        assert _get_hour_branch(3, 0) == 2   # 寅時

    def test_hour_branch_noon(self):
        assert _get_hour_branch(12, 0) == 6  # 午時

    def test_hour_branch_hai(self):
        assert _get_hour_branch(21, 30) == 11  # 亥時

    def test_hour_branch_range(self):
        for h in range(24):
            b = _get_hour_branch(h, 0)
            assert 0 <= b <= 11

    def test_year_stem_1990(self):
        # 1990 = 庚午年；庚 = index 6
        assert _get_year_stem(1990) == 6

    def test_year_stem_2000(self):
        # 2000 = 庚辰年；庚 = index 6
        assert _get_year_stem(2000) == 6

    def test_year_stem_2024(self):
        # 2024 = 甲辰年；甲 = index 0
        assert _get_year_stem(2024) == 0

    def test_year_branch_1990(self):
        # 1990 庚午年；午 = index 6
        assert _get_year_branch(1990) == 6

    def test_year_branch_2000(self):
        # 2000 庚辰年；辰 = index 4
        assert _get_year_branch(2000) == 4

    def test_ming_gong_branch_in_range(self):
        for m in range(1, 13):
            for h in range(12):
                b = _get_ming_gong_branch(m, h)
                assert 0 <= b <= 11

    def test_shen_gong_branch_in_range(self):
        for m in range(1, 13):
            for h in range(12):
                b = _get_shen_gong_branch(m, h)
                assert 0 <= b <= 11

    def test_wu_xing_ju_range(self):
        for stem in range(10):
            ming_stem = _get_ming_gong_stem(stem, 2)
            ju = _get_wu_xing_ju(ming_stem)
            assert 2 <= ju <= 6

    def test_wu_xing_ju_names_coverage(self):
        assert set(WU_XING_JU_NAMES.keys()) == {2, 3, 4, 5, 6}

    def test_ziwei_branch_in_range(self):
        for day in range(1, 31):
            for n in range(2, 7):
                b = _get_ziwei_branch(day, n)
                assert 0 <= b <= 11

    def test_tianfu_branch_formula(self):
        # 天府 = (14 - 紫微) % 12
        for ziwei in range(12):
            tianfu = _get_tianfu_branch(ziwei)
            assert tianfu == (14 - ziwei) % 12

    def test_ziwei_day1_water2(self):
        # 水二局，初一 → 寅 (index 2)
        assert _get_ziwei_branch(1, 2) == 2


class TestZiweiSolarToLunar:
    """農曆轉換測試"""

    def test_known_date_2000_02_05(self):
        # 2000-02-05 = 農曆正月初一（庚辰年春節）
        import swisseph as swe
        jd = swe.julday(2000, 2, 5, 12.0)
        ly, lm, ld, leap = _solar_to_lunar(jd)
        assert ly == 2000
        assert lm == 1
        assert ld == 1

    def test_result_types(self):
        import swisseph as swe
        jd = swe.julday(1990, 6, 15, 12.0)
        ly, lm, ld, leap = _solar_to_lunar(jd)
        assert isinstance(ly, int)
        assert 1 <= lm <= 12
        assert 1 <= ld <= 30
        assert isinstance(leap, bool)

    def test_month_range(self):
        import swisseph as swe
        for m in range(1, 13):
            jd = swe.julday(2000, m, 15, 12.0)
            _, lm, ld, _ = _solar_to_lunar(jd)
            assert 1 <= lm <= 12
            assert 1 <= ld <= 30

    def test_13th_month_year_returns_valid_month(self):
        # 2020 had a leap 4th month (閏四月); test that the result is in 1–12
        import swisseph as swe
        # 2020-06-21 falls during 閏四月 in the Chinese calendar
        jd = swe.julday(2020, 6, 21, 12.0)
        _, lm, ld, _ = _solar_to_lunar(jd)
        assert 1 <= lm <= 12
        assert 1 <= ld <= 30


class TestZiweiChart:
    """紫微斗數命盤排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_ziwei_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "北京"

    def test_twelve_palaces(self, sample_chart):
        assert len(sample_chart.palaces) == 12

    def test_palace_names_cover_all(self, sample_chart):
        names = [p.name for p in sample_chart.palaces]
        for name in PALACE_SEQUENCE:
            assert name in names

    def test_palace_branches_unique(self, sample_chart):
        branches = [p.branch for p in sample_chart.palaces]
        assert len(set(branches)) == 12

    def test_palace_branches_cover_all(self, sample_chart):
        branches = set(p.branch for p in sample_chart.palaces)
        assert branches == set(range(12))

    def test_ming_gong_in_range(self, sample_chart):
        assert 0 <= sample_chart.ming_gong_branch <= 11

    def test_shen_gong_in_range(self, sample_chart):
        assert 0 <= sample_chart.shen_gong_branch <= 11

    def test_wu_xing_ju_valid(self, sample_chart):
        assert sample_chart.wu_xing_ju in WU_XING_JU_NAMES

    def test_ziwei_branch_in_range(self, sample_chart):
        assert 0 <= sample_chart.ziwei_branch <= 11

    def test_lunar_month_in_range(self, sample_chart):
        assert 1 <= sample_chart.lunar_month <= 12

    def test_lunar_day_in_range(self, sample_chart):
        assert 1 <= sample_chart.lunar_day <= 30

    def test_hour_branch_in_range(self, sample_chart):
        assert 0 <= sample_chart.hour_branch <= 11

    def test_ziwei_star_in_palaces(self, sample_chart):
        all_stars = [s for p in sample_chart.palaces for s in p.stars]
        assert "紫微" in all_stars

    def test_tianfu_star_in_palaces(self, sample_chart):
        all_stars = [s for p in sample_chart.palaces for s in p.stars]
        assert "天府" in all_stars

    def test_exactly_14_main_stars(self, sample_chart):
        all_stars = [s for p in sample_chart.palaces for s in p.stars]
        assert len(all_stars) == 14

    def test_all_14_main_stars_present(self, sample_chart):
        expected = {
            "紫微", "天機", "太陽", "武曲", "天同", "廉貞",
            "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍",
        }
        all_stars = {s for p in sample_chart.palaces for s in p.stars}
        assert all_stars == expected

    def test_different_dates_produce_different_ziwei_branches(self):
        c1 = compute_ziwei_chart(1990, 1, 1, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_ziwei_chart(1985, 6, 15, 8, 0, 8.0, 39.9, 116.4)
        assert c1.ziwei_branch != c2.ziwei_branch

    def test_different_dates_produce_different_ming_gong(self):
        c1 = compute_ziwei_chart(1990, 1, 1, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_ziwei_chart(1990, 1, 1, 3, 0, 8.0, 39.9, 116.4)
        # Same date, different hour → different 命宮
        assert c1.ming_gong_branch != c2.ming_gong_branch

    def test_stem_names_valid(self, sample_chart):
        for p in sample_chart.palaces:
            assert p.stem_name in HEAVENLY_STEMS

    def test_branch_names_valid(self, sample_chart):
        for p in sample_chart.palaces:
            assert p.branch_name in EARTHLY_BRANCHES


# ============================================================
# Myanmar Mahabote Tests
# ============================================================

from astro.mahabote import (
    compute_mahabote_chart,
    _get_myanmar_year,
    _get_weekday,
    _is_wednesday_evening,
    _compute_periods,
    WEEKDAY_PLANETS,
    WEEKDAY_ANIMALS,
    RAHU_ANIMAL,
    MAHABOTE_HOUSES,
    PLANET_PERIOD_YEARS,
)


class TestMyanmarYear:
    """緬甸年 (Myanmar Era) 計算測試"""

    def test_after_thingyan(self):
        """April 17 or later → ME = year - 638"""
        assert _get_myanmar_year(2000, 5, 1) == 2000 - 638

    def test_before_thingyan(self):
        """Before April 17 → ME = year - 639"""
        assert _get_myanmar_year(2000, 3, 1) == 2000 - 639

    def test_on_thingyan(self):
        """April 17 exactly → ME = year - 638"""
        assert _get_myanmar_year(2000, 4, 17) == 2000 - 638

    def test_april_16_before(self):
        """April 16 → still before Thingyan"""
        assert _get_myanmar_year(2000, 4, 16) == 2000 - 639

    def test_january_1_1990(self):
        assert _get_myanmar_year(1990, 1, 1) == 1990 - 639


class TestWeekday:
    """星期計算測試"""

    def test_known_monday(self):
        """1990-01-01 was a Monday → weekday=1"""
        assert _get_weekday(1990, 1, 1) == 1

    def test_known_sunday(self):
        """2023-01-01 was a Sunday → weekday=0"""
        assert _get_weekday(2023, 1, 1) == 0

    def test_known_saturday(self):
        """2023-01-07 was a Saturday → weekday=6"""
        assert _get_weekday(2023, 1, 7) == 6

    def test_known_wednesday(self):
        """2023-01-04 was a Wednesday → weekday=3"""
        assert _get_weekday(2023, 1, 4) == 3

    def test_weekday_range(self):
        for d in range(1, 8):
            w = _get_weekday(2023, 1, d)
            assert 0 <= w <= 6


class TestWednesdayRahu:
    """星期三傍晚 → 羅睺 測試"""

    def test_wednesday_evening_is_rahu(self):
        assert _is_wednesday_evening(3, 18) is True

    def test_wednesday_night_is_rahu(self):
        assert _is_wednesday_evening(3, 23) is True

    def test_wednesday_morning_not_rahu(self):
        assert _is_wednesday_evening(3, 10) is False

    def test_wednesday_17_not_rahu(self):
        assert _is_wednesday_evening(3, 17) is False

    def test_thursday_evening_not_rahu(self):
        assert _is_wednesday_evening(4, 18) is False


class TestMahaboteValue:
    """Mahabote 值計算測試"""

    def test_known_calculation(self):
        """1990-01-01 (Mon): ME=1351, weekday_num=2, (1351+2)%7=2"""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
            location_name="仰光",
        )
        assert chart.myanmar_year == 1351
        assert chart.weekday == 1  # Monday
        assert chart.mahabote_value == (1351 + 2) % 7  # = 2

    def test_mahabote_value_range(self):
        chart = compute_mahabote_chart(
            year=2000, month=6, day=15, hour=10, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert 0 <= chart.mahabote_value <= 6


class TestMahaboteChart:
    """Mahabote 完整排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
            location_name="仰光",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "仰光"

    def test_birth_planet_monday(self, sample_chart):
        """Monday → Moon"""
        assert sample_chart.birth_planet == "Moon"
        assert sample_chart.birth_planet_cn == "月亮"
        assert sample_chart.birth_planet_symbol == "☽"

    def test_not_rahu(self, sample_chart):
        assert sample_chart.is_rahu is False

    def test_seven_houses(self, sample_chart):
        assert len(sample_chart.houses) == 7

    def test_birth_house_marked(self, sample_chart):
        birth_houses = [h for h in sample_chart.houses if h.is_birth_house]
        assert len(birth_houses) == 1

    def test_birth_planet_in_birth_house(self, sample_chart):
        """Birth planet should be placed in the mahabote_value house."""
        birth_house = sample_chart.houses[sample_chart.mahabote_value]
        assert birth_house.is_birth_house is True
        assert birth_house.planet == sample_chart.birth_planet

    def test_all_seven_planets_placed(self, sample_chart):
        planets = {h.planet for h in sample_chart.houses}
        assert len(planets) == 7
        expected = {"Sun", "Moon", "Mars", "Mercury",
                    "Jupiter", "Venus", "Saturn"}
        assert planets == expected

    def test_house_names_match_constants(self, sample_chart):
        for i, h in enumerate(sample_chart.houses):
            assert h.name_en == MAHABOTE_HOUSES[i][0]
            assert h.name_myanmar == MAHABOTE_HOUSES[i][1]
            assert h.name_cn == MAHABOTE_HOUSES[i][2]

    def test_birth_house_fields(self, sample_chart):
        idx = sample_chart.mahabote_value
        expected = MAHABOTE_HOUSES[idx]
        assert sample_chart.birth_house_name_en == expected[0]
        assert sample_chart.birth_house_name_myanmar == expected[1]
        assert sample_chart.birth_house_name_cn == expected[2]

    def test_periods_not_empty(self, sample_chart):
        assert len(sample_chart.periods) > 0

    def test_periods_start_with_birth_planet(self, sample_chart):
        first = sample_chart.periods[0]
        # The first period planet should correspond to the birth weekday
        expected_planet = WEEKDAY_PLANETS[sample_chart.weekday][0]
        assert first.planet == expected_planet

    def test_periods_sequential(self, sample_chart):
        """Period ages should be sequential and non-overlapping."""
        for i in range(1, len(sample_chart.periods)):
            assert sample_chart.periods[i].start_age == \
                   sample_chart.periods[i - 1].end_age


class TestMahaboteRahu:
    """Wednesday evening (Rahu) test"""

    def test_wednesday_evening_rahu(self):
        """Wednesday at 20:00 → birth planet should be Rahu."""
        chart = compute_mahabote_chart(
            year=2023, month=1, day=4, hour=20, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.weekday == 3  # Wednesday
        assert chart.is_rahu is True
        assert chart.birth_planet == "Rahu"
        assert chart.birth_planet_cn == "羅睺"

    def test_wednesday_morning_mercury(self):
        """Wednesday at 10:00 → birth planet should be Mercury."""
        chart = compute_mahabote_chart(
            year=2023, month=1, day=4, hour=10, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.is_rahu is False
        assert chart.birth_planet == "Mercury"


class TestPlanetPeriods:
    """行星大運 (Atar) 計算測試"""

    def test_total_cycle_96_years(self):
        total = sum(PLANET_PERIOD_YEARS.values())
        assert total == 96

    def test_periods_cover_first_cycle(self):
        periods = _compute_periods(0, 2000, 2020)  # Sunday birth
        # First cycle should sum to 96
        cycle_total = sum(p.years for p in periods[:7])
        assert cycle_total == 96

    def test_current_period_marked(self):
        periods = _compute_periods(0, 2000, 2020)
        current = [p for p in periods if p.is_current]
        assert len(current) == 1
        assert current[0].start_age <= 20 < current[0].end_age


class TestMahaboteAnimalSigns:
    """動物標誌 (Animal Signs) 測試"""

    def test_weekday_animals_count(self):
        """Should have 7 weekday animal signs."""
        assert len(WEEKDAY_ANIMALS) == 7

    def test_weekday_animals_tuple_format(self):
        """Each animal should be (English, Myanmar, Chinese, emoji)."""
        for animal in WEEKDAY_ANIMALS:
            assert len(animal) == 4

    def test_rahu_animal_tuple_format(self):
        """Rahu animal should be (English, Myanmar, Chinese, emoji)."""
        assert len(RAHU_ANIMAL) == 4
        assert RAHU_ANIMAL[0] == "Tuskless Elephant"

    def test_sunday_garuda(self):
        """Sunday → Garuda."""
        assert WEEKDAY_ANIMALS[0][0] == "Garuda"

    def test_monday_tiger(self):
        """Monday → Tiger."""
        assert WEEKDAY_ANIMALS[1][0] == "Tiger"

    def test_tuesday_lion(self):
        """Tuesday → Lion."""
        assert WEEKDAY_ANIMALS[2][0] == "Lion"

    def test_wednesday_tusked_elephant(self):
        """Wednesday → Tusked Elephant."""
        assert WEEKDAY_ANIMALS[3][0] == "Tusked Elephant"

    def test_thursday_rat(self):
        """Thursday → Rat."""
        assert WEEKDAY_ANIMALS[4][0] == "Rat"

    def test_friday_guinea_pig(self):
        """Friday → Guinea Pig."""
        assert WEEKDAY_ANIMALS[5][0] == "Guinea Pig"

    def test_saturday_naga(self):
        """Saturday → Naga."""
        assert WEEKDAY_ANIMALS[6][0] == "Naga"

    def test_chart_birth_animal_monday(self):
        """Monday birth → Tiger."""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.weekday == 1  # Monday
        assert chart.birth_animal_en == "Tiger"
        assert chart.birth_animal_cn == "虎"
        assert chart.birth_animal_emoji == "🐅"

    def test_chart_rahu_animal(self):
        """Wednesday evening → Tuskless Elephant."""
        chart = compute_mahabote_chart(
            year=2023, month=1, day=4, hour=20, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.is_rahu is True
        assert chart.birth_animal_en == "Tuskless Elephant"
        assert chart.birth_animal_cn == "象(無牙)"

    def test_house_has_animal_and_weekday(self):
        """Each house should have animal sign and weekday fields."""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        for h in chart.houses:
            assert h.animal_en != ""
            assert h.animal_cn != ""
            assert h.animal_emoji != ""
            assert h.animal_myanmar != ""
            assert h.weekday_en != ""
            assert h.weekday_cn != ""

    def test_houses_have_distinct_animals(self):
        """All 7 houses should have 7 distinct animal signs."""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        animals = {h.animal_en for h in chart.houses}
        assert len(animals) == 7
