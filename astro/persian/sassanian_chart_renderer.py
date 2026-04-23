"""
astro/sassanian/sassanian_chart_renderer.py — 薩珊傳統占星星盤渲染器（完整優化版）

Sassanian Traditional Star Chart Renderer
基於薩珊王朝藝術風格的方形/橫幅格式星盤

已針對 Plotly SVG 顯示問題全面修正：
- 使用 base64 + add_layout_image 正確渲染所有自訂 SVG 圖示（Faravahar、火壇、八芒星、石榴邊框）
- 完全鎖定像素座標 + 隱藏軸線（解決空白/座標異常）
- 宮位網格從左下角開始（符合薩珊傳統）
- 邊框與角落裝飾位置精準對齊
- 保留全部原有功能（Pahlavi 文字、皇家四星、Firdar 時間線）

References
----------
- Sassanian silver plates (Metropolitan Museum, Louvre)
- Taq-e Bostan rock reliefs (6th-7th century CE)
- Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
- Greater Bundahishn illustrations
"""

from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import swisseph as swe
from datetime import datetime
import json
import os
import base64  # ← 新增：用於 SVG base64 轉換

from astro.persian.sassanian_astronomy import (
    compute_sassanian_planet_positions,
    get_sassanian_houses,
    get_royal_stars_positions,
    calculate_sassanian_ayanamsa,
    SassanianPlanetPosition,
)
from astro.persian.sassanian_symbols import (
    get_sassanian_color_palette,
    get_pahlavi_name,
    get_royal_star_pahlavi,
    render_faravahar_element,
    render_eight_pointed_star,
    render_fire_altar,
    render_pomegranate_border,
    get_zodiac_glyph,
    get_planet_glyph,
)


def _add_svg_icon(
    fig: go.Figure,
    svg_str: str,
    x: float,
    y: float,
    size: float,
    row: int = 1,
    layer: str = "above",
    opacity: float = 0.95,
) -> None:
    """
    關鍵修復函數：將 sassanian_symbols 中的 SVG 片段轉成 Plotly 可正確顯示的 layout_image
    解決原本 add_annotation 直接顯示 SVG 程式碼的問題
    """
    if not svg_str or not svg_str.strip():
        return

    # 如果 render_* 函數回傳的是片段（<path>、<g> 等），自動包成完整 SVG
    svg_str = svg_str.strip()
    if not svg_str.startswith("<svg"):
        svg_str = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'{svg_str}</svg>'
        )

    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")

    fig.add_layout_image(
        dict(
            source=f"data:image/svg+xml;base64,{b64}",
            xref="x",
            yref="y",
            x=x,
            y=y,
            sizex=size,
            sizey=size,
            sizing="contain",
            opacity=opacity,
            layer=layer,
            xanchor="center",
            yanchor="middle",
        )
    )


