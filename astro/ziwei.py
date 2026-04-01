"""
紫微斗數排盤模組 (Zi Wei Dou Shu Chart Module)

紫微斗數是中國傳統命理學的重要命理排盤系統，以下是主要特點：
- 十二宮位（命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、
           遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮）
- 主星：紫微系（紫微、天機、太陽、武曲、天同、廉貞）+
         天府系（天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍）
- 五行局決定排盤規則（水二局、木三局、金四局、土五局、火六局）

使用農曆新年查找表搭配 pyswisseph 朔望月計算確定農曆月份。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

LUNAR_MONTH_NAMES = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月",
]

HOUR_BRANCH_NAMES = [
    "子時(23-01)", "丑時(01-03)", "寅時(03-05)", "卯時(05-07)",
    "辰時(07-09)", "巳時(09-11)", "午時(11-13)", "未時(13-15)",
    "申時(15-17)", "酉時(17-19)", "戌時(19-21)", "亥時(21-23)",
]

# 五行局
WU_XING_JU_NAMES = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}

# 十二宮位名稱（從命宮起，逆時針地支方向排列）
# 命宮在某地支，兄弟宮在下一個地支，依此類推
PALACE_SEQUENCE = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

# 紫微系：相對於紫微星地支的偏移（順方向 mod 12）
ZIWEI_GROUP = {
    "紫微": 0,
    "天機": 11,   # 逆1 → +11 mod 12
    "太陽": 2,
    "武曲": 3,
    "天同": 4,
    "廉貞": 7,
}

# 天府系：相對於天府星地支的偏移（順方向 mod 12）
TIANFU_GROUP = {
    "天府": 0,
    "太陰": 1,
    "貪狼": 2,
    "巨門": 3,
    "天相": 4,
    "天梁": 5,
    "七殺": 6,
    "破軍": 10,
}

# 主星屬性（五行、別稱、顏色）
STAR_ATTRIBUTES = {
    "紫微": ("土", "帝王星", "#C62828"),
    "天機": ("木", "謀略星", "#2E7D32"),
    "太陽": ("火", "官祿星", "#E65100"),
    "武曲": ("金", "財星", "#F9A825"),
    "天同": ("水", "福星", "#1565C0"),
    "廉貞": ("火", "囚星", "#AD1457"),
    "天府": ("土", "財帛星", "#6A1B9A"),
    "太陰": ("水", "田宅星", "#37474F"),
    "貪狼": ("木/水", "桃花星", "#4A148C"),
    "巨門": ("水", "是非星", "#004D40"),
    "天相": ("水", "印星", "#0D47A1"),
    "天梁": ("土", "蔭星", "#33691E"),
    "七殺": ("金/火", "將星", "#B71C1C"),
    "破軍": ("水", "耗星", "#311B92"),
}

# 農曆新年公曆日期查找表 1900–2050（月, 日）
# 資料來源：天文計算（公開領域）
_CHINESE_NEW_YEAR: dict[int, tuple[int, int]] = {
    1900: (1, 31), 1901: (2, 19), 1902: (2,  8), 1903: (1, 29), 1904: (2, 16),
    1905: (2,  4), 1906: (1, 25), 1907: (2, 13), 1908: (2,  2), 1909: (1, 22),
    1910: (2, 10), 1911: (1, 30), 1912: (2, 18), 1913: (2,  6), 1914: (1, 26),
    1915: (2, 14), 1916: (2,  3), 1917: (1, 23), 1918: (2, 11), 1919: (2,  1),
    1920: (2, 20), 1921: (2,  8), 1922: (1, 28), 1923: (2, 16), 1924: (2,  5),
    1925: (1, 25), 1926: (2, 13), 1927: (2,  2), 1928: (1, 23), 1929: (2, 10),
    1930: (1, 30), 1931: (2, 17), 1932: (2,  6), 1933: (1, 26), 1934: (2, 14),
    1935: (2,  4), 1936: (1, 24), 1937: (2, 11), 1938: (1, 31), 1939: (2, 19),
    1940: (2,  8), 1941: (1, 27), 1942: (2, 15), 1943: (2,  5), 1944: (1, 25),
    1945: (2, 13), 1946: (2,  2), 1947: (1, 22), 1948: (2, 10), 1949: (1, 29),
    1950: (2, 17), 1951: (2,  6), 1952: (1, 27), 1953: (2, 14), 1954: (2,  3),
    1955: (1, 24), 1956: (2, 12), 1957: (1, 31), 1958: (2, 18), 1959: (2,  8),
    1960: (1, 28), 1961: (2, 15), 1962: (2,  5), 1963: (1, 25), 1964: (2, 13),
    1965: (2,  2), 1966: (1, 21), 1967: (2,  9), 1968: (1, 30), 1969: (2, 17),
    1970: (2,  6), 1971: (1, 27), 1972: (2, 15), 1973: (2,  3), 1974: (1, 23),
    1975: (2, 11), 1976: (1, 31), 1977: (2, 18), 1978: (2,  7), 1979: (1, 28),
    1980: (2, 16), 1981: (2,  5), 1982: (1, 25), 1983: (2, 13), 1984: (2,  2),
    1985: (2, 20), 1986: (2,  9), 1987: (1, 29), 1988: (2, 17), 1989: (2,  6),
    1990: (1, 27), 1991: (2, 15), 1992: (2,  4), 1993: (1, 23), 1994: (2, 10),
    1995: (1, 31), 1996: (2, 19), 1997: (2,  7), 1998: (1, 28), 1999: (2, 16),
    2000: (2,  5), 2001: (1, 24), 2002: (2, 12), 2003: (2,  1), 2004: (1, 22),
    2005: (2,  9), 2006: (1, 29), 2007: (2, 18), 2008: (2,  7), 2009: (1, 26),
    2010: (2, 14), 2011: (2,  3), 2012: (1, 23), 2013: (2, 10), 2014: (1, 31),
    2015: (2, 19), 2016: (2,  8), 2017: (1, 28), 2018: (2, 16), 2019: (2,  5),
    2020: (1, 25), 2021: (2, 12), 2022: (2,  1), 2023: (1, 22), 2024: (2, 10),
    2025: (1, 29), 2026: (2, 17), 2027: (2,  6), 2028: (1, 26), 2029: (2, 13),
    2030: (2,  3), 2031: (1, 23), 2032: (2, 11), 2033: (1, 31), 2034: (2, 19),
    2035: (2,  8), 2036: (1, 28), 2037: (2, 15), 2038: (2,  4), 2039: (1, 24),
    2040: (2, 12), 2041: (2,  1), 2042: (1, 22), 2043: (2, 10), 2044: (1, 30),
    2045: (2, 17), 2046: (2,  6), 2047: (1, 26), 2048: (2, 14), 2049: (2,  2),
    2050: (1, 23),
}

# 平均朔望月長度（天）。此常數用於逼近下次朔望的初始估算；
# 精確朔日時刻由 pyswisseph 的日月黃經迭代法確定。
_SYNODIC_MONTH = 29.5305891

# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ZiweiPalace:
    """紫微斗數宮位資料"""
    index: int                      # 宮位序號 0-11（從命宮算起）
    name: str                       # 宮位名稱
    branch: int                     # 地支索引 0-11（子=0）
    branch_name: str                # 地支名稱
    stem: int                       # 天干索引 0-9
    stem_name: str                  # 天干名稱
    stars: list = field(default_factory=list)  # 在此宮的主星名稱


@dataclass
class ZiweiChart:
    """紫微斗數命盤資料"""
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

    # 農曆資訊
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool
    lunar_year_stem: int       # 天干索引
    lunar_year_branch: int     # 地支索引

    # 時辰
    hour_branch: int           # 0-11

    # 命盤關鍵資訊
    ming_gong_branch: int      # 命宮地支索引
    shen_gong_branch: int      # 身宮地支索引
    wu_xing_ju: int            # 五行局（2-6）
    ziwei_branch: int          # 紫微星地支索引

    # 宮位資料
    palaces: list              # List[ZiweiPalace]


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _get_hour_branch(hour: int, minute: int) -> int:
    """
    根據出生時間取得時辰地支索引（子=0, 丑=1, ..., 亥=11）。
    子時跨越午夜：23:00-01:00 為子時。
    """
    total_minutes = hour * 60 + minute
    if total_minutes < 60 or total_minutes >= 23 * 60:
        return 0   # 子時 (23:00–01:00)
    return (total_minutes + 60) // 120  # 每 2 小時一個時辰


def _find_new_moon_near(jd_approx: float) -> float:
    """
    以迭代法（牛頓法）找出最接近 jd_approx 的朔（新月）Julian Day。
    收斂至誤差 < 0.0001° 的日食相角。
    """
    jd = jd_approx
    for _ in range(50):
        sun_lon = _normalize(swe.calc_ut(jd, swe.SUN)[0][0])
        moon_lon = _normalize(swe.calc_ut(jd, swe.MOON)[0][0])
        diff = moon_lon - sun_lon
        if diff > 180:
            diff -= 360.0
        elif diff < -180:
            diff += 360.0
        # 月球相對太陽速度約 12.19°/天
        correction = diff / (360.0 / _SYNODIC_MONTH)
        jd -= correction
        if abs(diff) < 0.0001:
            break
    return jd


def _get_cny_jd(year: int) -> float:
    """取得農曆新年的 Julian Day。僅支援 1900–2050；超出範圍時回傳近似值。"""
    if year in _CHINESE_NEW_YEAR:
        m, d = _CHINESE_NEW_YEAR[year]
        return swe.julday(year, m, d, 12.0)
    # 超出查找表範圍：以鄰近端點外推（精度不佳，僅作 fallback）
    if year < 1900:
        m, d = _CHINESE_NEW_YEAR[1900]
        base_jd = swe.julday(1900, m, d, 12.0)
        return base_jd - (1900 - year) * 365.2425
    m, d = _CHINESE_NEW_YEAR[2050]
    base_jd = swe.julday(2050, m, d, 12.0)
    return base_jd + (year - 2050) * 365.2425


def _solar_to_lunar(jd: float) -> tuple[int, int, int, bool]:
    """
    將 Julian Day 轉換為農曆日期。

    Returns:
        (lunar_year, lunar_month, lunar_day, is_leap_month)
        lunar_month: 1-12（閏月與正常月同編號，is_leap_month=True 區分）
    """
    # 先由儒略日推算公曆年份
    gd = swe.revjul(jd)  # (year, month, day, hour)
    gy = int(gd[0])

    # 確定農曆年：若在當年農曆新年之前，則屬於前一農曆年
    cny_this = _get_cny_jd(gy)
    if jd < cny_this:
        lunar_year = gy - 1
        cny_jd = _get_cny_jd(gy - 1)
    else:
        lunar_year = gy
        cny_jd = cny_this

    # 找出農曆新年當天精確的朔日 JD
    nm_start = _find_new_moon_near(cny_jd)
    # 確保 nm_start <= cny_jd（處理精度邊界）
    while nm_start > cny_jd + 1.0:
        nm_start = _find_new_moon_near(nm_start - _SYNODIC_MONTH)

    # 從農曆新年（正月初一）的朔日開始，逐月計算
    month = 0
    prev_nm = nm_start
    next_nm = _find_new_moon_near(nm_start + _SYNODIC_MONTH)
    is_leap = False

    for m in range(14):  # 農曆年最多 13 個月
        if next_nm > jd:
            month = m + 1
            break
        prev_nm = next_nm
        next_nm = _find_new_moon_near(prev_nm + _SYNODIC_MONTH)
    else:
        month = 1  # fallback

    # 農曆日（1 起計）
    lunar_day = int(jd - prev_nm) + 1
    lunar_day = max(1, min(lunar_day, 30))

    # 閏月判斷（簡化版）：農曆年有 13 個月時，第 13 個月視為閏月並折回 12。
    # 嚴格的中氣判斷需要太陽黃經計算，此處採取保守近似——若月份計數超過
    # 12 即標記為閏月，並以相同月份編號記錄。對紫微斗數安星而言，正確的
    # 農曆月份編號（1–12）是關鍵輸入，閏月旗標供顯示用途參考。
    if month > 12:
        is_leap = True
        month = month - 12

    return lunar_year, month, lunar_day, is_leap


def _get_year_stem(lunar_year: int) -> int:
    """
    取得農曆年的天干索引（甲=0, 乙=1, ..., 癸=9）。
    公式：(year - 4) % 10
    """
    return (lunar_year - 4) % 10


def _get_year_branch(lunar_year: int) -> int:
    """
    取得農曆年的地支索引（子=0, 丑=1, ..., 亥=11）。
    公式：(year - 4) % 12
    """
    return (lunar_year - 4) % 12


def _get_ming_gong_branch(lunar_month: int, hour_branch: int) -> int:
    """
    計算命宮地支索引。

    規則（虎月法）：
      以寅宮（地支索引2）為正月所在，逐月順數；
      再由出生時辰逆數。
    公式：(1 + lunar_month - hour_branch) % 12
    """
    return (1 + lunar_month - hour_branch) % 12


def _get_shen_gong_branch(lunar_month: int, hour_branch: int) -> int:
    """
    計算身宮地支索引。

    規則：以寅宮起，逐月順數，再順數時辰。
    公式：(1 + lunar_month + hour_branch) % 12
    """
    return (1 + lunar_month + hour_branch) % 12


def _get_ming_gong_stem(year_stem: int, ming_gong_branch: int) -> int:
    """
    取得命宮天干索引（用於判斷五行局）。

    步驟：
      1. 以年天干推算寅宮天干（虎年起法）：
         寅宮天干 = (2 * (year_stem % 5) + 2) % 10
      2. 命宮天干 = (寅宮天干 + (命宮地支 - 2 + 12) % 12) % 10
    """
    yin_stem = (2 * (year_stem % 5) + 2) % 10
    steps = (ming_gong_branch - 2 + 12) % 12
    return (yin_stem + steps) % 10


def _get_wu_xing_ju(ming_gong_stem: int) -> int:
    """
    由命宮天干判斷五行局號（2-6）。

    甲/己 → 水二局（2）
    乙/庚 → 木三局（3）
    丙/辛 → 金四局（4）
    丁/壬 → 土五局（5）
    戊/癸 → 火六局（6）
    """
    return (ming_gong_stem % 5) + 2


def _get_ziwei_branch(lunar_day: int, wu_xing_ju: int) -> int:
    """
    由農曆生日與五行局計算紫微星所在地支索引。

    安紫微法（起寅宮，依局數推算）：
      d0 = lunar_day - 1
      main_offset = (d0 // n) * n
      back_offset = (n - d0 % n) % n
      branch = (2 + main_offset + back_offset) % 12
    """
    n = wu_xing_ju
    d0 = lunar_day - 1
    main_offset = (d0 // n) * n
    back_offset = (n - d0 % n) % n
    return (2 + main_offset + back_offset) % 12


def _get_tianfu_branch(ziwei_branch: int) -> int:
    """
    由紫微星地支計算天府星地支索引。
    公式：(14 - ziwei_branch) % 12
    """
    return (14 - ziwei_branch) % 12


def _place_main_stars(ziwei_branch: int) -> dict[int, list[str]]:
    """
    計算所有 14 顆主星的地支索引，返回 {branch_index: [star_names]} 映射。
    """
    stars: dict[int, list[str]] = {i: [] for i in range(12)}
    tianfu_branch = _get_tianfu_branch(ziwei_branch)

    for name, offset in ZIWEI_GROUP.items():
        b = (ziwei_branch + offset) % 12
        stars[b].append(name)

    for name, offset in TIANFU_GROUP.items():
        b = (tianfu_branch + offset) % 12
        stars[b].append(name)

    return stars


def _build_palaces(
    ming_gong_branch: int,
    year_stem: int,
    stars_by_branch: dict[int, list[str]],
) -> list[ZiweiPalace]:
    """
    建立十二宮位資料，命宮在 ming_gong_branch，依地支順序排列。
    宮位天干由虎年起法推算。
    """
    # 寅宮天干
    yin_stem = (2 * (year_stem % 5) + 2) % 10

    palaces = []
    for idx in range(12):
        branch = (ming_gong_branch + idx) % 12
        palace_name = PALACE_SEQUENCE[idx]
        steps = (branch - 2 + 12) % 12
        stem = (yin_stem + steps) % 10
        palaces.append(ZiweiPalace(
            index=idx,
            name=palace_name,
            branch=branch,
            branch_name=EARTHLY_BRANCHES[branch],
            stem=stem,
            stem_name=HEAVENLY_STEMS[stem],
            stars=list(stars_by_branch.get(branch, [])),
        ))
    return palaces


# ============================================================
# 計算函數 (Computation)
# ============================================================

def compute_ziwei_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> ZiweiChart:
    """
    計算紫微斗數命盤。

    Parameters:
        year, month, day: 公曆出生日期
        hour, minute:     出生時間（24 小時制）
        timezone:         時區偏移（UTC+N）
        latitude:         緯度（排盤資訊用途）
        longitude:        經度（排盤資訊用途）
        location_name:    地點名稱

    Returns:
        ZiweiChart: 命盤資料
    """
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # 農曆轉換
    lunar_year, lunar_month, lunar_day, is_leap = _solar_to_lunar(jd)

    # 時辰地支
    hour_branch = _get_hour_branch(hour, minute)

    # 農曆年天干地支
    year_stem = _get_year_stem(lunar_year)
    year_branch = _get_year_branch(lunar_year)

    # 命宮 / 身宮
    ming_gong_branch = _get_ming_gong_branch(lunar_month, hour_branch)
    shen_gong_branch = _get_shen_gong_branch(lunar_month, hour_branch)

    # 五行局
    mg_stem = _get_ming_gong_stem(year_stem, ming_gong_branch)
    wu_xing_ju = _get_wu_xing_ju(mg_stem)

    # 紫微星位置
    ziwei_branch = _get_ziwei_branch(lunar_day, wu_xing_ju)

    # 安星
    stars_by_branch = _place_main_stars(ziwei_branch)

    # 建立宮位
    palaces = _build_palaces(ming_gong_branch, year_stem, stars_by_branch)

    return ZiweiChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        lunar_year=lunar_year, lunar_month=lunar_month, lunar_day=lunar_day,
        is_leap_month=is_leap,
        lunar_year_stem=year_stem, lunar_year_branch=year_branch,
        hour_branch=hour_branch,
        ming_gong_branch=ming_gong_branch, shen_gong_branch=shen_gong_branch,
        wu_xing_ju=wu_xing_ju, ziwei_branch=ziwei_branch,
        palaces=palaces,
    )


# ============================================================
# 渲染函數 (Rendering)
# ============================================================

def render_ziwei_chart(chart: ZiweiChart) -> None:
    """渲染完整的紫微斗數命盤。"""
    st.subheader("🌟 紫微斗數命盤")
    _render_info(chart)
    st.divider()
    _render_palace_grid(chart)
    st.divider()
    _render_star_table(chart)
    st.divider()
    _render_palace_details(chart)


def _render_info(chart: ZiweiChart) -> None:
    """渲染基本排盤資訊卡片。"""
    leap_str = "（閏月）" if chart.is_leap_month else ""
    lunar_date = (
        f"{chart.lunar_year}年"
        f"（{HEAVENLY_STEMS[chart.lunar_year_stem]}{EARTHLY_BRANCHES[chart.lunar_year_branch]}年）"
        f" {LUNAR_MONTH_NAMES[chart.lunar_month - 1]}{leap_str}"
        f" 初{_day_to_chinese(chart.lunar_day)}"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**公曆:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**農曆:** {lunar_date}")
        st.write(f"**時辰:** {HOUR_BRANCH_NAMES[chart.hour_branch]}")
        st.write(f"**地點:** {chart.location_name}")
    with col3:
        wu_ju_name = WU_XING_JU_NAMES[chart.wu_xing_ju]
        st.write(f"**命宮:** {EARTHLY_BRANCHES[chart.ming_gong_branch]}宮")
        st.write(f"**身宮:** {EARTHLY_BRANCHES[chart.shen_gong_branch]}宮")
        st.write(f"**五行局:** {wu_ju_name}")


def _day_to_chinese(day: int) -> str:
    """將農曆日數字轉為中文（如 1→一、11→十一）。"""
    units = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    if day <= 10:
        return units[day]
    if day < 20:
        return f"十{units[day - 10]}"
    if day == 20:
        return "二十"
    if day < 30:
        return f"二十{units[day - 20]}"
    return "三十"


def _palace_cell_html(
    palace: ZiweiPalace, is_ming: bool, is_shen: bool
) -> str:
    """產生單一宮位的 HTML 卡片（用於 CSS Grid 命盤方格）。"""
    bg = "#1a1a2e"
    border_style = "border:1px solid #444;"
    if is_ming and is_shen:
        border_style = "border:3px solid #FFD700;"
        bg = "#2d1b00"
    elif is_ming:
        border_style = "border:3px solid #FF6B6B;"
        bg = "#2d0000"
    elif is_shen:
        border_style = "border:3px solid #4ECDC4;"
        bg = "#001a1a"

    label = ""
    if is_ming:
        label += '<span style="color:#FF6B6B;font-weight:bold;font-size:11px">【命】</span>'
    if is_shen:
        label += '<span style="color:#4ECDC4;font-weight:bold;font-size:11px">【身】</span>'

    stars_html = ""
    for star in palace.stars:
        attr = STAR_ATTRIBUTES.get(star, ("", "", "#aaa"))
        color = attr[2]
        alias = attr[1]
        stars_html += (
            f'<div style="color:{color};font-size:13px;font-weight:bold">'
            f'{star}</div>'
            f'<div style="color:#999;font-size:10px">{alias}</div>'
        )
    if not stars_html:
        stars_html = '<div style="color:#666;font-size:11px">─</div>'

    return (
        f'<div style="background:{bg};padding:8px 6px;border-radius:6px;'
        f'min-height:120px;{border_style}">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<span style="color:#c8a96e;font-size:11px">'
        f'{palace.stem_name}{palace.branch_name}</span>'
        f'{label}'
        f'</div>'
        f'<div style="color:#e0e0e0;font-size:12px;font-weight:bold;'
        f'border-bottom:1px solid #555;margin-bottom:4px;padding-bottom:2px">'
        f'{palace.name}</div>'
        f'{stars_html}'
        f'</div>'
    )


def _center_info_html(chart: ZiweiChart) -> str:
    """產生中宮資訊 HTML（顯示在命盤中央 2×2 格）。"""
    wu_ju = WU_XING_JU_NAMES[chart.wu_xing_ju]
    leap = "（閏）" if chart.is_leap_month else ""
    lm = LUNAR_MONTH_NAMES[chart.lunar_month - 1]
    ld = f"初{_day_to_chinese(chart.lunar_day)}"
    ys = HEAVENLY_STEMS[chart.lunar_year_stem]
    yb = EARTHLY_BRANCHES[chart.lunar_year_branch]
    return (
        f'<div style="background:#0d0d1a;border:2px solid #c8a96e;border-radius:10px;'
        f'padding:16px;text-align:center;height:100%;color:#e0d5b0;'
        f'display:flex;flex-direction:column;justify-content:center;">'
        f'<div style="font-size:22px;font-weight:bold;color:#c8a96e;margin-bottom:6px">'
        f'紫微斗數命盤</div>'
        f'<div style="font-size:13px;margin:3px 0">'
        f'{chart.lunar_year}年 {ys}{yb}年</div>'
        f'<div style="font-size:13px;margin:3px 0">'
        f'{lm}{leap} {ld}</div>'
        f'<div style="font-size:12px;margin:3px 0;color:#aaa">'
        f'{HOUR_BRANCH_NAMES[chart.hour_branch]}</div>'
        f'<div style="font-size:14px;margin:6px 0;color:#FFD700;font-weight:bold">'
        f'{wu_ju}</div>'
        f'<div style="font-size:12px;color:#FF6B6B">'
        f'命宮: {EARTHLY_BRANCHES[chart.ming_gong_branch]}宮</div>'
        f'<div style="font-size:12px;color:#4ECDC4">'
        f'身宮: {EARTHLY_BRANCHES[chart.shen_gong_branch]}宮</div>'
        f'</div>'
    )


def _render_palace_grid(chart: ZiweiChart) -> None:
    """
    渲染南式紫微斗數命盤方格（使用 CSS Grid 單一 HTML 元素）。

    佈局（4×4 方格，中央 2×2 為命盤資訊）：
      巳(5)  午(6)  未(7)  申(8)
      辰(4)  [中宮 info]   酉(9)
      卯(3)  [中宮 info]   戌(10)
      寅(2)  丑(1)  子(0)  亥(11)
    """
    st.markdown("#### 🀄 十二宮命盤方格")

    branch_to_palace: dict[int, ZiweiPalace] = {p.branch: p for p in chart.palaces}

    def cell(branch: int) -> str:
        p = branch_to_palace[branch]
        return _palace_cell_html(
            p,
            is_ming=(p.branch == chart.ming_gong_branch),
            is_shen=(p.branch == chart.shen_gong_branch),
        )

    # 4×4 grid 佈局，中央 2×2 合併為命盤資訊
    # Grid positions (row, col): 1-indexed
    grid_layout = [
        # Row 1: 巳5, 午6, 未7, 申8
        (1, 1, 5), (1, 2, 6), (1, 3, 7), (1, 4, 8),
        # Row 2 left + right: 辰4, 酉9
        (2, 1, 4), (2, 4, 9),
        # Row 3 left + right: 卯3, 戌10
        (3, 1, 3), (3, 4, 10),
        # Row 4: 寅2, 丑1, 子0, 亥11
        (4, 1, 2), (4, 2, 1), (4, 3, 0), (4, 4, 11),
    ]

    cells_html = ""
    for row, col, branch in grid_layout:
        cells_html += (
            f'<div style="grid-row:{row};grid-column:{col}">'
            f'{cell(branch)}</div>'
        )

    # 中宮（rows 2-3, cols 2-3）
    center_html = (
        f'<div style="grid-row:2/4;grid-column:2/4">'
        f'{_center_info_html(chart)}</div>'
    )

    full_html = (
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);'
        f'grid-template-rows:repeat(4,auto);gap:4px;'
        f'background:#111;padding:6px;border-radius:10px;'
        f'border:2px solid #c8a96e;">'
        f'{cells_html}'
        f'{center_html}'
        f'</div>'
    )

    st.markdown(full_html, unsafe_allow_html=True)


def _render_star_table(chart: ZiweiChart) -> None:
    """渲染主星位置匯總表格。"""
    st.markdown("#### ⭐ 主星分佈表")

    all_stars = list(ZIWEI_GROUP.keys()) + list(TIANFU_GROUP.keys())
    branch_to_palace: dict[int, ZiweiPalace] = {p.branch: p for p in chart.palaces}

    header = "| 星曜 | 五行 | 別稱 | 所在宮位 | 地支 | 天干地支 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]

    for star in all_stars:
        attr = STAR_ATTRIBUTES[star]
        wuxing, alias, color = attr
        # 找到星曜在哪個宮位
        palace = next(
            (p for p in chart.palaces if star in p.stars), None
        )
        if palace is None:
            continue
        is_ming = "【命】" if palace.branch == chart.ming_gong_branch else ""
        is_shen = "【身】" if palace.branch == chart.shen_gong_branch else ""
        marker = f"{is_ming}{is_shen}"
        name_html = f'<span style="color:{color};font-weight:bold">{star}</span>'
        rows.append(
            f"| {name_html} | {wuxing} | {alias} "
            f"| {palace.name}{marker} "
            f"| {palace.branch_name} "
            f"| {palace.stem_name}{palace.branch_name} |"
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_palace_details(chart: ZiweiChart) -> None:
    """渲染十二宮位詳細說明。"""
    st.markdown("#### 📋 十二宮位詳情")

    _PALACE_DESC = {
        "命宮":  "代表人的個性、才能、命運走向",
        "兄弟宮": "兄弟姐妹、朋友關係",
        "夫妻宮": "婚姻、伴侶、感情",
        "子女宮": "子女、創造、學生",
        "財帛宮": "金錢、財富、財運",
        "疾厄宮": "健康、疾病、意外",
        "遷移宮": "旅行、遷徙、外出緣份",
        "交友宮": "朋友、同事、下屬",
        "官祿宮": "事業、工作、官運",
        "田宅宮": "房產、家庭、祖業",
        "福德宮": "福份、精神、享樂",
        "父母宮": "父母、長輩、文書",
    }

    cols = st.columns(3)
    for i, palace in enumerate(chart.palaces):
        with cols[i % 3]:
            stars_str = "、".join(palace.stars) if palace.stars else "（空宮）"
            markers = []
            if palace.branch == chart.ming_gong_branch:
                markers.append("🔴命")
            if palace.branch == chart.shen_gong_branch:
                markers.append("🔵身")
            marker_str = " ".join(markers)
            desc = _PALACE_DESC.get(palace.name, "")
            st.markdown(
                f"**{palace.stem_name}{palace.branch_name} {palace.name}** {marker_str}\n\n"
                f"⭐ {stars_str}\n\n"
                f"*{desc}*"
            )
