"""
江恩占星（Gann Astrology）x 七政四餘宏觀股市模組。

核心原則：
1) 時間先於價格（Time first, then price）
2) 聖經周期縮放後用於市場時間窗
3) 聖經周期 + 七政四餘流時守照 + 江恩振動（Square of 9）多重共振才採信
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

import swisseph as swe


_IMPORTANT_STARS = ("木星", "土星", "羅睺", "計都", "月孛", "紫氣")
_ALL_QIZHENG_STARS = ("太陽", "太陰", "水星", "金星", "火星", "木星", "土星", "羅睺", "計都", "月孛", "紫氣")
_IMPORTANT_STAR_BONUS = 1
_CYCLE_SCORE_WEIGHT = 2
_HIGH_RESONANCE_THRESHOLD = 8
_MEDIUM_RESONANCE_THRESHOLD = 4
_WEAK_RESONANCE_THRESHOLD = 1
_SQ9_ANGLE_TO_SQRT_STEP = 1.0 / 180.0
_ASPECT_WEIGHTS = {
    0.0: ("合", 2),
    60.0: ("六合", 1),
    90.0: ("刑", -2),
    120.0: ("拱", 2),
    180.0: ("沖", -2),
}

# 常見指數「出生圖」建議（宏觀應用）
GANN_NATAL_PRESETS = {
    "Dow Jones（1896-05-26）": date(1896, 5, 26),
    "S&P 500（1957-03-04）": date(1957, 3, 4),
    "Hang Seng（1969-11-24）": date(1969, 11, 24),
    "TSEC 台灣加權（1967-02-09）": date(1967, 2, 9),
    "SSE Composite（1990-12-19）": date(1990, 12, 19),
}
GANN_NATAL_DEFAULT = "Hang Seng（1969-11-24）"
GANN_NATAL_REFERENCE_PRICES = {
    "Dow Jones（1896-05-26）": 40000.0,
    "S&P 500（1957-03-04）": 5000.0,
    "Hang Seng（1969-11-24）": 20000.0,
    "TSEC 台灣加權（1967-02-09）": 20000.0,
    "SSE Composite（1990-12-19）": 3500.0,
}


@dataclass(frozen=True)
class BiblicalCycle:
    """聖經時間周期定義。"""

    key: str
    name: str
    base_years: float
    source: str
    note: str


_BIBLICAL_CYCLES: tuple[BiblicalCycle, ...] = (
    BiblicalCycle(
        key="day_for_year",
        name="一日頂一年（Ezek. 4:6 / Num. 14:34）",
        base_years=1.0,
        source="《但以理書》《以西結書》與 Gann Robert Gordon 信件",
        note="可映射為 1 年、1 交易年或其比例縮放。",
    ),
    BiblicalCycle(
        key="daniel_70_weeks",
        name="但以理七十個七（490）",
        base_years=490.0,
        source="Dan. 9:24-27 + Gann biblical timing",
        note="常縮放為 49 年、7 年、3.5 年等分形節奏。",
    ),
    BiblicalCycle(
        key="seven_years",
        name="七年周期（7）",
        base_years=7.0,
        source="七數循環（Sabbatic rhythm）",
        note="常見於政策/景氣切換。",
    ),
    BiblicalCycle(
        key="time_times_half",
        name="一載二載半載（3.5 年）",
        base_years=3.5,
        source="Dan. 7:25, 12:7; Rev. 12:14",
        note="中期轉折核心窗。",
    ),
    BiblicalCycle(
        key="prophetic_1260",
        name="1260 預言日（3.5 年）",
        base_years=1260.0 / 360.0,
        source="Rev. 12:6 + 360 天預言年",
        note="可直接轉為 1260 日或比例縮放。",
    ),
    BiblicalCycle(
        key="jubilee_49",
        name="禧年週期（49）",
        base_years=49.0,
        source="Lev. 25",
        note="長期結構性頂底參考。",
    ),
    BiblicalCycle(
        key="jubilee_50",
        name="禧年釋放（50）",
        base_years=50.0,
        source="Lev. 25",
        note="制度切換、流動性再定價。",
    ),
)


def _normalize_degree(value: float) -> float:
    return value % 360.0


def _angle_diff(a: float, b: float) -> float:
    diff = abs(_normalize_degree(a - b))
    return 360.0 - diff if diff > 180.0 else diff


def _to_date(value: date | datetime) -> date:
    return value.date() if isinstance(value, datetime) else value


def _add_business_days(start_date: date, days: int) -> date:
    if days == 0:
        return start_date
    current = start_date
    remaining = days
    step = 1 if days > 0 else -1
    while remaining != 0:
        current += timedelta(days=step)
        if current.weekday() < 5:
            remaining -= step
    return current


def scale_cycle_to_days(
    cycle_years: float,
    *,
    scale: float = 1.0,
    year_basis_days: float = 365.2425,
) -> int:
    """將聖經週期（年）縮放為日數。"""
    return max(1, int(round(cycle_years * year_basis_days * scale)))


def compute_biblical_cycle_dates(
    anchor_date: date | datetime,
    *,
    as_of_date: date | datetime,
    scale: float = 1.0,
    year_basis_days: float = 365.2425,
    use_trading_days: bool = False,
    lookback_years: float = 2.0,
    lookahead_years: float = 2.0,
    max_multiple: int = 12,
) -> list[dict]:
    """
    計算 Gann 聖經周期到期點（可縮放、可切換自然日/交易日）。
    """
    anchor = _to_date(anchor_date)
    as_of = _to_date(as_of_date)
    window_start = as_of - timedelta(days=int(lookback_years * year_basis_days))
    window_end = as_of + timedelta(days=int(lookahead_years * year_basis_days))

    rows: list[dict] = []
    for cycle in _BIBLICAL_CYCLES:
        cycle_days = scale_cycle_to_days(cycle.base_years, scale=scale, year_basis_days=year_basis_days)
        for multiple in range(1, max_multiple + 1):
            total_days = cycle_days * multiple
            if use_trading_days:
                due = _add_business_days(anchor, total_days)
            else:
                due = anchor + timedelta(days=total_days)
            if window_start <= due <= window_end:
                rows.append(
                    {
                        "cycle_key": cycle.key,
                        "cycle_name": cycle.name,
                        "multiple": multiple,
                        "cycle_days": cycle_days,
                        "due_date": due.isoformat(),
                        "distance_days": (due - as_of).days,
                        "source": cycle.source,
                        "note": cycle.note,
                    }
                )
    rows.sort(key=lambda r: abs(r["distance_days"]))
    return rows


def build_market_natal_longitudes(
    market_natal_date: date | datetime,
    *,
    timezone: float = 0.0,
) -> dict[str, float]:
    """建立市場出生圖（七政四餘）星曜經度。"""
    from ..constants import FOUR_REMAINDERS, SEVEN_GOVERNORS

    d = _to_date(market_natal_date)
    local_noon_as_utc = datetime(d.year, d.month, d.day, 12, 0) - timedelta(hours=timezone)
    decimal_hour = local_noon_as_utc.hour + local_noon_as_utc.minute / 60.0
    jd = swe.julday(local_noon_as_utc.year, local_noon_as_utc.month, local_noon_as_utc.day, decimal_hour)

    planets: dict[str, float] = {}
    for name, pid in SEVEN_GOVERNORS.items():
        result, _ = swe.calc_ut(jd, pid)
        planets[name] = _normalize_degree(result[0])

    ketu_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["計都"])
    ketu_lon = _normalize_degree(ketu_result[0])
    planets["計都"] = ketu_lon
    planets["羅睺"] = _normalize_degree(ketu_lon + 180.0)

    for name in ("月孛", "紫氣"):
        result, _ = swe.calc_ut(jd, FOUR_REMAINDERS[name])
        planets[name] = _normalize_degree(result[0])
    return planets


def get_transit_longitudes(transit_dt: datetime, *, timezone: float = 8.0) -> dict[str, float]:
    """由現有 qizheng_transit 取得流時盤星曜經度。"""
    from ..qizheng_transit import compute_transit

    t = compute_transit(
        year=transit_dt.year,
        month=transit_dt.month,
        day=transit_dt.day,
        hour=transit_dt.hour,
        minute=transit_dt.minute,
        timezone=timezone,
    )
    return {p.name: p.longitude for p in t.planets}


def evaluate_qizheng_resonance(
    natal_longitudes: dict[str, float],
    transit_longitudes: dict[str, float],
    *,
    orb: float = 3.0,
) -> list[dict]:
    """評估七政四餘本命 vs 流時在關鍵星上的守照/相位共振。"""
    rows: list[dict] = []
    for star in _ALL_QIZHENG_STARS:
        natal = natal_longitudes.get(star)
        transit = transit_longitudes.get(star)
        if natal is None or transit is None:
            continue
        diff = _angle_diff(transit, natal)
        matched = None
        for target, (aspect_name, base_score) in _ASPECT_WEIGHTS.items():
            if abs(diff - target) <= orb:
                bonus = _IMPORTANT_STAR_BONUS if star in _IMPORTANT_STARS and base_score > 0 else 0
                score = base_score + bonus
                matched = (aspect_name, score, target)
                break
        if not matched:
            continue
        aspect_name, score, target = matched
        rows.append(
            {
                "star": star,
                "aspect": aspect_name,
                "target_angle": target,
                "actual_angle": round(diff, 2),
                "score": score,
                "is_important_star": star in _IMPORTANT_STARS,
            }
        )
    rows.sort(key=lambda r: (-r["score"], r["actual_angle"]))
    return rows


def compute_square_of_nine_levels(
    reference_price: float,
    *,
    max_ring: int = 2,
) -> list[dict]:
    """
    Gann Square of 9 價格振動層級（輪中輪簡化）。
    """
    if reference_price <= 0:
        raise ValueError("reference_price must be positive")
    root = reference_price ** 0.5
    levels: list[dict] = []
    # 傳統近似：sqrt 軸每 +2 約對應 360°；因此 angle_step = angle * (1/180)
    for ring in range(max_ring + 1):
        for angle in range(0, 360, 45):
            step = (2.0 * ring) + (angle * _SQ9_ANGLE_TO_SQRT_STEP)
            target = (root + step) ** 2
            levels.append(
                {
                    "ring": ring,
                    "angle": angle,
                    "target_price": round(target, 4),
                }
            )
    levels.sort(key=lambda r: r["target_price"])
    return levels


def _classify_resonance(score: int) -> str:
    if score >= _HIGH_RESONANCE_THRESHOLD:
        return "高共振（時間窗 + 星曜守照齊備）"
    if score >= _MEDIUM_RESONANCE_THRESHOLD:
        return "中度共振（可觀察，等待確認）"
    if score >= _WEAK_RESONANCE_THRESHOLD:
        return "弱共振（僅作輔助）"
    return "低共振（不建議單獨採信）"


def build_gann_macro_timing(
    *,
    market_natal_date: date | datetime,
    as_of_datetime: datetime,
    timezone: float = 8.0,
    cycle_scale: float = 0.1,
    use_trading_days: bool = False,
    cycle_orb_days: int = 12,
    year_basis_days: float = 365.2425,
    natal_longitudes: Optional[dict[str, float]] = None,
    transit_longitudes: Optional[dict[str, float]] = None,
) -> dict:
    """
    江恩宏觀 timing：
    - 聖經周期到期點
    - 七政四餘流時守照
    - 多重共振分數與進出場條件
    """
    cycle_hits = compute_biblical_cycle_dates(
        market_natal_date,
        as_of_date=as_of_datetime,
        scale=cycle_scale,
        year_basis_days=year_basis_days,
        use_trading_days=use_trading_days,
        lookback_years=2.0,
        lookahead_years=2.0,
    )
    near_hits = [x for x in cycle_hits if abs(x["distance_days"]) <= cycle_orb_days]

    natal_map = natal_longitudes or build_market_natal_longitudes(market_natal_date, timezone=timezone)
    transit_map = transit_longitudes or get_transit_longitudes(as_of_datetime, timezone=timezone)
    qizheng_hits = evaluate_qizheng_resonance(natal_map, transit_map, orb=3.0)

    cycle_score = _CYCLE_SCORE_WEIGHT * len(near_hits)
    astro_score = sum(x["score"] for x in qizheng_hits)
    total_score = cycle_score + astro_score

    positive_aspects = [x for x in qizheng_hits if x["score"] > 0]
    negative_aspects = [x for x in qizheng_hits if x["score"] < 0]
    entry_conditions = [
        "至少 1 個聖經周期在容差窗內",
        "七政四餘關鍵星曜（木星/土星/羅睺/計都/月孛/紫氣）出現至少 1 個正向守照",
        "總共振分數達中度（>=4）",
    ]
    exit_conditions = [
        "關鍵周期窗結束且未出現延伸共振",
        "負向守照（刑/沖）數量高於正向守照",
        "總共振分數降至 <=0",
    ]

    return {
        "market_natal_date": _to_date(market_natal_date).isoformat(),
        "as_of": as_of_datetime.isoformat(),
        "cycle_scale": cycle_scale,
        "use_trading_days": use_trading_days,
        "cycle_orb_days": cycle_orb_days,
        "cycle_hits": cycle_hits,
        "near_cycle_hits": near_hits,
        "qizheng_resonance_hits": qizheng_hits,
        "scores": {
            "cycle_score": cycle_score,
            "astro_score": astro_score,
            "total_score": total_score,
            "classification": _classify_resonance(total_score),
            "positive_aspect_count": len(positive_aspects),
            "negative_aspect_count": len(negative_aspects),
        },
        "entry_conditions": entry_conditions,
        "exit_conditions": exit_conditions,
        "notes": [
            "Gann 原則：時間先於價格，必須等待多重共振。",
            "市場實務建議：先以宏觀指數做時窗，再下鑽板塊與風險控制。",
        ],
    }


def build_gann_macro_with_dasha_context(
    *,
    market_natal_date: date | datetime,
    as_of_datetime: datetime,
    timezone: float = 8.0,
    cycle_scale: float = 0.1,
    use_trading_days: bool = False,
    dasha_context: Optional[dict] = None,
) -> dict:
    """
    與 qizheng_dasha 整合的示例封裝。

    dasha_context 需包含：
    - birth_year, ming_gong_branch, gender, houses
    """
    payload = build_gann_macro_timing(
        market_natal_date=market_natal_date,
        as_of_datetime=as_of_datetime,
        timezone=timezone,
        cycle_scale=cycle_scale,
        use_trading_days=use_trading_days,
    )
    if not dasha_context:
        payload["dasha"] = None
        return payload

    from ..qizheng_dasha import compute_dasha

    d = compute_dasha(
        birth_year=dasha_context["birth_year"],
        ming_gong_branch=dasha_context["ming_gong_branch"],
        gender=dasha_context["gender"],
        houses=dasha_context["houses"],
        current_year=as_of_datetime.year,
    )
    payload["dasha"] = {
        "current_period_idx": d.current_period_idx,
        "current_age": d.current_age,
        "flow_year_branch": d.flow_year_branch,
        "flow_year_palace": d.flow_year_palace,
    }
    return payload
