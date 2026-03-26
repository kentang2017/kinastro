"""
七政四餘天文計算模組 (Astronomical Calculator for Seven Governors and Four Remainders)

使用 pyswisseph 進行天文計算，包括：
- 七政（日月五星）位置計算
- 四餘（羅睺、計都、月孛、紫氣）位置計算
- 十二宮位計算
- 星次（中國黃道十二宮）對應
"""

import swisseph as swe
from dataclasses import dataclass, field

from .constants import (
    SEVEN_GOVERNORS,
    FOUR_REMAINDERS,
    TWELVE_SIGNS_CHINESE,
    TWELVE_SIGNS_WESTERN,
    TWELVE_PALACES,
    FIVE_ELEMENTS,
    TWENTY_EIGHT_MANSIONS,
)


@dataclass
class PlanetPosition:
    """星曜位置資料"""
    name: str
    longitude: float        # 黃經度數 (0-360)
    latitude: float         # 黃緯度數
    sign_western: str       # 西方星座
    sign_chinese: str       # 中國星次
    sign_degree: float      # 在星座中的度數
    element: str            # 五行屬性
    retrograde: bool        # 是否逆行
    palace_index: int = -1  # 所在宮位索引


@dataclass
class HouseData:
    """宮位資料"""
    index: int              # 宮位序號 (0-11)
    name: str               # 宮位名稱
    cusp: float             # 宮頭度數
    sign_western: str       # 所在西方星座
    sign_chinese: str       # 所在中國星次
    planets: list = field(default_factory=list)


