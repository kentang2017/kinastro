"""
泰國占星排盤模組 (Thai Astrology Chart Module)

泰國占星以印度占星 (Jyotish) 為基礎，使用恆星黃道 (sidereal zodiac)，
加入泰國傳統命名與詮釋體系。本模組使用 pyswisseph 搭配 Lahiri 歲差計算行星位置。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

THAI_PLANETS = {
    "พระอาทิตย์ (太陽)": swe.SUN,
    "พระจันทร์ (月亮)": swe.MOON,
    "พระอังคาร (火星)": swe.MARS,
    "พระพุธ (水星)": swe.MERCURY,
    "พระพฤหัสบดี (木星)": swe.JUPITER,
    "พระศุกร์ (金星)": swe.VENUS,
    "พระเสาร์ (土星)": swe.SATURN,
}

# Thai names for the 12 Rashis
THAI_RASHIS = [
    ("เมษ (Mesha)", "♈", "白羊", "พระอังคาร"),
    ("พฤษภ (Vrishabha)", "♉", "金牛", "พระศุกร์"),
    ("เมถุน (Mithuna)", "♊", "雙子", "พระพุธ"),
    ("กรกฎ (Karka)", "♋", "巨蟹", "พระจันทร์"),
    ("สิงห์ (Simha)", "♌", "獅子", "พระอาทิตย์"),
    ("กันย์ (Kanya)", "♍", "處女", "พระพุธ"),
    ("ตุลย์ (Tula)", "♎", "天秤", "พระศุกร์"),
    ("พิจิก (Vrischika)", "♏", "天蠍", "พระอังคาร"),
    ("ธนู (Dhanu)", "♐", "射手", "พระพฤหัสบดี"),
    ("มกร (Makara)", "♑", "摩羯", "พระเสาร์"),
    ("กุมภ์ (Kumbha)", "♒", "水瓶", "พระเสาร์"),
    ("มีน (Meena)", "♓", "雙魚", "พระพฤหัสบดี"),
]

# Thai day-planet correspondences for interpretive context
THAI_DAY_PLANETS = {
    0: ("วันอาทิตย์ (Sunday)", "พระอาทิตย์"),
    1: ("วันจันทร์ (Monday)", "พระจันทร์"),
    2: ("วันอังคาร (Tuesday)", "พระอังคาร"),
    3: ("วันพุธ (Wednesday)", "พระพุธ"),
    4: ("วันพฤหัสบดี (Thursday)", "พระพฤหัสบดี"),
    5: ("วันศุกร์ (Friday)", "พระศุกร์"),
    6: ("วันเสาร์ (Saturday)", "พระเสาร์"),
}

PLANET_COLORS = {
    "พระอาทิตย์ (太陽)": "#FF8C00",
    "พระจันทร์ (月亮)": "#C0C0C0",
    "พระอังคาร (火星)": "#DC143C",
    "พระพุธ (水星)": "#4169E1",
    "พระพฤหัสบดี (木星)": "#FFD700",
    "พระศุกร์ (金星)": "#FF69B4",
    "พระเสาร์ (土星)": "#8B4513",
    "ราหู (羅睺)": "#800080",
    "เกตุ (計都)": "#4B0082",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ThaiPlanet:
    """Thai planet position"""
    name: str
    longitude: float
    latitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    rashi_lord: str
    sign_degree: float
    retrograde: bool
    house: int = 0


@dataclass
class ThaiHouse:
    """Thai bhava (house)"""
    number: int
    cusp: float
    rashi: str
    rashi_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class ThaiChart:
    """Thai astrology chart"""
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
    ayanamsa: float
    day_of_week: int
    day_planet: str
    planets: list
    houses: list
    ascendant: float
    asc_rashi: str


# ============================================================
# 計算函數 (Calculation Functions)
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


def _find_house(lon, cusps):
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


def compute_thai_chart(year, month, day, hour, minute, timezone,
                       latitude, longitude, location_name=""):
    """計算泰國占星排盤 (Sidereal / Lahiri Ayanamsa)"""
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Day of week: 0=Mon … 6=Sun in Python, but we need 0=Sun … 6=Sat
    import datetime as _dt
    dt = _dt.date(year, month, day)
    # isoweekday: 1=Mon … 7=Sun → convert to 0=Sun,1=Mon,...,6=Sat
    dow = dt.isoweekday() % 7
    day_name, day_planet = THAI_DAY_PLANETS[dow]

    # Compute sidereal house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P",
                                 swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    planets = []
    for name, pid in THAI_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        rashi = THAI_RASHIS[idx]

        planets.append(ThaiPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], sign_degree=_sign_degree(lon),
            retrograde=speed < 0,
        ))

    # Rahu (ราหู)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = THAI_RASHIS[idx]
    planets.append(ThaiPlanet(
        name="ราหู (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(rahu_lon),
        retrograde=False,
    ))

    # Ketu (เกตุ)
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = THAI_RASHIS[idx]
    planets.append(ThaiPlanet(
        name="เกตุ (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(ketu_lon),
        retrograde=False,
    ))

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        rashi = THAI_RASHIS[idx]
        houses.append(ThaiHouse(
            number=i + 1, cusp=cusp,
            rashi=rashi[0], rashi_glyph=rashi[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_rashi = THAI_RASHIS[_sign_index(ascendant)][0]

    return ThaiChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        day_of_week=dow, day_planet=day_planet,
        planets=planets, houses=houses,
        ascendant=ascendant, asc_rashi=asc_rashi,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_thai_chart(chart):
    """渲染完整的泰國占星排盤"""
    _render_info(chart)
    st.divider()
    _render_thai_grid(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)


def _render_info(chart):
    st.subheader("📋 ข้อมูลดวง (排盤資訊)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**วันที่ (日期):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**เวลา (時間):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**เขตเวลา (時區):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**สถานที่ (地點):** {chart.location_name}")
        day_name = THAI_DAY_PLANETS[chart.day_of_week][0]
        st.write(f"**{day_name}**")
        st.write(f"**ดาวประจำวัน (日主星):** {chart.day_planet}")
        st.write(f"**ลัคนา (命宮):** {chart.asc_rashi} "
                 f"{_format_deg(chart.ascendant)}")
        st.write(f"**Ayanamsa (歲差):** {chart.ayanamsa:.4f}°")


def _render_thai_grid(chart):
    """渲染泰國式方盤"""
    st.subheader("📊 ผังดวงชาตา (泰國排盤)")

    # Thai chart uses similar layout to South Indian
    grid = [
        [3, 2, 1, 0],
        [4, -1, -1, 11],
        [5, -1, -1, 10],
        [6, 7, 8, 9],
    ]

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        # Use short Thai name (first word)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name))

    asc_idx = _sign_index(chart.ascendant)

    cell_style = (
        "border:1px solid #444; padding:6px; text-align:center; "
        "vertical-align:top; min-width:120px; font-size:13px;"
    )
    asc_cell_style = cell_style + " background:#3d3010;"
    center_style = (
        "border:1px solid #444; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a2a; "
        "color:#e0e0e0;"
    )

    html = '<table style="border-collapse:collapse; margin:auto; width:100%;">'
    for row_idx, row in enumerate(grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    center_content = (
                        f"<b>ดวงชาตา 泰國占星</b><br/>"
                        f"{chart.year}/{chart.month}/{chart.day}<br/>"
                        f"{chart.hour:02d}:{chart.minute:02d} "
                        f"UTC{chart.timezone:+.1f}<br/>"
                        f"{chart.location_name}<br/>"
                        f"Ayanamsa: {chart.ayanamsa:.2f}°"
                    )
                    html += (
                        f'<td colspan="2" rowspan="2" '
                        f'style="{center_style}">{center_content}</td>'
                    )
                    col_idx += 2
                    continue
                else:
                    col_idx += 1
                    continue
            else:
                rashi = THAI_RASHIS[idx]
                style = asc_cell_style if idx == asc_idx else cell_style
                p_list = rashi_planets[idx]
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(full, "#e0e0e0")};'
                    f'font-weight:bold">{short}</span>'
                    for short, full in p_list
                ) if p_list else '<span style="color:#666">—</span>'
                marker = " 🔺" if idx == asc_idx else ""
                cell_content = (
                    f"<b>{rashi[0]}{marker}</b><br/>"
                    f'<small style="color:#888">{rashi[1]} {rashi[2]}</small>'
                    f"<br/>{p_html}"
                )
                html += f'<td style="{style}">{cell_content}</td>'
            col_idx += 1
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


def _render_planet_table(chart):
    st.subheader("🪐 ตำแหน่งดาว (行星位置)")
    header = "| ดาว (Planet) | ราศี (Rashi) | องศา (Degree) | เจ้าเรือน (Lord) | ภพ (House) | ℞ |"
    sep = "|:------------:|:------------:|:-------------:|:----------------:|:----------:|:-:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        rows.append(
            f"| {name_html} | {p.rashi_glyph} {p.rashi} ({p.rashi_chinese}) "
            f"| {p.sign_degree:.2f}° | {p.rashi_lord} "
            f"| {p.house} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ ภพ (宮位)")
    header = "| ภพ (Bhava) | จุดเริ่ม (Cusp) | ราศี (Rashi) | ดาวในภพ (Planets) |"
    sep = "|:----------:|:--------------:|:------------:|:-----------------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.rashi_glyph} {h.rashi} | {planets_str} |"
        )
    st.markdown("\n".join(rows))


# ============================================================
# Thai Numerology 9-Box Grid (ตาราง 9 ช่อง)
# ============================================================

# Navagraha number → planet correspondence (Thai Numerology)
THAI_NUMEROLOGY_PLANETS = {
    1: ("พระอาทิตย์ (太陽)", "☀️", "#FF8C00"),
    2: ("พระจันทร์ (月亮)", "🌙", "#C0C0C0"),
    3: ("พระอังคาร (火星)", "🔴", "#DC143C"),
    4: ("พระพุธ (水星)", "💚", "#4169E1"),
    5: ("พระพฤหัสบดี (木星)", "💛", "#FFD700"),
    6: ("พระศุกร์ (金星)", "💗", "#FF69B4"),
    7: ("พระเสาร์ (土星)", "🟤", "#8B4513"),
    8: ("ราหู (羅睺)", "🟣", "#800080"),
    9: ("เกตุ (計都)", "🔵", "#4B0082"),
}

# Grid layout: 3 rows × 3 cols, each cell holds the number shown
# [1, 4, 7]
# [2, 5, 8]
# [3, 6, 9]
_NINE_GRID_LAYOUT = [
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
]

# Line definitions: name → list of numbers in that line
_NINE_GRID_LINES = {
    "147": [1, 4, 7],
    "258": [2, 5, 8],
    "369": [3, 6, 9],
    "123": [1, 2, 3],
    "456": [4, 5, 6],
    "789": [7, 8, 9],
    "159": [1, 5, 9],
    "357": [3, 5, 7],
}

# Line meaning descriptions (Thai + Chinese)
_LINE_MEANINGS = {
    "147": {
        "name_th": "เส้นพลังงาน (行動力線)",
        "name_zh": "行動力線",
        "desc": "意志力強、物質成就、行動果斷。此線完整代表您具備堅定的意志和實現目標的能力。",
        "desc_th": "ความแข็งแกร่งของความตั้งใจ ความสำเร็จทางวัตถุ ความเด็ดขาด",
        "remedy": "配戴橙色或棕色寶石，增強太陽與土星的力量。",
    },
    "258": {
        "name_th": "เส้นความสมดุลทางอารมณ์ (情感平衡線)",
        "name_zh": "情感平衡線",
        "desc": "情感豐富、同理心強、人際關係和諧。此線完整代表您在情感上非常均衡。",
        "desc_th": "อารมณ์อ่อนไหว ความเห็นอกเห็นใจ ความสัมพันธ์ที่ดี",
        "remedy": "配戴白色或銀色寶石，加強月亮能量；以薰衣草精油平衡情緒。",
    },
    "369": {
        "name_th": "เส้นสติปัญญา (思維線)",
        "name_zh": "思維線",
        "desc": "思維敏捷、創意十足、學習能力強。此線完整代表您擁有卓越的智力與創造力。",
        "desc_th": "ความฉลาด ความคิดสร้างสรรค์ ทักษะการเรียนรู้",
        "remedy": "配戴紅色或珊瑚色寶石，增強火星與計都的創意能量。",
    },
    "123": {
        "name_th": "เส้นเป้าหมาย (目標線)",
        "name_zh": "目標線",
        "desc": "目標明確、行動力強、勇於突破。此線完整代表您具備強烈的成就動機。",
        "desc_th": "เป้าหมายชัดเจน พลังงานสูง กล้าที่จะก้าวข้ามขีดจำกัด",
        "remedy": "選擇以1、2、3結尾的車牌，或在名字中加入對應數字的筆畫。",
    },
    "456": {
        "name_th": "เส้นการทำงานและความสามัคคี (工作和諧線)",
        "name_zh": "工作和諧線",
        "desc": "勤奮努力、工作穩定、人際和諧。此線完整代表您在職場中表現出色。",
        "desc_th": "ความขยันหมั่นเพียร ความมั่นคง ความสามัคคี",
        "remedy": "配戴藍色或深藍色寶石，增強水星與金星的職場能量。",
    },
    "789": {
        "name_th": "เส้นวิญญาณ (靈性線)",
        "name_zh": "靈性線",
        "desc": "靈性覺知高、智慧深厚、直覺敏銳。此線完整代表您具備深刻的靈性洞察力。",
        "desc_th": "จิตวิญญาณที่สูง ปัญญา สัญชาตญาณที่เฉียบแหลม",
        "remedy": "冥想與靜心修行，配戴紫色或靛藍色水晶，強化土星、羅睺、計都能量。",
    },
    "159": {
        "name_th": "เส้นผู้นำ (領導力線)",
        "name_zh": "領導力線",
        "desc": "天生領袖氣質、決策能力強、有遠見。此線完整代表您具備天賦的領導才能。",
        "desc_th": "ความเป็นผู้นำโดยธรรมชาติ ความสามารถในการตัดสินใจ วิสัยทัศน์",
        "remedy": "選擇以5結尾的手機號碼，配戴黃色寶石（黃玉或黃水晶）。",
    },
    "357": {
        "name_th": "เส้นสมาธิ (專注力線)",
        "name_zh": "專注力線",
        "desc": "專注力強、毅力持久、不輕易放棄。此線完整代表您具備超強的耐力與執行力。",
        "desc_th": "สมาธิสูง ความอดทน ไม่ยอมแพ้ง่าย",
        "remedy": "冥想訓練，配戴紅色或橙色寶石，增強火星與土星的持久力。",
    },
}

# Missing number remedies
_MISSING_NUMBER_REMEDIES = {
    1: "缺少太陽能量：可選擇以1結尾的車牌或電話號碼，多穿橙色衣物，配戴紅寶石或石榴石。",
    2: "缺少月亮能量：多親近水域，配戴珍珠或月光石，以白色或銀色為幸運色。",
    3: "缺少火星能量：多運動，配戴珊瑚或紅色寶石，增強行動力與決斷力。",
    4: "缺少水星能量：多閱讀與溝通，配戴祖母綠或綠色寶石，增強學習與表達能力。",
    5: "缺少木星能量：多行善積德，配戴黃色蛋白石或黃玉，增強幸運與擴展能量。",
    6: "缺少金星能量：注重美感與人際關係，配戴鑽石或白水晶，增強魅力與財運。",
    7: "缺少土星能量：培養耐心與紀律，配戴藍寶石或紫水晶，增強持久力與責任感。",
    8: "缺少羅睺能量：注意業力課題，配戴赫松石或灰色寶石，轉化羅睺帶來的考驗。",
    9: "缺少計都能量：深化靈性修行，配戴貓眼石或深色寶石，融化過去世業障。",
}


def _digit_reduce(n):
    """Reduce integer to single digit 1–9 (no master numbers in Thai system).

    Args:
        n (int): non-negative integer to reduce.

    Returns:
        int: value in range 1–9.  Returns 9 for multiples of 9, and 1 for 0.
    """
    if n <= 0:
        return 1
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def calculate_thai_nine_grid(day, month, year):
    """計算泰國 Numerology 9宮格數據 (Thai Numerology 9-Box Grid)

    Args:
        day (int): 出生日 (1–31)
        month (int): 出生月 (1–12)
        year (int): 出生年 (e.g. 1990)

    Returns:
        dict with keys:
            - counts (dict[int, int]): digit 1–9 occurrence counts
            - birth_number (int): 出生日數字（Birth Number, 1–9）
            - life_path (int): 生命靈數（Life Path Number, 1–9）
            - complete_lines (list[str]): list of complete line keys, e.g. ["147", "159"]
            - strongest (list[int]): digit(s) with highest count (>0)
            - missing (list[int]): digits with count 0
            - day, month, year (int): original inputs
    """
    # Collect all digits from DD/MM/YYYY, ignoring zeros
    date_str = f"{day:02d}{month:02d}{year:04d}"
    raw_digits = [int(c) for c in date_str if c != "0"]

    # Count raw occurrences of digits 1–9
    counts = {i: 0 for i in range(1, 10)}
    for d in raw_digits:
        if 1 <= d <= 9:
            counts[d] += 1

    # Birth Number: reduce birth day to single digit 1–9
    birth_number = _digit_reduce(day if day > 0 else 1)

    # Life Path Number: sum all non-zero digits then reduce
    total = sum(raw_digits)
    life_path = _digit_reduce(total) if total > 0 else 1

    # Add derived numbers to the grid counts
    counts[birth_number] += 1
    counts[life_path] += 1

    # If birth_number == life_path, it was counted twice — that is intentional
    # (both are independent derived numbers)

    # Detect complete lines (all 3 numbers in the line have count > 0)
    complete_lines = [
        line_name
        for line_name, nums in _NINE_GRID_LINES.items()
        if all(counts[n] > 0 for n in nums)
    ]

    # Strongest number(s)
    max_count = max(counts.values())
    strongest = [n for n, c in counts.items() if c == max_count and c > 0]

    # Missing numbers
    missing = [n for n, c in counts.items() if c == 0]

    return {
        "counts": counts,
        "birth_number": birth_number,
        "life_path": life_path,
        "complete_lines": complete_lines,
        "strongest": strongest,
        "missing": missing,
        "day": day,
        "month": month,
        "year": year,
    }


def render_nine_grid(result):
    """渲染泰國 Numerology 9宮格圖譜 (Thai Numerology 9-Box Grid UI)

    Args:
        result (dict): output from calculate_thai_nine_grid()
    """
    counts = result["counts"]
    complete_lines = result["complete_lines"]
    strongest = result["strongest"]
    missing = result["missing"]
    birth_number = result["birth_number"]
    life_path = result["life_path"]

    st.subheader("🔢 ตาราง 9 ช่อง — Thai Numerology 9宮格圖譜")

    # ── Summary row ──────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"**เลขวันเกิด (Birth Number / 出生日數):** "
            f"**{birth_number}** &nbsp; "
            f"{THAI_NUMEROLOGY_PLANETS[birth_number][1]} "
            f"{THAI_NUMEROLOGY_PLANETS[birth_number][0]}"
        )
    with col_b:
        st.markdown(
            f"**เลขชีวิต (Life Path / 生命靈數):** "
            f"**{life_path}** &nbsp; "
            f"{THAI_NUMEROLOGY_PLANETS[life_path][1]} "
            f"{THAI_NUMEROLOGY_PLANETS[life_path][0]}"
        )

    st.markdown("")

    # ── 3×3 grid ─────────────────────────────────────────────
    # Determine which cells are part of a complete line for highlighting
    highlighted = set()
    for line_name in complete_lines:
        for n in _NINE_GRID_LINES[line_name]:
            highlighted.add(n)

    cell_base = (
        "display:flex; flex-direction:column; align-items:center; "
        "justify-content:center; border:2px solid #555; border-radius:8px; "
        "padding:10px 6px; min-width:90px; min-height:90px; "
        "font-size:15px; text-align:center;"
    )

    grid_html = (
        '<div style="display:grid; grid-template-columns:repeat(3,1fr); '
        'gap:8px; max-width:360px; margin:0 auto 16px auto;">'
    )

    for row in _NINE_GRID_LAYOUT:
        for num in row:
            cnt = counts[num]
            planet_name, planet_emoji, planet_color = THAI_NUMEROLOGY_PLANETS[num]
            is_highlighted = num in highlighted
            is_missing = cnt == 0

            if is_missing:
                bg = "#1a1a2e"
                text_color = "#555"
                border_color = "#333"
                count_str = "—"
            elif is_highlighted:
                bg = "#1e3a1e"
                text_color = planet_color
                border_color = planet_color
                count_str = f"×{cnt}"
            else:
                bg = "#1a1a1a"
                text_color = planet_color
                border_color = "#555"
                count_str = f"×{cnt}"

            cell_style = (
                f"{cell_base} background:{bg}; "
                f"border-color:{border_color}; color:{text_color};"
            )

            num_display = (
                f'<span style="font-size:22px; font-weight:bold;">{num}</span>'
            )
            count_display = (
                f'<span style="font-size:13px; color:{text_color};">'
                f"{count_str}</span>"
            )
            emoji_display = (
                f'<span style="font-size:16px;">{planet_emoji}</span>'
            )

            grid_html += (
                f'<div style="{cell_style}">'
                f"{num_display}{count_display}{emoji_display}"
                f"</div>"
            )

    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    # ── Planet legend ─────────────────────────────────────────
    with st.expander("🪐 行星數字對應 (Navagraha Correspondence)", expanded=False):
        legend_cols = st.columns(3)
        for i, (num, (pname, pemoji, pcolor)) in enumerate(
            THAI_NUMEROLOGY_PLANETS.items()
        ):
            with legend_cols[i % 3]:
                st.markdown(
                    f'<span style="color:{pcolor}; font-weight:bold;">'
                    f"{pemoji} {num} = {pname}</span>",
                    unsafe_allow_html=True,
                )

    # ── Complete lines ────────────────────────────────────────
    st.markdown("### 🌟 完整線條 (เส้นที่สมบูรณ์ — Complete Lines)")
    if complete_lines:
        for line_name in complete_lines:
            meaning = _LINE_MEANINGS[line_name]
            nums = _NINE_GRID_LINES[line_name]
            emojis = "→".join(
                f"{THAI_NUMEROLOGY_PLANETS[n][1]}{n}" for n in nums
            )
            st.markdown(
                f"**{emojis} &nbsp; {line_name} {meaning['name_th']}**  \n"
                f"{meaning['desc']}  \n"
                f"*{meaning['desc_th']}*  \n"
                f"💊 後天化解：{meaning['remedy']}"
            )
            st.markdown("---")
    else:
        st.info("目前沒有完整的長線。透過補數字（改名、選車牌號碼、佩戴對應護符）可逐步形成能量線條。")

    # ── Strongest numbers ─────────────────────────────────────
    st.markdown("### 💪 最強數字 (ตัวเลขที่แข็งแกร่งที่สุด — Strongest Numbers)")
    if strongest:
        max_cnt = counts[strongest[0]]
        for n in strongest:
            pname, pemoji, pcolor = THAI_NUMEROLOGY_PLANETS[n]
            st.markdown(
                f'<span style="color:{pcolor}; font-size:16px; font-weight:bold;">'
                f"{pemoji} {n} — {pname}</span>  \n"
                f"出現 **{max_cnt}** 次。您的主要能量中心。",
                unsafe_allow_html=True,
            )
    else:
        st.info("數字分布均勻，無特別突出的主導數字。")

    # ── Missing numbers ───────────────────────────────────────
    st.markdown("### 🎯 缺失數字 (ตัวเลขที่ขาดหาย — Missing Numbers / 人生課題)")
    if missing:
        for n in missing:
            pname, pemoji, pcolor = THAI_NUMEROLOGY_PLANETS[n]
            remedy = _MISSING_NUMBER_REMEDIES[n]
            st.markdown(
                f'<span style="color:{pcolor}; font-size:16px; font-weight:bold;">'
                f"{pemoji} {n} — {pname}</span>  \n"
                f"此生課題：{remedy}",
                unsafe_allow_html=True,
            )
    else:
        st.success("🎉 您的生日包含所有數字 1–9，能量非常完整！")

    # ── Personality summary ───────────────────────────────────
    _render_numerology_summary(result)

    # ── Future expansion placeholder ──────────────────────────
    # TODO: 姓名 Numerology (Name Numerology)
    # 未來可加入以泰文/中文姓名字母對應數字的計算，
    # 進一步補強缺失數字，或強化現有優勢數字。


def _render_numerology_summary(result):
    """渲染數字學性格總結 (Personality summary based on Life Path and Birth Number)"""
    birth_number = result["birth_number"]
    life_path = result["life_path"]

    # Template personality summaries (to be refined in future)
    _personality = {
        1: "您是天生的先驅者與領導者，獨立自主、意志堅定。您喜歡開創新局，不畏挑戰。",
        2: "您具備敏感細膩的情感與強大的同理心，擅長協調與合作，是優秀的和平使者。",
        3: "您充滿創意與活力，表達能力強，天生樂觀，能為周圍帶來歡樂與靈感。",
        4: "您腳踏實地、勤奮努力，注重細節與秩序，是建設與穩定的力量。",
        5: "您愛好自由、適應力強，充滿好奇心，擅長交際，渴望多樣化的生命體驗。",
        6: "您富有責任感與愛心，重視家庭與和諧，是照顧者與守護者的典型。",
        7: "您深思熟慮、富有哲思，喜歡獨處與研究，具有深刻的靈性與分析能力。",
        8: "您具備強大的執行力與野心，擅長掌控資源，追求物質與精神的雙重成就。",
        9: "您慈悲博愛、視野寬廣，有強烈的使命感，渴望為世界帶來正面改變。",
    }

    st.markdown("### 🌸 性格總結 (สรุปบุคลิกภาพ — Personality Summary)")
    pname_bn, pemoji_bn, pcolor_bn = THAI_NUMEROLOGY_PLANETS[birth_number]
    pname_lp, pemoji_lp, pcolor_lp = THAI_NUMEROLOGY_PLANETS[life_path]

    st.markdown(
        f"**{pemoji_bn} 出生日數 {birth_number} — {pname_bn}**  \n"
        f"{_personality[birth_number]}"
    )
    if life_path != birth_number:
        st.markdown(
            f"**{pemoji_lp} 生命靈數 {life_path} — {pname_lp}**  \n"
            f"{_personality[life_path]}"
        )
