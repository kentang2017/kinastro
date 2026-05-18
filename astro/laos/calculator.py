"""Laos Horasat calculator.

此模組提供老撾占星（ໄທຣາສາດລາວ）的純計算能力：
- 出生盤（七曜 + 羅睺 / 計都）
- 老撾曆日期資訊與特殊年份分析
- ສັງຄົມ 擇日吉凶
- ສີກາດ 時段建議
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Literal

import swisseph as swe

from .data.calendar_rules import get_lao_date_info
from .data.sangkhom_tables import SUPPORTED_SANGKHOM_ACTIVITIES, get_sangkhom_for_date
from .data.sikarat import get_best_sikarat_hours, get_sikarat_for_datetime
from .data.special_years import analyze_special_year

HouseSystem = Literal["whole_sign"]

# 主要行星映射（依專案 Thai 模組風格，採用簡潔 key）
_LAO_GRAHA_IDS: Dict[str, int] = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
}

# 行星符號（含羅睺 / 計都）
_PLANET_SYMBOLS: Dict[str, str] = {
    "sun": "☉",
    "moon": "☾",
    "mars": "♂",
    "mercury": "☿",
    "jupiter": "♃",
    "venus": "♀",
    "saturn": "♄",
    "rahu": "☊",
    "ketu": "☋",
}


@dataclass
class LaoPlanet:
    """單一星曜資料。"""

    key: str
    symbol: str
    longitude: float
    latitude: float
    speed: float
    sign_index: int
    sign_degree: float
    house: int
    retrograde: bool


@dataclass
class LaoChart:
    """老撾出生盤資料模型。"""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    house_system: HouseSystem
    julian_day_ut: float
    ayanamsa: float
    ascendant: float
    lao_date: Dict[str, Any]
    special_year: Dict[str, Any]
    sangkhom: Dict[str, Any]
    sikarat: Dict[str, Any]
    planets: List[LaoPlanet] = field(default_factory=list)


def _init_swe() -> None:
    """初始化 Swiss Ephemeris，若專案初始化失敗則使用預設路徑。"""

    try:
        from astro.swe_init import init_swe

        init_swe()
    except Exception:
        swe.set_ephe_path("")


def _norm(deg: float) -> float:
    """角度正規化到 0~360。"""

    return deg % 360.0


def _sign_index(longitude: float) -> int:
    """回傳黃道宮位索引（0~11）。"""

    return int(_norm(longitude) // 30.0)


def _sign_degree(longitude: float) -> float:
    """回傳宮內度數（0~30）。"""

    return _norm(longitude) % 30.0


def _resolve_activity(activity: str | None) -> str:
    """標準化活動名稱，避免傳入未知活動造成表格查詢失敗。"""

    if activity and activity in SUPPORTED_SANGKHOM_ACTIVITIES:
        return activity
    return SUPPORTED_SANGKHOM_ACTIVITIES[0] if SUPPORTED_SANGKHOM_ACTIVITIES else "ການແຕ່ງງານ"


def _planet_house_whole_sign(lon: float, ascendant: float) -> int:
    """Whole-sign 宮位計算。"""

    return ((_sign_index(lon) - _sign_index(ascendant)) % 12) + 1


def _validate_datetime(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
) -> None:
    """輸入驗證，統一在入口處檢查，避免下游錯誤難以追查。"""

    try:
        datetime(year, month, day, hour, minute)
    except ValueError as exc:
        raise ValueError(f"出生日期時間不合法：{exc}") from exc

    if not -12.0 <= timezone <= 14.0:
        raise ValueError("timezone 必須介於 -12 到 +14")


def compute_lao_chart(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    house_system: HouseSystem = "whole_sign",
    sangkhom_activity: str = "ການແຕ່ງງານ",
    sikarat_type: str = "ສີກາດລາວ",
) -> LaoChart:
    """計算老撾占星出生盤。

    與 Thai 模組相同：
    - 純計算函式（不依賴 Streamlit）
    - 回傳結構化 dataclass，方便 UI 與 API 重用
    """

    _validate_datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
    )

    if house_system != "whole_sign":
        raise ValueError(f"目前僅支援 whole_sign，收到：{house_system}")

    _init_swe()
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # UTC 小時：與專案既有星盤計算邏輯一致
    decimal_hour_ut = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, decimal_hour_ut)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # 先取 Asc（sidereal）
    _, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    ascendant = _norm(ascmc[0])

    planets: List[LaoPlanet] = []
    for key, pid in _LAO_GRAHA_IDS.items():
        result, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        lon = _norm(result[0])
        speed = result[3]
        planets.append(
            LaoPlanet(
                key=key,
                symbol=_PLANET_SYMBOLS[key],
                longitude=lon,
                latitude=result[1],
                speed=speed,
                sign_index=_sign_index(lon),
                sign_degree=_sign_degree(lon),
                house=_planet_house_whole_sign(lon, ascendant),
                retrograde=speed < 0,
            )
        )

    # 羅睺 / 計都
    rahu_raw, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _norm(rahu_raw[0])
    ketu_lon = _norm(rahu_lon + 180.0)

    planets.extend(
        [
            LaoPlanet(
                key="rahu",
                symbol=_PLANET_SYMBOLS["rahu"],
                longitude=rahu_lon,
                latitude=rahu_raw[1],
                speed=rahu_raw[3],
                sign_index=_sign_index(rahu_lon),
                sign_degree=_sign_degree(rahu_lon),
                house=_planet_house_whole_sign(rahu_lon, ascendant),
                retrograde=True,
            ),
            LaoPlanet(
                key="ketu",
                symbol=_PLANET_SYMBOLS["ketu"],
                longitude=ketu_lon,
                latitude=-rahu_raw[1],
                speed=rahu_raw[3],
                sign_index=_sign_index(ketu_lon),
                sign_degree=_sign_degree(ketu_lon),
                house=_planet_house_whole_sign(ketu_lon, ascendant),
                retrograde=True,
            ),
        ]
    )

    local_dt = datetime(year, month, day, hour, minute)
    local_day = local_dt.date()

    lao_date = get_lao_date_info(local_day)
    special_year = analyze_special_year(year, era="gregorian")
    activity = _resolve_activity(sangkhom_activity)
    sangkhom = get_sangkhom_for_date(activity, local_day)

    # ສີກາດ：保留當下時段 + 推薦吉時列表
    sikarat = get_sikarat_for_datetime(local_dt, sikarat_type=sikarat_type)
    sikarat["best_hours"] = get_best_sikarat_hours(activity)

    return LaoChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        house_system=house_system,
        julian_day_ut=jd_ut,
        ayanamsa=ayanamsa,
        ascendant=ascendant,
        lao_date=lao_date,
        special_year=special_year,
        sangkhom=sangkhom,
        sikarat=sikarat,
        planets=planets,
    )


def chart_to_dict(chart: LaoChart) -> Dict[str, Any]:
    """序列化 LaoChart，供 API / AI / 前端存取。"""

    data = asdict(chart)
    data["system"] = "lao_horasat"
    data["system_name"] = "ໄທຣາສາດລາວ"
    return data


def get_lao_auspicious_time(
    target_dt: datetime,
    *,
    activity: str = "ການແຕ່ງງານ",
    sikarat_type: str = "ສີກາດລາວ",
) -> Dict[str, Any]:
    """查詢單一時間點的 ສັງຄົມ + ສີກາດ 建議。"""

    resolved = _resolve_activity(activity)
    sangkhom = get_sangkhom_for_date(resolved, target_dt.date())
    sikarat = get_sikarat_for_datetime(target_dt, sikarat_type=sikarat_type)
    sikarat["best_hours"] = get_best_sikarat_hours(resolved)

    return {
        "activity": resolved,
        "lao_date": sangkhom.get("lao_date"),
        "sangkhom": sangkhom,
        "sikarat": sikarat,
    }


def find_best_dates(
    start_dt: datetime,
    *,
    days: int = 30,
    activity: str = "ການແຕ່ງງານ",
) -> List[Dict[str, Any]]:
    """尋找未來 N 天較吉利的日期（基於 ສັງຄົມ 表格）。"""

    if days <= 0:
        raise ValueError("days 必須大於 0")

    resolved = _resolve_activity(activity)
    result: List[Dict[str, Any]] = []

    for i in range(days):
        current_day = (start_dt + timedelta(days=i)).date()
        daily = get_sangkhom_for_date(resolved, current_day)
        status = str(daily.get("status", ""))
        if "✅" in status:
            result.append(
                {
                    "date": current_day.isoformat(),
                    "status": daily.get("status", ""),
                    "recommendation": daily.get("recommendation", ""),
                    "lao_date": daily.get("lao_date", ""),
                }
            )

    return result


def get_monthly_fortune(
    year: int,
    month: int,
    *,
    activity: str = "ການແຕ່ງງານ",
) -> List[Dict[str, Any]]:
    """回傳指定月份的每日 ສັງຄົມ 吉凶摘要。"""

    first_day = date(year, month, 1)
    next_month = date(year + (month // 12), ((month % 12) + 1), 1)
    total_days = (next_month - first_day).days
    resolved = _resolve_activity(activity)

    rows: List[Dict[str, Any]] = []
    for d in range(1, total_days + 1):
        g_date = date(year, month, d)
        daily = get_sangkhom_for_date(resolved, g_date)
        rows.append(
            {
                "day": d,
                "date": g_date.isoformat(),
                "status": daily.get("status", ""),
                "recommendation": daily.get("recommendation", ""),
            }
        )

    return rows
