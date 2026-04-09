"""
Picatrix 星體魔法模組 (Picatrix Stellar Magic Module)
資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
Greer & Warnock 2011 translation / Attrell & Porreca 2019

功能：
- 28 阿拉伯月宿（Manazil al-Qamar）計算與查詢
- 行星時（Planetary Hours）計算（含日出日落調整）
- 護符推薦（Talisman Recommendation）

程式碼風格與 arabic.py、decans.py 一致。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta, timezone

import swisseph as swe
import streamlit as st
import plotly.graph_objects as go

from astro.picatrix_data import (
    PICATRIX_MANSIONS,
    CHALDEAN_ORDER,
    PLANET_GLYPHS,
    PLANET_NAMES_CN,
    DAY_PLANETS,
    DAY_NAMES_EN,
    DAY_NAMES_CN,
    TALISMAN_INTENTS,
)


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class PicatrixMansion:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    A Picatrix lunar mansion with all classical attributes.
    """
    index: int
    arabic_name: str
    arabic_script: str
    english_name: str
    chinese_name: str
    ruling_planet: str
    fortunate: bool
    magic_image: str
    magic_image_cn: str
    purposes: list
    purposes_cn: list
    incense: str
    color: str
    metal: str
    invocation_summary: str
    start_degree: float


@dataclass
class PlanetaryHour:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    A single planetary hour entry.
    """
    hour_number: int        # 1-24 (1-12 day hours, 13-24 night hours)
    is_day: bool
    planet: str
    planet_glyph: str
    planet_cn: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float


@dataclass
class PlanetaryHoursResult:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    Result of planetary hours calculation for a given day and location.
    """
    date_str: str
    weekday_en: str
    weekday_cn: str
    day_planet: str
    latitude: float
    longitude: float
    timezone: float
    sunrise: datetime
    sunset: datetime
    day_length_minutes: float
    night_length_minutes: float
    hours: list  # list[PlanetaryHour]


@dataclass
class TalismanRecommendation:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    A Picatrix talisman recommendation based on user intent.
    """
    intent_key: str
    intent_cn: str
    intent_en: str
    planet: str
    planet_glyph: str
    planet_cn: str
    mansion_indices: list
    mansion_names_cn: list
    metal: str
    incense: str
    color: str
    hour_planet: str
    description_cn: str
    description_en: str


# ============================================================
# 月宿計算函數 (Mansion Calculation Functions)
# ============================================================

def get_mansion_index(moon_lon: float) -> int:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    根據月亮黃經度數回傳 Picatrix 月宿索引（0-27）。

    每宿跨距 360/28 ≈ 12.857°，從 0° 牡羊座起算。

    Args:
        moon_lon: 月亮黃經度數（0-360）

    Returns:
        int: 月宿索引 0-27
    """
    lon = moon_lon % 360.0
    mansion_width = 360.0 / 28
    idx = int(lon / mansion_width)
    return min(idx, 27)


def get_mansion(moon_lon: float) -> PicatrixMansion:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    根據月亮黃經度數回傳 Picatrix 月宿物件。

    Args:
        moon_lon: 月亮黃經度數（0-360）

    Returns:
        PicatrixMansion: 對應的月宿資料
    """
    idx = get_mansion_index(moon_lon)
    return _build_mansion(PICATRIX_MANSIONS[idx])


def get_mansion_by_index(index: int) -> PicatrixMansion:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    根據索引（0-27）回傳 Picatrix 月宿物件。

    Args:
        index: 月宿索引 0-27

    Returns:
        PicatrixMansion: 對應的月宿資料

    Raises:
        IndexError: if index is out of range 0-27
    """
    if not (0 <= index <= 27):
        raise IndexError(f"Mansion index must be 0-27, got {index}")
    return _build_mansion(PICATRIX_MANSIONS[index])


