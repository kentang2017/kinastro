# Bazi Chart Redesign - Code Reference & Examples

## Quick Reference: Function Signatures

```python
# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Lines 723-916)
# ═══════════════════════════════════════════════════════════════════════════

def render_summary_cards(chart: BaziChart) -> None:
    """
    Render professional top-level summary metric cards.
    
    Location: Lines 723-840
    Dependencies: streamlit, WUXING_COLORS, SHISHEN_COLORS, auto_cn
    Output: 4 dark-themed metric cards in single row
    Time: ~50-100ms
    """
    # Displays: Day Master | Strength | Pattern | Use God
    # Colors: Dynamic based on Five Elements
    # Styling: Dark gradients + shadows + color borders
    pass

def format_pillar_table_component(chart: BaziChart) -> None:
    """
    Render compact pillar data table with structural information.
    
    Location: Lines 843-876
    Dependencies: streamlit, pandas, auto_cn
    Output: Structured dataframe with 9 columns
    Time: ~30-50ms
    
    Columns:
      柱 (Pillar) | 干支 (Ganzhi) | 天干 (Stem) | 地支 (Branch) |
      干五行 (Stem Element) | 支五行 (Branch Element) | 十神 (Ten God) |
      藏干 (Hidden Stems) | 長生 (Growth Stage)
    """
    # Creates DataFrame with 4 rows (one per pillar)
    # Displays using st.dataframe with full width
    pass

def render_chart_section(chart: BaziChart, width: int = 500) -> None:
    """
    Render traditional ink-style SVG chart visualization.
    
    Location: Lines 879-896
    Dependencies: streamlit, streamlit.components, render_bazi_chart_svg
    Output: SVG chart in HTML component container
    Time: ~200-500ms (SVG generation intensive)
    Parameters:
      chart: BaziChart instance
      width: SVG width in pixels (default 500, use 420 for right column)
    """
    # Calls render_bazi_chart_svg() to generate SVG
    # Wraps in HTML container with #F5F0E0 background
    # Sets height to 700px for responsive display
    pass

def render_sidebar_controls() -> None:
    """
    Render left sidebar control panel.
    
    Location: Lines 899-916
    Dependencies: streamlit, auto_cn
    Output: Collapsible expander with controls
    Time: ~20ms
    
    Contains:
      • Adjustment instructions
      • Download button (placeholder)
    """
    # Expander with default closed state
    # Info message about updating chart
    # Download CSV/PDF button (future feature)
    pass

def render_streamlit(chart: BaziChart) -> None:
    """
    Main orchestrating function - renders complete 3-column professional layout.
    
    Location: Lines 925-1242
    Dependencies: All above + pandas, streamlit tabs/columns
    Output: Complete professional Bazi chart display
    Time: ~500-1500ms (includes SVG generation)
    
    Structure:
      1. Summary cards (top)
      2. 3-column main area (sidebar | table | chart)
      3. Pillar detail cards
      4. 4 analysis tabs
    """
    pass
```

## Code Structure Breakdown

### Section 1: Summary Cards (Lines 723-840)

```python
def render_summary_cards(chart: BaziChart) -> None:
    # Creates 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Column 1: Day Master Card
    with col1:
        dm_wuxing = chart.day_master_wuxing
        dm_color = WUXING_COLORS.get(dm_wuxing, "#666")
        st.markdown(
            f"""<div style="
                padding: 16px 14px;
                border-radius: 12px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border: 1px solid {dm_color}44;
                ...styling...">
                ...card content...
            </div>""",
            unsafe_allow_html=True
        )
    
    # Columns 2-4: Similar pattern for Strength, Pattern, Use God
```

### Section 2: Pillar Table (Lines 843-876)

```python
def format_pillar_table_component(chart: BaziChart) -> None:
    import pandas as pd
    
    # Build pillar records (4 rows)
    pillars_data = []
    for label, p in [
        (auto_cn("年柱", "Year"), chart.year_pillar),
        (auto_cn("月柱", "Month"), chart.month_pillar),
        (auto_cn("日柱", "Day"), chart.day_pillar),
        (auto_cn("時柱", "Hour"), chart.hour_pillar),
    ]:
        pillars_data.append({
            auto_cn("柱", "Pillar"): label,
            auto_cn("干支", "Ganzhi"): p.ganzhi,
            auto_cn("天干", "Stem"): p.stem,
            auto_cn("地支", "Branch"): p.branch,
            auto_cn("干五行", "Stem El."): p.wuxing_stem,
            auto_cn("支五行", "Branch El."): p.wuxing_branch,
            auto_cn("十神", "Ten God"): p.shishen,
            auto_cn("藏干", "Hidden"): "、".join(p.canggan),
            auto_cn("長生", "Growth"): p.changsheng or "—",
        })
    
    df_pillars = pd.DataFrame(pillars_data)
    st.dataframe(df_pillars, width="stretch", use_container_width=True)
```

