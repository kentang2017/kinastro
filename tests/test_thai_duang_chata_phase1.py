"""Phase-1 tests for astro/thai/duang_chata.py and astro/thai/renderer.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DUANG_FILE = REPO_ROOT / "astro" / "thai" / "duang_chata.py"
RENDER_FILE = REPO_ROOT / "astro" / "thai" / "renderer.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_compute_duang_chata_basic_structure():
    mod = _load_module(DUANG_FILE, "duang_chata_phase1")

    chart = mod.compute_duang_chata(
        year=1992,
        month=7,
        day=14,
        hour=9,
        minute=30,
        timezone=7.0,
        latitude=13.7563,
        longitude=100.5018,
        location_name="Bangkok",
        house_system="whole_sign",
        target_year=2026,
    )

    assert len(chart.planets) == 9
    assert len(chart.houses) == 12
    assert 1 <= chart.fortune_number <= 9
    assert chart.annual_trend.target_year == 2026
    assert 1 <= chart.annual_trend.activated_house <= 12

    pkeys = {p.key for p in chart.planets}
    assert {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}.issubset(pkeys)

    rahu = next(p for p in chart.planets if p.key == "rahu")
    ketu = next(p for p in chart.planets if p.key == "ketu")
    opp = ((ketu.longitude - rahu.longitude) % 360.0)
    assert abs(opp - 180.0) < 1e-6


def test_house_system_switch_and_serialization():
    mod = _load_module(DUANG_FILE, "duang_chata_phase1_hsys")

    chart = mod.compute_duang_chata(
        year=1988,
        month=11,
        day=23,
        hour=21,
        minute=15,
        timezone=7.0,
        latitude=13.7563,
        longitude=100.5018,
        house_system="thai_traditional",
    )

    payload = mod.chart_to_dict(chart)
    assert payload["meta"]["house_system"] == "thai_traditional"
    assert len(payload["houses"]) == 12
    assert len(payload["planets"]) == 9


def test_renderer_svg_output():
    mod = _load_module(DUANG_FILE, "duang_chata_phase1_for_svg")
    renderer = _load_module(RENDER_FILE, "duang_renderer_phase1")

    chart = mod.compute_duang_chata(
        year=2001,
        month=2,
        day=1,
        hour=6,
        minute=0,
        timezone=7.0,
        latitude=13.7563,
        longitude=100.5018,
    )

    svg = renderer.build_duang_chata_svg(chart, lang="zh")
    assert "<svg" in svg
    assert "命數" in svg
    assert "☊" in svg or "☋" in svg