def get_all_mansions() -> list:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    回傳全部 28 個月宿物件列表。

    Returns:
        list[PicatrixMansion]
    """
    return [_build_mansion(d) for d in PICATRIX_MANSIONS]


def _build_mansion(d: dict) -> PicatrixMansion:
    """Build a PicatrixMansion dataclass from a raw dict."""
    return PicatrixMansion(
        index=d["index"],
        arabic_name=d["arabic_name"],
        arabic_script=d["arabic_script"],
        english_name=d["english_name"],
        chinese_name=d["chinese_name"],
        ruling_planet=d["ruling_planet"],
        fortunate=d["fortunate"],
        magic_image=d["magic_image"],
        magic_image_cn=d["magic_image_cn"],
        purposes=d["purposes"],
        purposes_cn=d["purposes_cn"],
        incense=d["incense"],
        color=d["color"],
        metal=d["metal"],
        invocation_summary=d["invocation_summary"],
        start_degree=d["start_degree"],
    )


# ============================================================
# 行星時計算函數 (Planetary Hours Calculation)
# ============================================================

def _chaldean_index(planet_name: str) -> int:
    """Return the 0-based index of a planet in the Chaldean order."""
    return CHALDEAN_ORDER.index(planet_name)


def _planet_for_hour(day_planet: str, hour_offset: int) -> str:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    Return the ruling planet for a given hour offset from day start.

    Args:
        day_planet: The planet ruling the day (from DAY_PLANETS)
        hour_offset: 0-based offset from first hour of day (0-23)

    Returns:
        str: Planet name
    """
    start_idx = _chaldean_index(day_planet)
    return CHALDEAN_ORDER[(start_idx + hour_offset) % 7]


def _julian_day(year: int, month: int, day: int, hour_ut: float) -> float:
    """Calculate Julian Day from UTC date and hour."""
    return swe.julday(year, month, day, hour_ut)


def _sun_rise_set(
    jd_date_start: float, latitude: float, longitude: float
) -> tuple[float, float]:
    """
    Calculate sunrise and sunset Julian Days for a given date and location.

    Args:
        jd_date_start: Julian Day at 00:00 UT for the requested date
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        tuple: (sunrise_jd, sunset_jd) in Julian Days (UT)
    """
    geopos = (longitude, latitude, 0.0)
    # Search from half a day before start to catch early-timezone sunrises
    search_start = jd_date_start - 0.5
    try:
        ret_rise, t_rise = swe.rise_trans(
            search_start, swe.SUN, swe.CALC_RISE, geopos
        )
        # Search for sunset after sunrise
        ret_set, t_set = swe.rise_trans(
            t_rise[0], swe.SUN, swe.CALC_SET, geopos
        )
    except Exception as exc:  # noqa: BLE001
        # Fallback for polar regions or ephemeris errors:
        # approximate sunrise at 06:00 UT, sunset at 18:00 UT.
        import warnings
        warnings.warn(
            f"Sunrise/sunset calculation failed ({exc}); "
            "using fallback values (06:00/18:00 UT).",
            RuntimeWarning,
            stacklevel=2,
        )
        t_rise = [jd_date_start + 6.0 / 24.0]
        t_set = [jd_date_start + 18.0 / 24.0]

    return float(t_rise[0]), float(t_set[0])


def _jd_to_local_datetime(jd: float, timezone: float) -> datetime:
    """Convert Julian Day (UT) to local datetime given timezone offset."""
    y, m, d, h = swe.revjul(jd)
    # h is decimal hours in UT; add timezone offset
    h_local = h + timezone
    # Base datetime in UT and apply offset
    base = datetime(int(y), int(m), int(d), 0, 0, 0)
    dt = base + timedelta(hours=h_local)
    return dt