### Section 3: SVG Chart (Lines 879-896)

```python
def render_chart_section(chart: BaziChart, width: int = 500) -> None:
    # Generate SVG from chart data
    svg_html = render_bazi_chart_svg(chart, width=width, height=650)
    
    # Wrap in styled HTML container
    components.html(
        f'<div style="background:#F5F0E0;padding:8px;border-radius:8px;'
        f'height:100%;display:flex;align-items:center;justify-content:center;">'
        f'{svg_html}</div>',
        height=700,
        scrolling=False,
    )
```

### Section 4: Main Layout (Lines 925-1000)

```python
def render_streamlit(chart: BaziChart) -> None:
    import pandas as pd
    
    # === SECTION 1: SUMMARY CARDS ===
    st.subheader(auto_cn("📊 命盤概覽", "Chart Overview"))
    render_summary_cards(chart)
    st.divider()
    
    # === SECTION 2: 3-COLUMN MAIN AREA ===
    st.subheader(auto_cn("🏛 四柱命盤", "Four Pillars Chart"))
    
    # Create 3 columns with ratio 0.8:1.2:1.2
    left_col, center_col, right_col = st.columns([0.8, 1.2, 1.2], gap="medium")
    
    # LEFT COLUMN: Sidebar
    with left_col:
        render_sidebar_controls()
        st.divider()
        st.caption(auto_cn("圖例 | Legend"))
        _render_ten_god_legend()
    
    # CENTER COLUMN: Pillar Table
    with center_col:
        st.markdown(
            f"<div style='font-size:0.9rem; color:#888; margin-bottom:10px;'>"
            f"{auto_cn('柱位結構', 'Pillar Structure')}</div>",
            unsafe_allow_html=True
        )
        format_pillar_table_component(chart)
    
    # RIGHT COLUMN: SVG Chart
    with right_col:
        st.markdown(
            f"<div style='font-size:0.9rem; color:#888; margin-bottom:10px;'>"
            f"{auto_cn('傳統水墨命盤', 'Traditional Ink-Style Chart')}</div>",
            unsafe_allow_html=True
        )
        render_chart_section(chart, width=420)
    
    st.divider()
    
    # === SECTION 3: PILLAR DETAIL CARDS ===
    st.subheader(auto_cn("🔍 四柱詳細", "Pillar Details"))
    _render_pillar_cards(chart)
    
    st.divider()
    
    # === SECTION 4: ANALYSIS TABS ===
    main_tabs = st.tabs([
        auto_cn("格局用神與神煞", "Pattern, Use God & Shen Sha"),
        auto_cn("大運與流年", "Great Luck & Annual Flow"),
        auto_cn("盲派論斷", "Blind School"),
        auto_cn("詳細解讀報告", "Detailed Reading"),
    ])
    
    # Tab 0: Pattern & Use God Analysis
    with main_tabs[0]:
        # Day Master Strength, Pattern, Use God, Shen Sha, Branch Interactions
        ...
    
    # Tab 1: Great Luck & Annual Flow
    with main_tabs[1]:
        # Dayun table, current liunian
        ...
    
    # Tab 2: Blind School
    with main_tabs[2]:
        # Blind school analysis with visual, structured, raw tabs
        ...
    
    # Tab 3: Detailed Reading
    with main_tabs[3]:
        # Classical Chinese and English interpretation
        ...
```

## Color Reference

### Five Elements (WUXING_COLORS)
```python
WUXING_COLORS = {
    "木": "#3D7A3D",  # Wood - Dark Green
    "火": "#C0392B",  # Fire - Dark Red
    "土": "#D4A017",  # Earth - Gold
    "金": "#7F8C8D",  # Metal - Gray
    "水": "#1A5276",  # Water - Dark Blue
}
```

### Light Variants (WUXING_COLORS_LIGHT)
```python
WUXING_COLORS_LIGHT = {
    "木": "#A8D5A2",  # Light Green
    "火": "#F1948A",  # Light Red
    "土": "#F9E4B7",  # Light Gold
    "金": "#BFC9CA",  # Light Gray
    "水": "#85C1E9",  # Light Blue
}
```

