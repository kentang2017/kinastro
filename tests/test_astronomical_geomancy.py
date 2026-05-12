"""
tests/test_astronomical_geomancy.py
════════════════════════════════════
Unit tests for the Astronomical Geomancy module
(Gerardus Cremonensis, 天文幾何占卜).
"""

from __future__ import annotations

import pytest

from astro.astronomical_geomancy.calculator import (
    compute_geomancy_chart,
    format_geomancy_for_prompt,
    _generate_figure,
    _build_houses,
    _place_planets,
)
from astro.astronomical_geomancy.constants import (
    FIGURES,
    PLANETS,
    ZODIAC_SIGNS,
    QUESTION_TYPES,
)
from astro.astronomical_geomancy.models import (
    GeomancyChart,
    GeomancyFigure,
    HouseInfo,
    PlanetInHouse,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

def test_figures_count():
    """There must be exactly 16 geomantic figures."""
    assert len(FIGURES) == 16


def test_all_figures_have_required_keys():
    required = {"name_en", "name_zh", "dots", "element", "planet", "sign", "sign_num", "quality"}
    for name, data in FIGURES.items():
        missing = required - set(data.keys())
        assert not missing, f"Figure '{name}' missing keys: {missing}"


def test_figure_dots_are_4_booleans():
    for name, data in FIGURES.items():
        dots = data["dots"]
        assert len(dots) == 4, f"Figure '{name}' has {len(dots)} rows, expected 4"
        assert all(isinstance(d, bool) for d in dots), f"Figure '{name}' dots must be bools"


def test_zodiac_signs_count():
    assert len(ZODIAC_SIGNS) == 12


def test_planets_count():
    """Must have exactly 9 bodies (7 planets + Caput + Cauda)."""
    assert len(PLANETS) == 9


def test_question_types_count():
    assert len(QUESTION_TYPES) >= 10


def test_all_signs_covered():
    """Every zodiac sign must appear in at least one figure's mapping."""
    sign_nums_covered = {d["sign_num"] for d in FIGURES.values()}
    for i in range(12):
        assert i in sign_nums_covered, f"Sign index {i} ({ZODIAC_SIGNS[i]['en']}) not covered"


# ─────────────────────────────────────────────────────────────────────────────
# Figure generation
# ─────────────────────────────────────────────────────────────────────────────

def test_generate_figure_returns_valid_figure():
    import random
    rng = random.Random(42)
    fig = _generate_figure(rng)
    assert isinstance(fig, GeomancyFigure)
    assert fig.name_en in {d["name_en"] for d in FIGURES.values()}
    assert len(fig.dots) == 4


def test_generate_figure_deterministic_with_seed():
    import random
    rng1 = random.Random(123)
    rng2 = random.Random(123)
    fig1 = _generate_figure(rng1)
    fig2 = _generate_figure(rng2)
    assert fig1.name_en == fig2.name_en
    assert fig1.dots == fig2.dots


# ─────────────────────────────────────────────────────────────────────────────
# House building
# ─────────────────────────────────────────────────────────────────────────────

def test_build_houses_returns_12_houses():
    houses = _build_houses(0)
    assert len(houses) == 12


def test_build_houses_sequential_signs():
    """Starting at sign 0 (Aries), house 2 should be Taurus, etc."""
    houses = _build_houses(0)
    for i, house in enumerate(houses):
        expected_sign = ZODIAC_SIGNS[i]["en"]
        assert house.sign == expected_sign, (
            f"House {i+1}: expected {expected_sign}, got {house.sign}"
        )


def test_build_houses_wraps_around():
    """Starting at sign 11 (Pisces), house 2 should be Aries (index 0)."""
    houses = _build_houses(11)
    assert houses[0].sign == "Pisces"
    assert houses[1].sign == "Aries"
    assert houses[11].sign == "Aquarius"


def test_build_houses_numbering():
    houses = _build_houses(3)
    for i, h in enumerate(houses):
        assert h.house == i + 1


# ─────────────────────────────────────────────────────────────────────────────
# Planet placement
# ─────────────────────────────────────────────────────────────────────────────

def test_place_planets_returns_9_entries():
    import random
    rng = random.Random(1)
    houses = _build_houses(0)
    placements = _place_planets(rng, houses)
    assert len(placements) == 9


def test_planet_houses_in_range():
    import random
    rng = random.Random(7)
    houses = _build_houses(0)
    placements = _place_planets(rng, houses)
    for p in placements:
        assert 1 <= p.house <= 12, f"{p.planet_en} has invalid house {p.house}"


def test_planet_placements_assigned_to_house_planets():
    import random
    rng = random.Random(99)
    houses = _build_houses(0)
    placements = _place_planets(rng, houses)
    # All planet placements should be reflected in house.planets
    for p in placements:
        house = houses[p.house - 1]
        assert any(hp.planet_key == p.planet_key for hp in house.planets), (
            f"{p.planet_en} not found in house {p.house}.planets"
        )


# ─────────────────────────────────────────────────────────────────────────────
# compute_geomancy_chart
# ─────────────────────────────────────────────────────────────────────────────

def test_compute_basic():
    chart = compute_geomancy_chart(
        question="Test question",
        question_type="wealth",
        seed_mode="manual",
        manual_seed=42,
    )
    assert isinstance(chart, GeomancyChart)
    assert len(chart.houses) == 12
    assert len(chart.planet_placements) == 9
    assert len(chart.mother_figures) == 4
    assert chart.question == "Test question"
    assert chart.question_type == "wealth"


def test_compute_deterministic():
    """Same seed should produce identical charts."""
    chart1 = compute_geomancy_chart(seed_mode="manual", manual_seed=555)
    chart2 = compute_geomancy_chart(seed_mode="manual", manual_seed=555)
    assert chart1.ascendant_sign == chart2.ascendant_sign
    assert chart1.ascendant_figure.name_en == chart2.ascendant_figure.name_en
    for p1, p2 in zip(chart1.planet_placements, chart2.planet_placements):
        assert p1.house == p2.house


def test_compute_different_seeds_differ():
    """Different seeds should (almost always) produce different results."""
    chart1 = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    chart2 = compute_geomancy_chart(seed_mode="manual", manual_seed=99999)
    # At least one planet should be in a different house
    diffs = sum(
        1 for p1, p2 in zip(chart1.planet_placements, chart2.planet_placements)
        if p1.house != p2.house
    )
    assert diffs > 0 or chart1.ascendant_sign != chart2.ascendant_sign


def test_ascendant_sign_is_valid():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=123)
    valid_signs = [s["en"] for s in ZODIAC_SIGNS]
    assert chart.ascendant_sign in valid_signs


