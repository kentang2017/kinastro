"""Focused tests for the structured Ziwei interpretation layer."""

from __future__ import annotations

from astro.interpretation import (
    InterpretationProviderConfig,
    ZiweiInterpretationResult,
    generate_ziwei_interpretation,
)
from astro.models import BirthData, LunarDate, ZiweiChartResult, ZiweiPalace


def _build_sample_chart() -> ZiweiChartResult:
    birth_data = BirthData(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8,
        latitude=22.3193,
        longitude=114.1694,
        location_name="Hong Kong",
        gender="male",
    )
    palaces = [
        ZiweiPalace(
            index=0,
            name="命宮",
            branch=4,
            branch_name="辰",
            stem=0,
            stem_name="甲",
            stars=["紫微", "天府"],
            auxiliary_stars=["左輔", "右弼"],
            brightness={"紫微": "廟", "天府": "旺"},
            sihua={"紫微": "祿"},
            da_xian="3-12",
            da_xian_start=3,
        ),
        ZiweiPalace(
            index=1,
            name="官祿",
            branch=8,
            branch_name="申",
            stem=1,
            stem_name="乙",
            stars=["武曲", "七殺"],
            auxiliary_stars=["文昌"],
            brightness={"武曲": "旺"},
            da_xian="13-22",
            da_xian_start=13,
        ),
        ZiweiPalace(
            index=2,
            name="遷移",
            branch=0,
            branch_name="子",
            stem=2,
            stem_name="丙",
            stars=["廉貞"],
            auxiliary_stars=["天魁"],
            sihua={"廉貞": "忌"},
            da_xian="23-32",
            da_xian_start=23,
        ),
        ZiweiPalace(
            index=3,
            name="財帛",
            branch=10,
            branch_name="戌",
            stem=3,
            stem_name="丁",
            stars=["太陰"],
            da_xian="33-42",
            da_xian_start=33,
        ),
    ]
    return ZiweiChartResult(
        birth_data=birth_data,
        lunar_date=LunarDate(year=1989, month=12, day=5, is_leap_month=False),
        gender="male",
        hour_branch=6,
        ming_gong_branch=4,
        shen_gong_branch=8,
        wu_xing_ju=5,
        ziwei_branch=4,
        yin_yang="陽男",
        ming_zhu="祿存",
        shen_zhu="天相",
        sihua={"紫微": "祿", "廉貞": "忌"},
        palaces=palaces,
        sanhe_groups=[[4, 8, 0]],
    )


def test_traditional_ziwei_interpretation_stays_local(monkeypatch):
    """Traditional mode should not call any LLM provider."""
    chart = _build_sample_chart()

    def _unexpected_provider_call(**_kwargs):
        raise AssertionError("provider should not be called in traditional mode")

    monkeypatch.setattr(
        "astro.interpretation.ziwei.request_llm_completion",
        _unexpected_provider_call,
    )
    result = generate_ziwei_interpretation(chart, mode="traditional")
    assert isinstance(result, ZiweiInterpretationResult)
    assert result.provider == "traditional"
    assert "命宮" in result.ming_gong_analysis
    assert "四化" in result.final_text


def test_hybrid_ziwei_interpretation_includes_ai_notes(monkeypatch):
    """Hybrid mode should retain structure and append AI notes."""
    chart = _build_sample_chart()
    monkeypatch.setattr(
        "astro.interpretation.ziwei.request_llm_completion",
        lambda **_kwargs: "AI 補充：此盤適合以制度化方式放大命宮資源。",
    )
    result = generate_ziwei_interpretation(
        chart,
        mode="hybrid",
        provider_config=InterpretationProviderConfig(provider="ollama"),
    )
    assert "AI 補充" in result.ai_enhanced_notes
    assert result.provider.startswith("Ollama")
    assert "AI Enhanced Notes" in result.final_text
