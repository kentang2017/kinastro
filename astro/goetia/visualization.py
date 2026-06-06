"""
astro/goetia/visualization.py — Goetia 占星 SVG 視覺化模組

提供三個主要視覺化：
  1. render_demon_sigil_svg()        — 魔神印記（Sigil）風格圓形圖
  2. render_goetia_natal_svg()       — Goetia Natal Overview 圓形命盤圖
  3. render_element_balance_svg()    — 元素平衡長條圖

設計原則：
  - 所有函式均為純函式，無 Streamlit 依賴
  - 輸出為 SVG 字串，可嵌入任何 HTML/Streamlit 元件
  - 視覺風格與 enochian/visualization.py 保持一致（深色背景、金色主調）
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from .constants import (
    SIGNS_EN,
    SIGNS_ZH,
    ELEMENT_COLORS,
    PLANET_COLORS,
    DIRECTION_ZH,
    ELEMENT_ZH,
    GoetiaChart,
    DemonData,
    GoetiaPlanetPoint,
)

# ============================================================
# 顏色常數（與 Enochian 模組一致）
# ============================================================

_COLORS = {
    "background":     "#0a0a1e",
    "gold":           "#FFD700",
    "silver":         "#C0C0C0",
    "fire_red":       "#FF4500",
    "water_blue":     "#4169E1",
    "air_sky":        "#87CEEB",
    "earth_brown":    "#8B6914",
    "dark_red":       "#8B0000",
    "text_light":     "#E8E0D0",
    "text_dim":       "#8080A0",
    "active_glow":    "#FFD70060",
    "circle_ring":    "#3a2a00",
    "solomon_purple": "#6B21A8",
}

_RANK_COLORS = {
    "King":      "#FFD700",
    "Duke":      "#FF69B4",
    "Prince":    "#FF8C00",
    "Marquis":   "#C0C0C0",
    "President": "#87CEEB",
    "Count":     "#808080",
    "Earl":      "#808080",
    "Knight":    "#8B6914",
}

# ============================================================
# 1. 魔神印記 SVG / Demon Sigil Style SVG
# ============================================================

def render_demon_sigil_svg(
    demon: DemonData,
    size: int = 400,
    show_labels: bool = True,
    highlighted: bool = True,
) -> str:
    """
    繪製魔神印記（Sigil）風格的圓形象徵圖。

    使用幾何圖案（五芒星、六芒星、螺旋線等）根據魔神的行星、元素屬性生成
    獨特的符號化印記視覺。真實的格提亞印記是傳統符號，此處以象徵性風格呈現。

    Args:
        demon:       DemonData 物件
        size:        SVG 尺寸（像素）
        show_labels: 是否顯示名稱/屬性標籤
        highlighted: 是否啟用輝光效果（推薦的魔神顯示時使用）

    Returns:
        str: SVG 字串
    """
    cx = size / 2
    cy = size / 2
    r = size * 0.42

    elem_color = ELEMENT_COLORS.get(demon.element, _COLORS["gold"])
    planet_color = PLANET_COLORS.get(demon.planet, _COLORS["gold"])
    rank_color = _RANK_COLORS.get(demon.rank, _COLORS["gold"])

    # 根據魔神編號生成獨特幾何（確保每個魔神視覺不同）
    seed = demon.number
    star_points = 5 + (seed % 4)   # 5–8 芒星
    inner_twist = seed % 3 + 2      # 內部扭轉係數
    rotation_offset = (seed * 7) % 360  # 旋轉偏移

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">',

        # 背景
        f'<rect width="{size}" height="{size}" fill="{_COLORS["background"]}" rx="12"/>',

        # SVG 定義（濾鏡）
        '<defs>',
        f'  <filter id="sigilGlow_{demon.number}">',
        f'    <feGaussianBlur stdDeviation="4" result="blur"/>',
        f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        f'  </filter>',
        f'  <filter id="softGlow_{demon.number}">',
        f'    <feGaussianBlur stdDeviation="8" result="blur"/>',
        f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        f'  </filter>',
        '</defs>',

        # 外圓（元素色）
        f'<circle cx="{cx}" cy="{cy}" r="{r}" '
        f'fill="none" stroke="{elem_color}" stroke-width="2" opacity="0.7"/>',

        # 中圓
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.7}" '
        f'fill="none" stroke="{planet_color}" stroke-width="1.5" opacity="0.5"/>',

        # 內圓
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.35}" '
        f'fill="none" stroke="{rank_color}" stroke-width="1" opacity="0.4"/>',
    ]

    # ── 多芒星 ──
    outer_pts = _compute_star_points(cx, cy, r * 0.92, star_points, rotation_offset)
    inner_pts = _compute_star_points(cx, cy, r * 0.92 * 0.4, star_points, rotation_offset + 180 / star_points)

    # 連線（每個外頂點連接隔 inner_twist 個外頂點）
    for i in range(star_points):
        j = (i + inner_twist) % star_points
        x1, y1 = outer_pts[i]
        x2, y2 = outer_pts[j]
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{elem_color}" stroke-width="1" opacity="0.5"/>'
        )

    # 外到內連線
    for i in range(star_points):
        ox, oy = outer_pts[i]
        ix, iy = inner_pts[i]
        lines.append(
            f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{ix:.1f}" y2="{iy:.1f}" '
            f'stroke="{planet_color}" stroke-width="0.8" opacity="0.4"/>'
        )

    # 頂點節點
    for i, (px, py) in enumerate(outer_pts):
        glow_attr = f'filter="url(#sigilGlow_{demon.number})"' if highlighted and i == 0 else ""
        lines.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" '
            f'fill="{rank_color}" stroke="{elem_color}" stroke-width="1" '
            f'{glow_attr} opacity="0.8"/>'
        )

    # 中心符號（根據元素）
    center_symbol = _element_center_symbol(demon.element, cx, cy, r * 0.25, elem_color, demon.number)
    lines.extend(center_symbol)

    # ── 方向符號（上方）──
    _add_direction_marker(lines, demon.direction, cx, r, size, elem_color)

    if show_labels:
        glow_filter = f'filter="url(#softGlow_{demon.number})"' if highlighted else ""

        # 魔神名稱
        lines.append(
            f'<text x="{cx}" y="{size - 52}" text-anchor="middle" '
            f'font-size="18" fill="{_COLORS["gold"]}" font-family="serif" '
            f'font-weight="bold" {glow_filter}>'
            f'{demon.name}</text>'
        )
        # 中文名稱
        lines.append(
            f'<text x="{cx}" y="{size - 34}" text-anchor="middle" '
            f'font-size="13" fill="{_COLORS["text_light"]}" font-family="serif">'
            f'{demon.name_zh}</text>'
        )
        # 等級 / 行星 / 元素
        info = f"{demon.rank} | {demon.planet} | {demon.element}"
        lines.append(
            f'<text x="{cx}" y="{size - 16}" text-anchor="middle" '
            f'font-size="10" fill="{_COLORS["text_dim"]}" font-family="monospace">'
            f'{info}</text>'
        )
        # 編號標籤
        lines.append(
            f'<text x="14" y="20" text-anchor="start" '
            f'font-size="11" fill="{_COLORS["text_dim"]}" font-family="monospace">'
            f'#{demon.number:02d}</text>'
        )
        # 軍團數
        lines.append(
            f'<text x="{size - 14}" y="20" text-anchor="end" '
            f'font-size="10" fill="{_COLORS["text_dim"]}" font-family="monospace">'
            f'{demon.legion_count} legions</text>'
        )

    lines.append('</svg>')
    return "\n".join(lines)


def _compute_star_points(
    cx: float, cy: float, radius: float, n: int, offset_deg: float,
) -> List[tuple]:
    """計算 n 芒星的頂點座標。"""
    pts = []
    for i in range(n):
        angle = math.radians(offset_deg + i * 360 / n - 90)
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts


def _element_center_symbol(
    element: str, cx: float, cy: float, r: float,
    color: str, seed: int,
) -> List[str]:
    """根據元素繪製中心符號。"""
    lines: List[str] = []
    if element == "Fire":
        # 向上三角形
        pts = [(cx, cy - r), (cx - r * 0.866, cy + r * 0.5), (cx + r * 0.866, cy + r * 0.5)]
        pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        lines.append(f'<polygon points="{pts_str}" fill="none" stroke="{color}" stroke-width="2" opacity="0.9"/>')

    elif element == "Water":
        # 向下三角形
        pts = [(cx, cy + r), (cx - r * 0.866, cy - r * 0.5), (cx + r * 0.866, cy - r * 0.5)]
        pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        lines.append(f'<polygon points="{pts_str}" fill="none" stroke="{color}" stroke-width="2" opacity="0.9"/>')

    elif element == "Air":
        # 向上三角形 + 橫線
        pts = [(cx, cy - r), (cx - r * 0.866, cy + r * 0.5), (cx + r * 0.866, cy + r * 0.5)]
        pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        lines.append(f'<polygon points="{pts_str}" fill="none" stroke="{color}" stroke-width="2" opacity="0.9"/>')
        lines.append(
            f'<line x1="{cx - r * 0.5:.1f}" y1="{cy + r * 0.17:.1f}" '
            f'x2="{cx + r * 0.5:.1f}" y2="{cy + r * 0.17:.1f}" '
            f'stroke="{color}" stroke-width="2" opacity="0.9"/>'
        )

    elif element == "Earth":
        # 向下三角形 + 橫線
        pts = [(cx, cy + r), (cx - r * 0.866, cy - r * 0.5), (cx + r * 0.866, cy - r * 0.5)]
        pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        lines.append(f'<polygon points="{pts_str}" fill="none" stroke="{color}" stroke-width="2" opacity="0.9"/>')
        lines.append(
            f'<line x1="{cx - r * 0.5:.1f}" y1="{cy - r * 0.17:.1f}" '
            f'x2="{cx + r * 0.5:.1f}" y2="{cy - r * 0.17:.1f}" '
            f'stroke="{color}" stroke-width="2" opacity="0.9"/>'
        )

    return lines


def _add_direction_marker(
    lines: List[str], direction: str,
    cx: float, r: float, size: float, color: str,
) -> None:
    """在圓形頂部添加方向標記。"""
    dir_symbols = {"East": "E↑", "West": "W↓", "North": "N←", "South": "S→"}
    symbol = dir_symbols.get(direction, direction[0])
    lines.append(
        f'<text x="{cx}" y="22" text-anchor="middle" '
        f'font-size="12" fill="{color}" font-family="monospace" opacity="0.7">'
        f'{symbol} {DIRECTION_ZH.get(direction, direction)}</text>'
    )


# ============================================================
# 2. Goetia Natal Overview 圓形圖
# ============================================================

def render_goetia_natal_svg(
    chart: GoetiaChart,
    size: int = 560,
) -> str:
    """
    繪製 Goetia Natal Overview 圓形命盤概覽圖。

    圖形包含：
    - 外圈：12 黃道星座帶（元素色）
    - 中圈：行星位置點（行星色）
    - 推薦魔神標示（依行星位置）
    - 四個方向指示（East/South/West/North）
    - 元素區域著色

    Args:
        chart: GoetiaChart 命盤物件
        size:  SVG 尺寸（像素）

    Returns:
        str: SVG 字串
    """
    cx = size / 2
    cy = size / 2
    r_outer = size * 0.44     # 星座帶外圓
    r_zodiac = size * 0.40    # 星座帶內圓
    r_planet = size * 0.30    # 行星軌道圓
    r_inner = size * 0.15     # 中心圓

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="{_COLORS["background"]}" rx="12"/>',

        '<defs>',
        '  <filter id="goetiaGlow">',
        '    <feGaussianBlur stdDeviation="3" result="blur"/>',
        '    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '  </filter>',
        '</defs>',
    ]

    # ── 星座外帶（12 格） ──────────────────────────────────────
    _sign_elements = ["Fire", "Earth", "Air", "Water",
                      "Fire", "Earth", "Air", "Water",
                      "Fire", "Earth", "Air", "Water"]

    for i, sign in enumerate(SIGNS_EN):
        start_angle = math.radians(i * 30 - 90)  # 白羊從頂部開始
        end_angle = math.radians((i + 1) * 30 - 90)
        elem = _sign_elements[i]
        fill_color = ELEMENT_COLORS.get(elem, "#333")

        # 計算扇形路徑
        x1o = cx + r_outer * math.cos(start_angle)
        y1o = cy + r_outer * math.sin(start_angle)
        x2o = cx + r_outer * math.cos(end_angle)
        y2o = cy + r_outer * math.sin(end_angle)
        x1i = cx + r_zodiac * math.cos(start_angle)
        y1i = cy + r_zodiac * math.sin(start_angle)
        x2i = cx + r_zodiac * math.cos(end_angle)
        y2i = cy + r_zodiac * math.sin(end_angle)

        path = (
            f"M {x1i:.1f},{y1i:.1f} "
            f"L {x1o:.1f},{y1o:.1f} "
            f"A {r_outer:.1f},{r_outer:.1f} 0 0,1 {x2o:.1f},{y2o:.1f} "
            f"L {x2i:.1f},{y2i:.1f} "
            f"A {r_zodiac:.1f},{r_zodiac:.1f} 0 0,0 {x1i:.1f},{y1i:.1f} Z"
        )
        lines.append(
            f'<path d="{path}" fill="{fill_color}" opacity="0.15" '
            f'stroke="{_COLORS["circle_ring"]}" stroke-width="0.5"/>'
        )

        # 星座符號
        mid_angle = math.radians(i * 30 + 15 - 90)
        label_r = (r_outer + r_zodiac) / 2
        lx = cx + label_r * math.cos(mid_angle)
        ly = cy + label_r * math.sin(mid_angle)
        sign_symbol = _SIGN_GLYPHS[i]
        lines.append(
            f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" '
            f'font-size="11" fill="{fill_color}" font-family="serif" opacity="0.9">'
            f'{sign_symbol}</text>'
        )

    # ── 行星軌道圓 ────────────────────────────────────────────
    lines.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_planet}" '
        f'fill="none" stroke="{_COLORS["circle_ring"]}" stroke-width="0.8" opacity="0.5"/>'
    )

    # ── 中心圓 ────────────────────────────────────────────────
    lines.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="{_COLORS["background"]}" stroke="{_COLORS["gold"]}" '
        f'stroke-width="1.5" opacity="0.8"/>'
    )

    # ── 行星點 ────────────────────────────────────────────────
    for pp in chart.planet_points:
        lon = pp.longitude
        angle = math.radians(lon - 90)  # 0°白羊從頂
        px = cx + r_planet * math.cos(angle)
        py = cy + r_planet * math.sin(angle)
        color = PLANET_COLORS.get(pp.planet_name, _COLORS["gold"])

        lines.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" '
            f'fill="{color}" stroke="{_COLORS["background"]}" stroke-width="1" '
            f'filter="url(#goetiaGlow)" opacity="0.9"/>'
        )
        # 行星縮寫標籤
        planet_abbr = _PLANET_ABBR.get(pp.planet_name, pp.planet_name[0])
        label_r2 = r_planet + 14
        lx2 = cx + label_r2 * math.cos(angle)
        ly2 = cy + label_r2 * math.sin(angle)
        lines.append(
            f'<text x="{lx2:.1f}" y="{ly2 + 4:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{color}" font-family="monospace" opacity="0.8">'
            f'{planet_abbr}</text>'
        )

    # ── 推薦魔神標示（前 3 名） ────────────────────────────────
    for i, rec in enumerate(chart.recommendations[:3]):
        demon = rec.demon
        # 使用魔神統治星座中點位置作為顯示位置
        sign_idx = SIGNS_EN.index(demon.zodiac_sign) if demon.zodiac_sign in SIGNS_EN else i * 4
        angle = math.radians(sign_idx * 30 + 15 - 90)
        dr = r_zodiac * 0.6
        dx = cx + dr * math.cos(angle)
        dy = cy + dr * math.sin(angle)
        rank_color = _RANK_COLORS.get(demon.rank, _COLORS["gold"])

        lines.append(
            f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="8" '
            f'fill="{rank_color}" opacity="0.7" '
            f'stroke="{_COLORS["gold"]}" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{dx:.1f}" y="{dy + 4:.1f}" text-anchor="middle" '
            f'font-size="7" fill="{_COLORS["background"]}" font-family="monospace" '
            f'font-weight="bold">{i + 1}</text>'
        )

    # ── 四方向線 ─────────────────────────────────────────────
    for angle_deg, dir_label, dir_zh in [
        (270, "E", "東"), (0, "S", "南"), (90, "W", "西"), (180, "N", "北"),
    ]:
        angle_rad = math.radians(angle_deg)
        x2 = cx + r_outer * 1.05 * math.cos(angle_rad)
        y2 = cy + r_outer * 1.05 * math.sin(angle_rad)
        lines.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{_COLORS["text_dim"]}" stroke-width="0.5" opacity="0.3" stroke-dasharray="4,4"/>'
        )

    # ── 中心文字（上升點星座） ───────────────────────────────
    lines.append(
        f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" '
        f'font-size="11" fill="{_COLORS["gold"]}" font-family="serif" font-weight="bold">'
        f'ASC</text>'
    )
    lines.append(
        f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" '
        f'font-size="10" fill="{_COLORS["text_light"]}" font-family="serif">'
        f'{chart.ascendant_sign_zh}</text>'
    )

    # ── 圖例（推薦魔神前 3 名） ─────────────────────────────
    legend_x = 10
    legend_y = size - 60
    lines.append(
        f'<text x="{legend_x}" y="{legend_y}" font-size="9" '
        f'fill="{_COLORS["text_dim"]}" font-family="monospace">Top Demons:</text>'
    )
    for i, rec in enumerate(chart.recommendations[:3]):
        lines.append(
            f'<text x="{legend_x}" y="{legend_y + 12 * (i + 1)}" font-size="9" '
            f'fill="{_COLORS["text_light"]}" font-family="monospace">'
            f'{i + 1}. {rec.demon.name} ({rec.demon.rank})</text>'
        )

    # ── 標題 ─────────────────────────────────────────────────
    lines.append(
        f'<text x="{cx}" y="20" text-anchor="middle" '
        f'font-size="12" fill="{_COLORS["text_dim"]}" font-family="serif">'
        f'Goetia Natal Overview</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


# 星座符號（天文符號）
_SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# 行星縮寫
_PLANET_ABBR = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
    "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
}


# ============================================================
# 3. 元素平衡圖 / Element Balance Chart
# ============================================================

def render_element_balance_svg(
    chart: GoetiaChart,
    size: int = 360,
) -> str:
    """
    繪製元素平衡長條圖（火/土/風/水）。

    Args:
        chart: GoetiaChart 物件
        size:  SVG 寬度（像素），高度自動計算

    Returns:
        str: SVG 字串
    """
    elements = ["Fire", "Earth", "Air", "Water"]
    height = 160
    bar_width = size * 0.55
    bar_height = 20
    bar_gap = 14
    label_x = 10
    bar_x = label_x + 70
    value_x = bar_x + bar_width + 8

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{height}" viewBox="0 0 {size} {height}">',
        f'<rect width="{size}" height="{height}" fill="{_COLORS["background"]}" rx="8"/>',
        f'<text x="{size / 2}" y="18" text-anchor="middle" '
        f'font-size="11" fill="{_COLORS["text_dim"]}" font-family="serif">'
        f'Goetia Elemental Balance</text>',
    ]

    for i, elem in enumerate(elements):
        score = chart.element_scores.get(elem, 0.0)
        color = ELEMENT_COLORS.get(elem, "#888")
        elem_zh = ELEMENT_ZH.get(elem, elem)

        y = 30 + i * (bar_height + bar_gap)
        filled = bar_width * score

        # 背景條
        lines.append(
            f'<rect x="{bar_x}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" '
            f'fill="{_COLORS["circle_ring"]}" rx="4" opacity="0.5"/>'
        )
        # 填充條
        if filled > 0:
            lines.append(
                f'<rect x="{bar_x}" y="{y}" width="{filled:.1f}" height="{bar_height}" '
                f'fill="{color}" rx="4" opacity="0.8"/>'
            )
        # 標籤
        lines.append(
            f'<text x="{label_x}" y="{y + bar_height - 5}" '
            f'font-size="11" fill="{color}" font-family="serif">'
            f'{elem} {elem_zh}</text>'
        )
        # 百分比
        lines.append(
            f'<text x="{value_x}" y="{y + bar_height - 5}" '
            f'font-size="10" fill="{_COLORS["text_light"]}" font-family="monospace">'
            f'{score * 100:.0f}%</text>'
        )

        # 主導元素標記
        if elem == chart.dominant_element:
            lines.append(
                f'<text x="{value_x + 36}" y="{y + bar_height - 5}" '
                f'font-size="10" fill="{_COLORS["gold"]}" font-family="monospace">★</text>'
            )

    lines.append('</svg>')
    return "\n".join(lines)


# ============================================================
# 4. 推薦魔神卡片組 SVG / Recommendation Summary SVG
# ============================================================

def render_recommendation_summary_svg(
    chart: GoetiaChart,
    size: int = 500,
) -> str:
    """
    繪製前 5 名推薦魔神的摘要圖表（橫向排列）。

    Returns:
        str: SVG 字串
    """
    n = min(5, len(chart.recommendations))
    card_w = size // n - 4
    card_h = 120
    height = card_h + 20

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{height}" viewBox="0 0 {size} {height}">',
        f'<rect width="{size}" height="{height}" fill="{_COLORS["background"]}" rx="8"/>',
    ]

    for i, rec in enumerate(chart.recommendations[:n]):
        demon = rec.demon
        x = i * (card_w + 4) + 2
        y = 10
        elem_color = ELEMENT_COLORS.get(demon.element, _COLORS["gold"])
        rank_color = _RANK_COLORS.get(demon.rank, _COLORS["gold"])

        # 卡片背景
        opacity = max(0.15, 0.4 - i * 0.05)
        lines.append(
            f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" '
            f'fill="{elem_color}" opacity="{opacity:.2f}" rx="6" '
            f'stroke="{rank_color}" stroke-width="1"/>'
        )

        # 排名
        lines.append(
            f'<text x="{x + 6}" y="{y + 16}" font-size="11" '
            f'fill="{_COLORS["gold"]}" font-family="monospace" font-weight="bold">#{i + 1}</text>'
        )

        # 名字
        lines.append(
            f'<text x="{x + card_w / 2}" y="{y + 34}" text-anchor="middle" '
            f'font-size="12" fill="{_COLORS["gold"]}" font-family="serif" font-weight="bold">'
            f'{demon.name}</text>'
        )
        lines.append(
            f'<text x="{x + card_w / 2}" y="{y + 48}" text-anchor="middle" '
            f'font-size="10" fill="{_COLORS["text_light"]}" font-family="serif">'
            f'{demon.name_zh}</text>'
        )

        # 等級
        lines.append(
            f'<text x="{x + card_w / 2}" y="{y + 62}" text-anchor="middle" '
            f'font-size="9" fill="{rank_color}" font-family="monospace">'
            f'{demon.rank}</text>'
        )

        # 行星/元素
        lines.append(
            f'<text x="{x + card_w / 2}" y="{y + 76}" text-anchor="middle" '
            f'font-size="9" fill="{elem_color}" font-family="monospace">'
            f'{demon.planet} | {demon.element}</text>'
        )

        # 分數條
        bar_x = x + 4
        bar_w = card_w - 8
        bar_y = y + card_h - 18
        filled = bar_w * rec.score
        lines.append(
            f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w:.1f}" height="6" '
            f'fill="{_COLORS["circle_ring"]}" rx="3"/>'
        )
        if filled > 0:
            lines.append(
                f'<rect x="{bar_x}" y="{bar_y}" width="{filled:.1f}" height="6" '
                f'fill="{rank_color}" rx="3" opacity="0.9"/>'
            )

        # 分數標籤
        lines.append(
            f'<text x="{x + card_w / 2}" y="{y + card_h - 4}" text-anchor="middle" '
            f'font-size="8" fill="{_COLORS["text_dim"]}" font-family="monospace">'
            f'{rec.score_zh}</text>'
        )

    lines.append('</svg>')
    return "\n".join(lines)
