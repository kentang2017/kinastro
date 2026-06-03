from astro.myanmar import compute_myanmar_mahabote_chart, gregorian_to_myanmar_year


def test_myanmar_year_cutoff_rule():
    assert gregorian_to_myanmar_year(2026, 4, 14) == 1387
    assert gregorian_to_myanmar_year(2026, 4, 15) == 1388


def test_chart_builds_eight_houses_and_polarity_groups():
    chart = compute_myanmar_mahabote_chart(
        year=1990,
        month=1,
        day=1,
        hour=10,
        minute=30,
        timezone=6.5,
        latitude=16.8661,
        longitude=96.1951,
        location_name="Yangon",
    )
    assert len(chart.houses) == 8
    assert len(chart.positive_houses) == 4
    assert len(chart.liability_houses) == 4
    assert chart.start_house_name_en == "Marana"
    assert chart.zodiac_wheel_svg.startswith("<svg")
    assert chart.house_board_svg.startswith("<svg")


def test_chart_includes_bilingual_direction_and_remedies():
    chart = compute_myanmar_mahabote_chart(
        year=2001,
        month=7,
        day=9,
        hour=20,
        minute=0,
    )
    assert chart.natal_direction_en
    assert chart.natal_direction_zh
    assert chart.natal_remedies_en
    assert chart.natal_remedies_zh
    assert chart.current_year_overlay is not None
    assert chart.target_year_overlay is not None
