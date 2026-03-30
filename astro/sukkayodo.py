"""
日本宿曜道 (Yojōdō) 排盤模組

宿曜道由空海大師於 9 世紀自印度 Jyotish 傳入日本，
使用 28 宿（比印度 27 Nakshatra 多出 Abhijit/牛宿），
以 Moon 所在宿計算六曜 (Rokuyō)。
"""

import streamlit as st

# 七曜名稱索引對照 (lord index → name string)
GRAHA_NAMES_BY_INDEX = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

# 日本宿曜道 28 宿
# (nak_name, japanese_name, chinese_name, lord_graha_index, symbol, deity, quality)
# lord: 0=Ketu, 1=Venus, 2=Sun, 3=Moon, 4=Mars, 5=Rahu, 6=Jupiter, 7=Saturn, 8=Mercury
SUKKAYODO_MANSION = [
    ("Ashwini",          "アシュヴィニ", "馬頭",   0, "馬", "Aswini Twins",   "Cheerful"),
    ("Bharani",          "バラニ",       "大陵",   1, "彡", "Yami",            "Passionate"),
    ("Krittika",         "クリティカー", "昴宿",   2, "卍", "Agni",            "Fierce"),
    ("Rohini",           "ロヒニー",     "畢宿",   3, "兔", "Brahma",          "Stable"),
    ("Mrigashira",       "ミルガシラ",   "觜宿",   4, "蚯", "Soma",            "Curious"),
    ("Ardra",            "アルドラ",     "參宿",   5, "獅子","Rudra",           "Restless"),
    ("Punarvasu",        "プナルヴァス", "井宿",   6, "福", "Aditi",           "Renewing"),
    ("Pushya",           "プシュヤ",     "鬼宿",   7, "邪", "Brihaspati",      "Nurturing"),
    ("Ashlesha",         "アシュレーシャ","柳宿",  8, "毒", "Naga",             "Seductive"),
    ("Magha",            "メリカ",       "星宿",   0, "慢", "Pitris",          "Regal"),
    ("Purva Phalguni",   "プールヴァ",   "張宿",   1, "栄", "Bhaga",           "Loving"),
    ("Uttara Phalguni",  "ウッター",     "翼宿",   2, "双", "Aryaman",         "Dutiful"),
    ("Hasta",            "ハスタ",       "軫宿",   3, "智", "Savitri",         "Skillful"),
    ("Chitra",           "チトラ",       "角宿",   4, "勝", "Tvashtar",        "Radiant"),
    ("Swati",            "スヴァティ",   "亢宿",   5, "撃", "Vayu",            "Independent"),
    ("Vishakha",         "ヴィシャーカー", "氐宿",  6, "力", "Indra/Agni",      "Multi-faceted"),
    ("Anuradha",         "アヌラーダー", "房宿",   7, "喜", "Mitra",           "Balanced"),
    ("Jyeshtha",         "ジェーシタ",   "心宿",   8, "主", "Indra",           "Protective"),
    ("Mula",             "ムーラ",       "尾宿",   0, "死", "Nirriti",         "Deep"),
    ("Purva Ashadha",    "プールヴァ",   "箕宿",   1, "満", "Apah",            "Victorious"),
    ("Uttara Ashadha",   "ウッター",    "斗宿",   2, "生", "Vishwa Devas",    "Truthful"),
    ("Abhijit",          "アビジート",   "牛宿",   2, "織", "Brahma/Vega",     "Noble"),
    ("Shravana",         "シュラヴァナ", "女宿",   3, "虚", "Vishnu",          "Devoted"),
    ("Dhanishta",        "ダニスター",   "虛宿",   4, "危", "Vasudev",         "Wealthy"),
    ("Shatabhisha",      "シャタビシャ", "危宿",   5, "命", "Varuna",          "Mysterious"),
    ("Purva Bhadrapada", "プールヴァ",   "室宿",   6, "留", "Aja Ekapada",     "Heroic"),
    ("Uttara Bhadrapada","ウッター",     "壁宿",   7, "堅", "Ahir Budhya",     "Serene"),
    ("Revati",           "レヴァティー", "奎宿",   8, "開", "Pushan",          "Nurturing"),
]