def test_houses_use_consecutive_signs():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=7)
    asc_idx = chart.ascendant_sign_num
    for i, house in enumerate(chart.houses):
        expected_idx = (asc_idx + i) % 12
        assert house.sign_num == expected_idx, (
            f"House {i+1}: expected sign index {expected_idx}, got {house.sign_num}"
        )


def test_time_seed_mode():
    """time_seed mode should produce a valid chart."""
    chart = compute_geomancy_chart(seed_mode="time_seed")
    assert isinstance(chart, GeomancyChart)
    assert chart.seed_mode == "time_seed"
    assert chart.seed > 0


def test_random_mode():
    chart = compute_geomancy_chart(seed_mode="random")
    assert isinstance(chart, GeomancyChart)
    assert chart.seed_mode == "random"


def test_to_json():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=10)
    d = chart.to_json()
    assert "question" in d
    assert "houses" in d
    assert "planet_placements" in d
    assert len(d["houses"]) == 12
    assert len(d["planet_placements"]) == 9


# ─────────────────────────────────────────────────────────────────────────────
# Prompt formatting
# ─────────────────────────────────────────────────────────────────────────────

def test_format_prompt_zh():
    chart = compute_geomancy_chart(
        question="我今年財運如何",
        question_type="wealth",
        seed_mode="manual",
        manual_seed=42,
    )
    prompt = format_geomancy_for_prompt(chart, lang="zh")
    assert "天文幾何占卜" in prompt
    assert "我今年財運如何" in prompt
    assert "第1宮" in prompt
    assert "上升圖形" in prompt


def test_format_prompt_en():
    chart = compute_geomancy_chart(
        question="What is my fortune this year?",
        question_type="wealth",
        seed_mode="manual",
        manual_seed=42,
    )
    prompt = format_geomancy_for_prompt(chart, lang="en")
    assert "Astronomical Geomancy" in prompt
    assert "What is my fortune" in prompt
    assert "House 1" in prompt
    assert "Ascendant Figure" in prompt


# ─────────────────────────────────────────────────────────────────────────────
# Question types
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("qtype", [
    "life", "health", "wealth", "marriage", "career",
    "children", "journey", "religion", "enemy", "death", "custom",
])
def test_question_type_maps_to_primary_house(qtype):
    chart = compute_geomancy_chart(
        question_type=qtype,
        seed_mode="manual",
        manual_seed=1,
    )
    assert 1 <= chart.primary_house <= 12


def test_unknown_question_type_defaults_to_custom():
    chart = compute_geomancy_chart(
        question_type="nonexistent_type",
        seed_mode="manual",
        manual_seed=1,
    )
    # Should not raise, primary_house should be valid
    assert 1 <= chart.primary_house <= 12


# ─────────────────────────────────────────────────────────────────────────────
# Timestamp
# ─────────────────────────────────────────────────────────────────────────────

def test_chart_has_timestamp():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    assert "UTC" in chart.timestamp
    assert len(chart.timestamp) > 10
