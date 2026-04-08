"""
七政四餘排盤渲染模組 (Chart Renderer for Seven Governors and Four Remainders)

使用 Streamlit 元件渲染七政四餘排盤結果。
"""

import math

import streamlit as st

from .calculator import (
    ChartData, format_degree, get_mansion_for_degree, _normalize_degree,
)
from .constants import (
    PLANET_COLORS, TWELVE_PALACES, TWENTY_EIGHT_MANSIONS,
    TWELVE_SIGNS_CHINESE, EARTHLY_BRANCHES,
)


def render_chart_info(chart: ChartData):
    """渲染排盤基本資訊"""
    st.subheader("📋 排盤資訊")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期：** {chart.year}年{chart.month}月{chart.day}日")
        st.write(f"**時間：** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區：** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點：** {chart.location_name}")
        st.write(f"**經度：** {chart.longitude:.4f}°")
        st.write(f"**緯度：** {chart.latitude:.4f}°")


def render_planet_table(chart: ChartData):
    """渲染星曜位置表格"""
    st.subheader("⭐ 七政四餘星曜位置")

    # 七政
    st.markdown("#### 七政（日月五星）")
    _render_planet_group(chart.planets[:7])

    # 四餘
    st.markdown("#### 四餘（虛星）")
    _render_planet_group(chart.planets[7:])


