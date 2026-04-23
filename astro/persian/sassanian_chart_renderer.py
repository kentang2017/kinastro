"""
astro/persian/sassanian_chart_renderer.py — 薩珊傳統占星星盤渲染器（純 SVG 版本）

Sassanian Traditional Star Chart Renderer (Pure SVG)
基於用戶提供的菱形 12 宮設計，完全按照參考 SVG 結構

References
----------
- Sassanian silver plates (Metropolitan Museum, Louvre)
- Taq-e Bostan rock reliefs (6th-7th century CE)
- Greater Bundahishn illustrations
- Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
"""

from typing import Dict, List, Optional
import swisseph as swe
import json
import os
import base64

from astro.persian.sassanian_astronomy import (
    compute_sassanian_planet_positions,
    get_sassanian_houses,
    get_royal_stars_positions,
    SassanianPlanetPosition,
)
from astro.persian.sassanian_symbols import (
    get_sassanian_color_palette,
    get_pahlavi_name,
    get_royal_star_pahlavi,
    get_zodiac_glyph,
    get_planet_glyph,
)

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_sassanian_svg(
    chart_data: Dict,
    width: int = 500,
    height: int = 650,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
) -> str:
    """
    生成薩珊傳統占星星盤（純 SVG 格式）
    
    完全按照用戶提供的菱形 12 宮設計：
    - 外框正方形
    - 內框正方形（菱形）
    - 對角線連接形成 12 宮
    - 星座符號在外圍 12 個位置

    Parameters
    ----------
    chart_data : Dict
        星盤資料
    width : int
        SVG 寬度（像素）
    height : int
        SVG 高度（像素）
    show_pahlavi : bool
        是否顯示 Pahlavi 文字
    show_royal_stars : bool
        是否顯示皇家恆星
    show_firdar : bool
        是否顯示 Firdar 時間線

    Returns
    -------
    str
        SVG 字串
    """
    palette = get_sassanian_color_palette()

    # 提取出生資料
    year = chart_data.get("year")
    month = chart_data.get("month")
    day = chart_data.get("day")
    hour = chart_data.get("hour", 12)
    minute = chart_data.get("minute", 0)
    longitude = chart_data.get("longitude", 0)
    latitude = chart_data.get("latitude", 0)
    timezone = chart_data.get("timezone", 0)

    # 計算儒略日
    julian_day = swe.julday(year, month, day, hour + minute / 60.0)

    # 計算薩珊行星位置
    planet_positions = compute_sassanian_planet_positions(
        year, month, day, hour, minute,
        longitude, latitude, timezone
    )

    # 計算薩珊宮位
    houses = get_sassanian_houses(
        year, month, day, hour, minute,
        longitude, latitude, timezone
    )

    # 獲取皇家恆星位置
    royal_stars = get_royal_stars_positions(julian_day) if show_royal_stars else {}

    # 計算縮放比例（基於 viewBox 500x650）
    base_width = 500
    base_height = 650
    scale_x = width / base_width
    scale_y = height / base_height
    scale = min(scale_x, scale_y)
    
    # viewBox 始終保持 500x650 座標系統（增加 50px 給 Firdar 時間線）
    viewBox = f"0 0 {base_width} {base_height}"
    
    # 計算幾何結構（完全按照參考 SVG，使用 500x650 座標系統）
    # 外框：x=50, y=100, width=400, height=400
    outer_x = 50
    outer_y = 100
    outer_width = 400
    outer_height = 400
    
    # 內框（菱形）：x=150, y=200, width=200, height=200
    inner_x = 150
    inner_y = 200
    inner_width = 200
    inner_height = 200
    
    # 中心點
    center_x = outer_x + outer_width / 2  # 250
    center_y = outer_y + outer_height / 2  # 300

    # 12 宮位區域的星座位置（按照參考 SVG 的 12 個位置）
    # 從頂部開始，順時針方向（使用固定座標，不需縮放）
    zodiac_positions = [
        # 頂部（3 個）
        {"sign_index": 7, "x": center_x, "y": outer_y - 15, "label": "top_center"},  # ♏ Scorpio
        {"sign_index": 8, "x": center_x - outer_width/4, "y": outer_y - 15, "label": "top_left"},  # ♐ Sagittarius
        {"sign_index": 6, "x": center_x + outer_width/4, "y": outer_y - 15, "label": "top_right"},  # ♎ Libra
        
        # 左側（3 個）
        {"sign_index": 9, "x": outer_x - 15, "y": outer_y + outer_height/4, "label": "left_top"},  # ♑ Capricorn
        {"sign_index": 10, "x": outer_x - 15, "y": center_y, "label": "left_center"},  # ♒ Aquarius
        {"sign_index": 11, "x": outer_x - 15, "y": outer_y + outer_height*3/4, "label": "left_bottom"},  # ♓ Pisces
        
        # 底部（3 個）
        {"sign_index": 0, "x": center_x - outer_width/4, "y": outer_y + outer_height + 15, "label": "bottom_left"},  # ♈ Aries
        {"sign_index": 1, "x": center_x, "y": outer_y + outer_height + 15, "label": "bottom_center"},  # ♉ Taurus
        {"sign_index": 2, "x": center_x + outer_width/4, "y": outer_y + outer_height + 15, "label": "bottom_right"},  # ♊ Gemini
        
        # 右側（3 個）
        {"sign_index": 3, "x": outer_x + outer_width + 15, "y": outer_y + outer_height*3/4, "label": "right_bottom"},  # ♋ Cancer
        {"sign_index": 4, "x": outer_x + outer_width + 15, "y": center_y, "label": "right_center"},  # ♌ Leo
        {"sign_index": 5, "x": outer_x + outer_width + 15, "y": outer_y + outer_height/4, "label": "right_top"},  # ♍ Virgo
    ]

    # 開始構建 SVG
    svg_parts = []

    # SVG 開頭（使用 viewBox 確保正確縮放）
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="{viewBox}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{palette['gold_gradient_start']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{palette['gold_gradient_end']};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="parchmentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{palette['parchment']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#E8D5C4;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- 背景 -->
  <rect width="{base_width}" height="{base_height}" fill="url(#parchmentGradient)" />
''')

    # 標題
    title_text = "薩珊傳統占星星盤"
    if show_pahlavi:
        title_text += " | 𐭮𐭠𐭮𐭠𐭭 𐭲𐭠𐭫𐭹𐭹𐭠"

    svg_parts.append(f'''
  <!-- 標題 -->
  <text x="{width/2}" y="50" font-family="serif" font-size="28" font-weight="bold"
        fill="{palette['crimson']}" text-anchor="middle" letter-spacing="8">
    {title_text}
  </text>
''')

    # 星盤框架（完全按照參考 SVG）
    svg_parts.append(f'''
  <!-- 星盤框架 -->
  <g stroke="{palette['black']}" stroke-width="2" fill="none">
    <!-- 外框正方形 -->
    <rect x="{outer_x}" y="{outer_y}" width="{outer_width}" height="{outer_height}" />
    
    <!-- 內框正方形（菱形） -->
    <rect x="{inner_x}" y="{inner_y}" width="{inner_width}" height="{inner_height}" />
    
    <!-- 四角對角線 -->
    <line x1="{outer_x}" y1="{outer_y}" x2="{inner_x}" y2="{inner_y}" />
    <line x1="{outer_x + outer_width}" y1="{outer_y}" x2="{inner_x + inner_width}" y2="{inner_y}" />
    <line x1="{outer_x}" y1="{outer_y + outer_height}" x2="{inner_x}" y2="{inner_y + inner_height}" />
    <line x1="{outer_x + outer_width}" y1="{outer_y + outer_height}" x2="{inner_x + inner_width}" y2="{inner_y + inner_height}" />
    
    <!-- 菱形到外框的連接線（形成 12 宮） -->
    <line x1="{center_x}" y1="{outer_y}" x2="{outer_x}" y2="{outer_y + outer_height/2}" />
    <line x1="{outer_x}" y1="{outer_y + outer_height/2}" x2="{center_x}" y2="{outer_y + outer_height}" />
    <line x1="{center_x}" y1="{outer_y + outer_height}" x2="{outer_x + outer_width}" y2="{outer_y + outer_height/2}" />
    <line x1="{outer_x + outer_width}" y1="{outer_y + outer_height/2}" x2="{center_x}" y2="{outer_y}" />
  </g>
''')

    # 12 星座符號（外圍 12 個位置）
    svg_parts.append(f'''
  <!-- 12 星座符號 -->
  <g font-family="serif" font-size="24" fill="{palette['black']}" text-anchor="middle">
''')

    zodiac_signs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    
    for pos in zodiac_positions:
        sign_glyph = zodiac_signs[pos["sign_index"]]
        svg_parts.append(f'''    <text x="{pos['x']}" y="{pos['y']}">{sign_glyph}</text>\n''')

    svg_parts.append('  </g>\n')

    # 行星位置（在 12 宮區域內）
    svg_parts.append(f'''
  <!-- 行星位置 -->
  <g font-family="serif" font-size="22" fill="{palette['black']}">
''')

    # 根據行星所在的宮位，放置在對應區域
    for planet in planet_positions:
        # 簡化：根據行星的星座索引確定大致位置
        sign_index = int(planet.longitude_sidereal // 30)
        
        # 找到對應的位置區域
        for pos in zodiac_positions:
            if pos["sign_index"] == sign_index:
                # 在該區域內放置行星符號
                planet_glyph = get_planet_glyph(planet.name)
                planet_label = f"{planet_glyph}"
                
                # 根據宮位調整位置（在區域內偏移）
                offset_x = 0
                offset_y = 0
                if planet.house <= 4:
                    offset_y = 25
                elif planet.house <= 8:
                    offset_x = -20
                    offset_y = 15
                else:
                    offset_x = 20
                    offset_y = -15
                
                svg_parts.append(f'''    <text x="{pos['x'] + offset_x}" y="{pos['y'] + offset_y}">{planet_label}</text>\n''')
                break

    svg_parts.append('  </g>\n')

    # 皇家恆星標記（如果有合相）
    if show_royal_stars and royal_stars:
        svg_parts.append(f'''
  <!-- 皇家恆星 -->
  <g font-family="serif" font-size="16" fill="{palette['gold_leaf']}" text-anchor="middle">
''')
        
        for star_name, star_data in royal_stars.items():
            star_longitude = star_data["sassanian_longitude"]
            star_sign_index = int(star_longitude // 30)
            
            # 找到對應的星座位置
            for pos in zodiac_positions:
                if pos["sign_index"] == star_sign_index:
                    # 八芒星標記
                    star_size = 10
                    cx, cy = pos['x'], pos['y'] - 35
                    
                    svg_parts.append(f'''
    <!-- {star_data['name_pahlavi']} -->
    <g transform="translate({cx}, {cy})">
      <path d="M 0,-{star_size} L {star_size*0.4},-{star_size*0.4} L {star_size},0 L {star_size*0.4},{star_size*0.4}
               L 0,{star_size} L -{star_size*0.4},{star_size*0.4} L -{star_size},0 L -{star_size*0.4},-{star_size*0.4} Z"
            fill="url(#goldGradient)" stroke="{palette['crimson']}" stroke-width="1.5"/>
      <circle cx="0" cy="0" r="{star_size*0.25}" fill="{palette['turquoise']}"/>
    </g>
    <text x="{cx}" y="{cy - 20}" font-size="14" fill="{palette['crimson']}">{star_data['name_pahlavi']}</text>
''')
                    break
        
        svg_parts.append('  </g>\n')

    # Firdar 時間線（底部）
    if show_firdar:
        firdar_y = outer_y + outer_height + 60  # y=560，增加間距
        firdar_height = 45
        firdar_width = outer_width
        
        firdar_periods = [
            {"planet": "Sun", "pahlavi": "Khwarshid", "years": 120, "glyph": "☉"},
            {"planet": "Moon", "pahlavi": "Mah", "years": 108, "glyph": "☽"},
            {"planet": "Saturn", "pahlavi": "Keyvan", "years": 135, "glyph": "♄"},
            {"planet": "Jupiter", "pahlavi": "Ohrmazd", "years": 108, "glyph": "♃"},
            {"planet": "Mars", "pahlavi": "Warhran", "years": 105, "glyph": "♂"},
            {"planet": "Venus", "pahlavi": "Anahid", "years": 108, "glyph": "♀"},
            {"planet": "Mercury", "pahlavi": "Tir", "years": 108, "glyph": "☿"},
        ]
        
        total_years = sum(p["years"] for p in firdar_periods)
        x_scale_firdar = firdar_width / total_years
        current_x = outer_x
        
        svg_parts.append(f'''
  <!-- Firdar 生命週期 -->
  <g>
    <text x="{width/2}" y="{firdar_y - 10}" font-family="serif" font-size="16"
          fill="{palette['crimson']}" text-anchor="middle" font-weight="bold">
      Firdar 生命週期
    </text>
''')
        
        for i, period in enumerate(firdar_periods):
            period_width = period["years"] * x_scale_firdar
            fill_color = palette["gold_leaf"] if i % 2 == 0 else f"rgba(212, 175, 55, 0.3)"
            
            svg_parts.append(f'''
    <rect x="{current_x}" y="{firdar_y}" width="{period_width - 1}" height="{firdar_height}"
          fill="{fill_color}" stroke="{palette['crimson']}" stroke-width="1" />
    <text x="{current_x + period_width/2}" y="{firdar_y + firdar_height/2 + 5}"
          font-family="serif" font-size="12" fill="{palette['dark_indigo']}"
          text-anchor="middle">
      {period['glyph']} {period['years']}
    </text>
''')
            current_x += period_width
        
        svg_parts.append('  </g>\n')

    # 歷史說明
    disclaimer_y = base_height - 15  # y=635
    svg_parts.append(f'''
  <!-- 歷史說明 -->
  <text x="{width/2}" y="{disclaimer_y}" font-family="serif" font-size="12"
        fill="{palette['dark_indigo']}" text-anchor="middle" font-style="italic">
    薩珊傳統占星（Bundahishn、Dorotheus Pahlavi）
  </text>
''')

    # SVG 結尾
    svg_parts.append('</svg>')

    return ''.join(svg_parts)


def generate_sassanian_chart(
    chart_data: Dict,
    width: int = 400,
    height: int = 450,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
):
    """
    生成薩珊傳統占星星盤（返回 Plotly Figure，使用 SVG 作為底圖）
    """
    import plotly.graph_objects as go

    svg_content = generate_sassanian_svg(
        chart_data, width, height,
        show_pahlavi, show_royal_stars, show_firdar
    )

    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=f"data:image/svg+xml;base64,{svg_base64}",
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            sizex=1,
            sizey=1,
            sizing="contain",
            opacity=1,
            layer="below"
        )
    )

    fig.update_layout(
        width=width,
        height=height,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1], scaleanchor="x"),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


def save_sassanian_svg(
    chart_data: Dict,
    output_path: str,
    width: int = 400,
    height: int = 450,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
) -> None:
    """保存薩珊星盤 SVG 到檔案"""
    svg_content = generate_sassanian_svg(
        chart_data, width, height,
        show_pahlavi, show_royal_stars, show_firdar
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)


def render_sassanian_banner_chart(
    chart_data: Dict,
    width: int = 500,
    height: int = 650,
    show_pahlavi: bool = True,
) -> str:
    """
    渲染橫幅格式薩珊星盤（純 SVG）
    
    Parameters
    ----------
    chart_data : Dict
        星盤資料
    width : int
        寬度
    height : int
        高度
    show_pahlavi : bool
        是否顯示 Pahlavi 文字
    
    Returns
    -------
    str
        SVG 字串
    """
    return generate_sassanian_svg(
        chart_data=chart_data,
        width=width,
        height=height,
        show_pahlavi=show_pahlavi,
        show_royal_stars=True,
        show_firdar=False,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("薩珊星盤渲染測試（菱形 12 宮設計）")
    print("=" * 60)

    test_chart = {
        "year": 1980,
        "month": 1,
        "day": 15,
        "hour": 10,
        "minute": 30,
        "longitude": 121.5,
        "latitude": 25.0,
        "timezone": 8.0,
    }

    print("\n生成薩珊星盤 SVG...")
    svg_content = generate_sassanian_svg(test_chart, width=500, height=650)
    print(f"  SVG 長度：{len(svg_content)} 字元")
    print(f"  SVG 尺寸：500x650 (viewBox)")

    output_path = "/tmp/sassanian_chart.svg"
    save_sassanian_svg(test_chart, output_path, width=500, height=650)
    print(f"  已保存至：{output_path}")

    print("\n" + "=" * 60)
    print("測試完成")
