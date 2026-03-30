"""
瑪雅占星排盤模組 (Mayan Astrology Chart Module)

瑪雅占星以瓜地馬拉瑪雅文明的天文與曆法傳統為基礎，包含：
- Long Count（長紀年）：以天數計算的絕對日期
- Tzolkin（神聖曆）：260天循環，20神明名 × 13數字
- Haab（民用曆）：365天，18月×20日 + 5日Wayeb
- Calendar Round：Tzolkin + Haab 的 52 年同步循環
- 九曜行星相位（西方占星技術疊加）

使用 pyswisseph 計算行星位置。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

# GMT  correlation: August 11, 3114 BCE (Gregorian) = Long Count 0.0.0.0.0
# 1 B'ak'tun = 144,000 days
MAYAN_EPOCH_JD = 584283.0  # Julian Day of Mayan epoch

# Tzolkin (Sacred Calendar) - 20 day names
TZOLKIN_NAMES = [
    ("0",   "Imix",      "伊米希 (黑豹)",   "⚫"),
    ("1",   "Ik",        "伊克 (風)",       "🌀"),
    ("2",   "Akbal",     "阿克巴 (夜)",     "🌙"),
    ("3",   "Kan",       "坎 (玉米)",       "🌽"),
    ("4",   "Chicchan",  "契查恩 (龍)",     "🐉"),
    ("5",   "Kimi",      "基米 (死亡)",     "💀"),
    ("6",   "Manik",     "瑪尼克 (鹿)",     "🦌"),
    ("7",   "Lamat",     "拉瑪特 (金星)",   "⭐"),
    ("8",   "Muluk",     "穆魯克 (水)",     "💧"),
    ("9",   "Ok",        "歐克 (狗)",       "🐕"),
    ("10",  "Chuwen",    "丘文 (猴)",       "🐒"),
    ("11",  "Eb",        "埃布 (道路)",     "🛤️"),
    ("12",  "Ben",       "本 (蘆葦)",       "📏"),
    ("13",  "Ix",        "伊克斯 (美洲豹)", "🟡"),
    ("14",  "Men",       "門 (老鷹)",       "🦅"),
    ("15",  "Kib",       "基布 (貓頭鷹)",   "🦉"),
    ("16",  "Kaban",     "卡班 (地震)",     "🌍"),
    ("17",  "Etznab",    "埃茲納布 (刀)",   "🗡️"),
    ("18",  "Kawak",     "卡瓦克 (風暴)",   "⛈️"),
    ("19",  "Ajaw",      "阿哈瓦 (太陽)",   "☀️"),
]

# Haab (Civil Calendar) - 18 months of 20 days + 5 unlucky days
HAAB_MONTHS = [
    ("Pop",    "POP",     "波普 (墊)",       "🟤"),
    ("Wo",     "WO",      "沃 (黑豹)",        "⚫"),
    ("Sip",    "SIP",     "西普 (鹿)",        "🦌"),
    ("Sotz",   "SOTZ",    "索茲 (蝙蝠)",      "🦇"),
    ("Sek",    "SEK",     "塞克 (骨)",        "🦴"),
    ("Xul",    "XUL",     "舒爾 (狗)",        "🐕"),
    ("Yaxkin", "YAXKIN",  "亞克斯金 (新生)",  "🌱"),
    ("Mol",    "MOL",     "莫爾 (水)",        "💧"),
    ("Chen",   "CHEN",    "陳 (黑曜石)",      "⬛"),
    ("Yax",    "YAX",     "亞克斯 (新生)",    "🌿"),
    ("Sak",    "SAK",     "薩克 (白玉米)",    "⚪"),
    ("Keh",    "KEH",     "凱 (紅玉米)",      "🔴"),
    ("Mak",    "MAK",     "瑪克 (覆蓋)",      "🟫"),
    ("Kankin", "KANKIN",  "坎金 (太陽)",      "☀️"),
    ("Muwan",  "MUWAN",   "穆萬 (貓頭鷹)",    "🦉"),
    ("Pax",    "PAX",     "帕克斯 (鼓)",      "🥁"),
    ("Kayab",  "KAYAB",   "卡亞布 (龜)",      "🐢"),
    ("Kumku",  "KUMKU",   "庫姆庫 (玉米)",    "🌽"),
    ("Wayeb",  "WAYEB",   "瓦耶布 (五無日)",  "🔥"),  # 5 unlucky days
]

# Mayan planets (as recognized in classical Mayan astrology)
# Classical Mayan astronomy recognized: Sun, Moon, Venus, Mars, Jupiter, Saturn
MAYAN_PLANETS = {
    "Sun ☉ (太陽)":   swe.SUN,
    "Moon ☽ (月亮)":  swe.MOON,
    "Venus ♀ (金星)": swe.VENUS,
    "Mars ♂ (火星)":   swe.MARS,
    "Jupiter ♃ (木星)": swe.JUPITER,
    "Saturn ♄ (土星)": swe.SATURN,
}

# Tzolkin deities / energies
TZOLKIN_ENERGIES = {
    0:  "創始 / 潛力 / 黑豹",
    1:  "風 / 溝通 / 精神",
    2:  "夜 / 夢境 / 直覺",
    3:  "玉米 / 豐盛 / 生育",
    4:  "龍 / 生命力 / 宇宙",
    5:  "死亡 / 轉化 / 地下",
    6:  "鹿 / 信任 / 優雅",
    7:  "金星 / 和諧 / 幸運",
    8:  "水 / 情緒 / 流動",
    9:  "狗 / 忠誠 / 引導",
    10: "猴 / 創造 / 遊戲",
    11: "道路 / 旅程 / 命運",
    12: "蘆葦 / 建築 / 原則",
    13: "美洲豹 / 神秘 / 力量",
    14: "老鷹 / 視野 / 智慧",
    15: "貓頭鷹 / 魔法 / 醫藥",
    16: "地震 / 催化 / 平衡",
    17: "刀 / 犧牲 / 純粹",
    18: "風暴 / 轉變 / 淨化",
    19: "太陽 / 輝煌 / 復活",
}

# 12 Zodiac signs (tropical) for planetary overlay
ZODIAC_SIGNS = [
    ("Aries",     "♈", "白羊座"),
    ("Taurus",    "♉", "金牛座"),
    ("Gemini",    "♊", "雙子座"),
    ("Cancer",    "♋", "巨蟹座"),
    ("Leo",       "♌", "獅子座"),
    ("Virgo",     "♍", "處女座"),
    ("Libra",     "♎", "天秤座"),
    ("Scorpio",   "♏", "天蠍座"),
    ("Sagittarius","♐","射手座"),
    ("Capricorn", "♑", "摩羯座"),
    ("Aquarius",  "♒", "水瓶座"),
    ("Pisces",    "♓", "雙魚座"),
]

PLANET_COLORS = {
    "Sun ☉ (太陽)":   "#FFD700",
    "Moon ☽ (月亮)":  "#C0C0C0",
    "Venus ♀ (金星)": "#228B22",
    "Mars ♂ (火星)":   "#DC143C",
    "Jupiter ♃ (木星)": "#4169E1",
    "Saturn ♄ (土星)": "#000080",
}

# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class MayanPlanet:
    """行星位置資料（帶瑪雅黃道對應）"""
    name: str
    longitude: float
    latitude: float
    sign: str           # Western zodiac sign
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    retrograde: bool
    maya_day_lord: int   # Tzolkin number that rules this day
    mayan_energy: str    # Tzolkin energy description


@dataclass
class MayanChart:
    """瑪雅占星排盤結果"""
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

    # Long Count
    baktun: int
    katun: int
    tun: int
    winal: int
    kin: int
    long_count_str: str

    # Tzolkin
    tzolkin_number: int    # 1-13
    tzolkin_day_name: str
    tzolkin_name_cn: str
    tzolkin_glyph: str
    tzolkin_energy: str

    # Haab
    haab_day: int          # 0-364
    haab_month: str
    haab_month_cn: str
    haab_month_glyph: str
    haab_date_str: str

    # Calendar Round
    calendar_round: str

    # Lord of the Night (based on Tzolkin)
    lord_of_night: str

    # Planetary positions
    planets: list


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg):
    return deg % 360.0


def _sign_index(deg):
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    return _normalize(deg) % 30.0


def _format_deg(deg):
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _long_count_to_jd(baktun, katun, tun, winal, kin):
    """將 Long Count 轉換為 Julian Day"""
    total_days = (
        baktun * 144000 +
        katun  *   7200 +
        tun    *    360 +
        winal  *     20 +
        kin
    )
    return MAYAN_EPOCH_JD + total_days


def _jd_to_long_count(jd):
    """將 Julian Day 轉換為 Long Count"""
    days_since_epoch = int(jd - MAYAN_EPOCH_JD)
    if days_since_epoch < 0:
        days_since_epoch = 0

    baktun = days_since_epoch // 144000
    remainder = days_since_epoch % 144000
    katun = remainder // 7200
    remainder = remainder % 7200
    tun = remainder // 360
    remainder = remainder % 360
    winal = remainder // 20
    kin = remainder % 20

    return baktun, katun, tun, winal, kin


def _get_tzolkin(jd):
    """計算 Tzolkin 日期（基於 GMT correlation）"""
    days_since_epoch = int(jd - MAYAN_EPOCH_JD)
    tzolkin_number = (days_since_epoch % 13) + 1  # 1-13
    tzolkin_name_idx = days_since_epoch % 20
    tzolkin_info = TZOLKIN_NAMES[tzolkin_name_idx]
    return tzolkin_number, tzolkin_info


def _get_haab(jd):
    """計算 Haab 日期"""
    days_since_epoch = int(jd - MAYAN_EPOCH_JD)
    haab_day = days_since_epoch % 365
    month_idx = haab_day // 20
    day_of_month = haab_day % 20
    month_info = HAAB_MONTHS[month_idx]
    return day_of_month, month_info


def _get_lord_of_night(tzolkin_number, tzolkin_name_idx):
    """計算夜之主宰（Lord of the Night）- 9位神明輪流主宰）"""
    # In classic Mayan astrology, 9 Lords of the Night (the Nine Lords of Xibalba)
    # ruled successive nights in a cycle of 9
    lord_index = (tzolkin_number - 1 + tzolkin_name_idx) % 9
    lords = [
        "G1 - 一號死亡之Lord",
        "G2 - 二號死亡之Lord",
        "G3 - 三號死亡之Lord",
        "G4 - 四號死亡之Lord",
        "G5 - 五號死亡之Lord",
        "G6 - 六號死亡之Lord",
        "G7 - 七號死亡之Lord",
        "G8 - 八號死亡之Lord",
        "G9 - 九號死亡之Lord",
    ]
    return lords[lord_index]


def _find_house(lon, cusps):
    """找出行星所在的宮位"""
    lon = _normalize(lon)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

def compute_maya_chart(year, month, day, hour, minute,
                       timezone, latitude, longitude, location_name=""):
    """計算瑪雅占星排盤"""
    swe.set_ephe_path("")

    # Calculate Julian Day
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # Long Count
    baktun, katun, tun, winal, kin = _jd_to_long_count(jd)
    long_count_str = f"{baktun}.{katun}.{tun}.{winal}.{kin}"

    # Tzolkin
    tzolkin_number, tzolkin_info = _get_tzolkin(jd)
    tzolkin_name_idx = int(jd - MAYAN_EPOCH_JD) % 20

    # Haab
    haab_day_of_month, haab_info = _get_haab(jd)
    haab_date_str = f"{haab_day_of_month} {haab_info[1]}"

    # Calendar Round
    tzolkin_str = f"{tzolkin_number} {tzolkin_info[1]}"
    calendar_round = f"{haab_date_str} / {tzolkin_str}"

    # Lord of the Night
    lord_of_night = _get_lord_of_night(tzolkin_number, tzolkin_name_idx)

    # Houses (for planetary positions)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    ascendant = ascmc[0]

    # Planetary positions
    planets = []
    for name, planet_id in MAYAN_PLANETS.items():
        result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]

        # Tzolkin day lord for this planetary position
        maya_day_for_planet = int(jd - MAYAN_EPOCH_JD + int(lon / 360 * 20)) % 20
        tzolkin_energy = TZOLKIN_ENERGIES.get(maya_day_for_planet, "")

        planets.append(MayanPlanet(
            name=name,
            longitude=lon,
            latitude=lat,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(lon),
            retrograde=speed < 0,
            maya_day_lord=maya_day_for_planet,
            mayan_energy=tzolkin_energy,
        ))

    return MayanChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        baktun=baktun, katun=katun, tun=tun, winal=winal, kin=kin,
        long_count_str=long_count_str,
        tzolkin_number=tzolkin_number,
        tzolkin_day_name=tzolkin_info[1],
        tzolkin_name_cn=tzolkin_info[2],
        tzolkin_glyph=tzolkin_info[3],
        tzolkin_energy=TZOLKIN_ENERGIES.get(tzolkin_name_idx, ""),
        haab_day=haab_day_of_month,
        haab_month=haab_info[1],
        haab_month_cn=haab_info[2],
        haab_month_glyph=haab_info[3],
        haab_date_str=haab_date_str,
        calendar_round=calendar_round,
        lord_of_night=lord_of_night,
        planets=planets,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_maya_chart(chart):
    """渲染完整的瑪雅占星排盤"""
    _render_info(chart)
    st.divider()
    _render_maya_calendar(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_maya_zodiac(chart)


def _render_info(chart):
    st.subheader("📋 排盤資訊 (Chart Information)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**日期:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點:** {chart.location_name}")
        st.write(f"**緯度:** {chart.latitude:.4f}°")
        st.write(f"**經度:** {chart.longitude:.4f}°")
    with col3:
        st.write(f"**儒略日:** {chart.julian_day:.2f}")
        st.write(f"**Long Count:** `{chart.long_count_str}`")
        st.write(f"**Calendar Round:** {chart.calendar_round}")


def _render_maya_calendar(chart):
    st.subheader("🗓️ 瑪雅日曆系統 (Mayan Calendar System)")

    # Long Count display
    st.markdown("#### 📅 長紀年 (Long Count)")
    lc_cols = st.columns(5)
    lc_data = [
        ("B'ak'tun", chart.baktun, "🅱️", "#8B4513"),
        ("Ka'tun",   chart.katun,  "🅺", "#CD853F"),
        ("Tu'n",     chart.tun,    "🅽", "#DAA520"),
        ("Winal",    chart.winal,   "🆆", "#808080"),
        ("K'in",     chart.kin,    "🅚", "#A0522D"),
    ]
    for col, (name, val, glyph, color) in zip(lc_cols, lc_data):
        col.markdown(
            f'<div style="background:{color};padding:12px;border-radius:8px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:24px">{glyph}</div>'
            f'<div style="font-size:28px;font-weight:bold">{val}</div>'
            f'<div style="font-size:11px">{name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f"**Long Count:** `{chart.long_count_str}`")

    # Tzolkin and Haab side by side
    tcol1, tcol2 = st.columns(2)

    # Tzolkin
    with tcol1:
        st.markdown("#### 🌀 Tzolkin（神聖曆）")
        tz_color = "#4B0082"
        st.markdown(
            f'<div style="background:{tz_color};padding:16px;border-radius:10px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:40px">{chart.tzolkin_glyph}</div>'
            f'<div style="font-size:32px;font-weight:bold">'
            f'{chart.tzolkin_number} {chart.tzolkin_day_name}</div>'
            f'<div style="font-size:16px">{chart.tzolkin_name_cn}</div>'
            f'<div style="font-size:14px;margin-top:8px;color:#DDA0DD">'
            f'能量: {chart.tzolkin_energy}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Tzolkin 循環:** 每 260 天（13 數字 × 20 神明名）<br/>"
            f"**今日神明:** {chart.tzolkin_day_name}（{chart.tzolkin_name_cn}）<br/>"
            f"**能量含義:** {chart.tzolkin_energy}",
        )

    # Haab
    with tcol2:
        st.markdown("#### 🏛️ Haab（民用曆）")
        haab_color = "#2F4F4F"
        st.markdown(
            f'<div style="background:{haab_color};padding:16px;border-radius:10px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:40px">{chart.haab_month_glyph}</div>'
            f'<div style="font-size:32px;font-weight:bold">'
            f'{chart.haab_day} {chart.haab_month}</div>'
            f'<div style="font-size:16px">{chart.haab_month_cn}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Haab 循環:** 每年 365 天（18 月 × 20 日 + 5 Wayeb 日）<br/>"
            f"**今日月日:** {chart.haab_date_str}<br/>"
            f"**月份含義:** {chart.haab_month_cn}",
        )

    # Lord of the Night and Calendar Round
    st.markdown("#### 🌙 夜之主宰與輪迴 (Lord of the Night & Calendar Round)")
    lord_col, cr_col = st.columns(2)
    with lord_col:
        st.info(f"**夜之主宰 (Lord of the Night):** {chart.lord_of_night}")
        st.caption("源自基切瑪雅神話中的九位冥界之王（Xibalba），輪流主宰每夜")
    with cr_col:
        st.info(f"**Calendar Round:** {chart.calendar_round}")
        st.caption("Tzolkin × Haab 同步循環，約 52 年（18980 天）完成一輪")


def _render_planet_table(chart):
    st.subheader("🪐 行星位置（西方占星疊加）")
    header = (
        "| 行星 | 星座 | 度數 | 逆行 | Tzolkin日神 | 瑪雅能量 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        tzolkin_day = TZOLKIN_NAMES[p.maya_day_lord]
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° "
            f"| {retro} "
            f"| {tzolkin_day[1]}（{tzolkin_day[2]}） "
            f"| {p.mayan_energy} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_maya_zodiac(chart):
    """渲染瑪雅黃道（結合 Tzolkin 神明與西方星座）"""
    st.subheader("🌀 瑪雅-黃道疊加圖（Maya-Zodiac Overlay）")

    # Tzolkin 20-day cycle grid
    tzolkin_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:20px;">'
    day_index = int(chart.julian_day - MAYAN_EPOCH_JD) % 20
    for i in range(20):
        info = TZOLKIN_NAMES[i]
        is_today = "border:3px solid #FFD700;" if i == day_index else ""
        bg_color = "#1a0d2e" if i != day_index else "#3d1a5c"
        tzolkin_html += (
            f'<div style="background:{bg_color};padding:8px;border-radius:6px;'
            f'text-align:center;color:white;{is_today}">'
            f'<div style="font-size:20px">{info[3]}</div>'
            f'<div style="font-size:12px;font-weight:bold">{info[1]}</div>'
            f'<div style="font-size:10px;color:#DDA0DD">{info[2]}</div>'
            f'</div>'
        )
    tzolkin_html += '</div>'
    st.markdown("**Tzolkin 二十日神循環（今日高亮）:**")
    st.markdown(tzolkin_html, unsafe_allow_html=True)

    # Haab months grid
    st.markdown("**Haab 十八月循環:**")
    haab_html = '<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:4px;">'
    haab_day_of_year = chart.haab_day + TZOLKIN_NAMES.index(
        next(d for d in TZOLKIN_NAMES if d[1] == chart.tzolkin_day_name)
    ) * 13 % 20  # approximate haab day of year
    haab_idx = haab_day_of_year // 20 % 19
    for i, m in enumerate(HAAB_MONTHS):
        is_today = "border:3px solid #FFD700;" if i == haab_idx else ""
        bg = "#2F4F4F" if i != 18 else "#8B0000"  # Wayeb is unlucky
        haab_html += (
            f'<div style="background:{bg};padding:6px;border-radius:4px;'
            f'text-align:center;color:white;{is_today}">'
            f'<div style="font-size:16px">{m[3]}</div>'
            f'<div style="font-size:10px">{m[1]}</div>'
            f'<div style="font-size:9px;color:#aaa">{m[2]}</div>'
            f'</div>'
        )
    haab_html += '</div>'
    st.markdown(haab_html, unsafe_allow_html=True)
    st.caption("⚠️ Wayeb（瓦耶布）是五無日，被視為不吉利之日")
