# -*- coding: utf-8 -*-
"""
Reamker Astrology Renderer - Pure SVG Charts
高棉占星渲染器 - 純 SVG 星盤圖
"""

from typing import Dict, List, Optional


def render_khmer_zodiac_svg(zodiac_data: Dict, language: str = "zh") -> str:
    """
    渲染高棉 12 生肖 SVG
    """
    kh = zodiac_data.get("kh", "ជូត")
    en = zodiac_data.get("en", "Rat")
    zh = zodiac_data.get("zh", "鼠")
    element_kh = zodiac_data.get("element", {}).get("kh", "ធាតុទឹក")
    element_zh = zodiac_data.get("element", {}).get("zh", "水")
    element_color = zodiac_data.get("element", {}).get("color", "#3b82f6")
    
    # 根據語言選擇顯示
    if language == "zh":
        zodiac_name = f"{zh} ({kh})"
        element_name = f"{element_zh} ({element_kh})"
    else:
        zodiac_name = f"{en} ({kh})"
        element_name = element_kh
    
    svg = f'''<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <!-- 背景 -->
  <rect width="400" height="200" fill="linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"/>
  
  <!-- 外框 -->
  <rect x="10" y="10" width="380" height="180" rx="15" fill="none" stroke="{element_color}" stroke-width="3"/>
  
  <!-- 高棉文標題 -->
  <text x="200" y="45" text-anchor="middle" font-family="Khmer OS, sans-serif" font-size="28" fill="#fbbf24" font-weight="bold">
    ឆ្នាំ {kh}
  </text>
  
  <!-- 生肖名稱 -->
  <text x="200" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#ffffff" font-weight="bold">
    {zodiac_name}
  </text>
  
  <!-- 五行元素 -->
  <text x="200" y="125" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="{element_color}" font-weight="bold">
    {element_name}
  </text>
  
  <!-- 裝飾圖案：高棉傳統花紋 -->
  <circle cx="50" cy="100" r="8" fill="{element_color}" opacity="0.6"/>
  <circle cx="350" cy="100" r="8" fill="{element_color}" opacity="0.6"/>
  <path d="M 80 150 Q 200 170 320 150" stroke="{element_color}" stroke-width="2" fill="none" opacity="0.4"/>
</svg>'''
    
    return svg


