"""
緬甸 Mahabote 排盤模組 (Myanmar Mahabote Astrology Chart Module)

Mahabote (မဟာဘုတ်) 是緬甸傳統占星術，意為「大創造」或「大決定」，以出生星期為核心：

- **七曜行星**：日（Sun）、月（Moon）、火（Mars）、水（Mercury）、
  木（Jupiter）、金（Venus）、土（Saturn），分別對應星期日至星期六
- **羅睺 (Rahu)**：星期三傍晚（18:00後）出生者歸羅睺管轄
- **八方位**：每個行星/羅睺對應一個羅盤方位
- **七宮位**：Bhin（本命）、Ayu（壽命）、Winya（意識）、
  Kiya（身體）、Hein（權勢）、Marana（死亡）、Thila（道德）
- **行星大運 (Atar)**：每顆行星主宰一定年數，七星循環共 96 年

計算公式：Mahabote 值 = (緬甸年 + 星期數) mod 7
"""

import streamlit as st
from dataclasses import dataclass
from datetime import date


# ============================================================
# 常量 (Constants)
# ============================================================

# Weekday planets: (English, Myanmar, Chinese, symbol, element, direction)
WEEKDAY_PLANETS = [
    ("Sun",     "တနင်္ဂနွေ", "太陽", "☉", "火 Fire",  "NE 東北"),   # Sunday=0
    ("Moon",    "တနင်္လာ",   "月亮", "☽", "水 Water", "E 東"),      # Monday=1
    ("Mars",    "အင်္ဂါ",    "火星", "♂", "火 Fire",  "SE 東南"),   # Tuesday=2
    ("Mercury", "ဗုဒ္ဓဟူး",  "水星", "☿", "土 Earth", "S 南"),      # Wednesday=3
    ("Jupiter", "ကြာသပတေး",  "木星", "♃", "風 Air",   "W 西"),      # Thursday=4
    ("Venus",   "သောကြာ",    "金星", "♀", "水 Water", "NW 西北"),   # Friday=5
    ("Saturn",  "စနေ",       "土星", "♄", "火 Fire",  "N 北"),      # Saturday=6
]

# Rahu (pseudo-planet for Wednesday evening, after 18:00)
RAHU_INFO = ("Rahu", "ရာဟု", "羅睺", "☊", "—", "SW 西南")

# Weekday animal signs: (English, Myanmar, Chinese, emoji)
WEEKDAY_ANIMALS = [
    ("Garuda",          "ဂဠုန်",    "迦樓羅",   "🦅"),  # Sunday=0
    ("Tiger",           "ကျား",     "虎",       "🐅"),  # Monday=1
    ("Lion",            "ခြင်္သေ့",  "獅",       "🦁"),  # Tuesday=2
    ("Tusked Elephant", "ဆင်စွယ်",  "象(有牙)",  "🐘"),  # Wednesday=3
    ("Rat",             "ကြွက်",    "鼠",       "🐀"),  # Thursday=4
    ("Guinea Pig",      "ပူးရွှေ",   "天竺鼠",   "🐹"),  # Friday=5
    ("Naga",            "နဂါး",     "龍/那伽",   "🐉"),  # Saturday=6
]

# Rahu animal sign (Wednesday evening)
RAHU_ANIMAL = ("Tuskless Elephant", "ဆင်", "象(無牙)", "🐘")

# Mahabote 7 Houses
# (English, Myanmar, Chinese, meaning, description)
MAHABOTE_HOUSES = [
    ("Bhin",   "ဘင်",     "本命宮", "State of Being",
     "出生狀態，代表此生的起點與本質。此宮主性格基調、天賦潛力。"),
    ("Ayu",    "အာယု",    "壽命宮", "Longevity",
     "壽命與健康。此宮主體能、壽限、生命活力。"),
    ("Winya",  "ဝိညာဉ်",  "意識宮", "Consciousness",
     "精神與意識。此宮主智力、學習能力、精神狀態。"),
    ("Kiya",   "ကိယာ",    "身體宮", "Physical Body",
     "肉體與物質。此宮主身體健康、外貌特徵、物質享受。"),
    ("Hein",   "ဟိန်း",    "權勢宮", "Power / Prosperity",
     "力量與繁榮。此宮主事業成就、社會地位、財富。"),
    ("Marana", "မရဏ",     "死亡宮", "Death / Decline",
     "衰退與終結。此宮主危機、挑戰、人生低谷。"),
    ("Thila",  "သီလ",     "道德宮", "Virtue / Morality",
     "品德與修為。此宮主道德標準、宗教修行、行善積德。"),
]

