"""
astro/tieban/tieban_renderer.py — 鐵板神數 SVG 渲染器

Tie Ban Shen Shu Chart SVG Renderer

純 SVG 星盤圖渲染（非 Plotly），遵循用戶偏好
參考 Sassanian/Persian 鑽石盤設計，融合鐵板神數特色

特點：
- 外層正方形 + 內層菱形（鑽石盤）
- 12 宮位環繞排列
- 鐵板神數號碼、刻分、密碼表可视化
- 支援繁體中文 UI

使用方式：
    svg = render_tieban_chart_svg(result, language='zh')
    st.components.v1.html(svg, height=600)
"""

from typing import Dict, Any, Optional
from astro.tieban.tieban_calculator import TieBanResult, EARTHLY_BRANCHES, PALACE_NAMES

# 十二宮名稱翻譯 (Palace Names Translation)
PALACE_NAMES_EN = {
    "命宮": "Life",
    "兄弟宮": "Siblings",
    "夫妻宮": "Spouse",
    "子女宮": "Children",
    "財帛宮": "Wealth",
    "疾厄宮": "Health",
    "遷移宮": "Travel",
    "交友宮": "Friends",
    "官祿宮": "Career",
    "田宅宮": "Property",
    "福德宮": "Fortune",
    "父母宮": "Parents",
}

def get_palace_name(palace_name: str, language: str = 'zh') -> str:
    """獲取宮位名稱（支持中英文）"""
    if language == 'en':
        return PALACE_NAMES_EN.get(palace_name, palace_name)
    return palace_name


def render_tieban_chart_svg(result: TieBanResult, 
                             language: str = 'zh',
                             width: int = 500,
                             height: int = 600) -> str:
    """
    渲染鐵板神數 SVG 星盤圖（響應式設計）
    
    Parameters
    ----------
    result : TieBanResult
        鐵板神數推算結果
    language : str
        語言 ('zh' 繁體中文 或 'en' 英文)
    width : int
        SVG 參考寬度（實際由容器控制）
    height : int
        SVG 參考高度（實際由容器控制）
    
    Returns
    -------
    str
        SVG XML 字符串（包含響應式 HTML 容器）
    """
    # 顏色配置（鐵板神數傳統配色：橙紅 #FF6B35）
    colors = {
        'bg': '#1a1a2e',
        'outer_square': '#FF6B35',
        'inner_diamond': '#FFD93D',
        'text_primary': '#FFFFFF',
        'text_secondary': '#A0A0A0',
        'accent': '#6BCB77',
        'palace_bg': '#16213e',
        'highlight': '#E94560',
    }
    
    # 中心點
    cx = width // 2
    cy = height // 2 - 50
    
    # 外層正方形（300x300）
    square_size = 300
    outer_x = cx - square_size // 2
    outer_y = cy - square_size // 2
    
    # 內層菱形（150x150）
    diamond_size = 150
    diamond_x = cx - diamond_size // 2
    diamond_y = cy - diamond_size // 2
    
    # 計算 12 宮位位置（環繞外層正方形）
    # 3 上、3 左、3 下、3 右
    palace_positions = _calculate_palace_positions(result.ming_palace, outer_x, outer_y, square_size)
    
    # SVG 內容
    svg_parts = []
    
    # SVG 頭
    title_zh = "鐵板神數"
    title_en = "Iron Plate Divine Numbers"
    subtitle = "Tie Ban Shen Shu · Iron Plate Divine Numbers"
    
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 {width} {height}"
     preserveAspectRatio="xMidYMid meet"
     style="width: 100%; height: auto; max-width: 100%;">
    
    <!-- 背景 -->
    <rect width="{width}" height="{height}" fill="{colors['bg']}"/>
    
    <!-- 標題 -->
    <text x="{cx}" y="40" text-anchor="middle" 
          font-size="24" font-weight="bold" fill="{colors['text_primary']}">
        {title_zh if language == 'zh' else title_en}
    </text>
    <text x="{cx}" y="65" text-anchor="middle" 
          font-size="14" fill="{colors['text_secondary']}">
        {subtitle}
    </text>
