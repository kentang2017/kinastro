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
    ("Ashwini",          "アシュヴィニ", "馬頭",  0, "馬", "Aswini Twins",    "Cheerful"),
    ("Bharani",          "バラニ",       "大陵",  1, "彡", "Yami",             "Passionate"),
    ("Krittika",         "クリティカー", "昴宿",  2, "卍", "Agni",             "Fierce"),
    ("Rohini",           "ロヒニー",     "畢宿",  3, "兔", "Brahma",           "Stable"),
    ("Mrigashira",       "ミルガシラ",   "觜宿",  4, "蚯", "Soma",             "Curious"),
    ("Ardra",            "アルドラ",     "參宿",  5, "獅子","Rudra",            "Restless"),
    ("Punarvasu",        "プナルヴァス", "井宿",  6, "福", "Aditi",            "Renewing"),
    ("Pushya",           "プシュヤ",     "鬼宿",  7, "邪", "Brihaspati",       "Nurturing"),
    ("Ashlesha",         "アシュレーシャ","柳宿", 8, "毒", "Naga",              "Seductive"),
    ("Magha",            "マガ",         "星宿",  0, "慢", "Pitris",           "Regal"),
    ("Purva Phalguni",   "プールヴァ・팔구니","張宿",1, "栄", "Bhaga",           "Loving"),
    ("Uttara Phalguni",  "ウッター・팔구니","翼宿", 2, "双", "Aryaman",          "Dutiful"),
    ("Hasta",            "ハスタ",       "軫宿",  3, "智", "Savitri",          "Skillful"),
    ("Chitra",           "チトラ",       "角宿",  4, "勝", "Tvashtar",         "Radiant"),
    ("Swati",            "スヴァティ",   "亢宿",  5, "撃", "Vayu",             "Independent"),
    ("Vishakha",         "ヴィシャーカー", "氐宿", 6, "力", "Indra/Agni",       "Multi-faceted"),
    ("Anuradha",         "アヌラーダー", "房宿",  7, "喜", "Mitra",            "Balanced"),
    ("Jyeshtha",         "ジェーシタ",   "心宿",  8, "主", "Indra",            "Protective"),
    ("Mula",             "ムーラ",       "尾宿",  0, "死", "Nirriti",          "Deep"),
    ("Purva Ashadha",    "プールヴァ・アシャダー","箕宿",1,"満","Apah",            "Victorious"),
    ("Uttara Ashadha",   "ウッター・アシャダー","斗宿",2,"生","Vishwa Devas",     "Truthful"),
    ("Abhijit",          "アビジート",   "牛宿",  2, "織", "Brahma/Vega",      "Noble"),
    ("Shravana",         "シュラヴァナ", "女宿",  3, "虚", "Vishnu",           "Devoted"),
    ("Dhanishta",        "ダニスター",   "虛宿",  4, "危", "Vasudev",          "Wealthy"),
    ("Shatabhisha",      "シャタビシャ", "危宿",  5, "命", "Varuna",           "Mysterious"),
    ("Purva Bhadrapada", "プールヴァ・巴拉德拉帕ダ","室宿",6,"留","Aja Ekapada",    "Heroic"),
    ("Uttara Bhadrapada","ウッター・巴拉德拉帕ダ","壁宿",7,"堅","Ahir Budhya",     "Serene"),
    ("Revati",           "レヴァティー", "奎宿",  8, "開", "Pushan",           "Nurturing"),
]

# 六曜 (Rokuyō)
# 順序：先勝 → 友引 → 先負 → 仏滅 → 大安 → 赤口
ROKUYO = [
    ("先勝",   "Senshō",   "吉(速)", "#228B22"),
    ("友引",   "Tomoyuki", "小吉",   "#4169E1"),
    ("先負",   "Senku",    "末吉",   "#8B4513"),
    ("仏滅",   "Butsumetsu","凶",    "#DC143C"),
    ("大安",   "Taian",    "大吉",   "#FFD700"),
    ("赤口",   "Shakuchō", "凶(吉)", "#FF4500"),
]

# 每宿對應的六曜索引（循環分配）
SUKKAYODO_NAKSHATRA_ROKUYO_MAP = [
    # 宿序 1-28 → 六曜索引
    0, 1, 2, 3, 4, 5,   # Ashwini → Ardra
    0, 1, 2, 3, 4, 5,   # Punarvasu → Uttara Phalguni
    0, 1, 2, 3, 4, 5,   # Hasta → Mula
    0, 1, 2, 3, 4, 5,   # Purva Ashadha → Dhanishta
    0, 1, 2, 3,         # Shatabhisha → Revati
]

PLANET_COLORS = {
    "Surya (太陽)": "#FF8C00",
    "Chandra (月亮)": "#C0C0C0",
    "Mangal (火星)": "#DC143C",
    "Budha (水星)": "#4169E1",
    "Guru (木星)": "#FFD700",
    "Shukra (金星)": "#FF69B4",
    "Shani (土星)": "#8B4513",
    "Rahu (羅睺)": "#800080",
    "Ketu (計都)": "#4B0082",
}