@dataclass
class ChartData:
    """排盤結果"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    planets: list           # List[PlanetPosition]
    houses: list            # List[HouseData]
    ascendant: float        # 上升點度數
    midheaven: float        # 中天度數


def _normalize_degree(deg: float) -> float:
    """將角度標準化到 0-360 度範圍"""
    return deg % 360.0


def _degree_to_sign_index(deg: float) -> int:
    """將黃經度數轉換為星座索引 (0-11)"""
    return int(_normalize_degree(deg) / 30.0)


def _degree_to_sign_degree(deg: float) -> float:
    """將黃經度數轉換為星座內度數"""
    return _normalize_degree(deg) % 30.0


def _get_western_sign(deg: float) -> str:
    """根據黃經度數取得西方星座名稱"""
    return TWELVE_SIGNS_WESTERN[_degree_to_sign_index(deg)]


def _get_chinese_sign(deg: float) -> str:
    """根據黃經度數取得中國星次名稱"""
    return TWELVE_SIGNS_CHINESE[_degree_to_sign_index(deg)]


def compute_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> ChartData:
    """
    計算七政四餘排盤

    Parameters:
        year: 年份
        month: 月份
        day: 日
        hour: 時
        minute: 分
        timezone: 時區偏移 (例如 +8.0 為東八區)
        latitude: 緯度
        longitude: 經度
        location_name: 地點名稱

    Returns:
        ChartData: 排盤結果資料
    """
    swe.set_ephe_path("")

    # 計算 Julian Day (轉為 UTC)
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # 計算宮位 (使用 Placidus 宮位制)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    ascendant = ascmc[0]
    midheaven = ascmc[1]

    # 計算七政位置
    planets = []
    for name, planet_id in SEVEN_GOVERNORS.items():
        result, flags = swe.calc_ut(jd, planet_id)
        lon = _normalize_degree(result[0])
        lat = result[1]
        speed = result[3]
        retrograde = speed < 0

        pos = PlanetPosition(
            name=name,
            longitude=lon,
            latitude=lat,
            sign_western=_get_western_sign(lon),
            sign_chinese=_get_chinese_sign(lon),
            sign_degree=_degree_to_sign_degree(lon),
            element=FIVE_ELEMENTS.get(name, ""),
            retrograde=retrograde,
        )
        planets.append(pos)

    # 計算四餘位置
    # 羅睺 (Rahu) = Mean North Node
    rahu_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["羅睺"])
    rahu_lon = _normalize_degree(rahu_result[0])
    planets.append(PlanetPosition(
        name="羅睺",
        longitude=rahu_lon,
        latitude=rahu_result[1],
        sign_western=_get_western_sign(rahu_lon),
        sign_chinese=_get_chinese_sign(rahu_lon),
        sign_degree=_degree_to_sign_degree(rahu_lon),
        element=FIVE_ELEMENTS.get("羅睺", ""),
        retrograde=False,
    ))

    # 計都 (Ketu) = 羅睺 + 180°
    ketu_lon = _normalize_degree(rahu_lon + 180.0)
    planets.append(PlanetPosition(
        name="計都",
        longitude=ketu_lon,
        latitude=-rahu_result[1],
        sign_western=_get_western_sign(ketu_lon),
        sign_chinese=_get_chinese_sign(ketu_lon),
        sign_degree=_degree_to_sign_degree(ketu_lon),
        element=FIVE_ELEMENTS.get("計都", ""),
        retrograde=False,
    ))

    # 月孛 (Yuebei) = Mean Apogee (Lilith)
    yuebei_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["月孛"])
    yuebei_lon = _normalize_degree(yuebei_result[0])
    planets.append(PlanetPosition(
        name="月孛",
        longitude=yuebei_lon,
        latitude=yuebei_result[1],
        sign_western=_get_western_sign(yuebei_lon),
        sign_chinese=_get_chinese_sign(yuebei_lon),
        sign_degree=_degree_to_sign_degree(yuebei_lon),
        element=FIVE_ELEMENTS.get("月孛", ""),
        retrograde=False,
    ))

    # 紫氣 (Ziqi) = 月孛 + 180°
    ziqi_lon = _normalize_degree(yuebei_lon + 180.0)
    planets.append(PlanetPosition(
        name="紫氣",
        longitude=ziqi_lon,
        latitude=-yuebei_result[1],
        sign_western=_get_western_sign(ziqi_lon),
        sign_chinese=_get_chinese_sign(ziqi_lon),
        sign_degree=_degree_to_sign_degree(ziqi_lon),
        element=FIVE_ELEMENTS.get("紫氣", ""),
        retrograde=False,
    ))

    # 建立宮位資料
    houses = []
    for i in range(12):
        cusp = cusps[i]
        house = HouseData(
            index=i,
            name=TWELVE_PALACES[i],
            cusp=cusp,
            sign_western=_get_western_sign(cusp),
            sign_chinese=_get_chinese_sign(cusp),
            planets=[],
        )
        houses.append(house)

    # 將星曜分配到宮位
    for planet in planets:
        palace_idx = _find_house(planet.longitude, cusps)
        planet.palace_index = palace_idx
        houses[palace_idx].planets.append(planet.name)

    return ChartData(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        julian_day=jd,
        planets=planets,
        houses=houses,
        ascendant=ascendant,
        midheaven=midheaven,
    )


def _find_house(lon: float, cusps: tuple) -> int:
    """根據黃經度數判斷星曜所在宮位"""
    lon = _normalize_degree(lon)
    for i in range(12):
        cusp_start = _normalize_degree(cusps[i])
        cusp_end = _normalize_degree(cusps[(i + 1) % 12])

        if cusp_start < cusp_end:
            if cusp_start <= lon < cusp_end:
                return i
        else:
            # 跨越 0° 的情況
            if lon >= cusp_start or lon < cusp_end:
                return i
    return 0


def format_degree(deg: float) -> str:
    """格式化度數顯示 (度°分'秒\")"""
    deg = _normalize_degree(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def get_mansion_for_degree(lon: float) -> dict:
    """
    根據黃經度數取得對應的二十八宿

    注意：這是簡化的對應方式，將 360° 平均分配給 28 宿。
    實際的二十八宿寬度不等，需要根據歷史星表進行精確計算。
    """
    lon = _normalize_degree(lon)
    mansion_width = 360.0 / 28.0
    idx = int(lon / mansion_width) % 28
    return TWENTY_EIGHT_MANSIONS[idx]
