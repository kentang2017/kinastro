"""
七政四餘排盤渲染模組 (Chart Renderer for Seven Governors and Four Remainders)

使用 Streamlit 元件渲染七政四餘排盤結果。
"""

import streamlit as st

from .calculator import ChartData, format_degree, get_mansion_for_degree
from .constants import PLANET_COLORS, TWELVE_PALACES


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
        color = PLANET_COLORS.get(p.name, "#000000")
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

    header = "| 宮位 | 宮頭度數 | 星座 | 星次 | 入宮星曜 |"
    separator = "|:----:|:--------:|:----:|:----:|:--------:|"
    rows = [header, separator]

    for house in chart.houses:
        planet_str = "、".join(house.planets) if house.planets else "—"
        rows.append(
            f"| {house.name} | {format_degree(house.cusp)} "
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
    """
    st.subheader("📊 七政四餘盤")

    # 傳統方盤的宮位排列（按照中國傳統方盤的順序）
    # 宮位索引對應: 命宮(0)在寅位開始按逆時針排列
    # 這裡按照十二地支排列宮位

    # 建立宮位到星曜的映射
    house_planets = {}
    for house in chart.houses:
        planet_list = house.planets if house.planets else []
        house_planets[house.index] = (house.name, planet_list, house.sign_western)

    # 方盤排列 (外圈12格，按傳統排列)
    # 格子位置: [top row] [left col] [right col] [bottom row]
    grid_order = [
        [5, 4, 3, 2],          # 上排: 巳午未申
        [6, -1, -1, 1],        # 中上: 辰 [中央] 酉
        [7, -1, -1, 0],        # 中下: 卯 [中央] 戌 (命宮位置調整)
        [8, 9, 10, 11],        # 下排: 寅丑子亥
    ]

    # 使用 HTML/CSS 渲染方盤
    html = _build_grid_html(chart, house_planets, grid_order)
    st.markdown(html, unsafe_allow_html=True)


def _build_grid_html(
    chart: ChartData,
    house_planets: dict,
    grid_order: list,
) -> str:
    """建構排盤 HTML"""
    cell_style = (
        "border:1px solid #666; padding:6px; text-align:center; "
        "vertical-align:top; min-width:120px; font-size:13px;"
    )
    center_style = (
        "border:1px solid #555; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a2a;"
    )

    html = '<table style="border-collapse:collapse; margin:auto; width:100%;">'

    for row_idx, row in enumerate(grid_order):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                # 中央區域（只在第一次遇到時渲染）
                if row_idx == 1 and col_idx == 1:
                    center_content = (
                        f"<b>七政四餘排盤</b><br/>"
                        f"{chart.year}年{chart.month}月{chart.day}日<br/>"
                        f"{chart.hour:02d}:{chart.minute:02d} "
                        f"UTC{chart.timezone:+.1f}<br/>"
                        f"{chart.location_name}<br/>"
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
                if idx in house_planets:
                    name, planets, sign = house_planets[idx]
                    planets_html = ""
                    for p_name in planets:
                        color = PLANET_COLORS.get(p_name, "#000000")
                        planets_html += (
                            f'<span style="color:{color};font-weight:bold">'
                            f'{p_name}</span> '
                        )
                    if not planets_html:
                        planets_html = '<span style="color:#999">—</span>'
                    cell_content = (
                        f"<b>{name}</b><br/>"
                        f'<small style="color:#888">{sign}</small><br/>'
                        f"{planets_html}"
                    )
                else:
                    cell_content = ""
                html += f'<td style="{cell_style}">{cell_content}</td>'
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