''')
    
    # 外層正方形
    svg_parts.append(f'''
    <!-- 外層正方形 -->
    <rect x="{outer_x}" y="{outer_y}" 
          width="{square_size}" height="{square_size}" 
          fill="none" stroke="{colors['outer_square']}" stroke-width="3"/>
''')
    
    # 內層菱形（旋轉 45 度的正方形）
    diamond_points = f"{cx},{diamond_y - diamond_size//2} {diamond_x + diamond_size//2},{cy} {cx},{diamond_y + diamond_size//2} {diamond_x - diamond_size//2},{cy}"
    svg_parts.append(f'''
    <!-- 內層菱形 -->
    <polygon points="{diamond_points}" 
             fill="none" stroke="{colors['inner_diamond']}" stroke-width="2"/>
''')
    
    # 對角線（連接外層正方形四角）
    svg_parts.append(f'''
    <!-- 對角線 -->
    <line x1="{outer_x}" y1="{outer_y}" x2="{outer_x + square_size}" y2="{outer_y + square_size}" 
          stroke="{colors['text_secondary']}" stroke-width="1" opacity="0.5"/>
    <line x1="{outer_x + square_size}" y1="{outer_y}" x2="{outer_x}" y2="{outer_y + square_size}" 
          stroke="{colors['text_secondary']}" stroke-width="1" opacity="0.5"/>
''')
    
    # 12 宮位
    svg_parts.append('''
    <!-- 12 宮位 -->
''')
    
    for i, (palace_name, branch) in enumerate(result.palaces.items()):
        pos = palace_positions[i]
        is_ming_palace = (palace_name == '命宮')
        
        # 宮位背景
        bg_color = colors['highlight'] if is_ming_palace else colors['palace_bg']
        text_color = colors['bg'] if is_ming_palace else colors['text_primary']
        
        # 獲取該宮位的條文
        palace_verse_info = result.palace_verses.get(palace_name, {})
        verse_text = palace_verse_info.get('verse', '')
        verse_number = palace_verse_info.get('number', '')
        # 截斷條文（最多 10 字）
        verse_preview = verse_text[:10] + "…" if len(verse_text) > 10 else verse_text
        
        # 宮位名稱（支持英文）
        palace_display_name = get_palace_name(palace_name, language)
        
        svg_parts.append(f'''
    <!-- {palace_name} -->
    <rect x="{pos['x']}" y="{pos['y']}" width="80" height="50" 
          fill="{bg_color}" stroke="{colors['outer_square']}" stroke-width="1" rx="5"/>
    <text x="{pos['x'] + 40}" y="{pos['y'] + 14}" text-anchor="middle" 
          font-size="9" font-weight="bold" fill="{text_color}">
        {palace_display_name}
    </text>
    <text x="{pos['x'] + 40}" y="{pos['y'] + 28}" text-anchor="middle" 
          font-size="13" font-weight="bold" fill="{colors['inner_diamond']}">
        {branch}
    </text>
    <text x="{pos['x'] + 40}" y="{pos['y'] + 40}" text-anchor="middle" 
          font-size="7" fill="{colors['text_secondary']}">
        {verse_preview}
    </text>
    <text x="{pos['x'] + 5}" y="{pos['y'] + 48}" text-anchor="start" 
          font-size="6" fill="{colors['highlight']}">
        #{verse_number}
    </text>
''')
    
    # 中心信息區
    info_y = cy + square_size // 2 + 30
    svg_parts.append(f'''
    <!-- 中心信息區 -->
    <rect x="{cx - 120}" y="{info_y}" width="240" height="120" 
          fill="{colors['palace_bg']}" stroke="{colors['accent']}" stroke-width="2" rx="10"/>
    
    <!-- 鐵板神數號碼 -->
    <text x="{cx}" y="{info_y + 25}" text-anchor="middle" 
          font-size="14" fill="{colors['text_secondary']}">
        鐵板神數號碼
    </text>
    <text x="{cx}" y="{info_y + 50}" text-anchor="middle" 
          font-size="24" font-weight="bold" fill="{colors['highlight']}">
        {result.tieban_number}
    </text>
    
    <!-- 刻分 -->
    <text x="{cx - 60}" y="{info_y + 80}" text-anchor="middle" 
          font-size="12" fill="{colors['text_primary']}">
        刻：{result.ke}
    </text>
    <text x="{cx + 60}" y="{info_y + 80}" text-anchor="middle" 
          font-size="12" fill="{colors['text_primary']}">
        分：{result.fen}
    </text>
    
    <!-- 河洛數 -->
    <text x="{cx}" y="{info_y + 105}" text-anchor="middle" 
          font-size="12" fill="{colors['text_secondary']}">
        河洛數：{result.he_luo_number}
    </text>