def generate_sassanian_chart(
    chart_data: Dict,
    width: int = 1200,
    height: int = 900,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
) -> go.Figure:
    """
    生成薩珊傳統占星星盤（方形格式）
    """
    # 獲取薩珊色彩調色盤
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

    # 計算薩珊行星位置與宮位
    planet_positions = compute_sassanian_planet_positions(
        year, month, day, hour, minute, longitude, latitude, timezone
    )
    houses = get_sassanian_houses(
        year, month, day, hour, minute, longitude, latitude, timezone
    )
    royal_stars = get_royal_stars_positions(julian_day) if show_royal_stars else {}

    # 創建子圖佈局
    if show_firdar:
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.75, 0.25],
            vertical_spacing=0.03,
            specs=[[{"type": "scatter"}], [{"type": "scatter"}]]
        )
        main_height = height * 0.75
    else:
        fig = make_subplots(rows=1, cols=1, specs=[[{"type": "scatter"}]])
        main_height = height

    # 設置圖表尺寸與背景
    fig.update_layout(
        width=width,
        height=height,
        plot_bgcolor=palette["parchment"],
        paper_bgcolor=palette["parchment"],
        margin=dict(l=15, r=15, t=60, b=40 if show_firdar else 30),
        showlegend=False,
        font_family="serif",  # 更接近古波斯手稿風格
    )

    # === 關鍵修正：鎖定像素座標 + 隱藏所有軸線 ===
    fig.update_xaxes(
        range=[0, width], visible=False, showgrid=False, zeroline=False, showticklabels=False,
        row=1, col=1
    )
    fig.update_yaxes(
        range=[0, main_height], visible=False, showgrid=False, zeroline=False, showticklabels=False,
        row=1, col=1
    )
    if show_firdar:
        fig.update_xaxes(range=[0, width], visible=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=1)
        fig.update_yaxes(range=[0, height*0.25], visible=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=1)

    # dummy trace 確保座標系統正確
    fig.add_trace(
        go.Scatter(x=[0, width], y=[0, main_height], mode='markers',
                   marker=dict(color='rgba(0,0,0,0)'), hoverinfo='skip'),
        row=1, col=1
    )

    # === 邊框裝飾（石榴邊框）===
    border_svg = render_pomegranate_border(0, 0, width, main_height)
    if border_svg:
        _add_svg_icon(
            fig, border_svg,
            x=width/2, y=main_height/2,
            size=max(width, main_height) * 1.02,
            row=1, layer="below"
        )

    # 渲染主星盤（方形格式）
    _render_square_chart(
        fig=fig,
        row=1,
        houses=houses,
        planet_positions=planet_positions,
        royal_stars=royal_stars,
        palette=palette,
        show_pahlavi=show_pahlavi,
        width=width,
        height=main_height,
    )

    # 添加 Firdar 時間線
    if show_firdar:
        _render_firdar_timeline(
            fig=fig,
            row=2,
            chart_data=chart_data,
            palette=palette,
            show_pahlavi=show_pahlavi,
            width=width,
            height=height * 0.25,
        )

    # === 角落 Faravahar 裝飾（薩珊經典對稱元素）===
    corner_size = 58
    faravahar_svg = render_faravahar_element(0, 0, corner_size)
    _add_svg_icon(fig, faravahar_svg, x=corner_size, y=main_height - corner_size,
                  size=corner_size * 2.1, row=1, layer="above")
    _add_svg_icon(fig, faravahar_svg, x=width - corner_size, y=main_height - corner_size,
                  size=corner_size * 2.1, row=1, layer="above")

    # 添加標題
    title_text = "波斯薩珊傳統占星星盤 | Sassanian Traditional Horoscope"
    if show_pahlavi:
        title_text += "\n𐭮𐭠𐭮𐭠𐭭 𐭲𐭠𐭫𐭹𐭹𐭠 (Sassanian Astrology)"

    fig.add_annotation(
        x=width / 2,
        y=height - 25,
        xref="x", yref="y",
        text=title_text,
        showarrow=False,
        font=dict(size=18, color=palette["crimson"], family="serif"),
        align="center",
    )

    # 添加歷史說明
    disclaimer = (
        "此星盤依據薩珊王朝古文獻（Bundahishn、Dorotheus Pahlavi 譯本）"
        "與出土波斯銀盤、印章藝術風格重建，非現代圓形輪盤。"
    )
    fig.add_annotation(
        x=width / 2,
        y=12,
        xref="x", yref="y",
        text=disclaimer,
        showarrow=False,
        font=dict(size=9.5, color=palette["dark_indigo"]),
        align="center",
    )

    return fig


