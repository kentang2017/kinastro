"""
七政四餘計算模組測試 (Tests for Seven Governors and Four Remainders Calculator)
"""

import pytest
from astro.calculator import (
    compute_chart,
    format_degree,
    get_mansion_for_degree,
    _normalize_degree,
    _degree_to_sign_index,
    _degree_to_sign_degree,
    _get_western_sign,
    _get_chinese_sign,
)


class TestNormalizeDegree:
    """測試角度標準化"""

    def test_normal_range(self):
        assert _normalize_degree(180.0) == 180.0

    def test_zero(self):
        assert _normalize_degree(0.0) == 0.0

    def test_negative(self):
        assert _normalize_degree(-90.0) == 270.0

    def test_over_360(self):
        assert _normalize_degree(450.0) == 90.0

    def test_exactly_360(self):
        assert _normalize_degree(360.0) == 0.0


class TestDegreeConversions:
    """測試度數轉換"""

    def test_sign_index_aries(self):
        assert _degree_to_sign_index(15.0) == 0  # 白羊

    def test_sign_index_capricorn(self):
        assert _degree_to_sign_index(280.0) == 9  # 摩羯

    def test_sign_index_pisces(self):
        assert _degree_to_sign_index(350.0) == 11  # 雙魚

    def test_sign_degree(self):
        assert abs(_degree_to_sign_degree(280.5) - 10.5) < 0.001

    def test_western_sign(self):
        assert _get_western_sign(280.0) == "摩羯"
        assert _get_western_sign(0.0) == "白羊"
        assert _get_western_sign(120.0) == "獅子"

    def test_chinese_sign(self):
        assert _get_chinese_sign(280.0) == "丑宮(星紀)"
        assert _get_chinese_sign(0.0) == "戌宮(降婁)"


class TestFormatDegree:
    """測試度數格式化"""

    def test_basic_format(self):
        result = format_degree(280.5)
        assert "280°" in result
        assert "30'" in result

    def test_zero(self):
        result = format_degree(0.0)
        assert "0°" in result


class TestGetMansion:
    """測試二十八宿對應"""

    def test_returns_dict(self):
        mansion = get_mansion_for_degree(0.0)
        assert "name" in mansion
        assert "element" in mansion
        assert "group" in mansion

    def test_different_degrees(self):
        m1 = get_mansion_for_degree(0.0)
        m2 = get_mansion_for_degree(180.0)
        assert m1["name"] != m2["name"]


class TestComputeChart:
    """測試排盤計算"""

    @pytest.fixture
    def sample_chart(self):
        """建立測試用排盤 (1990-01-01 12:00 北京)"""
        return compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "北京"

    def test_has_eleven_planets(self, sample_chart):
        """應有 11 顆星曜 (七政 + 四餘)"""
        assert len(sample_chart.planets) == 11

    def test_seven_governors_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets[:7]]
        assert "太陽" in names
        assert "太陰" in names
        assert "水星" in names
        assert "金星" in names
        assert "火星" in names
        assert "木星" in names
        assert "土星" in names

    def test_four_remainders_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets[7:]]
        assert "羅睺" in names
        assert "計都" in names
        assert "月孛" in names
        assert "紫氣" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_house_names(self, sample_chart):
        names = [h.name for h in sample_chart.houses]
        assert "命宮" in names
        assert "夫妻宮" in names
        assert "官祿宮" in names

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_planet_sign_degrees_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sign_degree < 30

    def test_ketu_opposite_rahu(self, sample_chart):
        """計都應在羅睺對面 (相差 180°)"""
        rahu = next(p for p in sample_chart.planets if p.name == "羅睺")
        ketu = next(p for p in sample_chart.planets if p.name == "計都")
        diff = abs(rahu.longitude - ketu.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ziqi_opposite_yuebei(self, sample_chart):
        """紫氣應在月孛對面 (相差 180°)"""
        yuebei = next(p for p in sample_chart.planets if p.name == "月孛")
        ziqi = next(p for p in sample_chart.planets if p.name == "紫氣")
        diff = abs(yuebei.longitude - ziqi.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ascendant_in_range(self, sample_chart):
        assert 0 <= sample_chart.ascendant < 360

    def test_midheaven_in_range(self, sample_chart):
        assert 0 <= sample_chart.midheaven < 360

    def test_sun_in_capricorn_for_jan1(self, sample_chart):
        """1月1日太陽應在摩羯座"""
        sun = sample_chart.planets[0]
        assert sun.sign_western == "摩羯"

    def test_all_planets_assigned_to_houses(self, sample_chart):
        """所有星曜都應被分配到宮位"""
        for p in sample_chart.planets:
            assert 0 <= p.palace_index < 12

    def test_different_dates_produce_different_results(self):
        """不同日期應產生不同結果"""
        chart1 = compute_chart(
            year=2000, month=6, day=15, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
        )
        chart2 = compute_chart(
            year=2020, month=12, day=25, hour=8, minute=30,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
        )
        sun1 = chart1.planets[0].longitude
        sun2 = chart2.planets[0].longitude
        assert abs(sun1 - sun2) > 1.0