# Weekday names
WEEKDAY_NAMES_EN = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]
WEEKDAY_NAMES_CN = [
    "星期日", "星期一", "星期二", "星期三",
    "星期四", "星期五", "星期六",
]

# Planet period durations (Atar / Dasa) — total 96 years
PLANET_PERIOD_YEARS = {
    "Sun": 6,
    "Moon": 15,
    "Mars": 8,
    "Mercury": 17,
    "Jupiter": 19,
    "Venus": 21,
    "Saturn": 10,
}

# Colours for rendering
PLANET_COLORS = {
    "Sun":     "#FFD700",
    "Moon":    "#C0C0C0",
    "Mars":    "#DC143C",
    "Mercury": "#228B22",
    "Jupiter": "#4169E1",
    "Venus":   "#FF69B4",
    "Saturn":  "#000080",
    "Rahu":    "#556B2F",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class MahaboteHouse:
    """Single house in the Mahabote chart."""
    index: int
    name_en: str
    name_myanmar: str
    name_cn: str
    meaning: str
    description: str
    planet: str            # Planet English name
    planet_cn: str         # Planet Chinese name
    planet_symbol: str
    is_birth_house: bool   # Whether this is the birth planet's house
    weekday_en: str        # Weekday English name (e.g. "Sunday")
    weekday_cn: str        # Weekday Chinese name (e.g. "星期日")
    animal_en: str         # Animal sign English name
    animal_myanmar: str    # Animal sign Myanmar name
    animal_cn: str         # Animal sign Chinese name
    animal_emoji: str      # Animal sign emoji


@dataclass
class MahabotePeriod:
    """A single planetary period (Atar)."""
    planet: str
    planet_cn: str
    planet_symbol: str
    years: int
    start_age: int
    end_age: int
    is_current: bool


@dataclass
class MahaboteChart:
    """Complete Myanmar Mahabote chart result."""
    # Input parameters
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # Myanmar calendar
    myanmar_year: int

    # Weekday info
    weekday: int               # 0=Sunday … 6=Saturday
    weekday_name_en: str
    weekday_name_cn: str
    weekday_name_myanmar: str

    # Birth planet info
    birth_planet: str
    birth_planet_cn: str
    birth_planet_symbol: str
    birth_planet_element: str
    birth_direction: str

    # Wednesday evening → Rahu?
    is_rahu: bool

    # Birth animal sign
    birth_animal_en: str
    birth_animal_myanmar: str
    birth_animal_cn: str
    birth_animal_emoji: str

    # Mahabote calculation
    mahabote_value: int        # (ME + weekday_num) mod 7

    # Birth house
    birth_house_name_en: str
    birth_house_name_myanmar: str
    birth_house_name_cn: str
    birth_house_meaning: str
    birth_house_description: str

    # All 7 houses
    houses: list               # list[MahaboteHouse]

    # Planetary periods (Atar)
    periods: list              # list[MahabotePeriod]


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _get_myanmar_year(year, month, day):
    """Calculate Myanmar Era (ME) year from Gregorian date.

    Myanmar New Year (Thingyan) typically falls around April 17.
    ME = Gregorian year - 638 (on/after Apr 17) or - 639 (before Apr 17).
    """
    if month > 4 or (month == 4 and day >= 17):
        return year - 638
    return year - 639


def _get_weekday(year, month, day):
    """Day of week: 0=Sunday, 1=Monday, … 6=Saturday."""
    d = date(year, month, day)
    # Python weekday(): Mon=0 … Sun=6  →  we want Sun=0 … Sat=6
    return (d.weekday() + 1) % 7


def _is_wednesday_evening(weekday, hour):
    """Wednesday after 18:00 is ruled by Rahu instead of Mercury."""
    return weekday == 3 and hour >= 18


def _compute_periods(weekday, birth_year, current_year):
    """Compute Atar (planetary periods), starting from the birth weekday."""
    periods = []
    age = 0
    current_age = current_year - birth_year

    # Build 2 full cycles (192 years) to cover any lifespan
    for _ in range(2):
        for offset in range(7):
            day_idx = (weekday + offset) % 7
            planet_info = WEEKDAY_PLANETS[day_idx]
            planet_name = planet_info[0]
            duration = PLANET_PERIOD_YEARS[planet_name]
            start_age = age
            end_age = age + duration
            is_current = start_age <= current_age < end_age
            periods.append(MahabotePeriod(
                planet=planet_name,
                planet_cn=planet_info[2],
                planet_symbol=planet_info[3],
                years=duration,
                start_age=start_age,
                end_age=end_age,
                is_current=is_current,
            ))
            age += duration
            if age > 120:
                break
        if age > 120:
            break

    return periods


# ============================================================
# 計算函數 (Calculation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_mahabote_chart(year, month, day, hour, minute,
                           timezone, latitude, longitude,
                           location_name=""):
    """Compute a Myanmar Mahabote astrology chart."""

    me_year = _get_myanmar_year(year, month, day)
    weekday = _get_weekday(year, month, day)
    is_rahu = _is_wednesday_evening(weekday, hour)

    # Birth planet
    planet_info = WEEKDAY_PLANETS[weekday]
    animal_info = WEEKDAY_ANIMALS[weekday]
    if is_rahu:
        birth_planet = RAHU_INFO[0]
        birth_planet_cn = RAHU_INFO[2]
        birth_planet_symbol = RAHU_INFO[3]
        birth_planet_element = RAHU_INFO[4]
        birth_direction = RAHU_INFO[5]
        birth_animal = RAHU_ANIMAL
    else:
        birth_planet = planet_info[0]
        birth_planet_cn = planet_info[2]
        birth_planet_symbol = planet_info[3]
        birth_planet_element = planet_info[4]
        birth_direction = planet_info[5]
        birth_animal = animal_info

    # Mahabote value: use 1-based weekday (Sunday=1 … Saturday=7)
    weekday_num = weekday + 1
    mahabote_value = (me_year + weekday_num) % 7

    birth_house = MAHABOTE_HOUSES[mahabote_value]

    # Place planets in the 7 houses.
    # Birth planet sits at *mahabote_value*; subsequent weekdays
    # fill the next houses cyclically.
    houses = []
    for i in range(7):
        h_info = MAHABOTE_HOUSES[i]
        planet_offset = (i - mahabote_value) % 7
        planet_weekday = (weekday + planet_offset) % 7
        p_info = WEEKDAY_PLANETS[planet_weekday]
        a_info = WEEKDAY_ANIMALS[planet_weekday]

        houses.append(MahaboteHouse(
            index=i,
            name_en=h_info[0],
            name_myanmar=h_info[1],
            name_cn=h_info[2],
            meaning=h_info[3],
            description=h_info[4],
            planet=p_info[0],
            planet_cn=p_info[2],
            planet_symbol=p_info[3],
            is_birth_house=(i == mahabote_value),
            weekday_en=WEEKDAY_NAMES_EN[planet_weekday],
            weekday_cn=WEEKDAY_NAMES_CN[planet_weekday],
            animal_en=a_info[0],
            animal_myanmar=a_info[1],
            animal_cn=a_info[2],
            animal_emoji=a_info[3],
        ))

    # Atar periods
    from datetime import date as _date
    current_year = _date.today().year
    periods = _compute_periods(weekday, year, current_year)

    return MahaboteChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        myanmar_year=me_year,
        weekday=weekday,
        weekday_name_en=WEEKDAY_NAMES_EN[weekday],
        weekday_name_cn=WEEKDAY_NAMES_CN[weekday],
        weekday_name_myanmar=planet_info[1],
        birth_planet=birth_planet,
        birth_planet_cn=birth_planet_cn,
        birth_planet_symbol=birth_planet_symbol,
        birth_planet_element=birth_planet_element,
        birth_direction=birth_direction,
        is_rahu=is_rahu,
        birth_animal_en=birth_animal[0],
        birth_animal_myanmar=birth_animal[1],
        birth_animal_cn=birth_animal[2],
        birth_animal_emoji=birth_animal[3],
        mahabote_value=mahabote_value,
        birth_house_name_en=birth_house[0],
        birth_house_name_myanmar=birth_house[1],
        birth_house_name_cn=birth_house[2],
        birth_house_meaning=birth_house[3],
        birth_house_description=birth_house[4],
        houses=houses,
        periods=periods,
    )


