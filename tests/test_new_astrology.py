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
