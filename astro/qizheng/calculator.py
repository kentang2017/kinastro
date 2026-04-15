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
    EARTHLY_BRANCHES,
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
    index: int              # 宮位序號 (0-11): 命宮=0, 財帛=1, ...
    name: str               # 宮位名稱
    branch: int             # 地支索引 (0-11): 子=0, 丑=1, ..., 亥=11
    branch_name: str        # 地支名稱
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
    solar_month: int        # 節氣月 (1-12)
    hour_branch: int        # 時辰地支索引 (0-11)
    ming_gong_branch: int   # 命宮地支索引 (0-11)
    gender: str             # 性別 ("male" / "female")


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


def _get_hour_branch(hour: int, minute: int) -> int:
    """
    根據出生時間取得時辰地支索引（子=0, 丑=1, ..., 亥=11）。
    子時跨越午夜：23:00-01:00 為子時。
    """
    total_minutes = hour * 60 + minute
    if total_minutes < 60 or total_minutes >= 23 * 60:
        return 0   # 子時 (23:00–01:00)
    return (total_minutes + 60) // 120  # 每 2 小時一個時辰


def _get_solar_month(sun_longitude: float) -> int:
    """
    根據太陽黃經取得節氣月 (1-12)。

    正月(寅)起於立春 (太陽黃經 ≈ 315°)，每 30° 為一個月：
      月1(寅): 315°–345°   月7(申): 135°–165°
      月2(卯): 345°–15°    月8(酉): 165°–195°
      月3(辰): 15°–45°     月9(戌): 195°–225°
      月4(巳): 45°–75°     月10(亥): 225°–255°
      月5(午): 75°–105°    月11(子): 255°–285°
      月6(未): 105°–135°   月12(丑): 285°–315°
    """
    return int((sun_longitude - 315) % 360 / 30) + 1


def _get_ming_gong_branch(solar_month: int, hour_branch: int) -> int:
    """
    計算命宮地支索引。

    規則（虎月法）：
      以寅宮（地支索引2）為正月所在，逐月順數；
      再由出生時辰逆數。
    公式：(1 + solar_month - hour_branch) % 12
    """
    return (1 + solar_month - hour_branch) % 12


def _branch_to_cusp(branch: int) -> float:
    """
    地支索引 → 對應的黃經起始度數。

    每個地支佔 30° 等宮，戌宮(10)=0°–30°, 酉宮(9)=30°–60°, ...
    """
    sign_index = (10 - branch) % 12
    return sign_index * 30.0


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
    gender: str = "male",
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
        gender: 性別 ("male" 男命 / "female" 女命)

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

    # ---- 計算命宮 (Life Palace) ----
    # 太陽黃經 → 節氣月
    sun_lon = planets[0].longitude  # 太陽 is first
    solar_month = _get_solar_month(sun_lon)

    # 時辰地支
    hour_branch = _get_hour_branch(hour, minute)

    # 命宮地支：以命度（上升點）所在地支為命宮
    # 黃經星座索引(0=白羊..11=雙魚) 與地支索引(0=子..11=亥)的對應：
    #   戌(10)=0°(白羊), 酉(9)=30°(金牛), ..., 亥(11)=330°(雙魚)
    # 公式：branch = (10 - sign_index) % 12
    asc_sign_idx = _degree_to_sign_index(ascendant)
    ming_gong_branch = (10 - asc_sign_idx) % 12

    # ---- 建立宮位資料 (按命宮地支及性別方向排列) ----
    # 男命：順時針 (地支遞減)；女命：逆時針 (地支遞增)
    direction = 1 if gender == "female" else -1

    # 建立 branch → palace_index 映射
    branch_to_palace: dict[int, int] = {}
    for palace_idx in range(12):
        branch = (ming_gong_branch + direction * palace_idx) % 12
        branch_to_palace[branch] = palace_idx

    houses = []
    for palace_idx in range(12):
        branch = (ming_gong_branch + direction * palace_idx) % 12
        cusp = _branch_to_cusp(branch)
        house = HouseData(
            index=palace_idx,
            name=TWELVE_PALACES[palace_idx],
            branch=branch,
            branch_name=EARTHLY_BRANCHES[branch],
            cusp=cusp,
            sign_western=_get_western_sign(cusp),
            sign_chinese=_get_chinese_sign(cusp),
            planets=[],
        )
        houses.append(house)

    # 將星曜分配到宮位（按黃經度數對應地支）
    for planet in planets:
        planet_sign_idx = _degree_to_sign_index(planet.longitude)
        planet_branch = (10 - planet_sign_idx) % 12
        palace_idx = branch_to_palace.get(planet_branch, 0)
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
        solar_month=solar_month,
        hour_branch=hour_branch,
        ming_gong_branch=ming_gong_branch,
        gender=gender,
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


def get_mansion_index_for_degree(lon: float) -> int:
    """
    根據黃經度數取得對應的二十八宿索引 (0-27)

    使用各宿距星（determinative star）的 J2000 黃經作為宿界，
    每宿從其距星黃經延伸到下一宿的距星黃經（寬度不等）。
    """
    lon = _normalize_degree(lon)
    n = len(TWENTY_EIGHT_MANSIONS)
    for i in range(n):
        start = TWENTY_EIGHT_MANSIONS[i]["start_lon"]
        end = TWENTY_EIGHT_MANSIONS[(i + 1) % n]["start_lon"]
        if start < end:
            if start <= lon < end:
                return i
        else:
            # 跨越 0° 的情況
            if lon >= start or lon < end:
                return i
    return 0


def get_mansion_for_degree(lon: float) -> dict:
    """
    根據黃經度數取得對應的二十八宿

    使用各宿距星（determinative star）的 J2000 黃經作為宿界，
    每宿從其距星黃經延伸到下一宿的距星黃經（寬度不等）。

    Returns:
        dict: 包含以下鍵值的字典:
            - name (str): 宿名，例如 "角"、"亢"
            - element (str): 七曜屬性，例如 "木"、"金"
            - animal (str): 對應動物，例如 "蛟"、"龍"
            - group (str): 所屬方位，例如 "東方青龍"、"北方玄武"
            - start_lon (float): 距星黃經度數
    """
    return TWENTY_EIGHT_MANSIONS[get_mansion_index_for_degree(lon)]
