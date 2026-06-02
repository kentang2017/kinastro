"""Mata Angin Lapan + Pelangkah Rijal Al-Ghalib computations."""

from __future__ import annotations

from datetime import datetime

import swisseph as swe

from .common import compute_name_abjad_profile, direction_by_index, get_eight_directions, summarize_moment


def _planet_longitude(moment: datetime, body: int) -> float:
    """Compute geocentric ecliptic longitude (UT) for a planet."""
    jd = swe.julday(moment.year, moment.month, moment.day, moment.hour + moment.minute / 60.0)
    values, _flags = swe.calc_ut(jd, body)
    return float(values[0]) % 360.0


def compute_mata_angin_lapan(
    name: str,
    moment: datetime,
    *,
    latitude: float = 0.0,
    longitude: float = 0.0,
    script_hint: str = "auto",
) -> dict[str, object]:
    """Compute directional election guidance for Mata Angin Lapan."""
    del latitude, longitude  # reserved for future refinements

    abjad = compute_name_abjad_profile(name, script_hint=script_hint)
    sun_lon = _planet_longitude(moment, swe.SUN)
    moon_lon = _planet_longitude(moment, swe.MOON)

    sun_sector = int(((sun_lon + 22.5) % 360.0) // 45.0)
    moon_sector = int(((moon_lon + 22.5) % 360.0) // 45.0)
    pelangkah_seed = (abjad["abjad_total"] + moment.day + moon_sector + moment.weekday()) % 8
    dominant_index = (sun_sector + pelangkah_seed) % 8

    favorable_indices = {
        dominant_index,
        (dominant_index + 1) % 8,
        (dominant_index - 1) % 8,
    }
    caution_indices = {
        (dominant_index + 4) % 8,
        (dominant_index + 3) % 8,
        (dominant_index + 5) % 8,
    }

    sectors: list[dict[str, object]] = []
    for direction in get_eight_directions():
        score = 5
        if direction.index in favorable_indices:
            score = 9 if direction.index == dominant_index else 7
        elif direction.index in caution_indices:
            score = 2 if direction.index == (dominant_index + 4) % 8 else 3

        if score >= 7:
            status = "auspicious"
            status_zh = "吉"
            reason = "Aligned with Pelangkah flow"
            reason_zh = "順應 Pelangkah 步進氣流"
        elif score <= 3:
            status = "inauspicious"
            status_zh = "凶"
            reason = "Opposed to dominant wind current"
            reason_zh = "逆主導風向，宜避開"
        else:
            status = "neutral"
            status_zh = "平"
            reason = "Secondary transit corridor"
            reason_zh = "次要過渡方位，可視情況使用"

        sectors.append(
            {
                "index": direction.index,
                "direction_key": direction.key,
                "direction_zh": direction.direction_zh,
                "direction_en": direction.direction_en,
                "direction_ms": direction.direction_ms,
                "animal_zh": direction.animal_zh,
                "animal_en": direction.animal_en,
                "angle_deg": direction.angle_deg,
                "score": score,
                "status": status,
                "status_zh": status_zh,
                "reason_en": reason,
                "reason_zh": reason_zh,
            }
        )

    dominant = direction_by_index(dominant_index)
    process_summary = {
        "zh": (
            f"以太陽落宮({sun_sector + 1}/8)為主軸，月亮風口({moon_sector + 1}/8)與姓名 Abjad 值"
            f"{abjad['abjad_total']} 共同推導 Pelangkah 步數 {pelangkah_seed + 1}，"
            f"主吉方向落在{dominant.direction_zh}。"
        ),
        "en": (
            f"Solar sector ({sun_sector + 1}/8), lunar gate ({moon_sector + 1}/8), and name Abjad value "
            f"{abjad['abjad_total']} derive Pelangkah step {pelangkah_seed + 1}, producing dominant "
            f"direction {dominant.direction_en}."
        ),
    }

    advice = {
        "zh": {
            "best_direction": dominant.direction_zh,
            "best_action": "出行、開工、簽約優先面向主吉方向。",
            "avoid_action": "避免在對沖方向破土與定柱。",
        },
        "en": {
            "best_direction": dominant.direction_en,
            "best_action": "Face the dominant sector for departures, launches, and agreements.",
            "avoid_action": "Avoid groundbreaking and pillar-setting in the opposite sector.",
        },
    }

    return {
        "system": "mata_angin_lapan",
        "method": "pelangkah_rijal_al_ghalib",
        "moment": summarize_moment(moment),
        "name_profile": abjad,
        "astronomy": {
            "sun_longitude": round(sun_lon, 4),
            "moon_longitude": round(moon_lon, 4),
            "sun_sector": sun_sector,
            "moon_sector": moon_sector,
        },
        "pelangkah": {
            "seed": pelangkah_seed,
            "step_number": pelangkah_seed + 1,
            "dominant_index": dominant_index,
            "dominant_direction_key": dominant.key,
        },
        "process_summary": process_summary,
        "fortune": {
            "verdict": "favorable" if any(item["score"] >= 9 for item in sectors) else "mixed",
            "verdict_zh": "偏吉" if any(item["score"] >= 9 for item in sectors) else "平衡",
        },
        "advice": advice,
        "sectors": sectors,
        "chart_payload": {
            "dominant_index": dominant_index,
            "favorable_indices": sorted(favorable_indices),
            "caution_indices": sorted(caution_indices),
        },
    }


__all__ = ["compute_mata_angin_lapan"]
