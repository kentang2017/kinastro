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
/* ── Global: prevent horizontal scroll ──────────────── */
.stMainBlockContainer, .stMain, [data-testid="stAppViewBlockContainer"] {
    max-width: 100vw;
    overflow-x: hidden;
}

/* ── Welcome hero card ─────────────────────────────── */
.welcome-hero {
    background: linear-gradient(135deg, #1a237e 0%, #4a148c 50%, #880e4f 100%);
    border-radius: 16px;
    padding: 32px 28px;
    margin-bottom: 24px;
    color: #fff;
    text-align: center;
}
.welcome-hero h2 {
    color: #fff !important;
    font-size: 1.6rem !important;
    margin-bottom: 8px;
}
.welcome-hero p {
    color: rgba(255,255,255,0.9);
    font-size: 1.05rem;
    margin-bottom: 0;
    line-height: 1.7;
}

/* ── Step cards (onboarding) ───────────────────────── */
.step-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    transition: box-shadow 0.2s, transform 0.2s;
}
.step-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.10);
    transform: translateY(-2px);
}
.step-num {
    display: inline-block;
    background: #1a73e8;
    color: #fff;
    width: 32px; height: 32px;
    border-radius: 50%;
    line-height: 32px;
    font-weight: bold;
    font-size: 0.95rem;
    margin-bottom: 8px;
}
.step-card h4 { margin: 6px 0 4px 0; font-size: 1rem; }
.step-card p { color: #555; font-size: 0.88rem; margin: 0; }

/* ── Category header in sidebar ────────────────────── */
.sidebar-cat {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 12px 0 4px 2px;
    font-weight: 600;
}

/* ── System button descriptions ────────────────────── */
.sys-desc {
    font-size: 0.72rem;
    color: #999;
    margin: -6px 0 6px 4px;
    line-height: 1.3;
}

/* ── Beginner badge ────────────────────────────────── */
.beginner-badge {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 0.65rem;
    padding: 1px 6px;
    border-radius: 8px;
    margin-left: 4px;
    font-weight: 600;
    vertical-align: middle;
}

/* ── Sidebar overall tweaks ────────────────────────── */
section[data-testid="stSidebar"] .stButton > button {
    font-size: 0.88rem;
    border-radius: 8px;
    transition: all 0.15s;
}

/* ── Mobile ─────────────────────────────────────────── */
@media (max-width: 768px) {
    /* Tabs: wrap onto multiple lines */
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; gap: 2px; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 3px 6px; min-height: 32px; }

    /* Sidebar */
    section[data-testid="stSidebar"] { min-width: 200px; }

    /* Columns: stack vertically on mobile
       Note: data-testid selectors are Streamlit internal; verify on upgrades. */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* DataFrames: allow horizontal scroll within container */
    .stDataFrame { font-size: 0.78rem; overflow-x: auto; }
    .stMetric { padding: 6px 8px !important; }
    .stExpander summary { font-size: 0.85rem; }

    /* Headings */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1.0rem !important; }

    /* Scrollable wrapper for wide astrology tables */
    .scroll-table-wrap {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        max-width: 100%;
        margin: 8px 0;
    }

    /* Markdown tables (pure Markdown syntax): horizontal scroll */
    [data-testid="stMarkdownContainer"] > div > table {
        display: block;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        font-size: 0.72rem;
    }
    [data-testid="stMarkdownContainer"] > div > table td,
    [data-testid="stMarkdownContainer"] > div > table th {
        padding: 3px 6px !important;
        white-space: nowrap;
    }

    /* HTML tables rendered via unsafe_allow_html: reduce font, wrap words */
    table {
        max-width: 100%;
        font-size: 0.78rem;
    }
    table td, table th {
        min-width: auto !important;
        word-break: break-word;
        font-size: 0.75rem;
    }

    /* SVG charts: fit within viewport */
    svg {
        max-width: 100% !important;
        height: auto !important;
    }

    /* Palace grid: shrink for small screens */
    .palace-grid td {
        width: 70px !important;
        height: 65px !important;
        font-size: 0.7rem !important;
    }

    /* Plotly charts: force full-width */
    .js-plotly-plot { width: 100% !important; }

    /* Welcome hero: compact on mobile */
    .welcome-hero { padding: 20px 16px; }
    .welcome-hero h2 { font-size: 1.2rem !important; }
    .welcome-hero p { font-size: 0.9rem; }
}
/* ── Tablet ─────────────────────────────────────────── */
@media (min-width: 769px) and (max-width: 1024px) {
    .stTabs [data-baseweb="tab"] { font-size: 0.82rem; padding: 5px 10px; }
}
/* ── General ────────────────────────────────────────── */
svg.chart-wheel { max-width: 100%; height: auto; }
.export-btn-row .stDownloadButton { margin-bottom: 4px; }

/* ── Palace grid (unified CSS for 天盤 / 宮位表) ──── */
.palace-grid {
    border-collapse: separate;
    border-spacing: 4px;
    margin: 10px auto;
    font-family: 'Noto Serif TC', serif;
}
.palace-grid td {
    width: 100px;
    height: 88px;
    text-align: center;
    vertical-align: middle;
    border: 2px solid #444;
    padding: 4px 2px;
    border-radius: 6px;
}
.palace-grid .center-cell {
    background: #fffde7;
    padding: 10px 8px;
    line-height: 1.6;
}
/* 五行配色 (Chinese five-element colours for palace cells) */
.palace-grid .elem-wood  { background: #d9f2d9; border-color: #388e3c; }
.palace-grid .elem-fire  { background: #ffe0d0; border-color: #c62828; }
.palace-grid .elem-earth { background: #fffbcc; border-color: #f57f17; }
.palace-grid .elem-metal { background: #e8e8e8; border-color: #616161; }
.palace-grid .elem-water { background: #cce5ff; border-color: #1565c0; }
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


# ── Plotly unified theme ────────────────────────────────────────

def get_plotly_theme() -> dict:
    """Return a unified Plotly layout theme dict for all chart modules."""
    return dict(
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        colorway=[
            PLANET_COLORS["Sun"], PLANET_COLORS["Moon"],
            PLANET_COLORS["Mercury"], PLANET_COLORS["Venus"],
            PLANET_COLORS["Mars"], PLANET_COLORS["Jupiter"],
            PLANET_COLORS["Saturn"],
        ],
    )


def apply_chart_theme(fig) -> None:
    """Apply the unified plotly theme to a plotly Figure *in place*."""
    fig.update_layout(**get_plotly_theme())


# ── SVG helpers ─────────────────────────────────────────────────

def svg_header(width: int = 600, height: int = 600, title: str = "") -> str:
    """Return a standardised SVG opening tag with consistent styling."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'class="chart-wheel" viewBox="0 0 {width} {height}" '
        f'style="background:{CHART_BG}; font-family:{FONT_FAMILY};">'
        f'<title>{title}</title>'
    )


def svg_footer() -> str:
    """Return the SVG closing tag."""
    return '</svg>'
