"""Solar-return annual flow-year timeline orchestrator."""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

from astro.annual.adapters.liuren import compute_liuren_at_sr
from astro.annual.models import (
    AnnualFlowYear,
    ReturnLocation,
    SolarReturnTimeline,
    SolarReturnTimelineRequest,
)
from astro.annual.natal_context import (
    liunian_branch_for_year,
    liunian_ganzhi_for_year,
    natal_sun_longitude,
    virtual_age,
    western_age,
    year_branch_from_birth,
)
from astro.annual.scoring.bazi_scorer import score_bazi_annual
from astro.annual.scoring.liuren_scorer import score_liuren_annual
from astro.annual.adapters.qizheng import compute_qizheng_annual, compute_qizheng_natal
from astro.annual.scoring.qizheng_scorer import score_qizheng_annual
from astro.annual.scoring.western_sr_scorer import score_western_sr
from astro.annual.scoring.ziwei_scorer import score_ziwei_annual
from astro.annual.timezone import jd_to_local_datetime, jd_to_utc_datetime
from astro.bazi import compute_bazi
from astro.models import BirthData, western_chart_to_result
from astro.western.solar_return_core import compute_solar_return_core
from astro.western.western import compute_western_chart
from astro.ziwei import compute_ziwei_chart

SUPPORTED_SYSTEMS = {"western", "liuren", "ziwei", "bazi", "qizheng"}
CAUTION_THRESHOLD = 45.0


def _normalize_systems(systems: Iterable[str] | None) -> set[str]:
    if not systems:
        return set(SUPPORTED_SYSTEMS)
    normalized = {item.strip().lower() for item in systems}
    unknown = normalized - SUPPORTED_SYSTEMS
    if unknown:
        raise ValueError(f"Unsupported systems: {', '.join(sorted(unknown))}")
    return normalized


def _build_integrated_summary(year: AnnualFlowYear) -> str:
    parts: list[str] = []
    if year.liuren_jixiong:
        parts.append(
            f"大六壬 {year.liuren_jixiong.score:.0f}（{year.liuren_jixiong.level.value}）："
            f"{year.liuren_jixiong.affair_summary}"
        )
    if year.western_sr:
        parts.append(f"西洋SR {year.western_sr.score:.0f}（{year.western_sr.level.value}）")
    for key, snapshot in year.other_chinese_systems.items():
        parts.append(f"{key} {snapshot.score:.0f}（{snapshot.level.value}）")
    return "｜".join(parts)


def _compute_single_year(
    *,
    birth: BirthData,
    year: int,
    natal_sun_lon: float,
    benming_zhi: str,
    return_location: ReturnLocation,
    include_systems: set[str],
    age_kind: str,
    include_full_western_chart: bool,
    natal_western_chart: object | None,
    natal_ziwei_chart: object | None,
    natal_bazi_chart: object | None,
    natal_qizheng_chart: object | None = None,
) -> AnnualFlowYear:
    sr = compute_solar_return_core(
        natal_sun_lon,
        year,
        return_location.latitude,
        return_location.longitude,
        timezone=return_location.timezone,
        location_name=return_location.location_name,
    )
    sr_utc = jd_to_utc_datetime(sr.return_jd)
    sr_local = jd_to_local_datetime(sr.return_jd, return_location.timezone)
    liunian_zhi = liunian_branch_for_year(year)
    liunian_gz = liunian_ganzhi_for_year(year)
    age = virtual_age(birth.year, year) if age_kind == "virtual" else western_age(birth.year, year)

    flow_year = AnnualFlowYear(
        year=year,
        age=age,
        age_kind=age_kind,  # type: ignore[arg-type]
        exact_sr_datetime_utc=sr_utc,
        exact_sr_datetime_local=sr_local,
        sr_jd=sr.return_jd,
        return_location=return_location,
        liunian_zhi=liunian_zhi,
        liunian_gz=liunian_gz,
        benming_zhi=benming_zhi,
    )

    if "western" in include_systems:
        flow_year.western_sr = score_western_sr(sr.return_chart, natal_western_chart)
        flow_year.system_scores["western"] = flow_year.western_sr.score
        if include_full_western_chart:
            flow_year.western_sr_chart = western_chart_to_result(sr.return_chart)

    if "liuren" in include_systems:
        chart, lunming = compute_liuren_at_sr(
            sr_local,
            return_location.timezone,
            benming_zhi,
            liunian_zhi,
        )
        flow_year.liuren_chart = chart
        flow_year.liuren_lunming = lunming
        flow_year.sr_day_gz = chart.get("_day_gz", "")
        flow_year.sr_hour_gz = chart.get("_hour_gz", "")
        flow_year.liuren_jixiong = score_liuren_annual(
            chart, lunming, benming_zhi, liunian_zhi
        )
        flow_year.system_scores["liuren"] = flow_year.liuren_jixiong.score

    if "bazi" in include_systems:
        gender = birth.legacy_gender or "男"
        bazi_chart = natal_bazi_chart
        if bazi_chart is None:
            bazi_chart = compute_bazi(
                birth.year,
                birth.month,
                birth.day,
                birth.hour,
                birth.minute,
                gender=gender,
                timezone=birth.timezone,
                latitude=birth.latitude,
                longitude=birth.longitude,
                location_name=birth.location_name,
                reference_date=date(sr_local.year, sr_local.month, sr_local.day),
            )
        else:
            bazi_chart = compute_bazi(
                birth.year,
                birth.month,
                birth.day,
                birth.hour,
                birth.minute,
                gender=gender,
                timezone=birth.timezone,
                latitude=birth.latitude,
                longitude=birth.longitude,
                location_name=birth.location_name,
                reference_date=date(sr_local.year, sr_local.month, sr_local.day),
            )
        snapshot = score_bazi_annual(bazi_chart)
        flow_year.other_chinese_systems["bazi"] = snapshot
        flow_year.system_scores["bazi"] = snapshot.score

    if "ziwei" in include_systems:
        gender = birth.legacy_gender or "男"
        ziwei_chart = natal_ziwei_chart
        if ziwei_chart is None:
            ziwei_chart = compute_ziwei_chart(
                birth.year,
                birth.month,
                birth.day,
                birth.hour,
                birth.minute,
                birth.timezone,
                birth.latitude,
                birth.longitude,
                birth.location_name,
                gender=gender,
            )
        snapshot = score_ziwei_annual(ziwei_chart, age, liunian_gz, liunian_zhi)
        flow_year.other_chinese_systems["ziwei"] = snapshot
        flow_year.system_scores["ziwei"] = snapshot.score

    if "qizheng" in include_systems:
        qz_context = compute_qizheng_annual(
            birth,
            year,
            natal_qizheng_chart,
            sr_local=sr_local,
            timezone=return_location.timezone,
        )
        snapshot = score_qizheng_annual(qz_context)
        flow_year.other_chinese_systems["qizheng"] = snapshot
        flow_year.system_scores["qizheng"] = snapshot.score

    flow_year.integrated_interpretation = _build_integrated_summary(flow_year)
    return flow_year