def _render_planet_group(planets: list):
    """渲染一組星曜的表格"""
    header = "| 星曜 | 五行 | 黃經 | 星座 | 度數 | 星次 | 二十八宿 | 逆行 |"
    separator = "|:----:|:----:|:----:|:----:|:----:|:----:|:--------:|:----:|"
    rows = [header, separator]

    for p in planets:
        mansion = get_mansion_for_degree(p.longitude)
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_styled = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        rows.append(
            f"| {name_styled} | {p.element} | {format_degree(p.longitude)} "
            f"| {p.sign_western} | {p.sign_degree:.2f}° "
            f"| {p.sign_chinese} | {mansion['name']}({mansion['group']}) | {retro} |"
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def render_house_table(chart: ChartData):
    """渲染十二宮位表格"""
    st.subheader("🏛️ 十二宮位")

    header = "| 宮位 | 地支 | 宮頭度數 | 星座 | 星次 | 入宮星曜 |"
    separator = "|:----:|:----:|:--------:|:----:|:----:|:--------:|"
    rows = [header, separator]

    for house in chart.houses:
        planet_str = "、".join(house.planets) if house.planets else "—"
        rows.append(
            f"| {house.name} | {house.branch_name} "
            f"| {format_degree(house.cusp)} "
            f"| {house.sign_western} | {house.sign_chinese} | {planet_str} |"
        )

    st.markdown("\n".join(rows))


def render_chart_grid(chart: ChartData):
    """
    渲染方形排盤圖（傳統中國式方盤）

    以 4×4 格局呈現，外圈 12 格為十二宮位，中央 2×2 合併為命主資訊：

        巳宮  |  午宮  |  未宮  |  申宮
        ------+--------+--------+------
        辰宮  |                  |  酉宮
        ------+  (中央合併格)   +------
        卯宮  |                  |  戌宮
        ------+--------+--------+------
        寅宮  |  丑宮  |  子宮  |  亥宮

    十二宮名稱根據命宮地支和性別方向輪轉到對應的地支位置。
    """
    st.subheader("📊 七政四餘盤")

    # 建立 地支 → 宮位資料 的映射
    branch_data: dict[int, tuple[str, list, str]] = {}
    for house in chart.houses:
        planet_list = house.planets if house.planets else []
        branch_data[house.branch] = (house.name, planet_list, house.sign_western)

    # 方盤排列 (外圈12格，按固定地支位置排列)
    # 格子中的數字是地支索引: 子=0, 丑=1, 寅=2, ..., 亥=11
    grid_order = [
        [5, 6, 7, 8],          # 上排: 巳午未申
        [4, -1, -1, 9],        # 中上: 辰 [中央] 酉
        [3, -1, -1, 10],       # 中下: 卯 [中央] 戌
        [2, 1, 0, 11],         # 下排: 寅丑子亥
    ]

    # 使用 HTML/CSS 渲染方盤
    html = _build_grid_html(chart, branch_data, grid_order)
    st.html(html)


def _build_grid_html(
    chart: ChartData,
    branch_data: dict,
    grid_order: list,
) -> str:
    """建構排盤 HTML

    Parameters:
        chart: 排盤資料
        branch_data: 地支索引 → (宮名, 星曜列表, 西方星座) 映射
        grid_order: 4×4 格局，值為地支索引 (0-11)，-1 為中央
    """
    cell_style = (
        "border:1px solid #555; padding:6px; text-align:center; "
        "vertical-align:top; min-width:120px; font-size:13px; "
        "background:#1a1a2e; color:#e0e0e0;"
    )
    ming_cell_style = (
        "border:2px solid #d4af37; padding:6px; text-align:center; "
        "vertical-align:top; min-width:120px; font-size:13px; "
        "background:#2a2a1e; color:#e0e0e0;"
    )
    center_style = (
        "border:1px solid #666; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a3e; "
        "color:#e0e0e0;"
    )

    gender_label = "男命" if chart.gender == "male" else "女命"
    direction_label = "順時針" if chart.gender == "male" else "逆時針"

    html = (
        '<table style="border-collapse:collapse; margin:auto; width:100%; '
        'background:#1a1a2e; color:#e0e0e0;">'
    )

    for row_idx, row in enumerate(grid_order):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            branch_idx = row[col_idx]
            if branch_idx == -1:
                # 中央區域（只在第一次遇到時渲染）
                if row_idx == 1 and col_idx == 1:
                    branch_name = EARTHLY_BRANCHES[chart.ming_gong_branch]
                    center_content = (
                        f"<b>七政四餘排盤</b><br/>"
                        f"{chart.year}年{chart.month}月{chart.day}日<br/>"
                        f"{chart.hour:02d}:{chart.minute:02d} "
                        f"UTC{chart.timezone:+.1f}<br/>"
                        f"{chart.location_name} ({gender_label})<br/>"
                        f"命宮: {branch_name} ({direction_label})<br/>"
                        f"命度: {format_degree(chart.ascendant)}<br/>"
                        f"中天: {format_degree(chart.midheaven)}"
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
                is_ming = (branch_idx == chart.ming_gong_branch)
                style = ming_cell_style if is_ming else cell_style
                branch_label = EARTHLY_BRANCHES[branch_idx]
                if branch_idx in branch_data:
                    name, planets, sign = branch_data[branch_idx]
                    planets_html = ""
                    for p_name in planets:
                        color = PLANET_COLORS.get(p_name, "#c8c8c8")
                        planets_html += (
                            f'<span style="color:{color};font-weight:bold">'
                            f'{p_name}</span> '
                        )
                    if not planets_html:
                        planets_html = '<span style="color:#999">—</span>'
                    ming_mark = "【命】" if is_ming else ""
                    cell_content = (
                        f'<small style="color:#888">{branch_label}</small> '
                        f'<b>{name}</b>'
                        f'<span style="color:#d4af37">{ming_mark}</span>'
                        f"<br/>"
                        f'<small style="color:#888">{sign}</small><br/>'
                        f"{planets_html}"
                    )
                else:
                    cell_content = f'<small style="color:#888">{branch_label}</small>'
                html += f'<td style="{style}">{cell_content}</td>'
            col_idx += 1
        html += "</tr>"

    html += "</table>"
    return html


def render_aspect_summary(chart: ChartData):
    """渲染星曜相位摘要"""
    st.subheader("🔗 主要相位")

    aspects = _calculate_aspects(chart.planets)
    if not aspects:
        st.info("無顯著相位")
        return

    header = "| 星曜 1 | 相位 | 星曜 2 | 角距 |"
    separator = "|:------:|:----:|:------:|:----:|"
    rows = [header, separator]

    for a in aspects:
        rows.append(
            f"| {a['planet1']} | {a['aspect_name']} | {a['planet2']} "
            f"| {a['orb']:.1f}° |"
        )

    st.markdown("\n".join(rows))


def _calculate_aspects(planets: list) -> list:
    """計算星曜之間的主要相位"""
    aspect_types = [
        {"name": "合(0°)", "angle": 0, "orb": 8},
        {"name": "沖(180°)", "angle": 180, "orb": 8},
        {"name": "刑(90°)", "angle": 90, "orb": 6},
        {"name": "三合(120°)", "angle": 120, "orb": 6},
        {"name": "六合(60°)", "angle": 60, "orb": 4},
    ]

    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1 = planets[i]
            p2 = planets[j]
            diff = abs(p1.longitude - p2.longitude)
            if diff > 180:
                diff = 360 - diff

            for asp in aspect_types:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    aspects.append({
                        "planet1": p1.name,
                        "planet2": p2.name,
                        "aspect_name": asp["name"],
                        "orb": orb,
                    })
                    break

    return aspects


# ============================================================
# 二十八宿圓環圖 (28 Lunar Mansions Ring Chart)
# ============================================================

# 四象顏色 (Four Symbols / Directional Colors)
_GROUP_COLORS = {
    "東方青龍": ("#1a3a1a", "#4caf50"),   # (background, text/border) green
    "北方玄武": ("#1a1a3a", "#5c6bc0"),   # blue/indigo
    "西方白虎": ("#3a3a1a", "#e0e0e0"),   # white/light
    "南方朱雀": ("#3a1a1a", "#ef5350"),   # red
}

# 四象標記
_GROUP_SYMBOLS = {
    "東方青龍": "🐉",
    "北方玄武": "🐢",
    "西方白虎": "🐅",
    "南方朱雀": "🐦",
}


def render_mansion_ring(chart: ChartData):
    """渲染二十八宿圓環圖 — 以 SVG 圓盤呈現 28 宿 + 十二星次 + 星曜位置"""
    st.subheader("🌕 二十八宿圓環盤")

    SIZE = 700
    CX, CY = SIZE / 2, SIZE / 2

    # 同心圓半徑
    R_OUTER = 310        # 最外圈
    R_MANSION_OUT = 310  # 28 宿環外沿
    R_MANSION_IN = 265   # 28 宿環內沿
    R_SIGN_OUT = 265     # 十二星次環外沿
    R_SIGN_IN = 235      # 十二星次環內沿
    R_PALACE_OUT = 235   # 十二宮名環外沿
    R_PALACE_IN = 200    # 十二宮名環內沿
    R_PLANET = 170       # 星曜環
    R_CENTER = 100       # 中央圓

    NUM_MANSIONS = len(TWENTY_EIGHT_MANSIONS)
    PLANET_SPREAD_FACTOR = 0.7  # 同宿多星的散佈範圍比例

    def _mansion_width(i):
        """Return angular width of mansion i in degrees."""
        s = TWENTY_EIGHT_MANSIONS[i]["start_lon"]
        e = TWENTY_EIGHT_MANSIONS[(i + 1) % NUM_MANSIONS]["start_lon"]
        return (e - s) % 360.0

    def _mansion_chart_start(i):
        """Return chart-angle of the start edge for mansion i."""
        e = TWENTY_EIGHT_MANSIONS[(i + 1) % NUM_MANSIONS]["start_lon"]
        return ecl_to_chart(e)

    def polar(r, angle_deg):
        rad = math.radians(angle_deg)
        return CX + r * math.cos(rad), CY + r * math.sin(rad)

    def annular_sector(r_in, r_out, a1, a2):
        """SVG path for an annular sector (donut slice)."""
        a1r, a2r = math.radians(a1), math.radians(a2)
        x1o = CX + r_out * math.cos(a1r)
        y1o = CY + r_out * math.sin(a1r)
        x2o = CX + r_out * math.cos(a2r)
        y2o = CY + r_out * math.sin(a2r)
        x1i = CX + r_in * math.cos(a2r)
        y1i = CY + r_in * math.sin(a2r)
        x2i = CX + r_in * math.cos(a1r)
        y2i = CY + r_in * math.sin(a1r)
        sweep = a2 - a1
        large = 1 if sweep > 180 else 0
        return (
            f"M {x1o:.1f},{y1o:.1f} "
            f"A {r_out},{r_out} 0 {large},1 {x2o:.1f},{y2o:.1f} "
            f"L {x1i:.1f},{y1i:.1f} "
            f"A {r_in},{r_in} 0 {large},0 {x2i:.1f},{y2i:.1f} Z"
        )

    def ecl_to_chart(ecl_deg):
        """Convert ecliptic longitude to SVG chart angle.

        Positions earthly branches at traditional compass directions:
        午(South) at top, 子(North) at bottom, 卯(East) at left, 酉(West) at right.
        Branches increase clockwise around the chart.
        """
        return (45.0 - ecl_deg) % 360.0

    def text_rotation(a):
        rot = (a + 90) % 360
        if 90 < rot < 270:
            rot = (rot + 180) % 360
        return rot

    svg = []
    svg.append(
        f'<svg viewBox="0 0 {SIZE} {SIZE}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%; max-width:700px; height:auto; margin:auto; '
        f'display:block; background:#0a0a1a; border-radius:12px;">'
    )
    svg.append(f'<rect width="{SIZE}" height="{SIZE}" fill="#0a0a1a" rx="12"/>')

    # --- 28 宿環 (outermost ring) ---
    for i, m in enumerate(TWENTY_EIGHT_MANSIONS):
        w = _mansion_width(i)
        a1 = _mansion_chart_start(i)
        a2 = a1 + w
        bg, fg = _GROUP_COLORS[m["group"]]
        # Background sector
        svg.append(
            f'<path d="{annular_sector(R_MANSION_IN, R_MANSION_OUT, a1, a2)}" '
            f'fill="{bg}" stroke="#555" stroke-width="0.5"/>'
        )
        # Mansion name
        mid_a = a1 + w / 2
        r_text = (R_MANSION_IN + R_MANSION_OUT) / 2
        x, y = polar(r_text, mid_a)
        rot = text_rotation(mid_a)
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{fg}" '
            f'font-size="12" font-weight="bold" font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{m["name"]}</text>'
        )

    # --- 四象標記 (group labels at four corners) ---
    # Compute ecliptic center for each group using actual mansion boundaries
    group_chart_angles: dict[str, list[float]] = {}
    for i, m in enumerate(TWENTY_EIGHT_MANSIONS):
        w = _mansion_width(i)
        mid = _mansion_chart_start(i) + w / 2
        group_chart_angles.setdefault(m["group"], []).append(mid)

    for grp, angles in group_chart_angles.items():
        center_a = sum(angles) / len(angles)
        _, fg = _GROUP_COLORS[grp]
        x, y = polar(R_OUTER + 16, center_a)
        symbol = _GROUP_SYMBOLS[grp]
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="16">'
            f'{symbol}</text>'
        )

    # --- 十二星次環 (12 Chinese zodiac stations ring) ---
    for i in range(12):
        a1 = ecl_to_chart((i + 1) * 30.0)
        a2 = a1 + 30.0
        # Thin background
        svg.append(
            f'<path d="{annular_sector(R_SIGN_IN, R_SIGN_OUT, a1, a2)}" '
            f'fill="#111122" stroke="#444" stroke-width="0.5"/>'
        )
        # Sign name (short form)
        mid_a = a1 + 15.0
        r_text = (R_SIGN_IN + R_SIGN_OUT) / 2
        x, y = polar(r_text, mid_a)
        rot = text_rotation(mid_a)
        sign_name = TWELVE_SIGNS_CHINESE[i]
        # Use the palace name part (e.g. "戌宮")
        short_name = sign_name.split("(")[0] if "(" in sign_name else sign_name
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#b0b0d0" '
            f'font-size="13" font-weight="bold" font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{short_name}</text>'
        )

    # --- 十二宮名環 (12 Palace Names ring) ---
    # Build branch → palace name mapping from chart houses
    branch_to_palace: dict[int, str] = {}
    for house in chart.houses:
        branch_to_palace[house.branch] = house.name

    for i in range(12):
        a1 = ecl_to_chart((i + 1) * 30.0)
        a2 = a1 + 30.0
        # Determine which earthly branch this segment corresponds to
        branch_idx = (10 - i) % 12
        is_ming = (branch_idx == chart.ming_gong_branch)
        # Background sector
        bg_fill = "#2a2a1e" if is_ming else "#0f0f22"
        stroke_col = "#d4af37" if is_ming else "#444"
        stroke_w = "1" if is_ming else "0.5"
        svg.append(
            f'<path d="{annular_sector(R_PALACE_IN, R_PALACE_OUT, a1, a2)}" '
            f'fill="{bg_fill}" stroke="{stroke_col}" stroke-width="{stroke_w}"/>'
        )
        # Palace name text
        mid_a = a1 + 15.0
        r_text = (R_PALACE_IN + R_PALACE_OUT) / 2
        x, y = polar(r_text, mid_a)
        rot = text_rotation(mid_a)
        palace_name = branch_to_palace.get(branch_idx, "")
        # Short palace name (remove 宮 suffix for compactness)
        short_palace = palace_name.replace("宮", "") if palace_name else ""
        text_color = "#d4af37" if is_ming else "#c8b888"
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{text_color}" '
            f'font-size="11" font-weight="bold" font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{short_palace}</text>'
        )

    # --- Division lines for 12 signs (from center to mansion ring) ---
    for i in range(12):
        a = ecl_to_chart(i * 30.0)
        x1, y1 = polar(R_CENTER, a)
        x2, y2 = polar(R_MANSION_OUT, a)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#555" stroke-width="0.8"/>'
        )

    # --- 28 宿分界線 (from sign ring inner to mansion ring outer) ---
    for i in range(28):
        a = ecl_to_chart(TWENTY_EIGHT_MANSIONS[i]["start_lon"])
        x1, y1 = polar(R_MANSION_IN, a)
        x2, y2 = polar(R_MANSION_OUT, a)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#555" stroke-width="0.5"/>'
        )

    # --- Inner circles ---
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTER}" '
        f'fill="#1a1a2e" stroke="#555" stroke-width="1"/>'
    )

    # --- 星曜位置 (planet positions in the planet ring) ---
    # Helper: find mansion index for a given ecliptic longitude
    def _find_mansion_idx(lon_deg):
        lon_deg = _normalize_degree(lon_deg)
        for i in range(NUM_MANSIONS):
            s = TWENTY_EIGHT_MANSIONS[i]["start_lon"]
            e = TWENTY_EIGHT_MANSIONS[(i + 1) % NUM_MANSIONS]["start_lon"]
            if s < e:
                if s <= lon_deg < e:
                    return i
            else:
                if lon_deg >= s or lon_deg < e:
                    return i
        return 0

    # Group planets by mansion to handle overlaps
    mansion_planets: dict[int, list] = {}
    for p in chart.planets:
        lon = _normalize_degree(p.longitude)
        mansion_idx = _find_mansion_idx(lon)
        if mansion_idx not in mansion_planets:
            mansion_planets[mansion_idx] = []
        mansion_planets[mansion_idx].append((p, lon))

    for mansion_idx, planet_data in mansion_planets.items():
        n = len(planet_data)
        w = _mansion_width(mansion_idx)
        # Mansion sector in chart space
        a1_chart = _mansion_chart_start(mansion_idx)
        base_a = a1_chart + w / 2
        for pi, (p, lon) in enumerate(planet_data):
            # Single planet: use exact longitude; multiple: spread within mansion
            if n == 1:
                a = ecl_to_chart(lon)
            else:
                span = w * PLANET_SPREAD_FACTOR
                a = base_a - span / 2 + span * pi / (n - 1)

            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            x, y = polar(R_PLANET, a)

            # Planet dot
            svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                f'fill="{color}" stroke="#fff" stroke-width="0.5"/>'
            )
            # Planet name
            x_t, y_t = polar(R_PLANET - 20, a)
            rot = text_rotation(a)
            retro = "℞" if p.retrograde else ""
            svg.append(
                f'<text x="{x_t:.1f}" y="{y_t:.1f}" text-anchor="middle" '
                f'dominant-baseline="central" fill="{color}" '
                f'font-size="11" font-weight="bold" font-family="serif" '
                f'transform="rotate({rot:.1f},{x_t:.1f},{y_t:.1f})">'
                f'{p.name}{retro}</text>'
            )

    # --- 中央資訊 (center info) ---
    svg.append(
        f'<text x="{CX}" y="{CY - 40}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#e0e0e0" '
        f'font-size="15" font-weight="bold" font-family="serif">'
        f'七政四餘</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 18}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#b0b0b0" '
        f'font-size="12" font-family="serif">'
        f'{chart.year}年{chart.month}月{chart.day}日</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 2}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#b0b0b0" '
        f'font-size="12" font-family="serif">'
        f'{chart.hour:02d}:{chart.minute:02d} '
        f'UTC{chart.timezone:+.1f}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 22}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#b0b0b0" '
        f'font-size="12" font-family="serif">'
        f'{chart.location_name}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 44}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#d4af37" '
        f'font-size="11" font-family="serif">'
        f'命度 {format_degree(chart.ascendant)}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 62}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#7ec8e3" '
        f'font-size="11" font-family="serif">'
        f'中天 {format_degree(chart.midheaven)}</text>'
    )

    svg.append("</svg>")

    st.markdown("\n".join(svg), unsafe_allow_html=True)

    # Legend
    legend_cols = st.columns(4)
    for i, (grp, (_, fg)) in enumerate(_GROUP_COLORS.items()):
        with legend_cols[i]:
            symbol = _GROUP_SYMBOLS[grp]
            st.markdown(
                f'<span style="color:{fg};font-weight:bold">'
                f'{symbol} {grp}</span>',
                unsafe_allow_html=True,
            )
