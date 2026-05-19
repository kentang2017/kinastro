"""astro/huangji/huangji.py — 皇極經世（Huangji Jingshi）wrapper for KinAstro."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any

import swisseph as swe

from astro.swe_init import init_swisseph

logger = logging.getLogger(__name__)

_SOLAR_TERMS_BY_LON = [
    (315.0, "立春", "Start of Spring"),
    (330.0, "雨水", "Rain Water"),
    (345.0, "驚蟄", "Awakening of Insects"),
    (0.0, "春分", "Spring Equinox"),
    (15.0, "清明", "Pure Brightness"),
    (30.0, "穀雨", "Grain Rain"),
    (45.0, "立夏", "Start of Summer"),
    (60.0, "小滿", "Lesser Fullness"),
    (75.0, "芒種", "Grain in Ear"),
    (90.0, "夏至", "Summer Solstice"),
    (105.0, "小暑", "Lesser Heat"),
    (120.0, "大暑", "Greater Heat"),
    (135.0, "立秋", "Start of Autumn"),
    (150.0, "處暑", "Limit of Heat"),
    (165.0, "白露", "White Dew"),
    (180.0, "秋分", "Autumn Equinox"),
    (195.0, "寒露", "Cold Dew"),
    (210.0, "霜降", "Frost's Descent"),
    (225.0, "立冬", "Start of Winter"),
    (240.0, "小雪", "Lesser Snow"),
    (255.0, "大雪", "Greater Snow"),
    (270.0, "冬至", "Winter Solstice"),
    (285.0, "小寒", "Lesser Cold"),
    (300.0, "大寒", "Greater Cold"),
]

EXPECTED_GUA_KEYS = ("正卦", "運卦", "世卦", "旬卦", "年卦", "月卦", "日卦", "時卦", "分卦")


@dataclass
class HistoricalContext:
    start_year: int
    duration: int
    dynasty: str
    title: str
    era: str
    name: str = ""


@dataclass
class CrossSystemSnapshot:
    zodiacal_releasing_l1: str = ""
    annual_profection: str = ""
    vedic_dasha: str = ""
    ziwei_daxian: str = ""


@dataclass
class HuangjiPan:
    yuan: int
    hui: int
    yun: int
    shi: int
    year_in_shi: int
    year_in_yun: int
    year_in_hui: int
    year_in_yuan: int
    total_years_from_epoch: int
    hui_global: int
    yun_global: int
    shi_global: int
    gua: dict[str, str] = field(default_factory=dict)
    moving_lines: dict[str, int] = field(default_factory=dict)
    ganzhi: list[str] = field(default_factory=list)
    jieqi_kinwangji: str = ""
    jieqi_swiss: str = ""
    historical_context: list[HistoricalContext] = field(default_factory=list)
    major_cycle_milestones: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class HuangjiPanResult:
    system: str
    location_name: str
    datetime_local: str
    board_text: str
    huangji_pan: HuangjiPan
    cross_system: CrossSystemSnapshot = field(default_factory=CrossSystemSnapshot)

    def to_dict(self) -> dict[str, Any]:
        return {
            "system": self.system,
            "location_name": self.location_name,
            "datetime_local": self.datetime_local,
            "board_text": self.board_text,
            "huangji_pan": asdict(self.huangji_pan),
            "cross_system": asdict(self.cross_system),
        }


def _get_kinwangji_exports() -> tuple[Any, Any, Any, Any]:
    try:
        from kinwangji import display_pan, history_for_year, jq, wanji_four_gua
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover
        raise ImportError(
            "kinwangji is required. Install via: pip install git+https://github.com/kentang2017/kinwangji.git"
        ) from exc
    return wanji_four_gua, display_pan, jq, history_for_year


def _solar_term_from_swiss(jd_ut: float) -> tuple[str, str, float]:
    sun_lon = swe.calc_ut(jd_ut, swe.SUN)[0][0] % 360.0
    best = min(
        _SOLAR_TERMS_BY_LON,
        key=lambda item: min(abs(sun_lon - item[0]), 360.0 - abs(sun_lon - item[0])),
    )
    return best[1], best[2], round(sun_lon, 6)


def _accumulated_year(adjusted_year: int) -> int:
    return 67017 + adjusted_year + (1 if adjusted_year < 0 else 0)


def _calc_cycle_hierarchy(adjusted_year: int) -> tuple[int, int, int, int, int, int, int, int]:
    total = _accumulated_year(adjusted_year)
    yuan = total // 129600 + 1
    year_in_yuan = total % 129600 + 1
    hui = (year_in_yuan - 1) // 10800 + 1
    year_in_hui = (year_in_yuan - 1) % 10800 + 1
    yun = (year_in_hui - 1) // 360 + 1
    year_in_yun = (year_in_hui - 1) % 360 + 1
    shi = (year_in_yun - 1) // 30 + 1
    year_in_shi = (year_in_yun - 1) % 30 + 1
    return total, yuan, hui, yun, shi, year_in_shi, year_in_yun, year_in_hui


def _build_milestones(adjusted_year: int, year_in_shi: int, year_in_yun: int, year_in_hui: int) -> list[dict[str, Any]]:
    return [
        {"label": "下個世起點", "year": adjusted_year + (31 - year_in_shi)},
        {"label": "下個運起點", "year": adjusted_year + (361 - year_in_yun)},
        {"label": "下個會起點", "year": adjusted_year + (10801 - year_in_hui)},
    ]


def _build_cross_system_snapshot(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str,
    reference_year: int,
    gender: str,
) -> CrossSystemSnapshot:
    out = CrossSystemSnapshot()

    try:
        from astro.western.western import compute_western_chart
        from astro.western.hellenistic import compute_hellenistic_chart
        from astro.hellenistic import get_current_periods_for_natal, get_current_profection

        western_chart = compute_western_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )
        prof = get_current_profection(western_chart.ascendant, year, target_date=date(reference_year, 1, 1))
        out.annual_profection = f"{prof.calendar_year}｜{prof.sign_cn}宮（{prof.lord_cn}）"

        hchart = compute_hellenistic_chart(western_chart, birth_year=year, current_year=reference_year)
        fortune_lon = next((l.longitude for l in hchart.lots if "Fortune" in l.name), 0.0)
        spirit_lon = next((l.longitude for l in hchart.lots if "Spirit" in l.name), 0.0)
        target_jd = western_chart.julian_day + max(0, reference_year - year) * 365.25
        zr = get_current_periods_for_natal(fortune_lon, spirit_lon, western_chart.julian_day, target_jd)
        l1 = zr.get("spirit", {}).get("L1")
        if l1:
            out.zodiacal_releasing_l1 = f"Spirit L1：{l1.sign}（{l1.start_year}-{l1.end_year}）"
    except Exception as exc:
        logger.debug("Huangji cross-system western/hellenistic snapshot skipped: %s", exc)

    try:
        from astro.vedic.indian import compute_vedic_chart
        from astro.vedic.vedic_dasha import compute_vimshottari

        vedic_chart = compute_vedic_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )
        moon = next((p for p in vedic_chart.planets if "Chandra" in p.name), None)
        if moon:
            vim = compute_vimshottari(moon.longitude, vedic_chart.julian_day)
            current = next(
                (p for p in vim.mahadasha_periods if p.start_date[:4] <= str(reference_year) <= p.end_date[:4]),
                vim.mahadasha_periods[0] if vim.mahadasha_periods else None,
            )
            if current:
                out.vedic_dasha = f"{current.lord_cn}大運（{current.start_date}～{current.end_date}）"
    except Exception as exc:
        logger.debug("Huangji cross-system vedic snapshot skipped: %s", exc)

    try:
        from astro.ziwei import compute_ziwei_chart

        zw = compute_ziwei_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            gender=gender,
        )
        age = max(0, reference_year - year)
        palace = next(
            (p for p in zw.palaces if p.da_xian_start <= age <= p.da_xian_start + 9),
            zw.palaces[0] if zw.palaces else None,
        )
        if palace:
            out.ziwei_daxian = f"{age}歲｜{palace.name}（{palace.da_xian}）"
    except Exception as exc:
        logger.debug("Huangji cross-system ziwei snapshot skipped: %s", exc)

    return out


def compute_huangji_pan(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    reference_year: int | None = None,
    include_cross_system: bool = True,
    gender: str = "男",
) -> HuangjiPanResult:
    """Compute Huangji Jingshi cycle position and cross-system snapshots."""
    init_swisseph()
    wanji_four_gua, display_pan, jq, history_for_year = _get_kinwangji_exports()

    pan = wanji_four_gua(year, month, day, hour, minute)
    board_text = display_pan(year, month, day, hour, minute)
    kinwangji_jieqi = jq(year, month, day, hour, minute)

    adjusted_year = int(str(pan.get("日期", f"{year}")).split("-")[0])
    total, yuan, hui, yun, shi, year_in_shi, year_in_yun, year_in_hui = _calc_cycle_hierarchy(adjusted_year)

    ut_hour = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, ut_hour)
    swiss_jq_zh, _, _ = _solar_term_from_swiss(jd_ut)

    history_rows = [HistoricalContext(**row) for row in history_for_year(reference_year or year)]
    huangji_pan = HuangjiPan(
        yuan=yuan,
        hui=hui,
        yun=yun,
        shi=shi,
        year_in_shi=year_in_shi,
        year_in_yun=year_in_yun,
        year_in_hui=year_in_hui,
        year_in_yuan=(total % 129600) + 1,
        total_years_from_epoch=total,
        hui_global=int(pan.get("會", 0)),
        yun_global=int(pan.get("運", 0)),
        shi_global=int(pan.get("世", 0)),
        gua={k: pan.get(k, "") for k in EXPECTED_GUA_KEYS},
        moving_lines={
            "運卦動爻": int(pan.get("運卦動爻", 0) or 0),
            "世卦動爻": int(pan.get("世卦動爻", 0) or 0),
            "旬卦動爻": int(pan.get("旬卦動爻", 0) or 0),
        },
        ganzhi=list(pan.get("干支", [])),
        jieqi_kinwangji=kinwangji_jieqi,
        jieqi_swiss=swiss_jq_zh,
        historical_context=history_rows,
        major_cycle_milestones=_build_milestones(adjusted_year, year_in_shi, year_in_yun, year_in_hui),
    )

    ref_year = reference_year or datetime.now().year
    cross = CrossSystemSnapshot()
    if include_cross_system:
        cross = _build_cross_system_snapshot(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            reference_year=ref_year,
            gender=gender,
        )

    return HuangjiPanResult(
        system="huangji",
        location_name=location_name,
        datetime_local=f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (UTC{timezone:+g})",
        board_text=board_text,
        huangji_pan=huangji_pan,
        cross_system=cross,
    )