def _render_square_chart(
    fig: go.Figure,
    row: int,
    houses: List[Dict],
    planet_positions: List[SassanianPlanetPosition],
    royal_stars: Dict,
    palette: Dict[str, str],
    show_pahlavi: bool,
    width: int,
    height: int,
) -> None:
    """
    渲染方形星盤（3×4 宮位網格，符合薩珊傳統）
    """
    grid_cols = 4
    grid_rows = 3
    cell_width = width / grid_cols
    cell_height = height / grid_rows

    # 宮位順序（薩珊傳統：左下角為第 1 宮，逆時針）
    house_positions = [
        (0, 0), (1, 0), (2, 0), (3, 0),  # 底部行（1-4 宮）
        (0, 1), (1, 1), (2, 1), (3, 1),  # 中間行（5-8 宮）
        (0, 2), (1, 2), (2, 2), (3, 2),  # 頂部行（9-12 宮）
    ]

    # 繪製宮位格線
    for i, house in enumerate(houses):
        col, row_idx = house_positions[i]
        x = col * cell_width
        y = row_idx * cell_height

        # 宮位邊框
        fig.add_shape(
            type="rect",
            x0=x + 6, y0=y + 6,
            x1=x + cell_width - 6, y1=y + cell_height - 6,
            xref="x", yref="y",
            line=dict(color=palette["gold_leaf"], width=2.5),
            fillcolor=palette["dark_indigo"] if i == 0 else "rgba(26, 35, 126, 0.25)",
        )

        # 宮位編號與意義
        house_label = f"宮 {house['house_number']}"
        if show_pahlavi:
            house_label += f"\n({house['meaning_pahlavi']})"

        fig.add_annotation(
            x=x + cell_width / 2,
            y=y + cell_height - 18,
            xref="x", yref="y",
            text=house_label,
            showarrow=False,
            font=dict(size=11, color=palette["gold_leaf"]),
            align="center",
        )

        # 星座名稱
        sign_label = f"{house['sign']}"
        if show_pahlavi:
            sign_label += f"\n({house['sign_pahlavi']})"

        fig.add_annotation(
            x=x + cell_width / 2,
            y=y + cell_height / 2,
            xref="x", yref="y",
            text=sign_label,
            showarrow=False,
            font=dict(size=13, color=palette["turquoise"]),
            align="center",
        )

        # 宮位內行星
        planets_in_house = [p for p in planet_positions if p.house == house["house_number"]]
        for j, planet in enumerate(planets_in_house):
            planet_y = y + cell_height / 2 - 28 - j * 24
            planet_label = f"{get_planet_glyph(planet.name)} {planet.name}"
            if show_pahlavi:
                planet_label += f" ({planet.name_pahlavi})"
            if planet.is_retrograde:
                planet_label += " ℞"

            fig.add_annotation(
                x=x + cell_width / 2,
                y=planet_y,
                xref="x", yref="y",
                text=planet_label,
                showarrow=False,
                font=dict(size=10.5, color=palette["white"]),
                align="center",
            )

    # 添加上升點標記（火壇）
    asc_col, asc_row = house_positions[0]
    _add_svg_icon(
        fig,
        render_fire_altar(0, 0, 40),
        x=asc_col * cell_width + 34,
        y=asc_row * cell_height + cell_height - 38,
        size=40,
        row=row,
        layer="above"
    )

    # 添加皇家恆星標記
    for star_name, star_data in royal_stars.items():
        star_longitude = star_data["sassanian_longitude"]
        star_sign_index = int(star_longitude // 30)

        for i, house in enumerate(houses):
            house_sign_index = int(house["longitude_start"] // 30)
            if house_sign_index == star_sign_index:
                col, row_idx = house_positions[i]
                x_pos = col * cell_width + cell_width - 32
                y_pos = row_idx * cell_height + 32

                _add_svg_icon(
                    fig,
                    render_eight_pointed_star(0, 0, 24),
                    x=x_pos, y=y_pos,
                    size=24,
                    row=row,
                    layer="above"
                )

                star_label = star_data["name_pahlavi"] if show_pahlavi else star_data["name_en"]
                fig.add_annotation(
                    x=x_pos, y=y_pos - 29,
                    xref="x", yref="y",
                    text=star_label,
                    showarrow=False,
                    font=dict(size=9.5, color=palette["gold_leaf"]),
                    align="center",
                )
                break


def _render_firdar_timeline(
    fig: go.Figure,
    row: int,
    chart_data: Dict,
    palette: Dict[str, str],
    show_pahlavi: bool,
    width: int,
    height: int,
) -> None:
    """Firdar 生命週期時間線（保持原功能）"""
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
    x_start = 20
    timeline_width = width - 40
    x_scale = timeline_width / total_years
    current_x = x_start

    for i, period in enumerate(firdar_periods):
        period_width = period["years"] * x_scale

        fig.add_shape(
            type="rect",
            x0=current_x, y0=20,
            x1=current_x + period_width, y1=height - 20,
            xref="x", yref="y",
            line=dict(color=palette["gold_leaf"], width=1.5),
            fillcolor=palette["gold_leaf"] if i % 2 == 0 else "rgba(212, 175, 55, 0.35)",
        )

        label = f"{period['glyph']} {period['planet']}"
        if show_pahlavi:
            label += f"\n({period['pahlavi']})"
        label += f"\n{period['years']}年"

        fig.add_annotation(
            x=current_x + period_width / 2,
            y=height / 2 + 25,
            xref="x", yref="y",
            text=label,
            showarrow=False,
            font=dict(size=10, color=palette["dark_indigo"]),
            align="center",
            textangle=90,
        )
        current_x += period_width

    fig.add_annotation(
        x=width / 2, y=height - 8,
        xref="x", yref="y",
        text="Firdar 生命週期 | Sassanian Planetary Periods",
        showarrow=False,
        font=dict(size=13, color=palette["crimson"]),
        align="center",
    )


def render_sassanian_banner_chart(
    chart_data: Dict,
    width: int = 1400,
    height: int = 600,
    show_pahlavi: bool = True,
) -> go.Figure:
    """橫幅格式（簡化版，直接呼叫主函數）"""
    return generate_sassanian_chart(
        chart_data=chart_data,
        width=width,
        height=height,
        show_pahlavi=show_pahlavi,
        show_firdar=False,
    )


if __name__ == "__main__":
    print("=" * 70)
    print("薩珊星盤渲染器測試（完整優化版）")
    print("=" * 70)

    test_chart = {
        "year": 1980, "month": 1, "day": 15,
        "hour": 10, "minute": 30,
        "longitude": 121.5, "latitude": 25.0, "timezone": 8.0,
    }

    print("生成方形薩珊星盤...")
    fig = generate_sassanian_chart(test_chart, width=1280, height=920)
    print(f"  ✓ 圖表尺寸：{fig.layout.width} × {fig.layout.height}")

    # 儲存高品質 SVG（推薦）
    fig.write_image("sassanian_chart_optimized.svg", format="svg", engine="kaleido")
    print("  ✓ 已儲存為 sassanian_chart_optimized.svg")

    print("\n測試完成！\n請在 Streamlit 中使用 st.plotly_chart(fig) 顯示")