''')
    
    # 命宮身宮信息
    svg_parts.append(f'''
    <!-- 命宮身宮 -->
    <text x="{cx - 150}" y="{info_y - 15}" text-anchor="middle" 
          font-size="12" fill="{colors['accent']}">
        命宮：{result.ming_palace}
    </text>
    <text x="{cx + 150}" y="{info_y - 15}" text-anchor="middle" 
          font-size="12" fill="{colors['accent']}">
        身宮：{result.shen_palace}
    </text>
''')
    
    # 五行局
    svg_parts.append(f'''
    <!-- 五行局 -->
    <text x="{cx}" y="{info_y - 15}" text-anchor="middle" 
          font-size="12" fill="{colors['inner_diamond']}">
        {result.wuxing_ju}
    </text>
''')
    
    # 條文預覽（截斷）
    verse_preview = result.verse[:40] + "..." if len(result.verse) > 40 else result.verse
    verse_y = info_y + 160
    
    # 條文分類和標籤
    category = result.verse_data.get('category', '') if isinstance(result.verse_data, dict) else ''
    tags = result.verse_data.get('tags', []) if isinstance(result.verse_data, dict) else []
    
    svg_parts.append(f'''
    <!-- 條文預覽 -->
    <text x="{cx}" y="{verse_y}" text-anchor="middle" 
          font-size="11" fill="{colors['text_secondary']}">
        {verse_preview}
    </text>
''')
    
    # 條文分類
    if category:
        svg_parts.append(f'''
    <text x="{cx}" y="{verse_y + 18}" text-anchor="middle" 
          font-size="10" fill="{colors['accent']}">
        【{category}】
    </text>
''')
    
    # 標籤（最多顯示 3 個）
    if tags:
        tags_text = " · ".join(tags[:3])
        svg_parts.append(f'''
    <text x="{cx}" y="{verse_y + 32}" text-anchor="middle" 
          font-size="9" fill="{colors['text_secondary']}">
        {tags_text}
    </text>
''')
    
    # SVG 尾
    svg_parts.append('''
</svg>
''')
    
    svg_content = ''.join(svg_parts)
    
    # 響應式 HTML 容器包裝（帶 CSS 樣式）
    html = f'''
<style>
.tieban-chart-container {{
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    padding: 10px;
}}

.tieban-chart-container svg {{
    width: 100%;
    height: auto;
    max-width: 100%;
}}

/* 移動端適配 */
@media (max-width: 768px) {{
    .tieban-chart-container {{
        max-width: 100%;
        padding: 5px;
    }}
}}

/* 桌面端適配 */
@media (min-width: 769px) {{
    .tieban-chart-container {{
        max-width: 600px;
    }}
}}
</style>

<div class="tieban-chart-container">
    <div style="position: relative; width: 100%; height: auto; aspect-ratio: 500/600;">
        {svg_content}
    </div>