# ============================================================
# 渲染函數 (Rendering)
# ============================================================

def render_mahabote_chart(chart):
    """Render the complete Myanmar Mahabote chart."""
    _render_info(chart)
    st.divider()
    _render_compass(chart)
    st.divider()
    _render_mahabote_grid(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_periods(chart)


# -- Info section ----------------------------------------------------------

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
        st.write(f"**緬甸年 (ME):** {chart.myanmar_year}")
        st.write(
            f"**出生星期:** {chart.weekday_name_cn} "
            f"({chart.weekday_name_en} / {chart.weekday_name_myanmar})"
        )
        rahu_note = " ⚠️ 星期三傍晚 → 羅睺 (Rahu)" if chart.is_rahu else ""
        st.write(
            f"**出生行星:** {chart.birth_planet_symbol} "
            f"{chart.birth_planet} ({chart.birth_planet_cn}){rahu_note}"
        )
        st.write(
            f"**生肖動物:** {chart.birth_animal_emoji} "
            f"{chart.birth_animal_en} ({chart.birth_animal_cn} / "
            f"{chart.birth_animal_myanmar})"
        )

    # Highlight box
    color = PLANET_COLORS.get(chart.birth_planet, "#888")
    st.markdown(
        f'<div style="background:{color}22;border:2px solid {color};'
        f'padding:12px;border-radius:8px;margin-top:8px;">'
        f'<b style="font-size:18px;">'
        f'{chart.birth_planet_symbol} {chart.birth_planet_cn} '
        f'({chart.birth_planet})</b> — '
        f'方位 {chart.birth_direction} · 元素 {chart.birth_planet_element} · '
        f'動物 {chart.birth_animal_emoji} {chart.birth_animal_cn}<br/>'
        f'<b>Mahabote 宮位:</b> '
        f'{chart.birth_house_name_cn} {chart.birth_house_name_myanmar} '
        f'({chart.birth_house_name_en}) — {chart.birth_house_meaning}<br/>'
        f'<span style="font-size:13px;color:#888;">'
        f'{chart.birth_house_description}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# -- Compass ---------------------------------------------------------------

def _render_compass(chart):
    """Render an 8-direction compass showing weekday-planet associations."""
    st.subheader("🧭 八方位行星羅盤 (Planetary Compass)")

    # Directions in display order:
    # (direction, weekday_idx, planet_en, symbol, planet_cn, weekday_cn, animal_emoji, animal_cn)
    # weekday_idx=-1 for Rahu (Wednesday evening)
    directions = [
        ("N 北",    6, "Saturn",  "♄", "土星", "星期六", "🐉", "龍/那伽"),
        ("NE 東北", 0, "Sun",     "☉", "太陽", "星期日", "🦅", "迦樓羅"),
        ("E 東",    1, "Moon",    "☽", "月亮", "星期一", "🐅", "虎"),
        ("SE 東南", 2, "Mars",    "♂", "火星", "星期二", "🦁", "獅"),
        ("S 南",    3, "Mercury", "☿", "水星", "星期三", "🐘", "象(有牙)"),
        ("SW 西南", -1, "Rahu",   "☊", "羅睺", "星期三夜", "🐘", "象(無牙)"),
        ("W 西",    4, "Jupiter", "♃", "木星", "星期四", "🐀", "鼠"),
        ("NW 西北", 5, "Venus",   "♀", "金星", "星期五", "🐹", "天竺鼠"),
    ]

    # Build a 3×5 compass layout:
    # Row 0:       NW    N    NE
    # Row 1:  W              E
    # Row 2:       SW    S    SE
    _cell = _compass_cell
    birth = chart.birth_planet

    row0 = [_cell(directions[7], birth), _cell(directions[0], birth),
            _cell(directions[1], birth)]
    row1_l = _cell(directions[6], birth)
    row1_r = _cell(directions[2], birth)
    row2 = [_cell(directions[5], birth), _cell(directions[4], birth),
            _cell(directions[3], birth)]

    center_html = (
        '<td style="text-align:center;font-size:28px;'
        'vertical-align:middle;">🧭</td>'
    )

    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:separate;border-spacing:4px;'
        'margin:auto;width:80%;max-width:500px;table-layout:fixed;">'
        f'<tr>{"".join(row0)}</tr>'
        f'<tr>{row1_l}{center_html}{row1_r}</tr>'
        f'<tr>{"".join(row2)}</tr>'
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _compass_cell(direction_info, birth_planet):
    """Build one compass cell."""
    (dir_label, _, planet_en, symbol,
     planet_cn, weekday_cn, animal_emoji, animal_cn) = direction_info
    is_birth = (planet_en == birth_planet)
    color = PLANET_COLORS.get(planet_en, "#888")
    border = f"3px solid {color}" if is_birth else "1px solid #555"
    bg = f"{color}22" if is_birth else "#1a1a2e"
    return (
        f'<td style="background:{bg};border:{border};padding:10px;'
        f'border-radius:8px;text-align:center;color:white;width:33%;">'
        f'<div style="font-size:10px;color:#aaa;">{dir_label}</div>'
        f'<div style="font-size:10px;color:#ccc;">{weekday_cn}</div>'
        f'<div style="font-size:24px;">{symbol}</div>'
        f'<div style="font-size:13px;font-weight:bold;color:{color};">'
        f'{planet_en}</div>'
        f'<div style="font-size:12px;">{planet_cn}</div>'
        f'<div style="font-size:11px;">{animal_emoji} {animal_cn}</div>'
        f'</td>'
    )


# -- Mahabote 3×3 grid -----------------------------------------------------

def _render_mahabote_grid(chart):
    """Render a 3×3 grid representing the 7 Mahabote houses."""
    st.subheader("🏛️ Mahabote 七宮盤 (Mahabote House Grid)")

    # Layout mapping:
    #   Row 0: Thila(6)  Marana(5)  Hein(4)
    #   Row 1: (empty)   Centre     Kiya(3)
    #   Row 2: Bhin(0)   Ayu(1)     Winya(2)
    grid_map = [
        [6, 5, 4],
        [None, "center", 3],
        [0, 1, 2],
    ]

    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:separate;border-spacing:4px;'
        'margin:auto;width:100%;min-width:280px;table-layout:fixed;">'
    )

    for row in grid_map:
        html += '<tr>'
        for cell in row:
            if cell == "center":
                html += _center_cell(chart)
            elif cell is None:
                html += (
                    '<td style="border:none;width:33%;'
                    'min-height:100px;"></td>'
                )
            else:
                html += _house_cell(chart.houses[cell])
        html += '</tr>'

    html += '</table></div>'
    st.markdown(html, unsafe_allow_html=True)


def _house_cell(house):
    """Render a single house cell."""
    color = PLANET_COLORS.get(house.planet, "#888")
    border = f"3px solid gold" if house.is_birth_house else "1px solid #555"
    bg = f"{color}15"
    star = "⭐ " if house.is_birth_house else ""
    return (
        f'<td style="background:{bg};border:{border};padding:12px;'
        f'border-radius:8px;text-align:center;vertical-align:top;'
        f'color:white;width:33%;">'
        f'<div style="font-size:11px;color:#aaa;">'
        f'{house.name_en} ({house.meaning})</div>'
        f'<div style="font-size:16px;font-weight:bold;">'
        f'{star}{house.name_cn} {house.name_myanmar}</div>'
        f'<div style="font-size:10px;color:#ccc;">{house.weekday_cn}</div>'
        f'<div style="font-size:26px;margin:4px 0;">{house.planet_symbol}</div>'
        f'<div style="font-size:13px;color:{color};font-weight:bold;">'
        f'{house.planet} ({house.planet_cn})</div>'
        f'<div style="font-size:12px;">'
        f'{house.animal_emoji} {house.animal_cn}</div>'
        f'</td>'
    )


def _center_cell(chart):
    """Center cell with summary info."""
    color = PLANET_COLORS.get(chart.birth_planet, "#888")
    return (
        f'<td style="background:#0d0d1a;border:2px solid {color};'
        f'padding:12px;border-radius:8px;text-align:center;'
        f'vertical-align:middle;color:white;width:33%;">'
        f'<div style="font-size:11px;color:#aaa;">Mahabote</div>'
        f'<div style="font-size:32px;">{chart.birth_planet_symbol}</div>'
        f'<div style="font-size:14px;font-weight:bold;color:{color};">'
        f'{chart.birth_planet_cn}</div>'
        f'<div style="font-size:11px;color:#bbb;">'
        f'ME {chart.myanmar_year}<br/>'
        f'{chart.weekday_name_cn}</div>'
        f'</td>'
    )


# -- House table ------------------------------------------------------------

def _render_house_table(chart):
    st.subheader("📊 七宮詳表 (House Details)")
    header = (
        "| # | 宮位 (House) | 緬甸文 | 含義 (Meaning) "
        "| 星期 | 行星 | 動物 | 說明 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|"
    rows = [header, sep]
    for h in chart.houses:
        star = "⭐" if h.is_birth_house else ""
        color = PLANET_COLORS.get(h.planet, "#888")
        planet_html = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{h.planet_symbol} {h.planet} ({h.planet_cn})</span>'
        )
        animal_html = f'{h.animal_emoji} {h.animal_cn}'
        rows.append(
            f"| {h.index} "
            f"| {star} {h.name_cn} ({h.name_en}) "
            f"| {h.name_myanmar} "
            f"| {h.meaning} "
            f"| {h.weekday_cn} "
            f"| {planet_html} "
            f"| {animal_html} "
            f"| {h.description} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# -- Atar periods -----------------------------------------------------------

def _render_periods(chart):
    st.subheader("📅 行星大運 (Atar / Planetary Periods)")
    st.markdown(
        "緬甸占星將人生分為七星循環大運，每顆行星主宰一段年歲"
        "（共 96 年一輪），由出生星期的行星開始："
    )

    header = "| 行星 | 起始年齡 | 結束年齡 | 年數 | 當前 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for p in chart.periods:
        if p.start_age > 110:
            break
        color = PLANET_COLORS.get(p.planet, "#888")
        current = "👈 **現行**" if p.is_current else ""
        planet_html = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{p.planet_symbol} {p.planet} ({p.planet_cn})</span>'
        )
        rows.append(
            f"| {planet_html} "
            f"| {p.start_age} "
            f"| {p.end_age} "
            f"| {p.years} "
            f"| {current} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # Visual timeline
    _render_period_timeline(chart)


def _render_period_timeline(chart):
    """Render a visual horizontal bar timeline of Atar periods."""
    max_age = 96
    html = (
        '<div style="display:flex;width:100%;height:36px;'
        'border-radius:6px;overflow:hidden;margin-top:8px;">'
    )
    for p in chart.periods:
        if p.start_age >= max_age:
            break
        end = min(p.end_age, max_age)
        width_pct = (end - p.start_age) / max_age * 100
        color = PLANET_COLORS.get(p.planet, "#888")
        border = "3px solid gold" if p.is_current else "none"
        html += (
            f'<div style="width:{width_pct:.1f}%;background:{color};'
            f'border:{border};display:flex;align-items:center;'
            f'justify-content:center;font-size:11px;color:white;'
            f'font-weight:bold;min-width:20px;" '
            f'title="{p.planet} ({p.planet_cn}): '
            f'{p.start_age}–{end} 歲">'
            f'{p.planet_symbol}'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.caption("行星大運時間軸（0–96 歲），金框為現行大運")
