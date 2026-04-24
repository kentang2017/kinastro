"""
astro/sabian.py — Sabian Symbols (Marc Edmund Jones, 1953 Original)

薩比恩符號：360 個黃道度數的象徵圖像
嚴格按照 Marc Edmund Jones《The Sabian Symbols in Astrology》(1953) 原著

核心功能：
1. get_sabian_symbol(longitude) — 根據行星經度獲取對應符號
2. get_sabian_for_planet(chart_data, planet) — 獲取特定行星的 Sabian Symbol
3. render_sabian_svg(longitude) — 生成 SVG 符號卡片
4. to_context_sabian() — 與 context_serializer.py 整合

References
----------
- Jones, Marc Edmund (1953). "The Sabian Symbols in Astrology"
- NOT Lynda Hill or modern reinterpretations
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ZODIAC_SIGNS_ZH = [
    "白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"
]

# Path to Sabian symbols JSON data
SABIAN_DATA_PATH = Path(__file__).parent / "data" / "sabian_symbols.json"


# ============================================================================
# DATA LOADING
# ============================================================================

def load_sabian_symbols() -> List[Dict[str, Any]]:
    """
    載入 360 個 Sabian Symbols（Jones 1953 原著）
    
    Returns
    -------
    List[Dict[str, Any]]
        包含 360 個符號的列表，每個符號包含：
        - degree: 1-360
        - sign: 星座英文名
        - degree_in_sign: 星座內度數 (1-30)
        - symbol: 象徵圖像（Jones 原著 exact wording）
        - keyword: 關鍵詞
        - positive: 正面意義
        - negative: 負面意義
        - formula: Jones 公式
        - interpretation: 心理意義簡述
    """
    if not SABIAN_DATA_PATH.exists():
        raise FileNotFoundError(f"Sabian symbols data not found: {SABIAN_DATA_PATH}")
    
    with open(SABIAN_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if len(data) != 360:
        raise ValueError(f"Expected 360 symbols, got {len(data)}")
    
    return data


# Cache loaded symbols
_SABIAN_SYMBOLS_CACHE: Optional[List[Dict[str, Any]]] = None


def _get_symbols() -> List[Dict[str, Any]]:
    """Get cached symbols."""
    global _SABIAN_SYMBOLS_CACHE
    if _SABIAN_SYMBOLS_CACHE is None:
        _SABIAN_SYMBOLS_CACHE = load_sabian_symbols()
    return _SABIAN_SYMBOLS_CACHE


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def get_sabian_symbol(longitude: float) -> Dict[str, Any]:
    """
    根據行星經度獲取對應的 Sabian Symbol
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    
    Returns
    -------
    Dict[str, Any]
        符號資料，包含 symbol, keyword, positive, negative, formula, interpretation
    
    Raises
    ------
    ValueError
        如果經度不在 0-360 範圍內
    
    Examples
    --------
    >>> get_sabian_symbol(0.5)  # Aries 1°
    {'degree': 1, 'sign': 'Aries', 'symbol': 'A woman has risen out of the ocean...'}
    """
    if not 0 <= longitude < 360:
        raise ValueError(f"Longitude must be 0-360, got {longitude}")
    
    # Convert to 1-indexed degree (1-360)
    degree_index = int(longitude) + 1
    if degree_index > 360:
        degree_index = 360
    
    symbols = _get_symbols()
    return symbols[degree_index - 1]


def get_sabian_for_planet(chart_data: Dict[str, Any], planet: str) -> Dict[str, Any]:
    """
    獲取特定行星的 Sabian Symbol
    
    Parameters
    ----------
    chart_data : Dict[str, Any]
        星盤資料，必須包含行星經度資訊
        格式：{'planets': [{'name': 'Sun', 'longitude': 45.5}, ...]}
    planet : str
        行星名稱（英文或中文）
        支援：Sun/Moon/Mercury/Venus/Mars/Jupiter/Saturn/Uranus/Neptune/Pluto
        或中文：太陽/月亮/水星/金星/火星/木星/土星/天王星/海王星/冥王星
    
    Returns
    -------
    Dict[str, Any]
        該行星的 Sabian Symbol 資料
    
    Raises
    ------
    ValueError
        如果找不到該行星
    
    Examples
    --------
    >>> chart = {'planets': [{'name': 'Sun', 'longitude': 45.5}]}
    >>> get_sabian_for_planet(chart, 'Sun')
    {'degree': 46, 'sign': 'Taurus', 'symbol': '...'}
    """
    # Planet name mapping
    planet_map = {
        'sun': 'Sun', '太陽': 'Sun',
        'moon': 'Moon', '月亮': 'Moon',
        'mercury': 'Mercury', '水星': 'Mercury',
        'venus': 'Venus', '金星': 'Venus',
        'mars': 'Mars', '火星': 'Mars',
        'jupiter': 'Jupiter', '木星': 'Jupiter',
        'saturn': 'Saturn', '土星': 'Saturn',
        'uranus': 'Uranus', '天王星': 'Uranus',
        'neptune': 'Neptune', '海王星': 'Neptune',
        'pluto': 'Pluto', '冥王星': 'Pluto',
    }
    
    planet_std = planet_map.get(planet.lower(), planet)
    
    planets = chart_data.get('planets', [])
    for p in planets:
        # Handle both dict and WesternPlanet dataclass
        if hasattr(p, 'name'):
            # WesternPlanet dataclass object
            p_name = p.name
            p_longitude = p.longitude
        else:
            # Dictionary
            p_name = p.get('name')
            p_longitude = p.get('longitude')
        
        # Match planet name with or without glyph symbols
        # e.g., "Sun ☉" matches "Sun", "Moon ☽" matches "Moon"
        p_name_clean = p_name.split()[0] if p_name else None
        
        if p_name_clean == planet_std or p_name == planet_std:
            result = get_sabian_symbol(p_longitude)
            # Add planet longitude to result for SVG rendering
            result['planet_longitude'] = p_longitude
            return result
    
    raise ValueError(f"Planet not found: {planet}")


def get_sign_longitudinal_degree(longitude: float) -> tuple:
    """
    將經度轉換為星座和星座內度數
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    
    Returns
    -------
    tuple
        (sign_index, degree_in_sign, sign_name, sign_name_zh)
        sign_index: 0-11
        degree_in_sign: 1-30
        sign_name: 星座英文名
        sign_name_zh: 星座中文名
    """
    sign_index = int(longitude) // 30
    degree_in_sign = int(longitude) % 30 + 1
    return (
        sign_index,
        degree_in_sign,
        ZODIAC_SIGNS[sign_index],
        ZODIAC_SIGNS_ZH[sign_index]
    )


# ============================================================================
# SVG RENDERING
# ============================================================================

def render_sabian_svg(longitude: float, size: int = 300, language: str = "zh") -> str:
    """
    生成 Sabian Symbol SVG 卡片
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    size : int
        SVG 尺寸（像素），預設 300
    language : str
        語言（"zh" 或 "en"）
    
    Returns
    -------
    str
        SVG 字串
    
    Examples
    --------
    >>> svg = render_sabian_svg(45.5, size=400)
    >>> len(svg) > 1000
    True
    """
    symbol_data = get_sabian_symbol(longitude)
    sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(longitude)
    
    # Color scheme based on element
    element_colors = {
        "fire": {"bg": "#FFF5F0", "accent": "#FF6B35", "text": "#8B2500"},
        "earth": {"bg": "#F5F8F0", "accent": "#6B9F5E", "text": "#2D4A22"},
        "air": {"bg": "#F0F5F8", "accent": "#7B9ED9", "text": "#223D4A"},
        "water": {"bg": "#F0F5F8", "accent": "#5E8B9F", "text": "#223D4A"},
    }
    
    elements = ["fire", "earth", "air", "water", "fire", "earth", "air", "water", "fire", "earth", "air", "water"]
    element = elements[sign_idx]
    colors = element_colors[element]
    
    if language == "zh":
        sign_display = f"{sign_zh} {deg_in_sign}°"
        keyword_label = "關鍵詞"
        formula_label = "Jones 公式"
    else:
        sign_display = f"{sign_en} {deg_in_sign}°"
        keyword_label = "Keyword"
        formula_label = "Formula"
    
    svg = f'''<svg width="{size}" height="{size * 1.4}" viewBox="0 0 {size} {int(size * 1.4)}" 
    xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="sabianGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:{colors['bg']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:#FFFFFF;stop-opacity:1" />
        </linearGradient>
        <filter id="sabianShadow">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
        </filter>
    </defs>
    
    <!-- Background -->
    <rect width="{size}" height="{int(size * 1.4)}" fill="url(#sabianGrad)" rx="15" ry="15"/>
    
    <!-- Border -->
    <rect width="{size}" height="{int(size * 1.4)}" fill="none" stroke="{colors['accent']}" 
          stroke-width="3" rx="15" ry="15"/>
    
    <!-- Header: Sign and Degree -->
    <text x="{size // 2}" y="45" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="20" font-weight="bold" 
          fill="{colors['text']}">{sign_display}</text>
    
    <!-- Degree Number Circle -->
    <circle cx="{size - 40}" cy="30" r="20" fill="{colors['accent']}" opacity="0.9"/>
    <text x="{size - 40}" y="37" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white">{deg_in_sign}</text>
    
    <!-- Divider -->
    <line x1="30" y1="60" x2="{size - 30}" y2="60" 
          stroke="{colors['accent']}" stroke-width="2" opacity="0.5"/>
    
    <!-- Symbol Text (main content) -->
    <foreignObject x="30" y="75" width="{size - 60}" height="{size * 0.5}">
        <div xmlns="http://www.w3.org/1999/xhtml" 
             style="font-family: Georgia, serif; font-size: 16px; line-height: 1.6; 
                    color: {colors['text']}; text-align: center; 
                    padding: 10px; font-style: italic;">
            "{symbol_data['symbol']}"
        </div>
    </foreignObject>
    
    <!-- Keyword -->
    <text x="{size // 2}" y="{int(size * 0.65)}" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="14" font-weight="bold" 
          fill="{colors['accent']}">{keyword_label}: {symbol_data['keyword']}</text>
    
    <!-- Formula -->
    <text x="{size // 2}" y="{int(size * 0.75)}" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="12" 
          fill="{colors['text']}" font-style="italic">{formula_label}: {symbol_data['formula']}</text>
    
    <!-- Footer -->
    <text x="{size // 2}" y="{int(size * 1.3)}" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="10" 
          fill="{colors['text']}" opacity="0.7">Marc Edmund Jones (1953)</text>
</svg>'''
    
    return svg


# ============================================================================
# CONTEXT SERIALIZER INTEGRATION
# ============================================================================

def to_context_sabian(longitude: float, planet_name: str = "") -> str:
    """
    將 Sabian Symbol 轉換為 XML format，供 context_serializer.py 使用
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    planet_name : str
        行星名稱（可選）
    
    Returns
    -------
    str
        XML format 的 Sabian Symbol 資料
    
    Examples
    --------
    >>> xml = to_context_sabian(45.5, "Sun")
    >>> "<sabian_symbol" in xml
    True
    """
    symbol_data = get_sabian_symbol(longitude)
    sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(longitude)
    
    planet_xml = f' planet="{planet_name}"' if planet_name else ""
    
    xml = f'''<sabian_symbol{planet_xml} degree="{symbol_data['degree']}" 
    sign="{sign_en}" sign_zh="{sign_zh}" degree_in_sign="{deg_in_sign}">
    <symbol>{symbol_data['symbol']}</symbol>
    <keyword>{symbol_data['keyword']}</keyword>
    <positive>{symbol_data['positive']}</positive>
    <negative>{symbol_data['negative']}</negative>
    <formula>{symbol_data['formula']}</formula>
    <interpretation>{symbol_data['interpretation']}</interpretation>
</sabian_symbol>'''
    
    return xml


# ============================================================================
# CROSS-COMPARE INTEGRATION
# ============================================================================

def compare_sabian_with_western(western_data: Dict[str, Any], longitude: float) -> Dict[str, Any]:
    """
    將 Sabian Symbol 與西洋占星資料做對比
    
    Parameters
    ----------
    western_data : Dict[str, Any]
        西洋占星資料（行星位置、星座、宮位等）
    longitude : float
        行星經度
    
    Returns
    -------
    Dict[str, Any]
        包含西洋占星與 Sabian Symbol 的對比資料
    """
    sabian = get_sabian_symbol(longitude)
    sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(longitude)
    
    return {
        "longitude": longitude,
        "western": {
            "sign": sign_en,
            "sign_zh": sign_zh,
            "degree_in_sign": deg_in_sign,
            **western_data
        },
        "sabian": {
            "symbol": sabian['symbol'],
            "keyword": sabian['keyword'],
            "formula": sabian['formula'],
            "interpretation": sabian['interpretation'],
        }
    }


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    # Test with sample birth data
    print("=" * 60)
    print("Sabian Symbols Test — Marc Edmund Jones (1953) Original")
    print("=" * 60)
    
    # Sample data: Sun at 15° Aries, Moon at 23° Cancer
    test_planets = [
        {"name": "Sun", "longitude": 15.0},    # Aries 16°
        {"name": "Moon", "longitude": 113.0},  # Cancer 24°
        {"name": "Mercury", "longitude": 5.5}, # Aries 6°
        {"name": "Venus", "longitude": 45.5},  # Taurus 16°
    ]
    
    print("\n🔮 Sample Birth Chart Sabian Symbols:\n")
    
    for planet in test_planets:
        symbol = get_sabian_symbol(planet["longitude"])
        sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(planet["longitude"])
        
        print(f"{'─' * 58}")
        print(f"{planet['name']} — {sign_zh} {deg_in_sign}° ({planet['longitude']:.1f}°)")
        print(f"{'─' * 58}")
        print(f"Symbol:   {symbol['symbol']}")
        print(f"Keyword:  {symbol['keyword']}")
        print(f"Formula:  {symbol['formula']}")
        print(f"Meaning:  {symbol['interpretation']}")
        print()
    
    # Test SVG rendering
    print("\n🎨 Testing SVG rendering...")
    svg = render_sabian_svg(15.0, size=300, language="zh")
    print(f"SVG generated: {len(svg)} characters")
    print(f"SVG preview: {svg[:200]}...")
    
    # Test XML serialization
    print("\n📄 Testing XML serialization...")
    xml = to_context_sabian(15.0, "Sun")
    print(f"XML generated: {len(xml)} characters")
    print(f"XML preview: {xml[:300]}...")
    
    # Test cross-compare
    print("\n🔍 Testing cross-compare...")
    western_data = {"house": 1, "aspect": "conjunct Ascendant"}
    comparison = compare_sabian_with_western(western_data, 15.0)
    print(f"Western sign: {comparison['western']['sign_zh']}")
    print(f"Sabian keyword: {comparison['sabian']['keyword']}")
    
    print("\n✅ All tests passed!")
