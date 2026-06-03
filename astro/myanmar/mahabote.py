"""Core computation + SVG helpers for Myanmar Bedin / Mahabote."""

from __future__ import annotations

import math
from dataclasses import asdict
from datetime import date
from html import escape

from .data import (
    HOUSE_FILL_ORDER,
    LORD_FILL_STEP,
    LORD_ORDER,
    MAHABOTE_HOUSES,
    ZODIAC_BY_CYCLE_INDEX,
    ZODIAC_BY_LORD_KEY,
    ZODIAC_8,
)
from .models import MahaboteHousePlacement, MyanmarMahaboteChart, YearOverlay, ZodiacAnimal


def gregorian_to_myanmar_year(year: int, month: int, day: int) -> int:
    """Convert Gregorian year to Myanmar year with 4/15 threshold."""
    if month > 4 or (month == 4 and day >= 15):
        return year - 638
    return year - 639


def _zodiac_from_weekday(year: int, month: int, day: int, hour: int) -> ZodiacAnimal:
    """Resolve natal zodiac by weekday (with Wednesday PM Rahu split)."""
    weekday = date(year, month, day).weekday()  # Mon=0...Sun=6
    sunday_first = (weekday + 1) % 7  # Sun=0...Sat=6
    if sunday_first == 3 and hour >= 12:
        return ZODIAC_8[4]
    mapping = {
        0: ZODIAC_8[0],
        1: ZODIAC_8[1],
        2: ZODIAC_8[2],
        3: ZODIAC_8[3],
        4: ZODIAC_8[5],
        5: ZODIAC_8[6],
        6: ZODIAC_8[7],
    }
    return mapping[sunday_first]


def _build_houses(year_mod7: int) -> list[MahaboteHousePlacement]:
    """Build the 8-house board from the year-mod-7 start lord."""
    houses: list[MahaboteHousePlacement] = []
    start_lord_index = year_mod7 % 7

    for offset, house_index in enumerate(HOUSE_FILL_ORDER):
        house = MAHABOTE_HOUSES[house_index]
        lord_index = (start_lord_index + (offset * LORD_FILL_STEP)) % 7
        lord_key = LORD_ORDER[lord_index]
        zodiac = ZODIAC_BY_LORD_KEY[lord_key]
        houses.append(
            MahaboteHousePlacement(
                house_index=house_index,
                house_key=house.key,
                house_name_en=house.name_en,
                house_name_zh=house.name_zh,
                house_name_myanmar=house.name_myanmar,
                house_meaning_en=house.meaning_en,
                house_meaning_zh=house.meaning_zh,
                polarity=house.polarity,
                zodiac=zodiac,
                is_start_house=(offset == 0),
            )
        )
    return sorted(houses, key=lambda x: x.house_index)


def _build_year_overlay(gregorian_year: int, birth_year: int, birth_month: int, birth_day: int) -> YearOverlay:
    """Build a simple 8-cycle flow-year reference."""
    myanmar_year = gregorian_to_myanmar_year(gregorian_year, birth_month, birth_day)
    cycle_index = myanmar_year % 8
    zodiac = ZODIAC_BY_CYCLE_INDEX[cycle_index]
    return YearOverlay(
        gregorian_year=gregorian_year,
        myanmar_year=myanmar_year,
        cycle_index=cycle_index,
        animal_key=zodiac.key,
        animal_en=zodiac.animal_en,
        animal_zh=zodiac.animal_zh,
        direction_en=zodiac.direction_en,
        direction_zh=zodiac.direction_zh,
        summary_en=f"{gregorian_year}: Favor {zodiac.direction_en}; align with {zodiac.planet_en} themes.",
        summary_zh=f"{gregorian_year} 年：利 {zodiac.direction_zh} 方，宜順應 {zodiac.planet_zh} 主題行事。",
    )


