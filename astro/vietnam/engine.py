"""Core engine for Vietnam Tử Vi module (shared Ziwei core + VN layers)."""

from __future__ import annotations

from dataclasses import replace

from astro.vietnam.comparison import build_comparison
from astro.vietnam.data.stars import get_star_profile
from astro.vietnam.interpreter import build_interpretation
from astro.vietnam.lunar import resolve_birth_date
from astro.vietnam.models import StarProfileVN, TuViChart, TuViInput
from astro.vietnam.remedies import suggest_remedies
from astro.vietnam.renderer import build_12_palace_svg
from astro.ziwei import compute_ziwei_chart


def compute_vietnam_tu_vi_chart(**kwargs) -> TuViChart:
    """Compute Vietnam Tử Vi chart by reusing Ziwei placement core."""
    payload = TuViInput(**kwargs)
    year, month, day, lunar_meta = resolve_birth_date(payload)

    base_chart = compute_ziwei_chart(
        year=year,
        month=month,
        day=day,
        hour=payload.hour,
        minute=payload.minute,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_name=payload.location_name,
        gender=payload.gender,
        vietnam_mode=True,
    )
    chinese_base = compute_ziwei_chart(
        year=year,
        month=month,
        day=day,
        hour=payload.hour,
        minute=payload.minute,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_name=payload.location_name,
        gender=payload.gender,
        vietnam_mode=False,
    )

    ming_palace = next((p for p in base_chart.palaces if p.branch == base_chart.ming_gong_branch), None)
    stars = [s for palace in base_chart.palaces for s in palace.stars + palace.aux_stars]
    unique_stars = list(dict.fromkeys(stars))

    star_profiles: dict[str, StarProfileVN] = {}
    for star in unique_stars:
        profile = get_star_profile(star)
        if profile:
            star_profiles[star] = profile

    interpretation = build_interpretation(
        stars=unique_stars,
        ming_palace_name=ming_palace.name if ming_palace else "命宮",
        da_xian=ming_palace.da_xian if ming_palace else "",
        interpret_mode=payload.interpret_mode,
        lang=payload.lang,
    )

    comparison = build_comparison(
        chinese_emphasis="傳統紫微以星曜格局與四化吉凶為主。",
        vietnam_emphasis="Trung Châu 側重心理、生理與後天實踐策略。",
        stars=unique_stars,
    )

    remedies = suggest_remedies(unique_stars, payload.lang)

    lunar_profile = {
        **lunar_meta,
        "resolved_lunar": {
            "year": base_chart.lunar_year,
            "month": base_chart.lunar_month,
            "day": base_chart.lunar_day,
            "is_leap": base_chart.is_leap_month,
        },
        "chinese_baseline_lunar": {
            "year": chinese_base.lunar_year,
            "month": chinese_base.lunar_month,
            "day": chinese_base.lunar_day,
            "is_leap": chinese_base.is_leap_month,
        },
    }

    visual = {"svg_12_palace": ""}
    result = TuViChart(
        system="vietnam_tu_vi",
        input_data=payload,
        solar_date_used=f"{year:04d}-{month:02d}-{day:02d}",
        lunar_profile=lunar_profile,
        base_chart=base_chart,
        interpretation_mode=payload.interpret_mode,
        language=payload.lang,
        star_profiles=star_profiles,
        interpretation=interpretation,
        remedies=remedies,
        comparison=comparison,
        visual=visual,
    )
    return replace(result, visual={"svg_12_palace": build_12_palace_svg(result, payload.lang)})