# 六曜 (Rokuyō) — 順序：先勝 → 友引 → 先負 → 仏滅 → 大安 → 赤口
ROKUYO = [
    ("先勝",   "Senshō",   "吉(速)",  "#228B22"),
    ("友引",   "Tomoyuki", "小吉",    "#4169E1"),
    ("先負",   "Senku",    "末吉",    "#8B4513"),
    ("仏滅",   "Butsumetsu","凶",     "#DC143C"),
    ("大安",   "Taian",    "大吉",    "#FFD700"),
    ("赤口",   "Shakuchō", "凶(吉)",  "#FF4500"),
]

# 每宿對應六曜索引（每 6 宿一循環）
SUKKAYODO_NAKSHATRA_ROKUYO_MAP = [
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3,
]

# 七曜顏色（深色主題）
GRAHA_COLORS = {
    "Ketu":     "#9B59B6",
    "Venus":    "#FF69B4",
    "Sun":      "#FF8C00",
    "Moon":     "#C0C0C0",
    "Mars":     "#DC143C",
    "Rahu":     "#8E44AD",
    "Jupiter":  "#FFD700",
    "Saturn":   "#8B4513",
    "Mercury":  "#4169E1",
}

PLANET_COLORS = {
    "Surya (太陽)": "#FF8C00",
    "Chandra (月亮)": "#C0C0C0",
    "Mangal (火星)": "#DC143C",
    "Budha (水星)": "#4169E1",
    "Guru (木星)": "#FFD700",
    "Shukra (金星)": "#FF69B4",
    "Shani (土星)": "#8B4513",
    "Rahu (羅睺)": "#8E44AD",
    "Ketu (計都)": "#9B59B6",
}


# ============================================================
# 計算函數
# ============================================================

def _normalize(deg):
    return deg % 360.0


def sukkayodo_info(deg):
    """Return (sukkayodo_mansion_index, pada) for sidereal longitude.

    宿曜道 28 宿，每宿 12°51'26"（360°/28）。
    """
    deg = _normalize(deg)
    nak_span = 360.0 / 28.0
    idx = int(deg / nak_span) % 28
    pada = int((deg % nak_span) / (nak_span / 4.0)) + 1
    return idx, min(pada, 4)


def get_rokuyo(mansion_index):
    """根據宿曜道索引取得六曜資訊"""
    if mansion_index < 0 or mansion_index >= 28:
        return None
    return ROKUYO[SUKKAYODO_NAKSHATRA_ROKUYO_MAP[mansion_index % 28]]


# ============================================================
# 渲染函數
# ============================================================

