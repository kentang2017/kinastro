"""
astro/astronomical_geomancy/calculator.py
══════════════════════════════════════════════════════════════
Pure computation module for Gerardus Cremonensis' Astronomical Geomancy.

Core algorithm (per Gerard's manuscript):
  1. Generate 4 "mother figures" using traditional random point-counting.
  2. The first mother figure determines the Ascendant (1st house sign).
  3. Fill the remaining 11 houses by stepping through the zodiac from ASC.
  4. For each of 7 planets + Caput + Cauda, compute a random dot count,
     take the remainder mod 12, and place the body in the corresponding house.
  5. Return a fully populated GeomancyChart.

Seed modes:
  - "random": fully random (traditional geomantic way)
  - "time_seed": seed from current UTC timestamp (modern enhancement)
  - int seed: deterministic (for testing / reproducibility)
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from typing import List, Optional, Union

from .constants import (
    FIGURES,
    HOUSE_MEANINGS,
    PLANETS,
    QUESTION_TYPES,
    ZODIAC_SIGNS,
)
from .models import (
    GeomancyChart,
    GeomancyFigure,
    HouseInfo,
    PlanetInHouse,
)


# ─────────────────────────────────────────────────────────────────────────────
# Figure list in canonical order (matches Polyphilus / Gerard tradition)
# ─────────────────────────────────────────────────────────────────────────────

_FIGURE_KEYS: List[str] = list(FIGURES.keys())


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_figure(key: str) -> GeomancyFigure:
    """Build a GeomancyFigure from FIGURES constant dict."""
    d = FIGURES[key]
    return GeomancyFigure(
        name_en=d["name_en"],
        name_zh=d["name_zh"],
        dots=list(d["dots"]),
        element=d["element"],
        element_zh=d["element_zh"],
        planet=d["planet"],
        planet_zh=d["planet_zh"],
        sign=d["sign"],
        sign_zh=d["sign_zh"],
        sign_num=d["sign_num"],
        quality=d["quality"],
        quality_zh=d["quality_zh"],
        keywords_zh=d["keywords_zh"],
        keywords_en=d["keywords_en"],
    )


def _generate_figure(rng: random.Random) -> GeomancyFigure:
    """
    Traditional geomantic figure generation:
    - Mark 4 rows of random dots (odd or even count → 1 or 2 dots per row).
    - Find the matching figure from FIGURES by dot pattern.
    - Fall back to random selection if no exact match (safety net).
    """
    # Generate 4 rows: each row has 1..16 dots; odd→single, even→double
    row_pattern: List[bool] = []
    for _ in range(4):
        n_dots = rng.randint(1, 16)
        row_pattern.append(n_dots % 2 == 1)  # True = single (odd)

    # Find matching figure
    for key, data in FIGURES.items():
        if list(data["dots"]) == row_pattern:
            return _make_figure(key)

    # Fallback: pick random figure
    key = rng.choice(_FIGURE_KEYS)
    return _make_figure(key)


def _figure_for_ascendant(rng: random.Random) -> GeomancyFigure:
    """Pick the ascendant figure randomly from all 16 figures."""
    key = rng.choice(_FIGURE_KEYS)
    return _make_figure(key)


def _build_houses(asc_sign_num: int) -> List[HouseInfo]:
    """
    Build 12 houses starting from asc_sign_num, cycling through zodiac.
    Returns list indexed 0..11 (house 1..12).
    """
    houses: List[HouseInfo] = []
    meanings = HOUSE_MEANINGS
    for i in range(12):
        sign_idx = (asc_sign_num + i) % 12
        sign_data = ZODIAC_SIGNS[sign_idx]
        m = meanings[i]
        houses.append(HouseInfo(
            house=i + 1,
            sign=sign_data["en"],
            sign_zh=sign_data["zh"],
            sign_num=sign_idx,
            glyph=sign_data["glyph"],
            element=sign_data["element"],
            quality=sign_data["quality"],
            name_en=m["name_en"],
            name_zh=m["name_zh"],
            topics_zh=m["topics_zh"],
            topics_en=m["topics_en"],
            gerard_zh=m["gerard_zh"],
        ))
    return houses


def _place_planets(rng: random.Random, houses: List[HouseInfo]) -> List[PlanetInHouse]:
    """
    For each planet, generate a random dot count, take remainder mod 12
    to determine which house (0-based), then assign.
    Gerard uses a simple random count method for planetary lots.
    """
    placements: List[PlanetInHouse] = []
    for planet_data in PLANETS:
        # Traditional method: count random dots, take mod 12
        dot_count = rng.randint(12, 144)  # enough variance for all 12 values
        remainder = dot_count % 12
        house_idx = remainder  # 0-based → house = remainder + 1
        # Remainder 0 means the count divides evenly into 12.
        # In Gerard's system a zero remainder conventionally rolls over to
        # the 12th (last) house rather than being treated as house 0
        # (which doesn't exist).  We therefore map index 0 → index 11 here.
        if remainder == 0:
            house_idx = 11
        house = houses[house_idx]
        placement = PlanetInHouse(
            planet_key=planet_data["key"],
            planet_en=planet_data["en"],
            planet_zh=planet_data["zh"],
            glyph=planet_data["glyph"],
            house=house.house,
            sign=house.sign,
            sign_zh=house.sign_zh,
            sign_num=house.sign_num,
            nature=planet_data["nature"],
            nature_zh=planet_data["nature_zh"],
            remainder=remainder if remainder != 0 else 12,
        )
        placements.append(placement)
        house.planets.append(placement)
    return placements


def _get_question_type_info(question_type: str) -> dict:
    for qt in QUESTION_TYPES:
        if qt["key"] == question_type:
            return qt
    return QUESTION_TYPES[-1]  # default to "custom"


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def compute_geomancy_chart(
    question: str = "",
    question_type: str = "custom",
    seed_mode: str = "random",
    manual_seed: Optional[int] = None,
) -> GeomancyChart:
    """
    Compute a complete Astronomical Geomancy chart.

    Args:
        question:      The querent's question (free text).
        question_type: One of the QUESTION_TYPES keys.
        seed_mode:     "random" | "time_seed" | "manual"
        manual_seed:   Used when seed_mode == "manual".

    Returns:
        GeomancyChart with all houses and planet placements populated.
    """
    # Determine seed
    if seed_mode == "time_seed":
        seed = int(time.time())
    elif seed_mode == "manual" and manual_seed is not None:
        seed = manual_seed
    else:
        seed = random.randint(0, 2**31 - 1)

    rng = random.Random(seed)

    # Generate 4 mother figures
    mother_figures: List[GeomancyFigure] = [
        _generate_figure(rng) for _ in range(4)
    ]

    # First mother figure = Ascendant figure
    asc_figure = mother_figures[0]
    asc_sign_num = asc_figure.sign_num
    asc_sign_data = ZODIAC_SIGNS[asc_sign_num]

    # Build 12 houses
    houses = _build_houses(asc_sign_num)

    # Place planets
    planet_placements = _place_planets(rng, houses)

    # Question type info
    qt_info = _get_question_type_info(question_type)
    primary_house = qt_info["primary_house"]

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return GeomancyChart(
        question=question,
        question_type=question_type,
        question_type_zh=qt_info["zh"],
        seed_mode=seed_mode,
        seed=seed,
        mother_figures=mother_figures,
        ascendant_figure=asc_figure,
        ascendant_sign=asc_sign_data["en"],
        ascendant_sign_zh=asc_sign_data["zh"],
        ascendant_sign_num=asc_sign_num,
        houses=houses,
        planet_placements=planet_placements,
        primary_house=primary_house,
        timestamp=timestamp,
    )


def format_geomancy_for_prompt(chart: GeomancyChart, lang: str = "zh") -> str:
    """
    Format chart data as a text prompt for AI reading.

    Args:
        chart: Computed GeomancyChart.
        lang:  "zh" | "en"

    Returns:
        Formatted string for the AI system prompt.
    """
    if lang == "en":
        lines = [
            "=== Astronomical Geomancy Chart (Gerard Cremonensis) ===",
            f"Question: {chart.question}",
            f"Question Type: {chart.question_type}",
            f"Ascendant Figure: {chart.ascendant_figure.name_en}",
            f"Ascendant Sign: {chart.ascendant_sign}",
            "",
            "--- House-Sign Summary ---",
        ]
        for h in chart.houses:
            planet_names = ", ".join(p.planet_en for p in h.planets) if h.planets else "—"
            lines.append(
                f"House {h.house} ({h.sign}, {h.glyph}): {h.name_en} | Planets: {planet_names}"
            )
        lines += [
            "",
            "--- Planet Placements ---",
        ]
        for p in chart.planet_placements:
            lines.append(f"{p.glyph} {p.planet_en}: House {p.house} ({p.sign})")
        lines += [
            "",
            "--- Mother Figures ---",
        ]
        for i, fig in enumerate(chart.mother_figures, 1):
            lines.append(f"Mother {i}: {fig.name_en} ({fig.sign}, {fig.quality})")
        lines.append(f"\nPrimary House: {chart.primary_house} ({chart.question_type})")
        return "\n".join(lines)

    else:  # zh
        lines = [
            "=== 地占占星（Gerard Cremonensis 地占占星）===",
            f"問題：{chart.question}",
            f"問題類型：{chart.question_type_zh}",
            f"上升圖形：{chart.ascendant_figure.name_zh}（{chart.ascendant_figure.name_en}）",
            f"上升星座：{chart.ascendant_sign_zh}",
            "",
            "--- 十二宮星座與行星 ---",
        ]
        for h in chart.houses:
            planet_names = "、".join(p.planet_zh for p in h.planets) if h.planets else "—"
            lines.append(
                f"第{h.house}宮 {h.sign_zh}（{h.glyph}）：{h.name_zh} | 行星：{planet_names}"
            )
        lines += [
            "",
            "--- 行星落宮 ---",
        ]
        for p in chart.planet_placements:
            lines.append(f"{p.glyph} {p.planet_zh}：第{p.house}宮 {p.sign_zh}")
        lines += [
            "",
            "--- 母親圖形 ---",
        ]
        for i, fig in enumerate(chart.mother_figures, 1):
            lines.append(f"母親{i}：{fig.name_zh}（{fig.sign_zh}，{fig.quality_zh}）")
        lines.append(f"\n主要宮位：第{chart.primary_house}宮（{chart.question_type_zh}）")
        return "\n".join(lines)
