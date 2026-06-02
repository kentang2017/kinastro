import astro.polynesian_hawaiian as polynesian_hawaiian


def test_polynesian_hawaiian_exports_legacy_renderer_entrypoint():
    assert callable(polynesian_hawaiian.render_streamlit)


def test_polynesian_hawaiian_exports_legacy_compute_entrypoint():
    assert callable(polynesian_hawaiian.compute_polynesian_chart)