### Ten Gods (SHISHEN_COLORS)
```python
SHISHEN_COLORS = {
    "比肩": "#2E7D32",   # Companion
    "劫財": "#388E3C",   # Robber
    "食神": "#C62828",   # Output-a
    "傷官": "#E53935",   # Output-b
    "偏財": "#1565C0",   # Wealth-a
    "正財": "#1E88E5",   # Wealth-b
    "七殺": "#6A1B9A",   # Authority-a
    "正官": "#8E24AA",   # Authority-b
    "偏印": "#212121",   # Seal-a
    "正印": "#424242",   # Seal-b
    "日主": "#8B4513",   # Day Master
}
```

### Accent Colors
```python
SVG_SEAL_RED = "#C41E3A"          # Seal red (朱砂紅)
SVG_PAPER_BG = "#F5F0E0"          # Paper (宣紙)
SVG_INK_DARK = "#1A0A00"          # Ink (墨色)
SVG_BORDER_COLOR = "#8B6914"      # Border (邊框)
SVG_SUBTITLE_COLOR = "#5C4033"    # Subtitle (副標)
```

## Data Types

### BaziChart Class (from astro/bazi/calculator.py)
```python
class BaziChart:
    # Pillars
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    
    # Key Properties
    day_master: str              # e.g., "甲"
    day_master_wuxing: str       # e.g., "木"
    day_master_strength: str     # "強" or "弱"
    day_master_strength_score: int
    day_master_vitality: str     # "旺" or "休" etc.
    
    # Pattern & Use God
    pattern: str                 # e.g., "建祿格"
    pattern_type: str            # e.g., "Formation"
    pattern_description_zh: str
    
    yongshen: str                # Use God
    xishen: str                  # Xi God
    jishen: str                  # Avoid God
    jiaoshen: str                # Enemy God
    tiaohoushen: str             # Seasonal Use God
    yongshen_description_zh: str
    
    # Shen Sha
    shensha_list: List[ShenSha]  # List of auspicious/inauspicious stars
    
    # Interactions
    interactions: Interactions   # 六合, 三合, 六冲, etc.
    
    # Great Luck
    dayun_direction: str         # "順行" or "逆行"
    dayun_start_age: float
    dayun_start_date: str
    dayun_steps: List[DayunStep]
    current_dayun: Optional[DayunStep]
    current_liunian: str         # e.g., "甲辰"
    current_liunian_year: int
    
    # Reading
    reading_zh: str              # Classical Chinese interpretation
    reading_en: str              # English translation
    
    # Optional
    blind_school_report: Optional[dict]
    gender: Optional[str]        # "Male" or "Female"
```

### Pillar Class (from astro/bazi/calculator.py)
```python
class Pillar:
    ganzhi: str                  # e.g., "甲子" (stem-branch)
    stem: str                    # e.g., "甲"
    branch: str                  # e.g., "子"
    wuxing_stem: str             # e.g., "木"
    wuxing_branch: str           # e.g., "水"
    shishen: str                 # e.g., "比肩"
    canggan: List[str]           # Hidden stems in branch
    canggan_shishen: List[str]   # Ten Gods of hidden stems
    changsheng: str              # e.g., "死", "絕", "胎", "養", "長生"
```

## Bilingual String Mapping

### auto_cn() Function Usage
```python
# Pattern: auto_cn("Chinese", "English")
auto_cn("日主", "Day Master")
auto_cn("強弱", "Strength")
auto_cn("格局", "Pattern")
auto_cn("用神", "Use God")
auto_cn("四柱", "Four Pillars")
auto_cn("命盤", "Chart")
auto_cn("分析", "Analysis")

# Returns Chinese string in Chinese mode, English in English mode
```

## Common Patterns

### Creating a Styled Card
```python
color = "#C41E3A"  # Seal red
st.markdown(
    f"""
    <div style="
        padding: 16px 14px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid {color}44;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-align: center;
    ">
        <div style="font-size: 0.85rem; color: #a0a0a0; margin-bottom: 8px; letter-spacing: 1px;">
            {auto_cn("標題", "Title")}
        </div>
        <div style="font-size: 2.2rem; font-weight: 700; color: {color}; margin-bottom: 6px;">
            Value
        </div>
        <div style="font-size: 0.75rem; color: #777; letter-spacing: 0.5px;">
            {auto_cn("說明", "Description")}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
```

### Creating a 3-Column Layout
```python
left_col, center_col, right_col = st.columns([0.8, 1.2, 1.2], gap="medium")

with left_col:
    # Left content (20% width)
    pass

with center_col:
    # Center content (40% width)
    pass

with right_col:
    # Right content (40% width)
    pass
```