def get_planetary_hours(
    year: int,
    month: int,
    day: int,
    timezone: float,
    latitude: float,
    longitude: float,
) -> PlanetaryHoursResult:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    計算指定日期和地點的 24 行星時（12 日間時 + 12 夜間時）。

    行星時依迦勒底序（Chaldean order）輪轉，每一日的第一時辰由當日主星管轄。
    日間時長 = 日出到日落 / 12；夜間時長 = 日落到次日日出 / 12。

    Args:
        year: 年
        month: 月
        day: 日
        timezone: 時區偏移（UTC+N）
        latitude: 緯度
        longitude: 經度

    Returns:
        PlanetaryHoursResult
    """
    swe.set_ephe_path("")

    # Build Julian Day at 00:00 UT for this date (used as search start)
    jd_day_start = _julian_day(year, month, day, 0.0)

    # Get sunrise / sunset in JD (UT)
    jd_rise, jd_set = _sun_rise_set(jd_day_start, latitude, longitude)

    # If sunset is before sunrise (polar edge case), fallback
    if jd_set <= jd_rise:
        jd_set = jd_rise + 0.5  # assume 12h day

    # Next sunrise: search after sunset
    geopos = (longitude, latitude, 0.0)
    try:
        _, t_next = swe.rise_trans(jd_set, swe.SUN, swe.CALC_RISE, geopos)
        jd_next_rise = float(t_next[0])
    except Exception as exc:  # noqa: BLE001
        # Fallback for polar regions or ephemeris errors.
        import warnings
        warnings.warn(
            f"Next sunrise calculation failed ({exc}); "
            "using sunset + 12h as fallback.",
            RuntimeWarning,
            stacklevel=2,
        )
        jd_next_rise = jd_set + 0.5
    if jd_next_rise <= jd_set:
        jd_next_rise = jd_set + 0.5

    # Weekday from local noon
    jd_noon = _julian_day(year, month, day, 12.0 - timezone)

    day_len_min = (jd_set - jd_rise) * 24 * 60
    night_len_min = (jd_next_rise - jd_set) * 24 * 60
    day_hour_len = day_len_min / 12
    night_hour_len = night_len_min / 12

    # Weekday (0=Sunday) at local noon
    dt_local_noon = _jd_to_local_datetime(jd_noon, timezone)
    weekday = dt_local_noon.weekday()  # Python: 0=Monday ... 6=Sunday
    # Convert Python weekday (Mon=0) to classical weekday (Sun=0)
    classical_weekday = (weekday + 1) % 7
    day_planet = DAY_PLANETS[classical_weekday]

    # Build 24 hours
    hours: list[PlanetaryHour] = []
    hour_offset = 0

    # 12 day hours
    for i in range(12):
        start_jd = jd_rise + i * (day_hour_len / (24 * 60))
        end_jd = jd_rise + (i + 1) * (day_hour_len / (24 * 60))
        planet = _planet_for_hour(day_planet, hour_offset)
        hours.append(PlanetaryHour(
            hour_number=i + 1,
            is_day=True,
            planet=planet,
            planet_glyph=PLANET_GLYPHS[planet],
            planet_cn=PLANET_NAMES_CN[planet],
            start_time=_jd_to_local_datetime(start_jd, timezone),
            end_time=_jd_to_local_datetime(end_jd, timezone),
            duration_minutes=day_hour_len,
        ))
        hour_offset += 1

    # 12 night hours
    for i in range(12):
        start_jd = jd_set + i * (night_hour_len / (24 * 60))
        end_jd = jd_set + (i + 1) * (night_hour_len / (24 * 60))
        planet = _planet_for_hour(day_planet, hour_offset)
        hours.append(PlanetaryHour(
            hour_number=i + 13,
            is_day=False,
            planet=planet,
            planet_glyph=PLANET_GLYPHS[planet],
            planet_cn=PLANET_NAMES_CN[planet],
            start_time=_jd_to_local_datetime(start_jd, timezone),
            end_time=_jd_to_local_datetime(end_jd, timezone),
            duration_minutes=night_hour_len,
        ))
        hour_offset += 1

    sunrise_dt = _jd_to_local_datetime(jd_rise, timezone)
    sunset_dt = _jd_to_local_datetime(jd_set, timezone)

    return PlanetaryHoursResult(
        date_str=f"{year}/{month:02d}/{day:02d}",
        weekday_en=DAY_NAMES_EN[classical_weekday],
        weekday_cn=DAY_NAMES_CN[classical_weekday],
        day_planet=day_planet,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        sunrise=sunrise_dt,
        sunset=sunset_dt,
        day_length_minutes=day_len_min,
        night_length_minutes=night_len_min,
        hours=hours,
    )


# ============================================================
# 護符推薦函數 (Talisman Recommendation)
# ============================================================

def get_picatrix_talisman_recommendation(intent: str) -> TalismanRecommendation | None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    根據使用者意圖推薦 Picatrix 護符配方。

    Args:
        intent: 意圖關鍵字，支援：
            "love" 愛情, "wealth" 財富, "health" 治病,
            "travel" 旅行, "protection" 保護,
            "knowledge" 知識, "power" 權力, "agriculture" 農業

    Returns:
        TalismanRecommendation | None: 護符推薦，若意圖不識別則回傳 None
    """
    intent_lower = intent.strip().lower()
    # Also match Chinese intents
    cn_map = {
        "愛情": "love", "財富": "wealth", "治病": "health",
        "旅行": "travel", "保護": "protection",
        "知識": "knowledge", "權力": "power", "農業": "agriculture",
    }
    if intent_lower in cn_map:
        intent_lower = cn_map[intent_lower]

    for t in TALISMAN_INTENTS:
        if t["intent_key"] == intent_lower:
            planet = t["planet"]
            mansion_names = [
                PICATRIX_MANSIONS[i]["chinese_name"]
                for i in t["mansion_indices"]
            ]
            return TalismanRecommendation(
                intent_key=t["intent_key"],
                intent_cn=t["intent_cn"],
                intent_en=t["intent_en"],
                planet=planet,
                planet_glyph=PLANET_GLYPHS[planet],
                planet_cn=PLANET_NAMES_CN[planet],
                mansion_indices=t["mansion_indices"],
                mansion_names_cn=mansion_names,
                metal=t["metal"],
                incense=t["incense"],
                color=t["color"],
                hour_planet=t["hour_planet"],
                description_cn=t["description_cn"],
                description_en=t["description_en"],
            )
    return None


