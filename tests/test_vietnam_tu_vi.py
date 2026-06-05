from astro.vietnam import compute_vietnam_tu_vi_chart


def _sample_kwargs():
    return {
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "timezone": 7.0,
        "latitude": 10.8231,
        "longitude": 106.6297,
        "location_name": "Ho Chi Minh City",
        "gender": "男",
        "calendar_mode": "solar_gregorian",
        "interpret_mode": "trung_chau_tam_hop",
        "lang": "vi",
    }


def test_compute_vietnam_tu_vi_chart_basic():
    chart = compute_vietnam_tu_vi_chart(**_sample_kwargs())
    assert chart.system == "vietnam_tu_vi"
    assert len(chart.base_chart.palaces) == 12
    assert chart.interpretation_mode == "trung_chau_tam_hop"
    assert chart.language == "vi"


def test_compute_vietnam_tu_vi_has_required_sections():
    chart = compute_vietnam_tu_vi_chart(**_sample_kwargs())
    assert chart.interpretation.personality
    assert chart.interpretation.dai_han
    assert chart.interpretation.luu_nien
    assert chart.remedies
    assert chart.comparison
    assert "svg_12_palace" in chart.visual


def test_compute_vietnam_tu_vi_traditional_mode():
    kwargs = _sample_kwargs()
    kwargs["interpret_mode"] = "traditional_cn"
    kwargs["lang"] = "zh"
    chart = compute_vietnam_tu_vi_chart(**kwargs)
    assert chart.interpretation_mode == "traditional_cn"
    assert "大限" in chart.interpretation.dai_han
