"""
astro/enochian/visualization.py — Enochian 占星 SVG 視覺化模組

提供三個主要視覺化：
  1. render_sigillum_svg()    — Sigillum Dei Aemeth（神之印）圓形魔法圖
  2. render_watchtower_svg()  — 四個守望塔的 2×2 網格示意圖
  3. render_aethyr_svg()      — 30 個以太層的層級示意圖（含高亮顯示）

設計原則：
  - 所有函式均為純函式，無 Streamlit 依賴
  - 輸出為 SVG 字串，可嵌入任何 HTML/Streamlit 元件
  - 支援個人化高亮（根據命盤中激活的元素）
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from .calculator import EnochianChart, EnochianPlanetPoint
from .constants import (
    AETHYRS,
    WATCHTOWERS,
    SIGILLUM_DEI_AEMETH,
    ELEMENT_TABLE,
    ENOCHIAN_PLANETS,
)

# ============================================================
# 顏色常數
# ============================================================

_COLORS = {
    "background":     "#0a0a1e",   # 深藍黑背景
    "gold":           "#FFD700",   # 金色（神聖）
    "silver":         "#C0C0C0",   # 銀色（月亮）
    "fire_red":       "#FF4500",   # 火焰紅
    "water_blue":     "#4169E1",   # 深藍（水）
    "air_sky":        "#87CEEB",   # 天藍（風）
    "earth_brown":    "#8B4513",   # 深棕（土）
    "spirit_violet":  "#8B5CF6",   # 紫羅蘭（靈）
    "text_light":     "#E8E0D0",   # 淺色文字
    "text_dim":       "#8080A0",   # 淡色文字
    "active_glow":    "#FFD70080", # 半透明金色
}

# 元素顏色對應
_ELEMENT_COLORS = {
    "Fire":   "#FF4500",
    "Water":  "#4169E1",
    "Air":    "#87CEEB",
    "Earth":  "#8B4513",
    "Spirit": "#8B5CF6",
}

# ============================================================
# 1. Sigillum Dei Aemeth SVG
# ============================================================

def render_sigillum_svg(
    chart: Optional[EnochianChart] = None,
    size: int = 500,
    show_labels: bool = True,
) -> str:
    """
    繪製 Sigillum Dei Aemeth（神之印）風格的圓形魔法圖。

    Args:
        chart: EnochianChart 物件（用於個人化高亮），若 None 則繪製通用圖
        size:  SVG 尺寸（像素）
        show_labels: 是否顯示天使名稱標籤

    Returns:
        str: SVG 字串
    """
    cx = size / 2
    cy = size / 2
    r = size * 0.44  # 外圓半徑

    # 確定激活的天使（如有命盤資料）
    active_angels: set = set()
    if chart:
        active_angels.update(chart.sigillum_active_angels)
        active_angels.add(chart.patron_angel.name)
        active_angels.add(chart.matron_angel.name)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">',

        # 背景
        f'<rect width="{size}" height="{size}" fill="{_COLORS["background"]}"/>',

        # 外圓輝光效果
        f'<defs>',
        f'  <radialGradient id="outerGlow" cx="50%" cy="50%" r="50%">',
        f'    <stop offset="0%" stop-color="#1a1a40"/>',
        f'    <stop offset="100%" stop-color="#0a0a1e"/>',
        f'  </radialGradient>',
        f'  <filter id="glow">',
        f'    <feGaussianBlur stdDeviation="3" result="blur"/>',
        f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        f'  </filter>',
        f'  <filter id="softGlow">',
        f'    <feGaussianBlur stdDeviation="6" result="blur"/>',
        f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        f'  </filter>',
        f'</defs>',

        # 背景輝光圓
        f'<circle cx="{cx}" cy="{cy}" r="{r * 1.1}" fill="url(#outerGlow)"/>',
    ]

    # ── 同心圓 (4 圈) ──────────────────────────────────────────
    for i, ring_r in enumerate([r, r * 0.78, r * 0.58, r * 0.38]):
        ring_color = SIGILLUM_DEI_AEMETH["ring_colors"][i % 7]
        opacity = 0.6 + i * 0.1
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="{ring_r}" '
            f'fill="none" stroke="{ring_color}" '
            f'stroke-width="{1.5}" opacity="{opacity}"/>'
        )

    # ── 七芒星 (Heptagram) ────────────────────────────────────
    seven_angels = SIGILLUM_DEI_AEMETH["seven_angels"]
    hept_r = r * 0.68
    hept_points = []
    for i in range(7):
        angle = math.radians(-90 + i * 360 / 7)
        px = cx + hept_r * math.cos(angle)
        py = cy + hept_r * math.sin(angle)
        hept_points.append((px, py))

    # 七芒星連線（每個頂點連接隔2個）
    hept_path_pts = []
    for i in range(7):
        hept_path_pts.append(hept_points[i])
        hept_path_pts.append(hept_points[(i * 2) % 7])
    # 繪製七芒星各邊
    star_path = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in hept_points)
    # 重新繪製為兩個交錯三角形
    for step in range(1, 4):
        star_pts = []
        for i in range(7):
            star_pts.append(hept_points[(i * step) % 7])
        pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in star_pts)
        lines.append(
            f'<polygon points="{pts_str}" '
            f'fill="none" stroke="{_COLORS["gold"]}" '
            f'stroke-width="1" opacity="0.4"/>'
        )

    # ── 五芒星 (Pentagram) ──────────────────────────────────────
    pent_r = r * 0.42
    pent_points = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        px = cx + pent_r * math.cos(angle)
        py = cy + pent_r * math.sin(angle)
        pent_points.append((px, py))

    # 五芒星線條（每個頂點連接隔1個）
    pent_star = [pent_points[i % 5] for i in [0, 2, 4, 1, 3, 0]]
    pent_d = " ".join(f"{'M' if i == 0 else 'L'}{p[0]:.1f},{p[1]:.1f}" for i, p in enumerate(pent_star))
    lines.append(
        f'<path d="{pent_d} Z" fill="none" stroke="{_COLORS["spirit_violet"]}" '
        f'stroke-width="1.5" opacity="0.6"/>'
    )

    # 五芒星頂點字母（BOLAN）
    pent_letters = SIGILLUM_DEI_AEMETH["pentagram_letters"]
    for i, (px, py) in enumerate(pent_points):
        letter = pent_letters[i] if i < len(pent_letters) else ""
        lines.append(
            f'<text x="{px:.1f}" y="{py + 4:.1f}" '
            f'text-anchor="middle" font-size="12" '
            f'fill="{_COLORS["spirit_violet"]}" font-family="serif" opacity="0.8">'
            f'{letter}</text>'
        )

    # ── 七個天使節點和名稱 ──────────────────────────────────────
    for i, (px, py) in enumerate(hept_points):
        angel = seven_angels[i]
        is_active = angel in active_angels
        node_color = _COLORS["gold"] if is_active else "#807050"
        ring_color = SIGILLUM_DEI_AEMETH["ring_colors"][i % 7]
        glow_filter = 'filter="url(#glow)"' if is_active else ""

        # 天使節點圓
        radius = 14 if is_active else 10
        lines.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{radius}" '
            f'fill="{_COLORS["background"]}" stroke="{ring_color}" '
            f'stroke-width="2" {glow_filter} opacity="{1.0 if is_active else 0.6}"/>'
        )
        if is_active:
            # 激活光暈
            lines.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{radius + 6}" '
                f'fill="none" stroke="{node_color}" stroke-width="1" opacity="0.3"/>'
            )

        if show_labels:
            # 天使名稱（外側）
            label_r = hept_r + r * 0.15
            label_angle = math.radians(-90 + i * 360 / 7)
            lx = cx + label_r * math.cos(label_angle)
            ly = cy + label_r * math.sin(label_angle)
            font_size = 10 if not is_active else 11
            text_color = node_color if is_active else _COLORS["text_dim"]
            lines.append(
                f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" '
                f'font-size="{font_size}" fill="{text_color}" font-family="serif">'
                f'{angel}</text>'
            )

    # ── 中心神名 AGLA ────────────────────────────────────────────
    lines.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.15}" '
        f'fill="{_COLORS["background"]}" stroke="{_COLORS["gold"]}" '
        f'stroke-width="2" filter="url(#softGlow)"/>'
    )
    lines.append(
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" '
        f'font-size="14" fill="{_COLORS["gold"]}" font-family="serif" font-weight="bold">'
        f'{SIGILLUM_DEI_AEMETH["center_name"]}</text>'
    )

    # ── 個人 Aethyr 標示（如有命盤） ──────────────────────────────
    if chart:
        aethyr_label = chart.primary_aethyr.name
        lines.append(
            f'<text x="{cx}" y="{size - 20}" text-anchor="middle" '
            f'font-size="11" fill="{_COLORS["gold"]}" font-family="serif" opacity="0.7">'
            f'Primary Aethyr: {aethyr_label}</text>'
        )

    # ── 標題 ────────────────────────────────────────────────────
    lines.append(
        f'<text x="{cx}" y="20" text-anchor="middle" '
        f'font-size="12" fill="{_COLORS["text_dim"]}" font-family="serif">'
        f'Sigillum Dei Aemeth</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


# ============================================================
# 2. Watchtower Grid SVG
# ============================================================

def render_watchtower_svg(
    chart: Optional[EnochianChart] = None,
    size: int = 480,
) -> str:
    """
    繪製四個守望塔的 2×2 網格示意圖。

    每個格子顯示：方向、元素、守護天使、對應黃道星座。
    若提供命盤，則高亮顯示激活的守望塔。

    Args:
        chart: EnochianChart 物件（用於個人化高亮）
        size:  SVG 尺寸

    Returns:
        str: SVG 字串
    """
    cell_w = size / 2
    cell_h = size / 2

    # 確定各守望塔強度
    wt_scores: Dict[str, float] = {}
    if chart:
        wt_scores = chart.watchtower_scores

    # 守望塔佈局：東→右上，西→左上，北→左下，南→右下
    layout = [
        ("West",  0,        0),
        ("East",  cell_w,   0),
        ("North", 0,        cell_h),
        ("South", cell_w,   cell_h),
    ]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="{_COLORS["background"]}"/>',
        # 中心十字
        f'<line x1="{size/2}" y1="0" x2="{size/2}" y2="{size}" '
        f'stroke="{_COLORS["gold"]}" stroke-width="1.5" opacity="0.5"/>',
        f'<line x1="0" y1="{size/2}" x2="{size}" y2="{size/2}" '
        f'stroke="{_COLORS["gold"]}" stroke-width="1.5" opacity="0.5"/>',
        # 中心圓
        f'<circle cx="{size/2}" cy="{size/2}" r="20" '
        f'fill="{_COLORS["background"]}" stroke="{_COLORS["gold"]}" stroke-width="2"/>',
        f'<text x="{size/2}" y="{size/2 + 5}" text-anchor="middle" '
        f'font-size="10" fill="{_COLORS["gold"]}" font-family="serif">ΛΩΓ</text>',
    ]

    for direction, ox, oy in layout:
        wt = WATCHTOWERS[direction]
        score = wt_scores.get(direction, 0.0)
        is_dominant = chart and chart.dominant_watchtower == direction

        # 元素顏色
        el_color = _ELEMENT_COLORS.get(wt.element, _COLORS["gold"])
        bg_opacity = 0.12 + score * 0.3 if score else 0.08
        border_width = 2.5 if is_dominant else 1.5
        border_opacity = 1.0 if is_dominant else 0.5

        # 背景填充
        lines.append(
            f'<rect x="{ox + 2}" y="{oy + 2}" '
            f'width="{cell_w - 4}" height="{cell_h - 4}" '
            f'fill="{el_color}" fill-opacity="{bg_opacity}" '
            f'rx="8" ry="8"/>'
        )
        # 邊框
        lines.append(
            f'<rect x="{ox + 2}" y="{oy + 2}" '
            f'width="{cell_w - 4}" height="{cell_h - 4}" '
            f'fill="none" stroke="{el_color}" stroke-width="{border_width}" '
            f'stroke-opacity="{border_opacity}" rx="8" ry="8"/>'
        )

        # 方向箭頭符號
        dir_symbols = {"East": "→", "West": "←", "North": "↑", "South": "↓"}
        dir_sym = dir_symbols.get(direction, "•")

        tx = ox + cell_w / 2
        ty_base = oy + 28

        # 方向 + 元素標題
        lines.append(
            f'<text x="{tx}" y="{ty_base}" text-anchor="middle" '
            f'font-size="16" fill="{el_color}" font-family="serif" font-weight="bold">'
            f'{dir_sym} {wt.direction_zh}方</text>'
        )
        lines.append(
            f'<text x="{tx}" y="{ty_base + 18}" text-anchor="middle" '
            f'font-size="12" fill="{el_color}" font-family="sans-serif">'
            f'{wt.element_zh} ({wt.element})</text>'
        )

        # 守護天使
        lines.append(
            f'<text x="{tx}" y="{ty_base + 38}" text-anchor="middle" '
            f'font-size="10" fill="{_COLORS["text_light"]}" font-family="serif">'
            f'King: {wt.king_angel}</text>'
        )
        lines.append(
            f'<text x="{tx}" y="{ty_base + 52}" text-anchor="middle" '
            f'font-size="10" fill="{_COLORS["text_light"]}" font-family="serif">'
            f'{wt.planet_zh} ({wt.ruling_planet})</text>'
        )

        # 對應黃道星座
        signs_str = " · ".join(wt.zodiac_signs[:3])
        lines.append(
            f'<text x="{tx}" y="{ty_base + 68}" text-anchor="middle" '
            f'font-size="9" fill="{_COLORS["text_dim"]}" font-family="sans-serif">'
            f'{signs_str}</text>'
        )

        # 強度條（如有命盤資料）
        if score > 0:
            bar_w = (cell_w - 20) * score
            lines.append(
                f'<rect x="{ox + 10}" y="{oy + cell_h - 18}" '
                f'width="{cell_w - 20}" height="8" '
                f'fill="rgba(80,80,80,0.4)" rx="4"/>'
            )
            lines.append(
                f'<rect x="{ox + 10}" y="{oy + cell_h - 18}" '
                f'width="{bar_w:.1f}" height="8" '
                f'fill="{el_color}" opacity="0.8" rx="4"/>'
            )
            pct = int(score * 100)
            lines.append(
                f'<text x="{tx}" y="{oy + cell_h - 6}" text-anchor="middle" '
                f'font-size="8" fill="{_COLORS["text_dim"]}" font-family="sans-serif">'
                f'{pct}%</text>'
            )

        # 主導標記
        if is_dominant:
            lines.append(
                f'<text x="{ox + cell_w - 12}" y="{oy + 16}" text-anchor="middle" '
                f'font-size="12" fill="{_COLORS["gold"]}" font-family="serif">★</text>'
            )

    lines.append('</svg>')
    return "\n".join(lines)


# ============================================================
# 3. Aethyr Hierarchy SVG
# ============================================================

def render_aethyr_svg(
    chart: Optional[EnochianChart] = None,
    width: int = 500,
    height: int = 800,
    show_all: bool = True,
) -> str:
    """
    繪製 30 個以太層的層級示意圖。

    顯示：
    - 30 個 Aethyr 按層次排列（30=最高 → 1=最低）
    - 各層的元素顏色編碼
    - 命盤激活的 Aethyr 高亮顯示
    - 主要 Aethyr 特別標示

    Args:
        chart:     EnochianChart 物件
        width:     SVG 寬度
        height:    SVG 高度
        show_all:  是否顯示全部 30 層（否則只顯示前 10 層）

    Returns:
        str: SVG 字串
    """
    # 活躍的 Aethyr 集合
    active_nums: set = set()
    primary_num: Optional[int] = None
    if chart:
        primary_num = chart.primary_aethyr.number
        active_nums.add(primary_num)
        for a in chart.secondary_aethyrs:
            active_nums.add(a.number)
        for r in chart.aethyr_readings:
            if r.relevance_score > 0.1:
                active_nums.add(r.aethyr.number)

    aethyrs_to_show = AETHYRS if show_all else AETHYRS[:10]
    n = len(aethyrs_to_show)
    row_h = (height - 60) / n

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{_COLORS["background"]}"/>',
        # 標題
        f'<text x="{width/2}" y="22" text-anchor="middle" '
        f'font-size="13" fill="{_COLORS["gold"]}" font-family="serif" font-weight="bold">'
        f'30 Aethyrs / 以太層</text>',
        f'<text x="{width/2}" y="38" text-anchor="middle" '
        f'font-size="10" fill="{_COLORS["text_dim"]}" font-family="sans-serif">'
        f'30 = Highest Celestial · 1 = Closest to Earth</text>',
    ]

    for idx, aethyr in enumerate(reversed(aethyrs_to_show)):
        # aethyr.number: 30=highest; reversed list: idx 0 = number 30
        y = 50 + idx * row_h
        el_color = _ELEMENT_COLORS.get(aethyr.element, _COLORS["gold"])
        is_active = aethyr.number in active_nums
        is_primary = aethyr.number == primary_num

        bg_opacity = 0.35 if is_primary else (0.2 if is_active else 0.05)
        bar_width = width * 0.55 if is_active else width * 0.35

        # 背景
        lines.append(
            f'<rect x="5" y="{y:.1f}" width="{width - 10}" height="{row_h - 1:.1f}" '
            f'fill="{el_color}" fill-opacity="{bg_opacity}" rx="3"/>'
        )

        # 層次條
        lines.append(
            f'<rect x="5" y="{y:.1f}" width="{bar_width:.1f}" height="{row_h - 1:.1f}" '
            f'fill="{el_color}" fill-opacity="0.08" rx="3"/>'
        )

        # 左側：Aethyr 編號和名稱
        ty = y + row_h * 0.55
        num_color = _COLORS["gold"] if is_primary else (el_color if is_active else _COLORS["text_dim"])
        font_weight = "bold" if is_active else "normal"
        font_size_num = 11 if is_active else 9
        font_size_name = 12 if is_active else 10

        lines.append(
            f'<text x="14" y="{ty:.1f}" '
            f'font-size="{font_size_num}" fill="{num_color}" '
            f'font-family="serif" font-weight="{font_weight}">'
            f'{aethyr.number:02d}</text>'
        )
        lines.append(
            f'<text x="38" y="{ty:.1f}" '
            f'font-size="{font_size_name}" fill="{num_color}" '
            f'font-family="serif" font-weight="{font_weight}">'
            f'{aethyr.name}</text>'
        )
        lines.append(
            f'<text x="80" y="{ty:.1f}" '
            f'font-size="9" fill="{_COLORS["text_dim"]}" '
            f'font-family="sans-serif">'
            f'{aethyr.name_zh}</text>'
        )

        # 右側：元素 + 行星
        lines.append(
            f'<text x="{width - 90}" y="{ty:.1f}" '
            f'font-size="9" fill="{el_color}" font-family="sans-serif">'
            f'{aethyr.element_zh}</text>'
        )
        lines.append(
            f'<text x="{width - 50}" y="{ty:.1f}" '
            f'font-size="9" fill="{_COLORS["text_dim"]}" font-family="sans-serif">'
            f'{aethyr.planet_zh}</text>'
        )

        # 主 Aethyr 標記
        if is_primary:
            lines.append(
                f'<text x="{width - 16}" y="{ty:.1f}" '
                f'font-size="12" fill="{_COLORS["gold"]}" font-family="serif">★</text>'
            )

    lines.append('</svg>')
    return "\n".join(lines)


# ============================================================
# 4. 合成概覽圖：Natal Chart Enochian Overlay 文字版
# ============================================================

def render_enochian_summary_svg(
    chart: EnochianChart,
    size: int = 500,
) -> str:
    """
    繪製 Enochian 命盤概覽圖（圓形佈局）。

    外圈：12 宮位 + 行星 Enochian 天使標示
    內圈：主要守望塔方向
    中心：Sigillum 中心圖案 + 守護天使

    Args:
        chart: EnochianChart 物件
        size:  SVG 尺寸

    Returns:
        str: SVG 字串
    """
    cx = size / 2
    cy = size / 2
    r_outer = size * 0.42
    r_inner = size * 0.25

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="{_COLORS["background"]}"/>',
        f'<defs>',
        f'  <filter id="glow2"><feGaussianBlur stdDeviation="4" result="b"/>',
        f'  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        f'</defs>',

        # 外圓
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" '
        f'fill="none" stroke="{_COLORS["gold"]}" stroke-width="1.5" opacity="0.6"/>',
        # 內圓
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="none" stroke="{_COLORS["spirit_violet"]}" stroke-width="1" opacity="0.5"/>',
    ]

    # ── 12 宮分割線 ────────────────────────────────────────────
    for i in range(12):
        angle = math.radians(-90 + i * 30)
        x1 = cx + r_inner * math.cos(angle)
        y1 = cy + r_inner * math.sin(angle)
        x2 = cx + r_outer * math.cos(angle)
        y2 = cy + r_outer * math.sin(angle)
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{_COLORS["text_dim"]}" stroke-width="0.5" opacity="0.4"/>'
        )

    # ── 行星在外圈的位置 ──────────────────────────────────────
    for point in chart.planet_points:
        angle = math.radians(point.longitude - 90)
        r_plot = r_outer * 0.88
        px = cx + r_plot * math.cos(angle)
        py = cy + r_plot * math.sin(angle)

        el_color = _ELEMENT_COLORS.get(point.element, _COLORS["gold"])

        # 行星標記點
        lines.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" '
            f'fill="{point.planet_color}" opacity="0.9" filter="url(#glow2)"/>'
        )

        # 行星名縮寫
        planet_abbr = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿",
            "Venus": "♀", "Mars": "♂", "Jupiter": "♃",
            "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
        }
        sym = planet_abbr.get(point.planet_name, point.planet_name[:2])
        lines.append(
            f'<text x="{px:.1f}" y="{py - 8:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{_COLORS["text_light"]}" font-family="serif">'
            f'{sym}</text>'
        )

    # ── 四個守望塔方向標示 ──────────────────────────────────────
    dir_positions = {"East": (r_inner + 15, 0), "West": (-r_inner - 15, 0),
                     "North": (0, -r_inner - 15), "South": (0, r_inner + 15)}
    dir_labels = {"East": "E 東", "West": "W 西", "North": "N 北", "South": "S 南"}

    for direction, (dx, dy) in dir_positions.items():
        wt = WATCHTOWERS[direction]
        score = chart.watchtower_scores.get(direction, 0.0)
        is_dom = direction == chart.dominant_watchtower
        el_color = _ELEMENT_COLORS.get(wt.element, _COLORS["gold"])
        font_size = 11 if is_dom else 9
        label = dir_labels[direction]
        lines.append(
            f'<text x="{cx + dx:.1f}" y="{cy + dy + 4:.1f}" text-anchor="middle" '
            f'font-size="{font_size}" fill="{el_color}" font-family="serif" '
            f'font-weight="{"bold" if is_dom else "normal"}">'
            f'{label}</text>'
        )

    # ── 中心：守護天使 ────────────────────────────────────────
    lines.append(
        f'<circle cx="{cx}" cy="{cy}" r="30" '
        f'fill="{_COLORS["background"]}" stroke="{_COLORS["gold"]}" stroke-width="2"/>'
    )
    lines.append(
        f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" '
        f'font-size="9" fill="{_COLORS["gold"]}" font-family="serif">'
        f'{chart.patron_angel.name}</text>'
    )
    lines.append(
        f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" '
        f'font-size="8" fill="{_COLORS["silver"]}" font-family="serif">'
        f'{chart.matron_angel.name}</text>'
    )
    lines.append(
        f'<text x="{cx}" y="{cy + 18}" text-anchor="middle" '
        f'font-size="8" fill="{_COLORS["text_dim"]}" font-family="serif">'
        f'{chart.primary_aethyr.name}</text>'
    )

    # ── 標題 ────────────────────────────────────────────────────
    lines.append(
        f'<text x="{cx}" y="16" text-anchor="middle" '
        f'font-size="11" fill="{_COLORS["gold"]}" font-family="serif" font-weight="bold">'
        f'Enochian Natal Chart / 伊諾克出生盤</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


def render_element_balance_svg(
    element_scores: Dict[str, float],
    width: int = 420,
    height: int = 220,
) -> str:
    """Render elemental balance bar chart as SVG."""
    el_order = [("Fire", "火"), ("Water", "水"), ("Air", "風"), ("Earth", "土")]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{_COLORS["background"]}"/>',
        f'<text x="{width/2}" y="20" text-anchor="middle" fill="{_COLORS["gold"]}" font-size="13" font-family="serif">Element Balance</text>',
    ]
    y = 50
    for element, zh in el_order:
        # Defensive clamp for API/UI callers that may pass non-normalized values.
        score = max(0.0, min(1.0, float(element_scores.get(element, 0.0))))
        color = _ELEMENT_COLORS.get(element, _COLORS["gold"])
        bar_w = int((width - 180) * score)
        lines.append(f'<text x="20" y="{y+6}" fill="{_COLORS["text_light"]}" font-size="11">{zh} ({element})</text>')
        lines.append(f'<rect x="130" y="{y-6}" width="{width-180}" height="14" fill="#252545" rx="4"/>')
        lines.append(f'<rect x="130" y="{y-6}" width="{bar_w}" height="14" fill="{color}" opacity="0.85" rx="4"/>')
        lines.append(f'<text x="{width-40}" y="{y+6}" fill="{color}" text-anchor="end" font-size="11">{int(score*100)}%</text>')
        y += 38
    lines.append("</svg>")
    return "\n".join(lines)


__all__ = [
    "render_sigillum_svg",
    "render_watchtower_svg",
    "render_aethyr_svg",
    "render_enochian_summary_svg",
    "render_element_balance_svg",
]
