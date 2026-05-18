# astro/lao/renderer.py
"""
婆羅門占星輪 SVG 渲染器 (Brahma Wheel Renderer)
基於《ໄທຣາສາດລາວ ພາກຕົ້ນ》封面與內頁傳統圖示完整實現
- 金色古典風格 + 火焰邊框 + 宇宙背景
- 12 宮位（ຣາສີ）精準分割
- 行星位置動態標註
- 老撾文字標籤
- 與 calculator.py 輸出的 chart_data 完美配合
"""

from typing import Dict, Any
import math

def render_brahma_wheel(chart_data: Dict[str, Any], size: int = 620) -> str:
    """
    生成老撾婆羅門占星輪 SVG
    chart_data 來自 LaoCalculator.get_birth_chart()
    """
    lao_date = chart_data.get("lao_date", {})
    planets = chart_data.get("planets", {})
    sangkhom = chart_data.get("sangkhom", {})

    cx = cy = size // 2
    outer_radius = size * 0.45
    inner_radius = size * 0.22
    house_radius = size * 0.38

    svg_parts = []

    # ==================== 背景與宇宙效果 ====================
    svg_parts.append(f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <!-- 深空背景 -->
        <defs>
            <radialGradient id="cosmic" cx="50%" cy="50%" r="50%" fx="40%" fy="40%">
                <stop offset="0%" stop-color="#1a0f2e"/>
                <stop offset="100%" stop-color="#0a0518"/>
            </radialGradient>
            <!-- 金色漸層 -->
            <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#f5d6a0"/>
                <stop offset="100%" stop-color="#d4a017"/>
            </linearGradient>
        </defs>
        <rect width="{size}" height="{size}" fill="url(#cosmic)"/>
        
        <!-- 細微星點背景 -->
        <g opacity="0.6">
            <circle cx="80" cy="90" r="2" fill="#fff"/>
            <circle cx="520" cy="140" r="1.5" fill="#fff"/>
            <circle cx="120" cy="480" r="2" fill="#fff"/>
            <circle cx="450" cy="420" r="1" fill="#fff"/>
            <!-- 可繼續新增更多星點 -->
        </g>
    ''')

    # ==================== 外圈火焰邊框 ====================
    svg_parts.append(f'''
        <!-- 外圈火焰風格金邊 -->
        <circle 
            cx="{cx}" cy="{cy}" r="{outer_radius + 35}" 
            fill="none" stroke="#b8860b" stroke-width="18" opacity="0.9"/>
        <circle 
            cx="{cx}" cy="{cy}" r="{outer_radius + 28}" 
            fill="none" stroke="#f5d6a0" stroke-width="8"/>
        
        <!-- 內圈金邊 -->
        <circle 
            cx="{cx}" cy="{cy}" r="{inner_radius - 10}" 
            fill="none" stroke="#d4a017" stroke-width="12"/>
    ''')

    # ==================== 12 宮位分割線 + 標籤 ====================
    lao_house_labels = [
        "ມີນ", "ມຶງ", "ເມສ", "ພະຣຸ", "ມິຖຸນ",
        "ກັກກະທັດ", "ສິງ", "ກັນ", "ຕຸລາ", "ພະຈິກ",
        "ທະນູ", "ມະກະຣ"
    ]  # 書中傳統 12 ຣາສີ（可依實際需求調整）

    for i in range(12):
        angle = i * 30 - 90  # 從頂部開始
        rad = math.radians(angle)
        x1 = cx + (inner_radius - 5) * math.cos(rad)
        y1 = cy + (inner_radius - 5) * math.sin(rad)
        x2 = cx + house_radius * math.cos(rad)
        y2 = cy + house_radius * math.sin(rad)

        # 宮位分割線
        svg_parts.append(f'''
            <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" 
                  stroke="#d4a017" stroke-width="3" opacity="0.85"/>
        ''')

        # 宮位標籤
        label_angle = math.radians(i * 30 - 75)
        lx = cx + (house_radius + 38) * math.cos(label_angle)
        ly = cy + (house_radius + 38) * math.sin(label_angle)
        svg_parts.append(f'''
            <text x="{lx}" y="{ly}" text-anchor="middle" dominant-baseline="middle" 
                  font-family="Noto Sans Lao, sans-serif" font-size="18" fill="#f5d6a0" font-weight="bold">
                {lao_house_labels[i]}
            </text>
        ''')

    # ==================== 行星放置 ====================
    planet_symbols = {
        "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀",
        "mars": "♂", "jupiter": "♃", "saturn": "♄",
        "rahu": "☊", "ketu": "☋"
    }

    for name, data in planets.items():
        if name not in planet_symbols:
            continue
        lon = data.get("longitude", 0)
        angle = math.radians(lon - 90)  # 黃道座標轉 SVG 角度
        r = house_radius * 0.75
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)

        symbol = planet_symbols.get(name, "★")
        color = "#ffeb3b" if name == "sun" else "#a5f3fc" if name == "moon" else "#f5d6a0"

        svg_parts.append(f'''
            <text x="{px}" y="{py}" font-size="28" text-anchor="middle" 
                  dominant-baseline="middle" fill="{color}" font-weight="bold">
                {symbol}
            </text>
            <!-- 行星名稱小標 -->
            <text x="{px}" y="{py + 38}" font-size="11" text-anchor="middle" 
                  fill="#d4a017" font-family="Noto Sans Lao, sans-serif">
                {name.upper()[:3]}
            </text>
        ''')

    # ==================== 中心資訊 ====================
    year_type = lao_date.get("year_type", "ປົກກະຕິ")
    fortune = sangkhom.get("fortune_level", "中")
    svg_parts.append(f'''
        <!-- 中心圓 -->
        <circle cx="{cx}" cy="{cy}" r="{inner_radius}" fill="#1a0f2e" stroke="#d4a017" stroke-width="14"/>
        
        <!-- 標題 -->
        <text x="{cx}" y="{cy - 45}" text-anchor="middle" font-family="Noto Sans Lao, sans-serif" 
              font-size="22" fill="#f5d6a0" font-weight="bold">ໄທຣາສາດລາວ</text>
        <text x="{cx}" y="{cy - 18}" text-anchor="middle" font-size="13" fill="#d4a017">
            {lao_date.get("lao_year", "")} ປີ {year_type}
        </text>
        
        <!-- 吉凶 -->
        <text x="{cx}" y="{cy + 18}" text-anchor="middle" font-size="18" fill="#ffeb3b" font-weight="bold">
            {fortune}
        </text>
        
        <!-- 日期 -->
        <text x="{cx}" y="{cy + 55}" text-anchor="middle" font-size="12" fill="#a5f3fc">
            {lao_date.get("weekday_lao", "")}
        </text>
    ''')

    svg_parts.append('</svg>')

    return ''.join(svg_parts)


# ==================== 測試用 ====================
if __name__ == "__main__":
    # 測試生成
    test_chart = {
        "lao_date": {"lao_year": 2076, "weekday_lao": "ວັນຈັນ", "year_type": "ປົກກະຕິ"},
        "planets": {
            "sun": {"longitude": 45},
            "moon": {"longitude": 120},
            "jupiter": {"longitude": 280},
        },
        "sangkhom": {"fortune_level": "大吉"}
    }
    svg = render_brahma_wheel(test_chart)
    print("✅ 婆羅門占星輪 SVG 生成成功！（長度:", len(svg), "字符）")
    # 可直接存成 .svg 檔案測試
    with open("/tmp/lao_brahma_wheel.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("已儲存測試檔案：/tmp/lao_brahma_wheel.svg")