def compute_solar_return_flowyear_timeline(
    birth_data: BirthData,
    start_year: int,
    end_year: int,
    return_location: ReturnLocation | None = None,
    include_systems: list[str] | None = None,
    *,
    benming_zhi: str | None = None,
    age_kind: str = "virtual",
    include_full_western_chart: bool = False,
) -> SolarReturnTimeline:
    """Compute a multi-year solar-return annual flow timeline."""
    systems = _normalize_systems(include_systems)
    location = return_location or ReturnLocation.from_birth(birth_data)
    benming = benming_zhi or year_branch_from_birth(birth_data)
    sun_lon = natal_sun_longitude(birth_data)

    request = SolarReturnTimelineRequest(
        birth_data=birth_data,
        start_year=start_year,
        end_year=end_year,
        return_location=location,
        include_systems=sorted(systems),
        benming_zhi=benming,
        age_kind=age_kind,  # type: ignore[arg-type]
        include_full_western_chart=include_full_western_chart,
    )

    natal_western = None
    natal_ziwei = None
    natal_bazi = None
    natal_qizheng_chart = None
    if "western" in systems:
        natal_western = compute_western_chart(**birth_data.to_compute_kwargs())
    if "ziwei" in systems:
        ziwei_kwargs = birth_data.to_compute_kwargs()
        ziwei_kwargs["gender"] = birth_data.legacy_gender or "男"
        natal_ziwei = compute_ziwei_chart(**ziwei_kwargs)
    if "bazi" in systems:
        bazi_kwargs = birth_data.to_compute_kwargs()
        bazi_kwargs["gender"] = birth_data.legacy_gender or "男"
        natal_bazi = compute_bazi(**bazi_kwargs)
    if "qizheng" in systems:
        natal_qizheng_chart = compute_qizheng_natal(birth_data)

    years: list[AnnualFlowYear] = []
    for year in range(start_year, end_year + 1):
        years.append(
            _compute_single_year(
                birth=birth_data,
                year=year,
                natal_sun_lon=sun_lon,
                benming_zhi=benming,
                return_location=location,
                include_systems=systems,
                age_kind=age_kind,
                include_full_western_chart=include_full_western_chart,
                natal_western_chart=natal_western,
                natal_ziwei_chart=natal_ziwei,
                natal_bazi_chart=natal_bazi,
                natal_qizheng_chart=natal_qizheng_chart,
            )
        )

    system_average_scores: dict[str, float] = {}
    best_years_by_system: dict[str, int] = {}
    caution_years_by_system: dict[str, list[int]] = {}

    for system in systems:
        scores = [
            (item.year, item.system_scores[system])
            for item in years
            if system in item.system_scores
        ]
        if not scores:
            continue
        system_average_scores[system] = sum(score for _, score in scores) / len(scores)
        best_year, _ = max(scores, key=lambda pair: pair[1])
        best_years_by_system[system] = best_year
        caution_years_by_system[system] = [
            yr for yr, score in scores if score < CAUTION_THRESHOLD
        ]

    liuren_scores = [item.system_scores.get("liuren", 0.0) for item in years if "liuren" in item.system_scores]
    trend_summary = ""
    if liuren_scores:
        avg = sum(liuren_scores) / len(liuren_scores)
        trend_summary = (
            f"共 {len(years)} 年，大六壬平均 {avg:.1f} 分；"
            f"最高 {max(liuren_scores):.0f}，最低 {min(liuren_scores):.0f}。"
        )

    return SolarReturnTimeline(
        request=request,
        natal_birth_data=birth_data,
        natal_sun_longitude=sun_lon,
        benming_zhi=benming,
        years=years,
        system_average_scores=system_average_scores,
        best_years_by_system=best_years_by_system,
        caution_years_by_system=caution_years_by_system,
        trend_summary=trend_summary,
        computed_at=datetime.now(),
    )