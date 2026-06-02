"""Bintang Tujuh calculations combining abjad and timing."""

from __future__ import annotations

from datetime import datetime

import swisseph as swe

from .common import compute_name_abjad_profile, summarize_moment


_STAR_TABLE: tuple[dict[str, object], ...] = (
    {"index": 1, "name_zh": "Bintang Raja", "name_en": "Royal Star", "base": 4},
    {"index": 2, "name_zh": "Bintang Rezeki", "name_en": "Provision Star", "base": 3},
    {"index": 3, "name_zh": "Bintang Safar", "name_en": "Travel Star", "base": 2},
    {"index": 4, "name_zh": "Bintang Hikmah", "name_en": "Wisdom Star", "base": 4},
    {"index": 5, "name_zh": "Bintang Ujian", "name_en": "Trial Star", "base": 1},
    {"index": 6, "name_zh": "Bintang Dagang", "name_en": "Trade Star", "base": 3},
    {"index": 7, "name_zh": "Bintang Penutup", "name_en": "Closure Star", "base": 2},
)


def _moon_phase_bucket(moment: datetime) -> int:
    jd = swe.julday(moment.year, moment.month, moment.day, moment.hour + moment.minute / 60.0)
    moon_val, _ = swe.calc_ut(jd, swe.MOON)
    sun_val, _ = swe.calc_ut(jd, swe.SUN)
    phase_angle = (float(moon_val[0]) - float(sun_val[0])) % 360.0
    return int(phase_angle // 45.0)


def compute_bintang_tujuh(
    name: str,
    moment: datetime,
    *,
    script_hint: str = "auto",
) -> dict[str, object]:
    """Compute seven-star timing fortune with name-abjad."""
    profile = compute_name_abjad_profile(name, script_hint=script_hint)
    abjad_mod = int(profile["abjad_total"]) % 7
    weekday_seed = moment.weekday() % 7
    clock_seed = ((moment.hour * 60 + moment.minute) // 210) % 7
    moon_bucket = _moon_phase_bucket(moment)

    star_index = (abjad_mod + weekday_seed + clock_seed + moon_bucket) % 7
    star = _STAR_TABLE[star_index]
    score = int(star["base"]) + (2 if moon_bucket in (0, 1, 6, 7) else 0) + (1 if clock_seed in (1, 2, 5) else 0)

    if score >= 6:
        verdict = "auspicious"
        verdict_zh = "吉"
        timing_tip_en = "Use this period for negotiations, openings, and funding requests."
        timing_tip_zh = "此時段宜談判、開局與求財。"
    elif score >= 4:
        verdict = "mixed"
        verdict_zh = "平"
        timing_tip_en = "Proceed with preparation first, then execute in a stronger hour."
        timing_tip_zh = "先籌備再執行，等待更強吉時。"
    else:
        verdict = "inauspicious"
        verdict_zh = "凶"
        timing_tip_en = "Limit to planning and avoid irreversible decisions."
        timing_tip_zh = "以規劃為主，避免不可逆決策。"

    process_summary = {
        "zh": (
            f"姓名 Abjad 餘數 {abjad_mod + 1}/7、星期因子 {weekday_seed + 1}/7、"
            f"時段因子 {clock_seed + 1}/7、月相因子 {moon_bucket + 1}/8，映射至第 {star['index']} 星。"
        ),
        "en": (
            f"Name Abjad residue {abjad_mod + 1}/7, weekday factor {weekday_seed + 1}/7, "
            f"clock factor {clock_seed + 1}/7, and lunar bucket {moon_bucket + 1}/8 map to Star #{star['index']}."
        ),
    }

    return {
        "system": "bintang_tujuh",
        "moment": summarize_moment(moment),
        "name_profile": profile,
        "star": {
            "index": star["index"],
            "name_zh": star["name_zh"],
            "name_en": star["name_en"],
            "score": score,
        },
        "factors": {
            "abjad_mod_7": abjad_mod,
            "weekday_seed": weekday_seed,
            "clock_seed": clock_seed,
            "moon_phase_bucket": moon_bucket,
        },
        "process_summary": process_summary,
        "fortune": {
            "verdict": verdict,
            "verdict_zh": verdict_zh,
        },
        "advice": {
            "zh": {
                "timing": timing_tip_zh,
                "practical": "若需擇吉，優先安排在同星連續兩個時段內行動。",
            },
            "en": {
                "timing": timing_tip_en,
                "practical": "For elections, act within two contiguous periods under the same star current.",
            },
        },
    }


__all__ = ["compute_bintang_tujuh"]
