"""
astro/chart_theme.py — 全域圖表主題 (Global Chart Theme)

統一各體系的顏色常量、字型、網格風格，並提供行動裝置適配 CSS。
"""

# ── Primary UI colours ──────────────────────────────────────────
PRIMARY_COLOR = "#1a73e8"
SECONDARY_COLOR = "#e8710a"
BG_LIGHT = "#f8f9fa"
BG_DARK = "#1e1e1e"
TEXT_PRIMARY = "#202124"
TEXT_SECONDARY = "#5f6368"

# ── Zodiac sign colours (by element) ───────────────────────────
ELEMENT_COLORS = {
    "Fire": "#e25822",
    "Earth": "#8b7355",
    "Air": "#87ceeb",
    "Water": "#4682b4",
}

ZODIAC_COLORS = {
    "Aries": "#e25822", "Leo": "#e25822", "Sagittarius": "#e25822",
    "Taurus": "#8b7355", "Virgo": "#8b7355", "Capricorn": "#8b7355",
    "Gemini": "#87ceeb", "Libra": "#87ceeb", "Aquarius": "#87ceeb",
    "Cancer": "#4682b4", "Scorpio": "#4682b4", "Pisces": "#4682b4",
}

# ── Universal planet colours (canonical key → hex) ─────────────
PLANET_COLORS = {
    "Sun": "#FF8C00",
    "Moon": "#C0C0C0",
    "Mercury": "#4169E1",
    "Venus": "#FF69B4",
    "Mars": "#DC143C",
    "Jupiter": "#228B22",
    "Saturn": "#8B4513",
    "Uranus": "#00CED1",
    "Neptune": "#7B68EE",
    "Pluto": "#800080",
    "Rahu": "#556B2F",
    "Ketu": "#4B0082",
    "MoonApogee": "#2F4F4F",
    "PurpleQi": "#9400D3",
}

# ── Aspect colours ──────────────────────────────────────────────
ASPECT_COLORS = {
    "Conjunction": "#FFD700",
    "Opposition": "#FF0000",
    "Trine": "#00AA00",
    "Square": "#FF4500",
    "Sextile": "#4169E1",
}

# ── SVG / Chart drawing defaults ────────────────────────────────
CHART_BG = "#FFFFFF"
CHART_RING_STROKE = "#333333"
CHART_GRID_LINE = "#CCCCCC"
CHART_TEXT_COLOR = "#333333"
FONT_FAMILY = "Arial, Helvetica, sans-serif"

# ── Mobile responsive CSS ───────────────────────────────────────
MOBILE_CSS = """<style>
@media (max-width: 768px) {
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; gap: 2px; }
    .stTabs [data-baseweb="tab"] { font-size: 0.75rem; padding: 4px 8px; }
    section[data-testid="stSidebar"] { min-width: 260px; }
    .stDataFrame { font-size: 0.8rem; }
}
svg.chart-wheel { max-width: 100%; height: auto; }
</style>"""

# ── Planet name → canonical key mapping ─────────────────────────
_PLANET_ALIASES: dict[str, str] = {
    # Chinese
    "太陽": "Sun", "太陰": "Moon", "水星": "Mercury", "金星": "Venus",
    "火星": "Mars", "木星": "Jupiter", "土星": "Saturn", "天王星": "Uranus",
    "海王星": "Neptune", "冥王星": "Pluto", "羅睺": "Rahu", "計都": "Ketu",
    "月孛": "MoonApogee", "紫氣": "PurpleQi",
    # Sanskrit / Vedic
    "Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars", "Budha": "Mercury",
    "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn",
    # Western with glyph
    "Sun ☉": "Sun", "Moon ☽": "Moon", "Mercury ☿": "Mercury",
    "Venus ♀": "Venus", "Mars ♂": "Mars", "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn", "Uranus ♅": "Uranus", "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
}


def get_planet_color(name: str) -> str:
    """Return hex colour for *name*, resolving aliases. Falls back to grey."""
    # Direct canonical match
    if name in PLANET_COLORS:
        return PLANET_COLORS[name]
    # Alias match
    canonical = _PLANET_ALIASES.get(name)
    if canonical:
        return PLANET_COLORS.get(canonical, "#666666")
    # Substring search (e.g. "Surya (太陽)")
    for alias, key in _PLANET_ALIASES.items():
        if alias in name:
            return PLANET_COLORS.get(key, "#666666")
    return "#666666"
