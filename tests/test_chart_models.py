"""Focused tests for unified KinAstro chart models."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import astro
from astro.models import BirthData, western_chart_to_result, ziwei_chart_to_result


def test_birth_data_normalizes_gender_and_validates_bounds() -> None:
    """BirthData should normalize gender and reject invalid coordinates."""
    birth_data = BirthData(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=30,
        timezone=8,
        latitude=25.03,
        longitude=121.56,
        gender="male",
    )

    assert birth_data.legacy_gender == "男"
    assert birth_data.to_compute_kwargs(include_gender=True)["gender"] == "男"

    with pytest.raises(ValueError):
        BirthData(
            year=1990,
            month=1,
            day=1,
            hour=12,
            minute=30,
            timezone=8,
            latitude=95,
            longitude=121.56,
        )


def test_western_legacy_chart_converts_to_unified_result() -> None:
    """Legacy western dataclasses should map into WesternChartResult."""
    legacy_chart = SimpleNamespace(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8.0,
        latitude=25.03,
        longitude=121.56,
        location_name="Taipei",
        julian_day=2447893.5,
        planets=[
            SimpleNamespace(
                name="Sun ☉",
                longitude=280.0,
                latitude=0.0,
                sign="Capricorn",
                sign_glyph="♑",
                sign_chinese="摩羯座",
                sign_degree=10.0,
                element="Earth",
                retrograde=False,
                house=10,
                essential_dignity="—",
                joy_status="—",
                fixed_star_conjunctions=[],
            )
        ],
        houses=[
            SimpleNamespace(
                number=1,
                cusp=15.0,
                sign="Aries",
                sign_glyph="♈",
                planets=["Sun ☉"],
            )
        ],
        ascendant=15.0,
        midheaven=280.0,
        asc_sign="Aries",
        mc_sign="Capricorn",
        is_day_chart=True,
        chart_ruler="Mars ♂",
        chart_ruler_dignity="domicile",
        lot_of_fortune=123.4,
        arabic_parts=[
            SimpleNamespace(
                english_name="Lot of Fortune",
                chinese_name="幸運點",
                longitude=123.4,
                sign="Leo",
                sign_glyph="♌",
                sign_chinese="獅子座",
                sign_degree=3.4,
                house=5,
            )
        ],
        fixed_star_conjunctions=[
            SimpleNamespace(
                star_name="Regulus",
                star_name_cn="軒轅十四",
                star_longitude=150.0,
                planet_name="Sun ☉",
                orb=0.5,
                meaning="royalty",
            )
        ],
        sidereal_mode=False,
        ayanamsa=0.0,
    )

    result = western_chart_to_result(legacy_chart)

    assert result.system == "western"
    assert result.birth_data.location_name == "Taipei"
    assert result.planets[0].name == "Sun ☉"
    assert result.house_system is not None
    assert result.house_system.cusps[0].occupants == ["Sun ☉"]
    assert result.fixed_stars[0].name == "Regulus"


def test_ziwei_legacy_chart_converts_to_unified_result() -> None:
    """Legacy Ziwei dataclasses should map into ZiweiChartResult."""
    legacy_chart = SimpleNamespace(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8.0,
        latitude=25.03,
        longitude=121.56,
        location_name="Taipei",
        julian_day=2447893.5,
        gender="男",
        lunar_year=1989,
        lunar_month=12,
        lunar_day=5,
        is_leap_month=False,
        lunar_year_stem=5,
        lunar_year_branch=5,
        hour_branch=6,
        ming_gong_branch=2,
        shen_gong_branch=8,
        wu_xing_ju=4,
        ziwei_branch=1,
        yin_yang="陽",
        ming_zhu="貪狼",
        shen_zhu="火星",
        sihua={"太陽": "化祿"},
        palaces=[
            SimpleNamespace(
                index=0,
                name="命宮",
                branch=2,
                branch_name="寅",
                stem=0,
                stem_name="甲",
                stars=["紫微"],
                aux_stars=["文昌"],
                brightness={"紫微": "廟"},
                sihua={"太陽": "化祿"},
                da_xian="3~12",
                da_xian_start=3,
                liu_nian_ages=[3, 4],
                xiao_xian_ages=[1, 13],
            )
        ],
        sanhe_groups=[(2, 6, 10)],
        vietnam_mode=False,
    )

    result = ziwei_chart_to_result(legacy_chart)

    assert result.system == "ziwei"
    assert result.lunar_date.month == 12
    assert result.palaces[0].name == "命宮"
    assert result.palaces[0].auxiliary_stars == ["文昌"]
    assert result.sanhe_groups == [[2, 6, 10]]


def test_compute_chart_dispatches_through_unified_registry() -> None:
    """astro.compute_chart should use the unified registry adapters."""
    birth_data = BirthData(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8,
        latitude=25.03,
        longitude=121.56,
    )
    sentinel = {"ok": True}

    astro.register_chart_computer("mock_system", lambda _: sentinel)

    assert astro.compute_chart("mock_system", birth_data) is sentinel