def render_reamker_grid_svg(reamker_data: Dict, language: str = "zh") -> str:
    """
    渲染 Reamker 32 格命盤 SVG
    基於 Bizot TK480 手稿的傳統格格式
    """
    character = reamker_data.get("character", {})
    stage_zh = reamker_data.get("stage_zh", "童年期")
    stage_kh = reamker_data.get("stage_kh", "កុមារភាព")
    prophecy_zh = reamker_data.get("prophecy_zh", "預言內容")
    prophecy_kh = reamker_data.get("prophecy_kh", "ព្យាករណ៍")
    remedy_zh = reamker_data.get("remedy_zh", "化解儀式")
    remedy_kh = reamker_data.get("remedy_kh", "ពិធីសង្គ្រោះ")
    direction = reamker_data.get("direction", {})
    cell = reamker_data.get("cell", 0)
    age = reamker_data.get("age", 0)
    
    char_kh = character.get("kh", "ពិភេក")
    char_en = character.get("en", "Bibhek")
    char_clan = character.get("clan", "human")
    
    # 根據氏族選擇顏色
    clan_colors = {
        "god": "#fbbf24",      # 金色 - 神族
        "human": "#60a5fa",    # 藍色 - 人族
        "yaksha": "#f87171",   # 紅色 - 夜叉族
    }
    clan_color = clan_colors.get(char_clan, "#60a5fa")
    
    # 根據語言選擇顯示
    if language == "zh":
        stage_text = f"{stage_kh} ({stage_zh})"
        prophecy_text = prophecy_zh
        remedy_text = remedy_zh
        direction_text = f"{direction.get('zh', '東北')} ({direction.get('kh', 'ឦសាន')})"
        title = "羅摩衍那占星命盤"
    else:
        stage_text = f"{stage_kh} ({reamker_data.get('stage_en', 'Childhood')})"
        prophecy_text = "Prophecy content"
        remedy_text = "Remedy ritual"
        direction_text = f"{direction.get('en', 'Northeast')} ({direction.get('kh', 'ឦសាន')})"
        title = "Reamker Astrology Chart"
    
    # 計算化解儀式區所需高度（根據文字長度）
    # 每行約 40 個字符，每行高度約 25px
    remedy_kh_lines = max(1, len(remedy_kh) // 40 + 1)
    remedy_zh_lines = max(1, len(remedy_text) // 40 + 1)
    remedy_total_lines = remedy_kh_lines + remedy_zh_lines
    remedy_section_height = max(160, remedy_total_lines * 30 + 60)  # 最小 160px
    
    # 計算 SVG 總高度（基礎 650 + 額外高度）
    extra_height = max(0, remedy_section_height - 160)
    svg_total_height = 650 + extra_height
    
    svg = f'''<svg viewBox="0 0 500 {svg_total_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="headerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{clan_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 背景 -->
  <rect width="500" height="{svg_total_height}" fill="url(#bgGradient)"/>
  
  <!-- 主外框 -->
  <rect x="15" y="15" width="470" height="{svg_total_height - 30}" rx="20" fill="none" stroke="{clan_color}" stroke-width="4"/>
  
  <!-- 標題區 -->
  <rect x="20" y="20" width="460" height="70" rx="15" fill="url(#headerGradient)"/>
  <text x="250" y="50" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="26" fill="#ffffff" font-weight="bold">
    {title}
  </text>
  <text x="250" y="75" text-anchor="middle" font-family="Khmer OS, sans-serif" font-size="20" fill="#fbbf24">
    ហោរាសាស្ត្រ Reamker
  </text>
  
  <!-- 命主資訊區 -->
  <rect x="30" y="100" width="440" height="80" rx="10" fill="#1e293b" stroke="{clan_color}" stroke-width="2"/>
  <text x="250" y="125" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="22" fill="{clan_color}" font-weight="bold">
    {char_kh} ({char_en})
  </text>
  <text x="250" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#94a3b8">
    氏族：{char_clan.upper()} | 格數：{cell} | 年齡：{age}
  </text>
  
  <!-- 人生階段與方位 -->
  <rect x="30" y="190" width="210" height="70" rx="10" fill="#334155" stroke="#fbbf24" stroke-width="2"/>
  <text x="135" y="215" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="16" fill="#fbbf24" font-weight="bold">
    人生階段
  </text>
  <text x="135" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#ffffff">
    {stage_text}
  </text>
  
  <rect x="260" y="190" width="210" height="70" rx="10" fill="#334155" stroke="#fbbf24" stroke-width="2"/>
  <text x="365" y="215" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="16" fill="#fbbf24" font-weight="bold">
    方位
  </text>
  <text x="365" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#ffffff">
    {direction_text}
  </text>
  
  <!-- 預言區 -->
  <rect x="30" y="270" width="440" height="140" rx="10" fill="#1e293b" stroke="{clan_color}" stroke-width="2"/>
  <text x="250" y="295" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="18" fill="{clan_color}" font-weight="bold">
    預言 / ព្យាករណ៍
  </text>
  <text x="250" y="325" text-anchor="middle" font-family="Khmer OS, sans-serif" font-size="16" fill="#fbbf24">
    {prophecy_kh}
  </text>
  <text x="250" y="355" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">
    {prophecy_text}
  </text>
  <text x="250" y="385" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#64748b">
    （基於 Bizot TK480 手稿）
  </text>
  
  <!-- 化解儀式區（動態高度） -->
  <rect x="30" y="420" width="440" height="{remedy_section_height}" rx="10" fill="#1e293b" stroke="#22c55e" stroke-width="2"/>
  <text x="250" y="445" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="18" fill="#22c55e" font-weight="bold">
    化解儀式 / ពិធីសង្គ្រោះ
  </text>
  <text x="250" y="480" text-anchor="middle" font-family="Khmer OS, sans-serif" font-size="15" fill="#86efac">
    {remedy_kh}
  </text>
  <text x="250" y="{515 + (remedy_kh_lines - 1) * 25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#86efac">
    {remedy_text}
  </text>
  <text x="250" y="{550 + (remedy_kh_lines - 1) * 25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#64748b">
    （基於 Bizot TK480 手稿）
  </text>
  
  <!-- 底部裝飾：羅摩衍那象徵圖案 -->
  <path d="M 100 {550 + extra_height} Q 250 {570 + extra_height} 400 {550 + extra_height}" stroke="{clan_color}" stroke-width="3" fill="none" opacity="0.6"/>
  <circle cx="100" cy="{550 + extra_height}" r="6" fill="{clan_color}" opacity="0.8"/>
  <circle cx="400" cy="{550 + extra_height}" r="6" fill="{clan_color}" opacity="0.8"/>
  <text x="250" y="{585 + extra_height}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#64748b">
    Reamker Astrology System • kinastro
  </text>
</svg>'''
    
    return svg


def render_rama_arrows_svg(arrows_data: Dict, language: str = "zh") -> str:
    """
    渲染羅摩之箭 SVG
    """
    arrow = arrows_data.get("arrow", 1)
    age = arrows_data.get("age", 0)
    data = arrows_data.get("data", {})
    
    arrow_kh = data.get("kh", "ព្រួញទី ១")
    arrow_en = data.get("en", "Arrow 1")
    arrow_zh = data.get("zh", "第一箭")
    interpretation = data.get("interpretation", "解讀")
    remedy = data.get("remedy", "化解方法")
    
    # 根據箭頭吉凶選擇顏色
    good_arrows = [1, 4, 7, 9]
    color = "#22c55e" if arrow in good_arrows else "#ef4444"
    
    if language == "zh":
        arrow_text = f"{arrow_zh} - {arrow}"
        title = "羅摩之箭"
    else:
        arrow_text = f"{arrow_en}"
        title = "Rama Arrows"
    
    svg = f'''<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="arrowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 背景 -->
  <rect width="400" height="300" fill="url(#arrowGradient)"/>
  
  <!-- 外框 -->
  <rect x="10" y="10" width="380" height="280" rx="15" fill="none" stroke="{color}" stroke-width="3"/>
  
  <!-- 箭頭圖示 -->
  <polygon points="200,50 180,90 190,90 190,140 180,140 200,180 220,140 210,140 210,90 220,90" 
           fill="{color}" opacity="0.8"/>
  
  <!-- 標題 -->
  <text x="200" y="210" text-anchor="middle" font-family="Khmer OS, Arial, sans-serif" font-size="20" fill="#fbbf24" font-weight="bold">
    {title}
  </text>
  
  <!-- 箭頭編號 -->
  <text x="200" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="{color}" font-weight="bold">
    {arrow_text}
  </text>
  
  <!-- 年齡 -->
  <text x="200" y="265" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8">
    年齡：{age} 歲
  </text>
  
  <!-- 吉凶指示 -->
  <text x="200" y="290" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="{color}">
    {"吉兆" if arrow in good_arrows else "凶兆"}
  </text>
</svg>'''
    
    return svg


def render_khmer_chart(chart_data: Dict, language: str = "zh") -> str:
    """
    渲染完整高棉占星報告（組合所有 SVG）
    """
    zodiac_svg = render_khmer_zodiac_svg(chart_data.get("zodiac", {}), language)
    reamker_svg = render_reamker_grid_svg(chart_data.get("reamker", {}), language)
    arrows_svg = render_rama_arrows_svg(chart_data.get("rama_arrows", {}), language)
    
    # 返回組合 HTML
    html = f'''<div style="display: flex; flex-direction: column; gap: 20px; align-items: center;">
  {zodiac_svg}
  {reamker_svg}
  {arrows_svg}
</div>'''
    
    return html