def build_zodiac_wheel_svg(chart: MyanmarMahaboteChart, size: int = 520) -> str:
    """Render traditional-style 8-animal circle SVG."""
    cx, cy = size / 2, size / 2
    outer = size * 0.46
    inner = size * 0.2
    label_r = size * 0.39
    symbol_r = size * 0.31
    animal_r = size * 0.24
    start_deg = -157.5

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" aria-label="Myanmar Mahabote Zodiac Wheel">',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="#0f1426" rx="16"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{outer}" fill="#18203b" stroke="#c9a96e" stroke-width="3"/>',
    ]
    for i, z in enumerate(ZODIAC_8):
        a0 = math.radians(start_deg + i * 45)
        a1 = math.radians(start_deg + (i + 1) * 45)
        am = math.radians(start_deg + i * 45 + 22.5)
        x0o, y0o = cx + outer * math.cos(a0), cy + outer * math.sin(a0)
        x1o, y1o = cx + outer * math.cos(a1), cy + outer * math.sin(a1)
        x0i, y0i = cx + inner * math.cos(a0), cy + inner * math.sin(a0)
        x1i, y1i = cx + inner * math.cos(a1), cy + inner * math.sin(a1)
        path = (
            f"M {x0i:.2f} {y0i:.2f} L {x0o:.2f} {y0o:.2f} "
            f"A {outer:.2f} {outer:.2f} 0 0 1 {x1o:.2f} {y1o:.2f} "
            f"L {x1i:.2f} {y1i:.2f} A {inner:.2f} {inner:.2f} 0 0 0 {x0i:.2f} {y0i:.2f} Z"
        )
        is_natal = z.key == chart.natal_animal_key
        stroke = "#ffd700" if is_natal else "#7a6a3a"
        stroke_w = "3" if is_natal else "1.2"
        opacity = "0.52" if is_natal else "0.23"
        parts.append(
            f'<path d="{path}" fill="{escape(z.color_hex)}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{stroke_w}" />'
        )
        lx, ly = cx + label_r * math.cos(am), cy + label_r * math.sin(am)
        sx, sy = cx + symbol_r * math.cos(am), cy + symbol_r * math.sin(am)
        ax, ay = cx + animal_r * math.cos(am), cy + animal_r * math.sin(am)
        parts.append(f'<text x="{lx:.2f}" y="{ly:.2f}" fill="#eac57a" font-size="11" text-anchor="middle">{escape(z.direction_zh)}</text>')
        parts.append(f'<text x="{sx:.2f}" y="{sy:.2f}" fill="{escape(z.color_hex)}" font-size="24" text-anchor="middle">{escape(z.planet_symbol)}</text>')
        parts.append(f'<text x="{ax:.2f}" y="{ay:.2f}" fill="#ffffff" font-size="10" text-anchor="middle">{escape(z.animal_emoji)} {escape(z.animal_zh)}</text>')

    parts.extend(
        [
            f'<circle cx="{cx}" cy="{cy}" r="{inner}" fill="#0d1224" stroke="#d4af37" stroke-width="2"/>',
            f'<text x="{cx}" y="{cy - 18}" fill="#eac57a" font-size="11" text-anchor="middle">Mahabote</text>',
            f'<text x="{cx}" y="{cy + 4}" fill="#ffd700" font-size="26" text-anchor="middle">{escape(chart.start_lord_planet_zh)}</text>',
            f'<text x="{cx}" y="{cy + 24}" fill="#ffffff" font-size="11" text-anchor="middle">ME {chart.myanmar_year}</text>',
            "</svg>",
        ]
    )
    return "".join(parts)


def build_house_board_svg(chart: MyanmarMahaboteChart, size: int = 520) -> str:
    """Render 8-house board with polarity marker."""
    pad = 16
    cell = (size - pad * 2) / 3
    # 3x3 board index map where center is title.
    board_positions = {
        0: (0, 1),  # Binga
        1: (0, 2),  # Athun
        2: (1, 2),  # Yaza
        3: (2, 2),  # Adipati
        4: (2, 1),  # Marana
        5: (2, 0),  # Thike
        6: (1, 0),  # Puti
        7: (0, 0),  # Kamma
    }
    by_index = {h.house_index: h for h in chart.houses}
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" aria-label="Mahabote House Board">',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="#121827" rx="16"/>',
    ]
    for idx, (row, col) in board_positions.items():
        h = by_index[idx]
        x = pad + col * cell
        y = pad + row * cell
        stroke = "#ffd700" if h.is_start_house else "#3a4a73"
        fill = "#1f2b4a" if h.polarity == "positive" else "#3a1f2f"
        out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell:.2f}" height="{cell:.2f}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(f'<text x="{x + cell/2:.2f}" y="{y + 24:.2f}" fill="#dfe7ff" font-size="11" text-anchor="middle">{escape(h.house_name_zh)}</text>')
        out.append(f'<text x="{x + cell/2:.2f}" y="{y + 48:.2f}" fill="{escape(h.zodiac.color_hex)}" font-size="18" text-anchor="middle">{escape(h.zodiac.planet_symbol)}</text>')
        out.append(f'<text x="{x + cell/2:.2f}" y="{y + 68:.2f}" fill="#fff" font-size="10" text-anchor="middle">{escape(h.zodiac.animal_emoji)} {escape(h.zodiac.animal_zh)}</text>')
    out.append(f'<rect x="{pad + cell:.2f}" y="{pad + cell:.2f}" width="{cell:.2f}" height="{cell:.2f}" rx="8" fill="#0d1224" stroke="#c9a96e" stroke-width="2"/>')
    out.append(f'<text x="{pad + 1.5*cell:.2f}" y="{pad + 1.5*cell - 8:.2f}" fill="#eac57a" font-size="13" text-anchor="middle">House Ring</text>')
    out.append(f'<text x="{pad + 1.5*cell:.2f}" y="{pad + 1.5*cell + 12:.2f}" fill="#fff" font-size="11" text-anchor="middle">+ Positive / - Liability</text>')
    out.append("</svg>")
    return "".join(out)