def render_sukkayodo_chart(chart):
    """渲染日本宿曜道排盤"""
    st.subheader("🈳 日本宿曜道 (Yojōdō)")

    # 找出 Moon
    moon_planet = None
    for p in chart.planets:
        if "Moon" in p.name or "月亮" in p.name:
            moon_planet = p
            break

    moon_mansion_idx = -1
    if moon_planet and moon_planet.sukkayodo_mansion_index >= 0:
        moon_mansion_idx = moon_planet.sukkayodo_mansion_index
        rokuyo = get_rokuyo(moon_mansion_idx)
    else:
        rokuyo = None

    # 六曜卡片
    st.markdown("### 當日六曜 (Rokuyō)")
    cols = st.columns(6)
    for i, (jp, romaji, meaning, color) in enumerate(ROKUYO):
        active = (rokuyo and rokuyo[0] == jp)
        bg = color if active else "#1a1a2e"
        fg = "#fff" if active else "#aaa"
        border = f"2px solid {color}" if active else "1px solid #333"
        style = (
            f"background:{bg}; color:{fg}; padding:10px; "
            f"border-radius:8px; text-align:center; border:{border};"
        )
        with cols[i]:
            st.markdown(
                f'<div style="{style}">'
                f'<b>{jp}</b><br/><small>{romaji}</small><br/>'
                f'<small>{meaning}</small>{" ✅" if active else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if moon_planet:
        st.caption(
            f"Moon 位於：{moon_planet.sukkayodo_mansion}"
            f"（{moon_planet.sukkayodo_mansion_chinese}）"
            f"　{moon_planet.sukkayodo_pada}足　"
            f"→ 六曜：{rokuyo[0] if rokuyo else '?'} ({rokuyo[1] if rokuyo else ''})"
        )

    # 宿曜道圓環圖
    st.markdown("### 宿曜道圓環圖 (二十八宿)")
    _render_wheel(chart, moon_mansion_idx)

    # 行星宿曜道位置
    st.markdown("### 行星宿曜道位置")
    rows2 = [
        "| Graha | 宿名 | 中國 | Pada | 六曜 |",
        "|:-----:|:-----|:-----|:----:|:----:|",
    ]
    for p in chart.planets:
        if p.sukkayodo_mansion_index >= 0:
            m = SUKKAYODO_MANSION[p.sukkayodo_mansion_index]
            rk = get_rokuyo(p.sukkayodo_mansion_index)
            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            rows2.append(
                f"| <span style='color:{color}'>{p.name}</span> | "
                f"**{p.sukkayodo_mansion}** ({m[1]}) | "
                f"{p.sukkayodo_mansion_chinese} | {p.sukkayodo_pada} | "
                f"<span style='color:{rk[3]}'>{rk[0]}</span> |"
            )
    st.markdown("\n".join(rows2), unsafe_allow_html=True)

    # 28 宿列表
    st.markdown("### 二十八宿 (28 Mansions)")
    rows = [
        "| # | 宿名 | 日名 | 中國 | 符 | 主曜 | 六曜 |",
        "|:--:|:-----|:-----|:-----|:--:|:-----|:----:|",
    ]
    for i, m in enumerate(SUKKAYODO_MANSION):
        nak_name, jp_name, chinese = m[0], m[1], m[2]
        lord_idx, symbol = m[3], m[4]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        lord_color = GRAHA_COLORS.get(lord_name, "#c8c8c8")
        is_moon = (i == moon_mansion_idx)
        rk = get_rokuyo(i)
        star = "⭐" if is_moon else ""
        rows.append(
            f"| {star}{i+1} | "
            f'<b>{"⭐" if is_moon else ""}{nak_name}</b> | '
            f'{jp_name} | {chinese} | {symbol} | '
            f'<span style="color:{lord_color}">{lord_name}</span> | '
            f'<span style="color:{rk[3]}">{rk[0]}</span> |'
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_wheel(chart, moon_mansion_idx):
    """渲染宿曜道圓環圖 — 三層同心結構"""

    # 建立每宿行星列表
    mansion_planets = {i: [] for i in range(28)}
    for p in chart.planets:
        if p.sukkayodo_mansion_index >= 0:
            mansion_planets[p.sukkayodo_mansion_index].append(p.name.split(" ")[0])

    # 28 個扇形，每個 360/28 ≈ 12.857°
    # 用 HTML table 模擬：外圈 (宿名+符號) / 中圈 (主曜) / 內圈 (六曜)

    CELL_STYLE = (
        "border:1px solid #333; padding:3px 0; text-align:center; "
        "vertical-align:middle; font-size:11px; background:#1a1a2e; color:#c8c8c8;"
    )
    MOON_CELL = (
        "border:1px solid #FFD700; padding:3px 0; text-align:center; "
        "vertical-align:middle; font-size:11px; background:#3d3010; color:#FFD700; font-weight:bold;"
    )
    ROKUYO_CELL = (
        "border:1px solid #333; padding:2px 0; text-align:center; "
        "vertical-align:middle; font-size:10px; color:#aaa;"
    )
    ROKUYO_CELL_ACTIVE = (
        "border:1px solid #FFD700; padding:2px 0; text-align:center; "
        "vertical-align:middle; font-size:10px; color:#FFD700; font-weight:bold;"
    )
    CENTER_STYLE = (
        "border:2px solid #555; border-radius:50%; padding:12px; "
        "text-align:center; vertical-align:middle; background:#1a1a2e; color:#e0e0e0;"
    )

    # 每個宿 3 個格子（外→中→內），共 28 列
    html = (
        '<table style="border-collapse:collapse; margin:auto; width:100%; max-width:900px; '
        'table-layout:fixed;">'
    )

    # --- Header Row: 28 個外圈格子（宿名+符號）---
    html += "<tr>"
    for i in range(28):
        m = SUKKAYODO_MANSION[i]
        nak_name, jp_name, chinese = m[0], m[1], m[2]
        symbol = m[4]
        is_moon = (i == moon_mansion_idx)
        style = MOON_CELL if is_moon else CELL_STYLE
        rk = get_rokuyo(i)
        p_list = mansion_planets[i]
        planets_html = "".join(
            f'<span style="color:{PLANET_COLORS.get(pp, "#c8c8c8")};font-size:9px">{pp}</span> '
            for pp in p_list
        ) if p_list else ""
        html += (
            f'<td style="{style}">'
            f'<b style="font-size:12px">{"⭐" if is_moon else ""}{nak_name[:3]}</b><br/>'
            f'<span style="font-size:13px">{symbol}</span><br/>'
            f'<small style="color:#888">{chinese}</small><br/>'
            f'{planets_html}'
            f'</td>'
        )
    html += "</tr>"

    # --- Middle Row: 28 個中圈格子（主曜名）---
    html += "<tr>"
    for i in range(28):
        m = SUKKAYODO_MANSION[i]
        lord_idx = m[3]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        lord_color = GRAHA_COLORS.get(lord_name, "#c8c8c8")
        is_moon = (i == moon_mansion_idx)
        style = MOON_CELL if is_moon else (
            "border:1px solid #333; padding:4px 0; text-align:center; "
            "vertical-align:middle; font-size:10px; background:#12122a; "
            f"color:{lord_color};"
        )
        html += (
            f'<td style="{style}">'
            f'<span style="color:{lord_color}">{lord_name}</span>'
            f'</td>'
        )
    html += "</tr>"

    # --- Inner Row: 28 個內圈格子（六曜）---
    html += "<tr>"
    for i in range(28):
        rk = get_rokuyo(i)
        is_moon = (i == moon_mansion_idx)
        rk_bg = "#2a1a00" if is_moon else "transparent"
        style = (
            "border:1px solid #333; padding:3px 0; text-align:center; "
            f"vertical-align:middle; font-size:10px; background:{rk_bg}; "
            f"color:{rk[3]};"
        )
        html += (
            f'<td style="{style}">'
            f'<span style="color:{rk[3]};font-weight:bold">{rk[0]}</span>'
            f'<br/><small>{rk[2]}</small>'
            f'</td>'
        )
    html += "</tr>"
    html += "</table>"

    # 說明
    html += (
        '<p style="text-align:center; color:#666; font-size:12px; margin-top:8px;">'
        "外圈：宿名 + 符號 + 中國星名 + 行星　"
        "中圈：主曜（七曜）　"
        "內圈：六曜"
        "</p>"
    )

    st.markdown(html, unsafe_allow_html=True)

    # 二十八宿分組（四象）
    st.markdown("### 四象二十八宿")
    cols = st.columns(4)
    groups = [
        ("🌿 東宮蒼龍", list(range(0, 7)),   "#228B22"),
        ("🌑 北宮玄武", list(range(7, 14)),  "#4169E1"),
        ("🌾 西宮白虎", list(range(14, 21)), "#DC143C"),
        ("🔥 南宮朱雀", list(range(21, 28)), "#FF8C00"),
    ]
    for ci, (name, indices, color) in enumerate(groups):
        with cols[ci]:
            items = []
            for i in indices:
                m = SUKKAYODO_MANSION[i]
                symbol, chinese = m[4], m[2]
                rk = get_rokuyo(i)
                is_moon = (i == moon_mansion_idx)
                star = "⭐" if is_moon else ""
                lord_color = GRAHA_COLORS.get(GRAHA_NAMES_BY_INDEX[m[3]], "#c8c8c8")
                items.append(
                    f"<b>{star}{symbol}</b> "
                    f'<span style="color:{lord_color}">{GRAHA_NAMES_BY_INDEX[m[3]]}</span> '
                    f'<span style="color:{rk[3]}">({rk[0]})</span>'
                )
            st.markdown(
                f'<div style="background:#1a1a2e; border:1px solid {color}; '
                f'border-radius:8px; padding:10px; color:#e0e0e0;">'
                f'<b style="color:{color}">{name}</b><br/>'
                f'<small>{"　".join(items)}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )
