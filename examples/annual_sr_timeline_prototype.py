#!/usr/bin/env python3
"""Prototype: solar-return + Liu Ren annual timeline summary table."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astro.annual import compute_solar_return_flowyear_timeline
from astro.models import BirthData


def main() -> None:
    birth = BirthData(
        year=1990,
        month=5,
        day=15,
        hour=14,
        minute=30,
        timezone=8.0,
        latitude=25.033,
        longitude=121.565,
        location_name="台北",
        gender="male",
    )

    # 30-45 虛歲區間：1990 年生人 → 2019-2034 太陽回歸年
    timeline = compute_solar_return_flowyear_timeline(
        birth,
        start_year=2019,
        end_year=2034,
        include_systems=["western", "liuren", "ziwei", "bazi", "qizheng"],
    )

    print("=" * 120)
    print("KinAstro 太陽回歸流年多體系時間軸（Prototype）")
    print(f"本命：{birth.year}-{birth.month:02d}-{birth.day:02d} {birth.hour:02d}:{birth.minute:02d} @ {birth.location_name}")
    print(f"本命年支：{timeline.benming_zhi}　太陽黃經：{timeline.natal_sun_longitude:.4f}°")
    print(timeline.trend_summary)
    print("=" * 120)

    header = (
        f"{'虛歲':>4} | {'SR年':>4} | {'SR精確時間(當地)':^22} | "
        f"{'三傳摘要':^20} | {'六壬':>4} | {'流年宮':^6} | {'小限宮':^6} | "
        f"{'紫微':>4} | {'八字':>4} | {'七政':>4} | {'西洋':>4} | {'等級':^4}"
    )
    print(header)
    print("-" * len(header))

    for year in timeline.years:
        lr = year.liuren_jixiong
        san = lr.san_chuan_summary[:18] + "…" if lr and len(lr.san_chuan_summary) > 18 else (lr.san_chuan_summary if lr else "—")
        liuren_score = f"{year.system_scores.get('liuren', 0):.0f}" if lr else "—"
        ziwei_raw = year.other_chinese_systems.get("ziwei", {}).raw if year.other_chinese_systems.get("ziwei") else {}
        ln_palace = ziwei_raw.get("liunian_palace", "—")
        xx_palace = ziwei_raw.get("xiaoxian_palace", "—")
        ziwei_score = f"{year.system_scores.get('ziwei', 0):.0f}"
        bazi_score = f"{year.system_scores.get('bazi', 0):.0f}"
        qizheng_score = f"{year.system_scores.get('qizheng', 0):.0f}"
        western_score = f"{year.system_scores.get('western', 0):.0f}"
        level = lr.level.value if lr else "—"
        sr_local = year.exact_sr_datetime_local.strftime("%Y-%m-%d %H:%M")
        print(
            f"{year.age:>4} | {year.year:>4} | {sr_local:^22} | "
            f"{san:^20} | {liuren_score:>4} | {ln_palace:^6} | {xx_palace:^6} | {ziwei_score:>4} | {bazi_score:>4} | "
            f"{qizheng_score:>4} | {western_score:>4} | {level:^4}"
        )

    print("=" * 120)
    print("各體系平均分：", ", ".join(
        f"{k}={v:.1f}" for k, v in timeline.system_average_scores.items()
    ))
    print("各體系最佳年：", timeline.best_years_by_system)


if __name__ == "__main__":
    main()