def compute_myanmar_mahabote_chart(
    *,
    year: int,
    month: int,
    day: int,
    hour: int = 12,
    minute: int = 0,
    timezone: float = 6.5,
    latitude: float = 0.0,
    longitude: float = 0.0,
    location_name: str = "",
    target_year: int | None = None,
) -> MyanmarMahaboteChart:
    """Compute Myanmar Bedin / Mahabote chart with bilingual output fields."""
    me_year = gregorian_to_myanmar_year(year, month, day)
    year_mod7 = me_year % 7
    houses = _build_houses(year_mod7)

    natal = _zodiac_from_weekday(year, month, day, hour)
    positive_houses = [h.house_name_en for h in houses if h.polarity == "positive"]
    liability_houses = [h.house_name_en for h in houses if h.polarity == "liability"]

    current_year = date.today().year
    current_overlay = _build_year_overlay(current_year, year, month, day)
    target_overlay = _build_year_overlay(target_year or current_year, year, month, day)

    direction_advice_en = (
        f"Primary favorable directions: {', '.join(natal.favorable_directions_en)}.",
        f"Use caution toward: {', '.join(natal.caution_directions_en)}.",
        f"Current flow-year direction: {current_overlay.direction_en}.",
    )
    direction_advice_zh = (
        f"主要吉方：{'、'.join(natal.favorable_directions_zh)}。",
        f"需避開方位：{'、'.join(natal.caution_directions_zh)}。",
        f"當前流年主方位：{current_overlay.direction_zh}。",
    )

    start_house = MAHABOTE_HOUSES[HOUSE_FILL_ORDER[0]]
    start_lord = ZODIAC_BY_LORD_KEY[LORD_ORDER[year_mod7]]
    chart = MyanmarMahaboteChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        myanmar_year=me_year,
        year_mod7=year_mod7,
        start_house_index=HOUSE_FILL_ORDER[0],
        start_house_key=start_house.key,
        start_house_name_en=start_house.name_en,
        start_house_name_zh=start_house.name_zh,
        start_lord_key=LORD_ORDER[year_mod7],
        start_lord_planet_en=start_lord.planet_en,
        start_lord_planet_zh=start_lord.planet_zh,
        houses=houses,
        positive_houses=positive_houses,
        liability_houses=liability_houses,
        natal_animal_key=natal.key,
        natal_animal_en=natal.animal_en,
        natal_animal_zh=natal.animal_zh,
        natal_direction_en=natal.direction_en,
        natal_direction_zh=natal.direction_zh,
        natal_traits_en=natal.traits_en,
        natal_traits_zh=natal.traits_zh,
        natal_remedies_en=natal.remedies_en,
        natal_remedies_zh=natal.remedies_zh,
        direction_advice_en=direction_advice_en,
        direction_advice_zh=direction_advice_zh,
        current_year_overlay=current_overlay,
        target_year_overlay=target_overlay,
    )
    chart.zodiac_wheel_svg = build_zodiac_wheel_svg(chart)
    chart.house_board_svg = build_house_board_svg(chart)
    return chart


def chart_to_dict(chart: MyanmarMahaboteChart) -> dict[str, object]:
    """Stable dict serializer for API payloads."""
    payload = asdict(chart)
    payload["houses"] = [
        {
            **{
                k: v for k, v in asdict(h).items()
                if k != "zodiac"
            },
            "zodiac": asdict(h.zodiac),
        }
        for h in chart.houses
    ]
    return payload