### Creating a Tab Section
```python
tabs = st.tabs([
    auto_cn("標籤1", "Tab 1"),
    auto_cn("標籤2", "Tab 2"),
    auto_cn("標籤3", "Tab 3"),
])

with tabs[0]:
    st.subheader(auto_cn("第一標籤內容", "First Tab Content"))
    # Content for tab 0

with tabs[1]:
    st.subheader(auto_cn("第二標籤內容", "Second Tab Content"))
    # Content for tab 1

with tabs[2]:
    st.subheader(auto_cn("第三標籤內容", "Third Tab Content"))
    # Content for tab 2
```

### Color-Coding by Five Element
```python
def get_element_color(element: str) -> str:
    return WUXING_COLORS.get(element, "#666")

def get_element_color_light(element: str) -> str:
    return WUXING_COLORS_LIGHT.get(element, "#ccc")

# Usage
color = get_element_color(pillar.wuxing_stem)  # e.g., "#3D7A3D" for 木
```

## Import Requirements

```python
# At top of render.py (Lines 13-36)
from __future__ import annotations

import textwrap
from datetime import date
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

from astro.i18n import auto_cn, t

from astro.bazi.calculator import BaziChart, DayunStep, compute_bazi, _get_kongwang
from astro.bazi.constants import (
    SHISHEN_COLORS,
    SHISHEN_RELATIONS_F,
    SHISHEN_RELATIONS_M,
    SVG_BORDER_COLOR,
    SVG_INK_DARK,
    SVG_PAPER_BG,
    SVG_SEAL_RED,
    SVG_SUBTITLE_COLOR,
    WUXING_COLORS,
    WUXING_COLORS_LIGHT,
)
```

## File Locations & Line Numbers

```
ui/handlers/tab_bazi/render.py

Line 1-36:     Imports & Module Documentation
Line 40-568:   SVG Generation (render_bazi_chart_svg)
Line 571-607:  Helper Functions (_get_kongwang_for_chart, _normalize_gender, _pillar_records)
Line 610-690:  Legend & Card Rendering (_render_ten_god_legend, _render_pillar_cards)
Line 692-716:  Wuxing Balance (_render_wuxing_balance)

Line 723-840:  render_summary_cards() [NEW]
Line 843-876:  format_pillar_table_component() [NEW]
Line 879-896:  render_chart_section() [NEW]
Line 899-916:  render_sidebar_controls() [NEW]

Line 925-1242: render_streamlit() [REDESIGNED]
  Line 940-945:  Summary Cards Section
  Line 948-977:  3-Column Main Layout
  Line 980-984:  Pillar Detail Cards
  Line 989-999:  Tab Definition
  Line 1001-1080: Tab 0 - Pattern & Use God
  Line 1082-1111: Tab 1 - Dayun & Liunian
  Line 1113-1229: Tab 2 - Blind School
  Line 1231-1242: Tab 3 - Detailed Reading
```

## Performance Metrics (Estimated)

```
Function Call Times:
  render_summary_cards():              50-100ms
  format_pillar_table_component():     30-50ms
  render_chart_section():              200-500ms (SVG generation)
  render_sidebar_controls():           20ms
  render_streamlit() [total]:          500-1500ms
  
Memory Usage:
  BaziChart object:                    ~50-100KB
  SVG HTML output:                     ~200-500KB
  Rendered page:                       ~1-2MB
  
Rerender on change:
  Same day/time:                       ~500ms (cached)
  Different day/time:                  ~1500ms (recalculate)
  Tab switch:                          <50ms
```

## Next Steps for Extension

To add new features to the Bazi display:

1. **Create new helper function**:
   ```python
   def render_new_feature(chart: BaziChart) -> None:
       """Description of new feature."""
       # No streamlit imports at function level
       # Return None - modify st.* directly
       pass
   ```

2. **Place in appropriate section**:
   - Top metrics → modify `render_summary_cards()`
   - Table data → modify `format_pillar_table_component()`
   - Chart area → modify `render_chart_section()`
   - Sidebar → modify `render_sidebar_controls()`
   - New tab → add to `main_tabs = st.tabs([...])`

3. **Ensure bilingual support**:
   - Use `auto_cn()` for all user-facing strings
   - Test in both Chinese and English mode

4. **Test responsive layout**:
   - Desktop (1920px)
   - Tablet (1024px)
   - Mobile (375px)

5. **Update documentation**:
   - Add to BAZI_REDESIGN_SUMMARY.md
   - Add to BAZI_LAYOUT_REFERENCE.md
   - Update this code reference

6. **Commit with clear message**:
   ```bash
   git commit -m "feat: add [feature name] to Bazi display
   
   - Add render_[feature]() helper function
   - Integrate into [section] of layout
   - Bilingual support for [languages]
   - Tested on [platforms]"
   ```
