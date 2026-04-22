"""
astro/sabian.py — Sabian Symbols 模組 (Marc Edmund Jones 1953 原著)

本模組實現 Marc Edmund Jones 原著《The Sabian Symbols in Astrology》(1953 年版) 
的 360 個 Sabian Symbols。每個黃道度數對應一個象徵圖像（symbolical picture），
包含 keyword、positive/negative 表達、formula 和 interpretation。

注意：本模組嚴格使用 Jones 原書的 wording，不使用 Lynda Hill、Diana Roche 
或其他現代改寫版本。

Usage
-----
    from astro.sabian import get_sabian_symbol, get_sabian_for_planet, render_sabian_svg
    
    # 根據經度取得符號
    symbol = get_sabian_symbol(45.5)  # 金牛座 15.5°
    
    # 從星盤資料取得行星的 Sabian Symbol
    sabian = get_sabian_for_planet(chart_data, "Sun")
    
    # 生成 SVG 符號卡片
    svg = render_sabian_svg(45.5, size=300)

Public API
----------
    get_sabian_symbol(longitude: float) -> dict
        輸入行星經度（0-360），回傳對應的 Sabian Symbol 資料。
    
    get_sabian_for_planet(chart_data: dict, planet: str) -> dict
        從星盤資料中取得指定行星的 Sabian Symbol。
    
    render_sabian_svg(longitude: float, size: int = 300) -> str
        生成 SVG 格式的 Sabian Symbol 卡片，可與 chart_renderer_v2 整合。
    
    to_context_sabian(sabian_data: dict) -> str
        將 Sabian 資料轉為 XML section，供 context_serializer 使用。
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# 資料載入
# ═══════════════════════════════════════════════════════════════

def _load_sabian_data() -> list[dict]:
    """載入 Sabian Symbols JSON 資料。"""
    # 尋找資料檔案路徑
    data_path = Path(__file__).parent / "data" / "sabian_symbols.json"
    
    if not data_path.exists():
        # 嘗試其他可能路徑
        alt_paths = [
            Path("astro/data/sabian_symbols.json"),
            Path("data/sabian_symbols.json"),
            Path.home() / ".kinastro" / "sabian_symbols.json",
        ]
        for alt_path in alt_paths:
            if alt_path.exists():
                data_path = alt_path
                break
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# 全域載入 Sabian 資料
_SABIAN_DATA = _load_sabian_data()

# 建立經度索引快取 (0-359)
_SABIAN_INDEX: dict[int, dict] = {}
for item in _SABIAN_DATA:
    degree = item["degree"]
    _SABIAN_INDEX[degree] = item


# ═══════════════════════════════════════════════════════════════
# 核心函數
# ═══════════════════════════════════════════════════════════════

def get_sabian_symbol(longitude: float) -> dict:
    """根據行星經度取得對應的 Sabian Symbol。
    
    Parameters
    ----------
    longitude : float
        行星的黃道經度（0-360 度）。0° = 白羊座 0°，30° = 金牛座 0°，以此類推。
    
    Returns
    -------
    dict
        包含以下欄位的字典：
        - degree: 總度數 (1-360)
        - sign: 星座名稱 (英文)
        - degree_in_sign: 在星座內的度數 (1-30)
        - symbol: 象徵圖像（symbolical picture）
        - keyword: 關鍵字
        - positive: 正面表達
        - negative: 負面表達
        - formula: Jones 原書的 formula
        - interpretation: 心理意義簡述（中文）
    
    Examples
    --------
    >>> get_sabian_symbol(0.0)  # 白羊座 0°
    {'degree': 1, 'sign': 'Aries', 'degree_in_sign': 1, ...}
    
    >>> get_sabian_symbol(45.5)  # 金牛座 15.5°
    {'degree': 46, 'sign': 'Taurus', 'degree_in_sign': 16, ...}
    """
    # 確保經度在 0-360 範圍內
    longitude = longitude % 360
    
    # Sabian Symbols 使用 1-based 度數系統
    # 0° = 第 1 度，29.999° = 第 30 度
    sabian_degree = int(longitude) + 1
    
    # 處理邊界情況：359.999° 應該是第 360 度
    if sabian_degree > 360:
        sabian_degree = 360
    
    # 從索引取得資料
    if sabian_degree in _SABIAN_INDEX:
        return _SABIAN_INDEX[sabian_degree].copy()
    
    # 如果找不到，回傳預設值
    return {
        "degree": sabian_degree,
        "sign": "Unknown",
        "degree_in_sign": (sabian_degree - 1) % 30 + 1,
        "symbol": "Data not available",
        "keyword": "Unknown",
        "positive": "N/A",
        "negative": "N/A",
        "formula": "N/A",
        "interpretation": "資料尚未建立"
    }


def get_sabian_for_planet(chart_data: dict, planet: str) -> dict:
    """從星盤資料中取得指定行星的 Sabian Symbol。
    
    Parameters
    ----------
    chart_data : dict
        星盤資料字典，應包含 'planets' 列表，每個行星物件應有
        'name' 和 'longitude' 欄位。
    planet : str
        行星名稱（英文或中文），例如 "Sun"、"Moon"、"太陽"、"太陰"。
    
    Returns
    -------
    dict
        該行星的 Sabian Symbol 資料，包含經度資訊和完整符號內容。
        如果找不到行星，回傳 None。
    
    Examples
    --------
    >>> chart = {"planets": [{"name": "Sun", "longitude": 45.5}]}
    >>> get_sabian_for_planet(chart, "Sun")
    {'planet': 'Sun', 'longitude': 45.5, 'degree': 46, 'sign': 'Taurus', ...}
    """
    # 行星名稱對照表
    PLANET_NAME_MAP = {
        "Sun": ["Sun", "太陽", "☉"],
        "Moon": ["Moon", "太陰", "☽"],
        "Mercury": ["Mercury", "水星", "☿"],
        "Venus": ["Venus", "金星", "♀"],
        "Mars": ["Mars", "火星", "♂"],
        "Jupiter": ["Jupiter", "木星", "♃"],
        "Saturn": ["Saturn", "土星", "♄"],
        "Uranus": ["Uranus", "天王星", "♅"],
        "Neptune": ["Neptune", "海王星", "♆"],
        "Pluto": ["Pluto", "冥王星", "♇"],
        "Ascendant": ["Ascendant", "上升點", "ASC", "上升"],
        "Midheaven": ["Midheaven", "天頂", "MC", "中天"],
    }
    
    # 尋找目標行星
    target_names = PLANET_NAME_MAP.get(planet, [planet])
    
    planets = chart_data.get("planets", [])
    target_planet = None
    
    for p in planets:
        # 支援 dataclass 物件和字典兩種格式
        if hasattr(p, 'name'):
            # dataclass 物件 (如 WesternPlanet)
            p_name = p.name
            p_longitude = p.longitude
        else:
            # 字典格式
            p_name = p.get("name", "")
            p_longitude = p.get("longitude")
        
        for target in target_names:
            if target in p_name or p_name in target:
                target_planet = p
                break
        if target_planet:
            break
    
    if not target_planet:
        return None
    
    # 取得經度
    if hasattr(target_planet, 'longitude'):
        # dataclass 物件
        longitude = target_planet.longitude
    else:
        # 字典格式
        longitude = target_planet.get("longitude")
        if longitude is None:
            # 嘗試其他可能的欄位名稱
            longitude = target_planet.get("lon") or target_planet.get("position")
    
    if longitude is None:
        return None
    
    # 取得 Sabian Symbol
    sabian = get_sabian_symbol(float(longitude))
    
    # 加入行星資訊
    result = sabian.copy()
    if hasattr(target_planet, 'name'):
        result["planet"] = target_planet.name
    else:
        result["planet"] = target_planet.get("name", planet)
    result["planet_longitude"] = float(longitude)
    
    return result


def render_sabian_svg(longitude: float, size: int = 300) -> str:
    """生成 Sabian Symbol 的 SVG 卡片。
    
    Parameters
    ----------
    longitude : float
        行星的黃道經度（0-360 度）。
    size : int, optional
        SVG 卡片的大小（像素），預設 300。
    
    Returns
    -------
    str
        SVG 格式的字串，可直接用於 st.markdown(..., unsafe_allow_html=True)。
    
    Examples
    --------
    >>> svg = render_sabian_svg(45.5, size=300)
    >>> st.markdown(svg, unsafe_allow_html=True)
    """
    sabian = get_sabian_symbol(longitude)
    
    # 星座顏色對應表
    SIGN_COLORS = {
        "Aries": "#FF6B6B",
        "Taurus": "#4ECDC4",
        "Gemini": "#FFE66D",
        "Cancer": "#95E1D3",
        "Leo": "#FFD93D",
        "Virgo": "#F7FFF7",
        "Libra": "#FF85A2",
        "Scorpio": "#FF6B9D",
        "Sagittarius": "#C7F464",
        "Capricorn": "#A8D8EA",
        "Aquarius": "#AA96DA",
        "Pisces": "#FCBAD3",
    }
    
    sign = sabian.get("sign", "Unknown")
    color = SIGN_COLORS.get(sign, "#CCCCCC")
    
    # 生成 SVG
    svg = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <!-- 背景 -->
  <defs>
    <linearGradient id="grad-{int(longitude)}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color};stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:{color};stop-opacity:0.1" />
    </linearGradient>
  </defs>
  
  <rect width="{size}" height="{size}" fill="url(#grad-{int(longitude)})" rx="10" ry="10"/>
  
  <!-- 邊框 -->
  <rect x="2" y="2" width="{size-4}" height="{size-4}" fill="none" stroke="{color}" stroke-width="2" rx="8" ry="8"/>
  
  <!-- 星座名稱 -->
  <text x="{size//2}" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{color}">
    {sign} {sabian.get('degree_in_sign', '')}°
  </text>
  
  <!-- 度數 -->
  <text x="{size//2}" y="55" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
    Degree {sabian.get('degree', '')} / 360
  </text>
  
  <!-- 關鍵字 -->
  <text x="{size//2}" y="80" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-style="italic" fill="#444">
    "{sabian.get('keyword', '')}"
  </text>
  
  <!-- 象徵圖像（換行處理） -->
  <foreignObject x="20" y="95" width="{size-40}" height="120">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial, sans-serif; font-size: 11px; color: #333; text-align: center; line-height: 1.4;">
      {sabian.get('symbol', '')}
    </div>
  </foreignObject>
  
  <!-- Formula -->
  <text x="{size//2}" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#888">
    {sabian.get('formula', '')}
  </text>
  
  <!-- 裝飾 -->
  <circle cx="{size//2}" cy="265" r="5" fill="{color}" opacity="0.5"/>
</svg>'''
    
    return svg


# ═══════════════════════════════════════════════════════════════
# Context Serializer 整合
# ═══════════════════════════════════════════════════════════════

def to_context_sabian(sabian_data: dict) -> str:
    """將 Sabian Symbol 資料轉換為 XML section，供 context_serializer 使用。
    
    Parameters
    ----------
    sabian_data : dict
        Sabian Symbol 資料字典，通常來自 get_sabian_symbol() 或 
        get_sabian_for_planet()。
    
    Returns
    -------
    str
        XML 格式的字串，可嵌入至 context_serializer 的輸出中。
    
    Examples
    --------
    >>> sabian = get_sabian_symbol(45.5)
    >>> xml = to_context_sabian(sabian)
    """
    if not sabian_data:
        return ""
    
    # 建立 XML 元素
    lines = []
    lines.append("  <sabian_symbol>")
    
    # 基本資訊
    lines.append(f'    <degree>{sabian_data.get("degree", "")}</degree>')
    lines.append(f'    <sign>{sabian_data.get("sign", "")}</sign>')
    lines.append(f'    <degree_in_sign>{sabian_data.get("degree_in_sign", "")}</degree_in_sign>')
    lines.append(f'    <keyword>{sabian_data.get("keyword", "")}</keyword>')
    
    # 象徵圖像
    symbol = sabian_data.get("symbol", "")
    lines.append(f"    <symbol>{symbol}</symbol>")
    
    # 正負面表達
    lines.append(f'    <positive>{sabian_data.get("positive", "")}</positive>')
    lines.append(f'    <negative>{sabian_data.get("negative", "")}</negative>')
    
    # Formula
    lines.append(f'    <formula>{sabian_data.get("formula", "")}</formula>')
    
    # 詮釋（中文）
    lines.append(f'    <interpretation>{sabian_data.get("interpretation", "")}</interpretation>')
    
    # 如果有行星資訊
    if "planet" in sabian_data:
        lines.append(f'    <planet>{sabian_data.get("planet", "")}</planet>')
        lines.append(f'    <planet_longitude>{sabian_data.get("planet_longitude", "")}</planet_longitude>')
    
    lines.append("  </sabian_symbol>")
    
    return "\n".join(lines)


def serialize_sabian_for_context(chart_data: dict, planets: list[str] = None) -> str:
    """為星盤中的行星生成完整的 Sabian Symbol XML section。
    
    Parameters
    ----------
    chart_data : dict
        星盤資料字典。
    planets : list[str], optional
        要包含的行星列表。如果為 None，則包含所有主要行星。
    
    Returns
    -------
    str
        完整的 Sabian Symbols XML section。
    """
    if planets is None:
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                   "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                   "Ascendant", "Midheaven"]
    
    lines = []
    lines.append("<sabian_symbols>")
    
    for planet_name in planets:
        sabian = get_sabian_for_planet(chart_data, planet_name)
        if sabian:
            xml = to_context_sabian(sabian)
            lines.append(xml)
    
    lines.append("</sabian_symbols>")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Cross-Compare 整合
# ═══════════════════════════════════════════════════════════════

def compare_sabian_with_degree(degree: float, western_sign: str, western_degree: float) -> dict:
    """比較 Sabian Symbol 與西洋行星度數。
    
    Parameters
    ----------
    degree : float
        行星的黃道經度（0-360）。
    western_sign : str
        西洋星座名稱（英文）。
    western_degree : float
        在星座內的度數（0-29.99）。
    
    Returns
    -------
    dict
        包含 Sabian 和西洋度數的比較結果。
    """
    sabian = get_sabian_symbol(degree)
    
    return {
        "longitude": degree,
        "western": {
            "sign": western_sign,
            "degree": round(western_degree, 2),
        },
        "sabian": {
            "degree": sabian.get("degree"),
            "sign": sabian.get("sign"),
            "degree_in_sign": sabian.get("degree_in_sign"),
            "symbol": sabian.get("symbol"),
            "keyword": sabian.get("keyword"),
        }
    }


# ═══════════════════════════════════════════════════════════════
# 輔助函數
# ═══════════════════════════════════════════════════════════════

def get_sign_from_longitude(longitude: float) -> str:
    """從經度取得星座名稱。
    
    Parameters
    ----------
    longitude : float
        黃道經度（0-360）。
    
    Returns
    -------
    str
        星座名稱（英文）。
    """
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_index = int(longitude) // 30
    return signs[sign_index % 12]


def get_degree_in_sign(longitude: float) -> float:
    """從經度取得星座內的度數。
    
    Parameters
    ----------
    longitude : float
        黃道經度（0-360）。
    
    Returns
    -------
    float
        在星座內的度數（0-29.99）。
    """
    return longitude % 30


def get_all_sabian_symbols_for_sign(sign: str) -> list[dict]:
    """取得指定星座的所有 30 個 Sabian Symbols。
    
    Parameters
    ----------
    sign : str
        星座名稱（英文），例如 "Aries"、"Taurus"。
    
    Returns
    -------
    list[dict]
        該星座的 30 個 Sabian Symbol 資料。
    """
    sign_order = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    if sign not in sign_order:
        return []
    
    sign_index = sign_order.index(sign)
    start_degree = sign_index * 30 + 1
    end_degree = start_degree + 29
    
    return [_SABIAN_INDEX.get(i, {}) for i in range(start_degree, end_degree + 1)]


def load_sabian_symbols() -> list[dict]:
    """載入所有 360 個 Sabian Symbols。
    
    Returns
    -------
    list[dict]
        包含所有 360 個 Sabian Symbol 的列表，每個元素為完整的 symbol dict。
    
    Example
    -------
    >>> symbols = load_sabian_symbols()
    >>> len(symbols)
    360
    >>> symbols[0]['degree']
    1
    >>> symbols[0]['sign']
    'Aries'
    """
    return _SABIAN_DATA.copy()


# ═══════════════════════════════════════════════════════════════
# 測試
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """測試 Sabian Symbols 模組。"""
    
    print("=" * 60)
    print("Sabian Symbols 模組測試")
    print("=" * 60)
    
    # 範例出生資料：1990 年 1 月 15 日 12:00 台北
    # 太陽約在摩羯座 24°，月亮約在雙子座 10°
    test_cases = [
        (0.0, "白羊座 0° (起點)"),
        (45.5, "金牛座 15.5°"),
        (90.0, "巨蟹座 0°"),
        (180.0, "天秤座 0°"),
        (270.0, "摩羯座 0°"),
        (359.9, "雙魚座 29.9° (終點)"),
    ]
    
    print("\n【測試 get_sabian_symbol()】\n")
    for longitude, description in test_cases:
        sabian = get_sabian_symbol(longitude)
        print(f"{description} (經度：{longitude}°)")
        print(f"  度數：{sabian['degree']} / 360")
        print(f"  星座：{sabian['sign']} {sabian['degree_in_sign']}°")
        print(f"  關鍵字：{sabian['keyword']}")
        print(f"  象徵：{sabian['symbol'][:60]}...")
        print(f"  Formula: {sabian['formula']}")
        print()
    
    # 測試星盤資料
    print("\n【測試 get_sabian_for_planet()】\n")
    test_chart = {
        "planets": [
            {"name": "Sun", "longitude": 294.5},  # 摩羯座 24.5°
            {"name": "Moon", "longitude": 70.3},  # 雙子座 10.3°
            {"name": "Mercury", "longitude": 280.0},  # 摩羯座 10°
            {"name": "Venus", "longitude": 315.5},  # 水瓶座 15.5°
            {"name": "Mars", "longitude": 15.2},  # 白羊座 15.2°
        ]
    }
    
    for planet_name in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
        sabian = get_sabian_for_planet(test_chart, planet_name)
        if sabian:
            print(f"{planet_name}:")
            print(f"  經度：{sabian['planet_longitude']}°")
            print(f"  Sabian: {sabian['sign']} {sabian['degree_in_sign']}° - {sabian['keyword']}")
            print(f"  象徵：{sabian['symbol'][:50]}...")
            print()
    
    # 測試 XML 序列化
    print("\n【測試 to_context_sabian()】\n")
    sun_sabian = get_sabian_for_planet(test_chart, "Sun")
    xml = to_context_sabian(sun_sabian)
    print(xml)
    print()
    
    # 測試 SVG 生成
    print("\n【測試 render_sabian_svg()】\n")
    svg = render_sabian_svg(294.5, size=200)
    print(f"SVG 長度：{len(svg)} 字元")
    print(f"SVG 開頭：{svg[:100]}...")
    print()
    
    # 測試 cross-compare
    print("\n【測試 compare_sabian_with_degree()】\n")
    comparison = compare_sabian_with_degree(294.5, "Capricorn", 24.5)
    print(f"經度：{comparison['longitude']}°")
    print(f"西洋：{comparison['western']['sign']} {comparison['western']['degree']}°")
    print(f"Sabian: {comparison['sabian']['sign']} {comparison['sabian']['degree_in_sign']}° - {comparison['sabian']['keyword']}")
    print()
    
    print("=" * 60)
    print("測試完成！")
    print("=" * 60)
