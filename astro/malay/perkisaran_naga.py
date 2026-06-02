"""Perkisaran Naga (dragon cycle) electional guidance."""

from __future__ import annotations

from datetime import datetime

import swisseph as swe

from .common import direction_by_index, get_eight_directions, summarize_moment


def _moon_sector(moment: datetime) -> int:
    jd = swe.julday(moment.year, moment.month, moment.day, moment.hour + moment.minute / 60.0)
    moon_val, _ = swe.calc_ut(jd, swe.MOON)
    moon_lon = float(moon_val[0]) % 360.0
    return int(((moon_lon + 22.5) % 360.0) // 45.0)


def compute_perkisaran_naga(
    moment: datetime,
    *,
    locale_hint: str = "nusantara",
) -> dict[str, object]:
    """Compute directional dragon-cycle guidance for construction and planting."""
    del locale_hint  # reserved for future regional variants

    moon_sector = _moon_sector(moment)
    yearly_shift = moment.year % 8
    naga_index = (moon_sector + yearly_shift + moment.month) % 8

    construction_indices = {(naga_index + 2) % 8, (naga_index + 3) % 8}
    planting_indices = {(naga_index + 1) % 8, (naga_index + 2) % 8, (naga_index + 6) % 8}
    avoid_indices = {naga_index, (naga_index - 1) % 8, (naga_index + 4) % 8}

    sectors: list[dict[str, object]] = []
    for direction in get_eight_directions():
        sector_type = "neutral"
        if direction.index in avoid_indices:
            sector_type = "avoid"
        elif direction.index in construction_indices and direction.index in planting_indices:
            sector_type = "dual_favorable"
        elif direction.index in construction_indices:
            sector_type = "construction"
        elif direction.index in planting_indices:
            sector_type = "planting"

        sectors.append(
            {
                "index": direction.index,
                "direction_key": direction.key,
                "direction_zh": direction.direction_zh,
                "direction_en": direction.direction_en,
                "direction_ms": direction.direction_ms,
                "animal_zh": direction.animal_zh,
                "animal_en": direction.animal_en,
                "sector_type": sector_type,
            }
        )

    naga_direction = direction_by_index(naga_index)
    process_summary = {
        "zh": (
            f"以月亮宮位({moon_sector + 1}/8)配合年份位移({yearly_shift})與月份校準，"
            f"龍位落在{naga_direction.direction_zh}，據此推導建築與種植擇向。"
        ),
        "en": (
            f"Moon sector ({moon_sector + 1}/8) combined with yearly shift ({yearly_shift}) and month tuning "
            f"places the dragon current in {naga_direction.direction_en}, from which building/planting directions are elected."
        ),
    }

    return {
        "system": "perkisaran_naga",
        "moment": summarize_moment(moment),
        "cycle": {
            "moon_sector": moon_sector,
            "yearly_shift": yearly_shift,
            "naga_index": naga_index,
            "naga_direction_key": naga_direction.key,
        },
        "process_summary": process_summary,
        "fortune": {
            "verdict": "directional_mixed",
            "verdict_zh": "依方向分吉凶",
        },
        "recommendations": {
            "construction": [direction_by_index(index).direction_en for index in sorted(construction_indices)],
            "construction_zh": [direction_by_index(index).direction_zh for index in sorted(construction_indices)],
            "planting": [direction_by_index(index).direction_en for index in sorted(planting_indices)],
            "planting_zh": [direction_by_index(index).direction_zh for index in sorted(planting_indices)],
            "avoid": [direction_by_index(index).direction_en for index in sorted(avoid_indices)],
            "avoid_zh": [direction_by_index(index).direction_zh for index in sorted(avoid_indices)],
        },
        "advice": {
            "zh": {
                "construction": "建築破土與立柱優先採用建築吉向。",
                "planting": "播種、移栽以種植吉向為主，並避開龍首對沖位。",
            },
            "en": {
                "construction": "Prioritize construction-favorable sectors for groundbreaking and pillar setting.",
                "planting": "Use planting-favorable sectors for sowing/transplanting and avoid the dragon-opposed axis.",
            },
        },
        "sectors": sectors,
    }


__all__ = ["compute_perkisaran_naga"]