def get_all_talisman_intents() -> list[str]:
    """Return all supported intent keys."""
    return [t["intent_key"] for t in TALISMAN_INTENTS]


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_mansion_lookup(moon_lon: float | None = None) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    渲染月宿查詢器（Mansion Lookup Tool）。

    Args:
        moon_lon: 月亮黃經度數（可選；若提供則直接顯示對應月宿）
    """
    st.subheader("🌙 月宿查詢器 (Lunar Mansion Lookup)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) — Greer & Warnock 2011 translation")

    all_mansions = get_all_mansions()

    # Interactive selector
    mansion_options = [
        f"{m.index + 1}. {m.arabic_name} ({m.chinese_name})"
        for m in all_mansions
    ]

    if moon_lon is not None:
        default_idx = get_mansion_index(moon_lon)
    else:
        default_idx = 0

    selected_label = st.selectbox(
        "選擇月宿 (Select Mansion)",
        options=mansion_options,
        index=default_idx,
        key="picatrix_mansion_select",
    )
    selected_idx = mansion_options.index(selected_label)
    mansion = all_mansions[selected_idx]

    _render_single_mansion(mansion)

    st.divider()
    _render_mansion_wheel(all_mansions, highlight_index=mansion.index)


def _render_single_mansion(m: PicatrixMansion) -> None:
    """Render a detailed card for a single mansion."""
    fortune_icon = "✨ 吉宿" if m.fortunate else "⚠️ 凶宿"
    st.markdown(
        f"### {m.index + 1}. {m.arabic_name} — {m.chinese_name} {fortune_icon}"
    )
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**阿拉伯文 (Arabic):** {m.arabic_script}")
        st.write(f"**英文名 (English):** {m.english_name}")
        st.write(f"**統治行星 (Ruling Planet):** "
                 f"{PLANET_GLYPHS[m.ruling_planet]} {m.ruling_planet} "
                 f"({PLANET_NAMES_CN[m.ruling_planet]})")
        st.write(f"**起始度數 (Start Degree):** {m.start_degree:.3f}°")
    with col2:
        st.write(f"**顏色 (Color):** {m.color}")
        st.write(f"**金屬 (Metal):** {m.metal}")
        st.write(f"**香料 (Incense):** {m.incense}")

    st.write(f"**魔法圖像 (Magic Image):** {m.magic_image}")
    st.write(f"**魔法圖像（中文）:** {m.magic_image_cn}")
    st.write(
        f"**用途 (Purposes):** {'; '.join(m.purposes_cn)} "
        f"/ {'; '.join(m.purposes)}"
    )
    st.write(f"**咒語摘要 (Invocation):** {m.invocation_summary}")


def _render_mansion_wheel(mansions: list, highlight_index: int = -1) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    使用 Plotly 繪製 28 月宿輪圖。
    """
    st.subheader("🌐 月宿輪圖 (Lunar Mansion Wheel)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)")

    n = 28
    angle_step = 360.0 / n
    # Each mansion as a sector
    labels = [f"{m.arabic_name}<br>{m.chinese_name}" for m in mansions]
    parents = [""] * n
    values = [1] * n
    colors = []
    for m in mansions:
        if m.index == highlight_index:
            colors.append("#FFD700")  # gold highlight
        elif m.fortunate:
            colors.append("#2E8B57")  # sea green for fortunate
        else:
            colors.append("#8B0000")  # dark red for unfortunate

    fig = go.Figure(go.Pie(
        labels=[f"{m.index + 1}. {m.arabic_name} ({m.chinese_name})" for m in mansions],
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo="label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Ruling Planet: %{customdata[0]}<br>"
            "Fortune: %{customdata[1]}<br>"
            "Metal: %{customdata[2]}<br>"
            "<extra></extra>"
        ),
        customdata=[
            [
                f"{PLANET_GLYPHS[m.ruling_planet]} {m.ruling_planet}",
                "✨ 吉" if m.fortunate else "⚠️ 凶",
                m.metal,
            ]
            for m in mansions
        ],
        direction="clockwise",
    ))
    fig.update_layout(
        title="Picatrix 28 Lunar Mansions (阿拉伯月宿輪圖)",
        showlegend=False,
        height=600,
        paper_bgcolor="#1a1a2e",
        font=dict(color="#e0e0e0", size=9),
        annotations=[dict(
            text="月宿輪",
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False,
            font_color="#e0e0e0",
        )],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_planetary_hours_tool(
    year: int, month: int, day: int,
    timezone: float, latitude: float, longitude: float,
) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    渲染行星時計算器（Planetary Hours Tool）。

    Args:
        year, month, day: Date
        timezone: UTC offset
        latitude, longitude: Location coordinates
    """
    st.subheader("⏰ 行星時計算器 (Planetary Hours Calculator)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9")

    with st.spinner("正在計算行星時..."):
        result = get_planetary_hours(year, month, day, timezone, latitude, longitude)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {result.date_str}")
        st.write(f"**星期 (Weekday):** {result.weekday_cn} ({result.weekday_en})")
        st.write(
            f"**當日主星 (Day Planet):** "
            f"{PLANET_GLYPHS[result.day_planet]} {result.day_planet} "
            f"({PLANET_NAMES_CN[result.day_planet]})"
        )
    with col2:
        st.write(f"**日出 (Sunrise):** {result.sunrise.strftime('%H:%M:%S')}")
        st.write(f"**日落 (Sunset):** {result.sunset.strftime('%H:%M:%S')}")
        st.write(f"**日間時長 (Day Hour):** {result.day_length_minutes / 12:.1f} 分鐘")
        st.write(f"**夜間時長 (Night Hour):** {result.night_length_minutes / 12:.1f} 分鐘")

    # Table
    header = (
        "| # | 日/夜 | 行星 (Planet) | 時辰 | 開始時間 | 結束時間 | 時長(分) |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    planet_colors = {
        "Saturn": "#4169E1", "Jupiter": "#9400D3", "Mars": "#DC143C",
        "Sun": "#FFD700", "Venus": "#228B22", "Mercury": "#FF8C00", "Moon": "#C0C0C0",
    }
    for h in result.hours:
        color = planet_colors.get(h.planet, "#c8c8c8")
        p_html = (
            f'<span style="color:{color};font-weight:bold">'
            f"{h.planet_glyph} {h.planet} ({h.planet_cn})</span>"
        )
        day_night = "☀️ 日" if h.is_day else "🌙 夜"
        rows.append(
            f"| {h.hour_number} "
            f"| {day_night} "
            f"| {p_html} "
            f"| {h.hour_number if h.is_day else h.hour_number - 12} "
            f"| {h.start_time.strftime('%H:%M')} "
            f"| {h.end_time.strftime('%H:%M')} "
            f"| {h.duration_minutes:.1f} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # Plotly bar chart
    _render_planetary_hours_chart(result)


def _render_planetary_hours_chart(result: PlanetaryHoursResult) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    Draw a Plotly timeline bar chart for planetary hours.
    """
    st.subheader("📊 行星時圖 (Planetary Hours Chart)")
    planet_colors = {
        "Saturn": "#4169E1", "Jupiter": "#9400D3", "Mars": "#DC143C",
        "Sun": "#FFD700", "Venus": "#228B22", "Mercury": "#FF8C00", "Moon": "#C0C0C0",
    }

    fig = go.Figure()
    for h in result.hours:
        start_str = h.start_time.strftime("%H:%M")
        end_str = h.end_time.strftime("%H:%M")
        label = f"{h.planet_glyph} {h.planet}<br>({h.planet_cn})"
        fig.add_trace(go.Bar(
            x=[h.duration_minutes],
            y=[f"{'☀️' if h.is_day else '🌙'} H{h.hour_number}"],
            orientation="h",
            marker_color=planet_colors.get(h.planet, "#888"),
            name=h.planet,
            hovertemplate=(
                f"<b>Hour {h.hour_number}</b><br>"
                f"Planet: {h.planet} ({h.planet_cn})<br>"
                f"Start: {start_str}<br>End: {end_str}<br>"
                f"Duration: {h.duration_minutes:.1f} min<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        # Add text annotation in bar
        fig.add_annotation(
            x=h.duration_minutes / 2,
            y=f"{'☀️' if h.is_day else '🌙'} H{h.hour_number}",
            text=f"{h.planet_glyph}",
            showarrow=False,
            font=dict(size=12, color="white"),
        )

    fig.update_layout(
        title=f"Picatrix 行星時 — {result.date_str} ({result.weekday_cn})",
        xaxis_title="時長（分鐘）",
        yaxis_title="時辰",
        barmode="stack",
        height=700,
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font=dict(color="#e0e0e0"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_talisman_generator() -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    渲染護符生成器（Talisman Generator）。
    """
    st.subheader("🔮 護符生成器 (Talisman Generator)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12")

    intent_options = {
        "愛情 (Love & Romance)": "love",
        "財富 (Wealth & Prosperity)": "wealth",
        "治病 (Health & Healing)": "health",
        "旅行 (Safe Travel)": "travel",
        "保護 (Protection & Warding)": "protection",
        "知識 (Knowledge & Wisdom)": "knowledge",
        "權力 (Power & Authority)": "power",
        "農業 (Agriculture & Planting)": "agriculture",
    }

    selected_intent_label = st.selectbox(
        "選擇意圖 (Select Intent)",
        options=list(intent_options.keys()),
        key="picatrix_talisman_intent",
    )
    intent_key = intent_options[selected_intent_label]

    rec = get_picatrix_talisman_recommendation(intent_key)
    if rec is None:
        st.warning("未找到對應護符配方。")
        return

    st.markdown(
        f"### {PLANET_GLYPHS[rec.planet]} {rec.intent_cn} — "
        f"{rec.intent_en} 護符"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**守護行星 (Planet):** "
                 f"{rec.planet_glyph} {rec.planet} ({rec.planet_cn})")
        st.write(f"**金屬 (Metal):** {rec.metal}")
        st.write(f"**顏色 (Color):** {rec.color}")
        st.write(f"**香料 (Incense):** {rec.incense}")
        st.write(f"**施咒時辰行星 (Hour Planet):** "
                 f"{PLANET_GLYPHS[rec.hour_planet]} {rec.hour_planet} "
                 f"({PLANET_NAMES_CN[rec.hour_planet]})")
    with col2:
        st.write("**適合月宿 (Favorable Mansions):**")
        for i, (idx, cn) in enumerate(
            zip(rec.mansion_indices, rec.mansion_names_cn)
        ):
            m = PICATRIX_MANSIONS[idx]
            fortune = "✨" if m["fortunate"] else "⚠️"
            st.write(
                f"  {fortune} 第 {idx + 1} 宿：{m['arabic_name']} ({cn})"
            )

    st.markdown("---")
    st.markdown(f"**施作指引（中文）:** {rec.description_cn}")
    st.markdown(f"**Instructions (English):** {rec.description_en}")

    # Show mansion images for recommended mansions
    st.markdown("#### 月宿魔法圖像 (Magic Images for Recommended Mansions)")
    for idx in rec.mansion_indices:
        m = PICATRIX_MANSIONS[idx]
        fortune_icon = "✨" if m["fortunate"] else "⚠️"
        st.markdown(
            f"**{m['index'] + 1}. {m['arabic_name']} ({m['chinese_name']})** "
            f"{fortune_icon}"
        )
        st.write(f"  🖼️ {m['magic_image_cn']}")
        st.write(f"  🖼️ _{m['magic_image']}_")


# ============================================================
# 瀏覽函數 (Browse / Reference Functions)
# ============================================================

def render_picatrix_browse() -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    渲染 Picatrix 完整參考瀏覽器（不需要排盤資料）。
    包含：今日月宿、28 月宿總覽表、月宿輪圖、迦勒底行星序、護符意圖總覽。
    """
    st.subheader("📜 Picatrix 星體魔法參考 (Reference)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) "
        "— Greer & Warnock 2011 / Attrell & Porreca 2019"
    )

    # --- 今日月宿 ---
    swe.set_ephe_path("")
    now = datetime.now(tz=timezone.utc)
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    moon_now, _ = swe.calc_ut(now_jd, swe.MOON)
    today_moon_lon = float(moon_now[0]) % 360.0
    today_idx = get_mansion_index(today_moon_lon)
    today_mansion = get_mansion_by_index(today_idx)

    _render_today_mansion_card(today_moon_lon, today_mansion)

    # Sub-tabs for browsing
    browse_tabs = st.tabs([
        "🌐 月宿輪圖", "📋 28 月宿總覽", "🪐 迦勒底行星序",
        "🔮 護符意圖總覽",
    ])

    all_mansions = get_all_mansions()

    with browse_tabs[0]:
        _render_mansion_wheel(all_mansions, highlight_index=today_idx)

    with browse_tabs[1]:
        _render_mansion_grid(all_mansions, highlight_index=today_idx)

    with browse_tabs[2]:
        _render_chaldean_reference()

    with browse_tabs[3]:
        _render_talisman_intents_table()


def _render_today_mansion_card(
    moon_lon: float, mansion: PicatrixMansion
) -> None:
    """渲染今日月宿速覽卡片。"""
    fortune_icon = "✨ 吉宿" if mansion.fortunate else "⚠️ 凶宿"
    st.markdown(
        f"### 🌙 今日月宿：{mansion.index + 1}. {mansion.arabic_name} "
        f"— {mansion.chinese_name} {fortune_icon}"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("月亮黃經", f"{moon_lon:.2f}°")
    with col2:
        st.metric(
            "統治行星",
            f"{PLANET_GLYPHS[mansion.ruling_planet]} "
            f"{PLANET_NAMES_CN[mansion.ruling_planet]}",
        )
    with col3:
        st.metric("吉凶", fortune_icon)
    st.write(f"**魔法圖像:** {mansion.magic_image_cn}")
    st.write(
        f"**用途:** {' · '.join(mansion.purposes_cn)}"
    )
    st.divider()


def _render_mansion_grid(
    mansions: list, highlight_index: int = -1
) -> None:
    """渲染 28 月宿總覽表格。"""
    st.subheader("📋 28 月宿總覽 (Complete Mansions Reference)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book I, Ch. 4"
    )

    # Summary table
    header = (
        "| # | 中文名 | 阿拉伯名 (Arabic) | 英文名 | "
        "統治行星 | 吉凶 | 顏色 | 金屬 | 香料 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for m in mansions:
        fortune = "✨ 吉" if m.fortunate else "⚠️ 凶"
        highlight = " **→**" if m.index == highlight_index else ""
        rows.append(
            f"| {m.index + 1}{highlight} "
            f"| {m.chinese_name} "
            f"| {m.arabic_name} ({m.arabic_script}) "
            f"| {m.english_name} "
            f"| {PLANET_GLYPHS[m.ruling_planet]} {PLANET_NAMES_CN[m.ruling_planet]} "
            f"| {fortune} "
            f"| {m.color} "
            f"| {m.metal} "
            f"| {m.incense} |"
        )
    st.markdown("\n".join(rows))

    # Expandable detail cards
    st.divider()
    st.subheader("🔍 月宿詳細資料 (Detailed Mansion Cards)")
    for m in mansions:
        fortune_icon = "✨ 吉宿" if m.fortunate else "⚠️ 凶宿"
        with st.expander(
            f"{m.index + 1}. {m.arabic_name} — {m.chinese_name} "
            f"({m.english_name}) {fortune_icon}",
            expanded=(m.index == highlight_index),
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**阿拉伯文:** {m.arabic_script}")
                st.write(
                    f"**統治行星:** {PLANET_GLYPHS[m.ruling_planet]} "
                    f"{m.ruling_planet} ({PLANET_NAMES_CN[m.ruling_planet]})"
                )
                st.write(f"**起始度數:** {m.start_degree:.3f}°")
                st.write(f"**顏色:** {m.color}")
            with col2:
                st.write(f"**金屬:** {m.metal}")
                st.write(f"**香料:** {m.incense}")
                st.write(f"**吉凶:** {fortune_icon}")
            st.write(f"**魔法圖像:** {m.magic_image_cn}")
            st.write(f"**Magic Image:** _{m.magic_image}_")
            st.write(
                f"**用途:** {' · '.join(m.purposes_cn)} "
                f"/ {' · '.join(m.purposes)}"
            )
            st.write(f"**咒語摘要:** {m.invocation_summary}")


def _render_chaldean_reference() -> None:
    """渲染迦勒底行星序參考表。"""
    st.subheader("🪐 迦勒底行星序 (Chaldean Planetary Order)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9"
    )
    st.markdown(
        """
        **迦勒底序**是古代占星術中行星的基本排列順序，由最慢（土星）
        到最快（月亮），用於決定每日每時辰的行星主宰：

        > ♄ 土星 → ♃ 木星 → ♂ 火星 → ☉ 太陽 → ♀ 金星 → ☿ 水星 → ☽ 月亮

        每一日的**第一時辰**由該日的主星管轄，之後每時辰按迦勒底序輪轉。
        """
    )

    # Planet table
    st.markdown("#### 七曜與星期對應 (Planets & Weekdays)")
    header = "| 星期 | Weekday | 主星 | 符號 | 金屬 | 顏色 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    planet_metals = {
        "Saturn": "鉛 (Lead)", "Jupiter": "錫 (Tin)",
        "Mars": "鐵 (Iron)", "Sun": "金 (Gold)",
        "Venus": "銅 (Copper)", "Mercury": "水銀 (Quicksilver)",
        "Moon": "銀 (Silver)",
    }
    planet_colors = {
        "Saturn": "黑色 (Black)", "Jupiter": "藍紫色 (Purple)",
        "Mars": "紅色 (Red)", "Sun": "金色 (Golden)",
        "Venus": "綠色 (Green)", "Mercury": "橙色 (Orange)",
        "Moon": "銀白色 (Silver)",
    }
    rows = [header, sep]
    for i in range(7):
        planet = DAY_PLANETS[i]
        rows.append(
            f"| {DAY_NAMES_CN[i]} "
            f"| {DAY_NAMES_EN[i]} "
            f"| {PLANET_NAMES_CN[planet]} ({planet}) "
            f"| {PLANET_GLYPHS[planet]} "
            f"| {planet_metals[planet]} "
            f"| {planet_colors[planet]} |"
        )
    st.markdown("\n".join(rows))

    # Chaldean order visual
    st.markdown("#### 迦勒底序環 (Chaldean Circle)")
    order_display = " → ".join(
        f"{PLANET_GLYPHS[p]} {PLANET_NAMES_CN[p]}" for p in CHALDEAN_ORDER
    )
    st.markdown(f"> {order_display} → (循環)")


def _render_talisman_intents_table() -> None:
    """渲染護符意圖總覽表。"""
    st.subheader("🔮 護符意圖總覽 (Talisman Intents Reference)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12"
    )
    st.markdown(
        """
        Picatrix 記載了八種主要護符意圖，每種有對應的守護行星、
        適合施作的月宿、使用材質和儀式指引：
        """
    )

    header = (
        "| 意圖 | Intent | 守護行星 | 金屬 | 香料 | 顏色 | "
        "適合月宿 | 施作時辰 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for t in TALISMAN_INTENTS:
        planet = t["planet"]
        mansion_names = [
            f"{PICATRIX_MANSIONS[i]['chinese_name']}({i + 1})"
            for i in t["mansion_indices"]
        ]
        rows.append(
            f"| {t['intent_cn']} "
            f"| {t['intent_en']} "
            f"| {PLANET_GLYPHS[planet]} {PLANET_NAMES_CN[planet]} "
            f"| {t['metal']} "
            f"| {t['incense']} "
            f"| {t['color']} "
            f"| {'、'.join(mansion_names)} "
            f"| {PLANET_GLYPHS[t['hour_planet']]} "
            f"{PLANET_NAMES_CN[t['hour_planet']]} |"
        )
    st.markdown("\n".join(rows))

    # Detailed expanders for each intent
    st.divider()
    st.markdown("#### 📖 護符詳細指引 (Detailed Talisman Instructions)")
    for t in TALISMAN_INTENTS:
        planet = t["planet"]
        with st.expander(
            f"{PLANET_GLYPHS[planet]} {t['intent_cn']} — {t['intent_en']}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(
                    f"**守護行星:** {PLANET_GLYPHS[planet]} "
                    f"{planet} ({PLANET_NAMES_CN[planet]})"
                )
                st.write(f"**金屬:** {t['metal']}")
                st.write(f"**香料:** {t['incense']}")
                st.write(f"**顏色:** {t['color']}")
                st.write(
                    f"**施咒時辰:** {PLANET_GLYPHS[t['hour_planet']]} "
                    f"{t['hour_planet']} ({PLANET_NAMES_CN[t['hour_planet']]})"
                )
            with col2:
                st.write("**適合月宿:**")
                for i in t["mansion_indices"]:
                    m = PICATRIX_MANSIONS[i]
                    fortune = "✨" if m["fortunate"] else "⚠️"
                    st.write(
                        f"  {fortune} 第 {i + 1} 宿："
                        f"{m['arabic_name']} ({m['chinese_name']})"
                    )
            st.markdown(f"**施作指引（中文）:** {t['description_cn']}")
            st.markdown(f"**Instructions:** {t['description_en']}")
