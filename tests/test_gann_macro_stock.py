from datetime import date, datetime

import pytest

from astro.qizheng.financial.gann_macro_stock import (
    build_gann_macro_timing,
    compute_anniversary_dates,
    compute_biblical_cycle_dates,
    find_nearest_square_of_nine_levels,
    compute_square_of_nine_levels,
    evaluate_qizheng_resonance,
    scale_cycle_to_days,
)


def test_scale_cycle_to_days_basic():
    days = scale_cycle_to_days(3.5, scale=1.0, year_basis_days=360.0)
    assert days == int(round(3.5 * 360.0 * 1.0))  # 3.5 年 × 360 天 = 1260


def test_compute_biblical_cycle_dates_includes_scaled_day_for_year():
    rows = compute_biblical_cycle_dates(
        anchor_date=date(2020, 1, 1),
        as_of_date=date(2020, 2, 10),
        scale=0.1,
        year_basis_days=365.0,
        lookback_years=1.0,
        lookahead_years=1.0,
        max_multiple=3,
    )
    assert rows
    assert any(r["cycle_key"] == "day_for_year" for r in rows)


def test_evaluate_qizheng_resonance_scores():
    natal = {"木星": 10.0, "土星": 20.0}
    transit = {"木星": 10.5, "土星": 110.0}
    rows = evaluate_qizheng_resonance(natal, transit, orb=3.0)
    assert len(rows) == 2
    jupiter = next(r for r in rows if r["star"] == "木星")
    saturn = next(r for r in rows if r["star"] == "土星")
    assert jupiter["aspect"] == "合"
    assert jupiter["score"] == 3
    assert saturn["aspect"] == "刑"
    assert saturn["score"] == -2


def test_build_gann_macro_timing_with_injected_maps():
    result = build_gann_macro_timing(
        market_natal_date=date(2020, 1, 1),
        as_of_datetime=datetime(2020, 2, 10, 12, 0),
        timezone=8.0,
        cycle_scale=0.1,
        cycle_orb_days=30,
        natal_longitudes={"木星": 10.0, "土星": 20.0},
        transit_longitudes={"木星": 10.2, "土星": 20.0},
    )
    assert "scores" in result
    assert result["scores"]["total_score"] > 0
    assert result["near_cycle_hits"]


def test_compute_square_of_nine_levels():
    levels = compute_square_of_nine_levels(reference_price=100.0, max_ring=1)
    assert len(levels) == 16
    assert levels[0]["target_price"] > 0
    assert any(row["angle"] == 45 for row in levels)


def test_compute_square_of_nine_levels_invalid():
    with pytest.raises(ValueError):
        compute_square_of_nine_levels(reference_price=0.0)


def test_compute_square_of_nine_levels_descending_and_step():
    levels = compute_square_of_nine_levels(
        reference_price=100.0,
        max_ring=1,
        angle_step=90,
        include_descending=True,
    )
    assert levels
    assert any(row["direction"] == "down" for row in levels)
    assert any(row["angle"] == 270 for row in levels)


def test_compute_square_of_nine_levels_cardinal_current_price():
    levels = compute_square_of_nine_levels(
        reference_price=100.0,
        current_price=121.0,
        max_ring=1,
        angle_step=45,
        angle_system="cardinal",
        include_descending=True,
    )
    assert levels
    assert all(row["angle"] in {0, 90, 180, 270} for row in levels)
    assert any(row["direction"] == "up" for row in levels)
    assert any(row["direction"] == "down" for row in levels)
    assert all("turn" in row for row in levels)


def test_find_nearest_square_of_nine_levels():
    result = find_nearest_square_of_nine_levels(current_price=123.0, reference_price=100.0, max_ring=2)
    assert result["nearest_level"] is not None
    assert result["support_level"]["target_price"] <= 123.0
    assert result["resistance_level"]["target_price"] >= 123.0
    assert result["distance_to_nearest"] >= 0


def test_compute_anniversary_dates_basic():
    rows = compute_anniversary_dates(
        anchor_date=date(2020, 1, 1),
        as_of_date=date(2022, 1, 1),
        lookback_years=1.0,
        lookahead_years=1.0,
        monthly_step=6,
    )
    assert rows
    assert any(x["type"] == "yearly_anniversary" for x in rows)
    assert any(x["type"] == "monthly_anniversary" for x in rows)


def test_compute_anniversary_dates_supports_multiple_anchors_and_day_windows():
    rows = compute_anniversary_dates(
        anchor_date=date(2020, 1, 1),
        anchor_dates=[date(2020, 1, 1), date(2020, 3, 1)],
        as_of_date=date(2020, 5, 30),
        lookback_years=0.5,
        lookahead_years=0.5,
        monthly_step=3,
    )
    assert any(row["type"] == "gann_day_window" and row["base_days"] == 45 for row in rows)
    assert any(row["anchor_date"] == "2020-03-01" for row in rows)
    assert any(row["gann_harmonic"] == "1/4年" for row in rows if row["base_days"] in {90, 91, 92})


def test_compute_anniversary_dates_trading_day_alignment():
    rows = compute_anniversary_dates(
        anchor_date=date(2020, 1, 31),
        as_of_date=date(2020, 4, 30),
        lookback_years=0.5,
        lookahead_years=0.5,
        monthly_step=1,
        use_trading_days=True,
        include_day_windows=False,
    )
    monthly = next(row for row in rows if row["type"] == "monthly_anniversary")
    assert monthly["use_trading_days"] is True
    assert date.fromisoformat(monthly["due_date"]).weekday() < 5


def test_build_gann_macro_timing_contains_anniversary_scores():
    result = build_gann_macro_timing(
        market_natal_date=date(2020, 1, 1),
        as_of_datetime=datetime(2020, 2, 10, 12, 0),
        timezone=8.0,
        cycle_scale=0.1,
        cycle_orb_days=30,
        natal_longitudes={"木星": 10.0, "土星": 20.0},
        transit_longitudes={"木星": 10.2, "土星": 20.0},
    )
    assert "anniversary_hits" in result
    assert "anniversary_score" in result["scores"]
