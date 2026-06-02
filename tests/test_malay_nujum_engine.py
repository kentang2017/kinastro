from __future__ import annotations

from datetime import datetime

from astro.malay import MalayNujumEngine


def test_mata_angin_lapan_returns_eight_sectors_and_dominant() -> None:
    engine = MalayNujumEngine()
    result = engine.compute_mata_angin_lapan("Ahmad", datetime(2026, 6, 2, 10, 30))
    assert result["system"] == "mata_angin_lapan"
    assert len(result["sectors"]) == 8
    assert 0 <= result["pelangkah"]["dominant_index"] <= 7


def test_bintang_tujuh_has_star_and_verdict() -> None:
    engine = MalayNujumEngine()
    result = engine.compute_bintang_tujuh("Fatimah", datetime(2026, 6, 2, 10, 30))
    assert result["system"] == "bintang_tujuh"
    assert 1 <= result["star"]["index"] <= 7
    assert result["fortune"]["verdict"] in {"auspicious", "mixed", "inauspicious"}


def test_perkisaran_naga_recommendations_present() -> None:
    engine = MalayNujumEngine()
    result = engine.compute_perkisaran_naga(datetime(2026, 6, 2, 10, 30))
    assert result["system"] == "perkisaran_naga"
    assert result["recommendations"]["construction"]
    assert result["recommendations"]["planting"]


def test_bintang_duabelas_plus_contains_abjad_profiles() -> None:
    engine = MalayNujumEngine()
    result = engine.compute_bintang_duabelas_plus("Ahmad", "Khadijah")
    assert result["system"] == "bintang_duabelas_plus"
    assert result["name_profile"]["abjad_total"] > 0
    assert "interpretation_template" in result