</div>
'''
    
    return html


def _calculate_palace_positions(ming_palace_branch: str, 
                                 outer_x: int, 
                                 outer_y: int, 
                                 square_size: int) -> list:
    """
    計算 12 宮位位置（環繞外層正方形）
    
    排列方式：
    - 上方 3 宮（從右到左：父母、福德、田宅）
    - 左方 3 宮（從上到下：官祿、交友、遷移）
    - 下方 3 宮（從左到右：疾厄、財帛、子女）
    - 右方 3 宮（從下到上：夫妻、兄弟、命宮）
    
    Returns
    -------
    list
        [{x, y}, ...] 12 個位置
    """
    positions = []
    
    # 宮位間距
    gap = square_size // 3
    palace_width = 80
    palace_height = 50
    
    # 上方 3 宮（從右到左）
    for i in range(3):
        x = outer_x + square_size - palace_width - (i * gap) + gap // 2 - 10
        y = outer_y - palace_height - 10
        positions.append({'x': x, 'y': y})
    
    # 左方 3 宮（從上到下）
    for i in range(3):
        x = outer_x - palace_width - 10
        y = outer_y + (i * gap) + gap // 2 - palace_height // 2
        positions.append({'x': x, 'y': y})
    
    # 下方 3 宮（從左到右）
    for i in range(3):
        x = outer_x + (i * gap) + gap // 2 - palace_width // 2 - 10
        y = outer_y + square_size + 10
        positions.append({'x': x, 'y': y})
    
    # 右方 3 宮（從下到上）
    for i in range(3):
        x = outer_x + square_size + 10
        y = outer_y + square_size - palace_height - (i * gap) + gap // 2 - 10
        positions.append({'x': x, 'y': y})
    
    # 根據命宮位置調整順序（使命宮在右方第一位）
    if ming_palace_branch:
        ming_idx = EARTHLY_BRANCHES.index(ming_palace_branch)
        # 旋轉位置列表使命宮對應正確
        positions = positions[ming_idx:] + positions[:ming_idx]
    
    return positions


def render_tieban_number_card(result: TieBanResult, 
                               language: str = 'zh') -> str:
    """
    渲染鐵板神數號碼卡片（簡化版）
    
    用於 Streamlit 側邊欄或信息卡片
    """
    colors = {
        'bg': '#16213e',
        'text': '#FFFFFF',
        'accent': '#FF6B35',
        'highlight': '#FFD93D',
    }
    
    html = f'''
<div style="background: {colors['bg']}; padding: 20px; border-radius: 10px; border: 2px solid {colors['accent']};">
    <h3 style="color: {colors['text']}; margin: 0 0 15px 0; text-align: center;">
        🔮 鐵板神數
    </h3>
    
    <div style="text-align: center; margin: 20px 0;">
        <div style="font-size: 32px; font-weight: bold; color: {colors['highlight']};">
            {result.tieban_number}
        </div>
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7;">
            萬千百十號
        </div>
    </div>
    
    <div style="display: flex; justify-content: space-around; margin: 15px 0;">
        <div style="text-align: center;">
            <div style="font-size: 18px; color: {colors['text']};">{result.ke}</div>
            <div style="font-size: 11px; color: {colors['text']}; opacity: 0.7;">刻</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 18px; color: {colors['text']};">{result.fen}</div>
            <div style="font-size: 11px; color: {colors['text']}; opacity: 0.7;">分</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 18px; color: {colors['text']};">{result.he_luo_number}</div>
            <div style="font-size: 11px; color: {colors['text']}; opacity: 0.7;">河洛數</div>
        </div>
    </div>
    
    <div style="border-top: 1px solid {colors['accent']}; margin: 15px 0; padding-top: 15px;">
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7; margin-bottom: 5px;">
            命宮 / 身宮
        </div>
        <div style="font-size: 16px; color: {colors['highlight']};">
            {result.ming_palace} / {result.shen_palace}
        </div>
    </div>
    
    <div style="border-top: 1px solid {colors['accent']}; margin: 15px 0; padding-top: 15px;">
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7; margin-bottom: 5px;">
            五行局
        </div>
        <div style="font-size: 16px; color: {colors['accent']};">
            {result.wuxing_ju}
        </div>
    </div>
    
    <div style="border-top: 1px solid {colors['accent']}; margin: 15px 0; padding-top: 15px;">
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7; margin-bottom: 5px;">
            條文
        </div>
        <div style="font-size: 13px; color: {colors['text']}; line-height: 1.6;">
            {result.verse}
        </div>
        {f'<div style="font-size: 11px; color: {colors["accent"]}; margin-top: 8px;">【{result.verse_data.get("category", "")}】</div>' if isinstance(result.verse_data, dict) and result.verse_data.get('category') else ''}
        {f'<div style="font-size: 10px; color: {colors["text"]}; opacity: 0.6; margin-top: 4px;">{" · ".join(result.verse_data.get("tags", [])[:3])}</div>' if isinstance(result.verse_data, dict) and result.verse_data.get('tags') else ''}
    </div>
</div>
'''
    
    return html