# ============================================================
# 計算函數
# ============================================================

def _normalize(deg):
    return deg % 360.0


def sukkayodo_info(deg):
    """Return (sukkayodo_mansion_index, pada) for sidereal longitude.

    宿曜道 28 宿，每宿 12°51'26"（360°/28）。
    Abhijit（牛宿）位於 Uttara Ashadha 與 Shravana 之间，約 4°10'；
    為計算便利，Abhijit 視為獨立宿，與其餘 27 宿均分 12°51'26"。
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
    rk_idx = SUKKAYODO_NAKSHATRA_ROKUYO_MAP[mansion_index % 28]
    return ROKUYO[rk_idx]


# ============================================================
# 渲染函數
# ============================================================

def render_sukkayodo_chart(chart):
    """渲染日本宿曜道排盤"""
    st.subheader("🈳 日本宿曜道 (Yojōdō 二十八宿)")

    st.markdown(
        "**宿曜道**由空海大師於 9 世紀自印度傳入日本，以 **Moon 所在宿** 計算"
        "**六曜 (Rokuyō)**：先勝・友引・先負・仏滅・大安・赤口。"
    )

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
        bg = color if active else "#f0f0f0"
        fg = "#fff" if active else "#333"
        style = (
            f"background:{bg}; color:{fg}; padding:10px; "
            f"border-radius:8px; text-align:center;"
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
            f" ・ {moon_planet.sukkayodo_pada}足"
        )

    # 28 宿列表
    st.markdown("### 二十八宿 (28 Mansions)")
    rows = [
        "| # | 宿名 | 日名 | 中國 | 符 | 主曜 | 象徵 | 吉凶 |",
        "|:--:|:-----|:-----|:-----|:--:|:-----|:-----|:----:|",
    ]
    for i, m in enumerate(SUKKAYODO_MANSION):
        nak_name, jp_name, chinese, lord_idx = m[0], m[1], m[2], m[3]
        symbol, deity, quality = m[4], m[5], m[6]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        lord_color = PLANET_COLORS.get(lord_name, "#000000")
        is_moon = (i == moon_mansion_idx)
        rk = get_rokuyo(i)
        rows.append(
            f"| {'⭐' if is_moon else ''}{i+1} | "
            f'<b>{"⭐" if is_moon else ""}{nak_name}</b> | '
            f'{jp_name} | {chinese} | {symbol} | '
            f'<span style="color:{lord_color}">{lord_name}</span> | '
            f'<span style="color:{rk[3]}">{rk[0]}</span> |'
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # 行星宿曜道位置
    st.markdown("### 行星宿曜道位置")
    rows2 = [
        "| Graha | 宿名 Mansion | 中國星名 | Pada |",
        "|:-----:|:------------|:---------|:-----:|",
    ]
    for p in chart.planets:
        if p.sukkayodo_mansion_index >= 0:
            m = SUKKAYODO_MANSION[p.sukkayodo_mansion_index]
            color = PLANET_COLORS.get(p.name, "#000000")
            rows2.append(
                f"| <span style='color:{color}'>{p.name}</span> | "
                f"**{p.sukkayodo_mansion}** ({m[1]}) | "
                f"{p.sukkayodo_mansion_chinese} | {p.sukkayodo_pada} |"
            )
    st.markdown("\n".join(rows2), unsafe_allow_html=True)

    # 方盤
    st.markdown("### 宿曜道方盤")
    cell_style = (
        "border:1px solid #ccc; padding:4px 2px; text-align:center; "
        "vertical-align:top; font-size:11px;"
    )
    moon_cell_style = cell_style + " background:#fffde7; font-weight:bold;"

    mansion_planets = {i: [] for i in range(28)}
    for p in chart.planets:
        if p.sukkayodo_mansion_index >= 0:
            mansion_planets[p.sukkayodo_mansion_index].append(p.name.split(" ")[0])

    html = '<table style="border-collapse:collapse; margin:auto; width:100%; max-width:700px;">'
    for row in range(4):
        html += "<tr>"
        for col in range(7):
            idx = row * 7 + col
            if idx >= 28:
                html += "<td></td>"
                continue
            m = SUKKAYODO_MANSION[idx]
            nak_name, jp_name, chinese = m[0], m[1], m[2]
            symbol = m[4]
            is_moon = (idx == moon_mansion_idx)
            style = moon_cell_style if is_moon else cell_style
            p_list = mansion_planets[idx]
            p_html = "".join(
                f'<span style="color:{PLANET_COLORS.get(p, "#000")}">{p}</span> '
                for p in p_list
            ) if p_list else ""
            rk = get_rokuyo(idx)
            html += (
                f'<td style="{style}">'
                f'<b>{"⭐" if is_moon else ""}{nak_name[:3]}</b>'
                f'<br/><small>{jp_name[:4]}</small>'
                f'<br/>{symbol} {chinese}'
                f'<br/>{p_html}'
                f'<br/><small style="color:{rk[3]}">{rk[0]}</small>'
                f'</td>'
            )
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
