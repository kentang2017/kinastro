import sys
import types
import re


def test_mansion_ring_uses_compact_planet_labels(monkeypatch):
    streamlit_stub = types.SimpleNamespace(
        subheader=lambda *args, **kwargs: None,
        markdown=lambda *args, **kwargs: None,
    )
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)

    from astro.qizheng.calculator import compute_chart
    from ui.handlers.tab_chinese import render as qizheng_render

    chart = compute_chart(
        year=1990, month=1, day=1, hour=12, minute=0,
        timezone=8.0, latitude=22.3193, longitude=114.1694,
        location_name="Hong Kong", gender="male",
    )

    svg = qizheng_render.render_mansion_ring(chart)

    assert re.search(r">木(?:℞)?<", svg)
    assert ">木星<" not in svg
    assert "木·木星" not in svg
