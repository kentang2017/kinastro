# Changelog

All notable changes to Kin Astro (堅占星) will be documented in this file.

## [Unreleased]

### Added

#### 🔀 Multi-System Cross-Comparison AI Synthesis
- **`astro/ai_analysis.py`**: New `get_cross_system_analysis()` function that
  extracts key insights (planet positions, dignities, yogas, palaces, etc.) from
  Western, Vedic, Chinese Qi Zheng, Zi Wei Dou Shu, and Hellenistic charts into
  a structured dict.
- **`astro/ai_analysis.py`**: New `format_cross_system_for_prompt()` function
  formats the structured analysis into a human-readable text block for the AI.
- **`astro/ai_analysis.py`**: `CROSS_SYSTEM_SYNTHESIS_PROMPT` and
  `CROSS_SYSTEM_SYNTHESIS_PROMPT_EN` — dedicated bilingual system prompts guiding
  Cerebras to cross-reference all systems, highlighting agreements, contradictions,
  and unique insights (e.g. "Western T-Square vs Zi Wei conflict stars").
- **`app.py` sidebar**: New toggle "🔀 啟用多體系交叉比對 / Enable Cross-System
  Comparison" that activates the synthesis section from any system tab.
- **`app.py` cross-system section**: When the toggle is on, simultaneously computes
  Western, Vedic, Chinese, Zi Wei, and Hellenistic charts, shows a cross-comparison
  planet table, detects aspect patterns, and provides a dedicated AI chat for
  synthesized interpretation with one-click "generate synthesis" button.

#### 🔷 Aspect Pattern Detection & Visualization
- **`astro/western/aspect_patterns.py`** (new module): `detect_aspect_patterns()`
  scans all planet positions and detects:
  - Grand Trine (大三角), T-Square (T形相位), Grand Cross (大十字)
  - Yod / Finger of God (命運指), Kite (風箏), Mystic Rectangle (神秘長方形)
  - Grand Sextile (大六芒星), Stellium (星群), Boomerang (回力鏢)
  Each pattern includes element, quality, apex planet, and bilingual descriptions.
- **`astro/western/aspect_patterns.py`**: `build_aspect_pattern_figure()` — Plotly
  polar figure showing planet positions and colored pattern lines, with zodiac glyphs
  and interactive legend.
- **`astro/western/aspect_patterns.py`**: `render_aspect_patterns()` — Streamlit
  renderer with summary table, Plotly wheel, and colour-coded detail cards.
- **`astro/western/aspect_patterns.py`**: `format_patterns_for_prompt()` — formats
  detected patterns for inclusion in AI analysis prompts.
- **`app.py` Western natal tab**: New checkbox "🔷 顯示相位圖案 / Show Aspect Patterns"
  that renders the Aspect Pattern Wheel and detail cards.
- **AI integration**: Detected aspect patterns are automatically included in the
  cross-system AI prompt data for synthesized interpretation.

#### i18n
- Added translation keys: `show_aspect_patterns`, `aspect_patterns_header`,
  `enable_cross_system`, `tab_cross_system`, `cross_system_header`,
  `cross_system_intro`, `cross_system_computing`, `cross_system_ai_btn`,
  `cross_system_ai_generating`, `cross_system_comparison_table`,
  `cross_system_api_missing`.

- **Hellenistic Astrology** (`astro/hellenistic.py`): Greek Lots (Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis), Egyptian Bounds/Terms, Annual Profections, Zodiacal Releasing (L1), Planetary Condition scoring, Sect analysis

#### New Features — Western Astrology
- **Transit Analysis** (`astro/western_transit.py`): Real-time transit planet aspects to natal chart
- **Solar & Lunar Return** (`astro/western_return.py`): Newton-Raphson precision return charts
- **Synastry** (`astro/western_synastry.py`): Cross-aspects, harmony scoring, element compatibility

#### New Features — Vedic Astrology
- **Vimshottari & Yogini Dasha** (`astro/vedic_dasha.py`): 120-year and 36-year dasha cycles with Antardasha sub-periods
- **Ashtakavarga** (`astro/ashtakavarga.py`): 7-planet Bhinnashtakavarga + Sarvashtakavarga
- **Vedic Yogas** (`astro/vedic_yogas.py`): 12 yoga detections including Gajakesari, Kemdruma, Gandanta, 5 Mahapurusha

#### New Features — Chinese Astrology
- **Electional Tool** (`astro/qizheng_electional.py`): Date selection with stem-branch scoring

#### New Shared Modules
- **Fixed Stars** (`astro/fixed_stars.py`): 25 classical stars via Swiss Ephemeris
- **Asteroids** (`astro/asteroids.py`): Chiron, Ceres, Pallas, Juno, Vesta
- **Cross-System Comparison** (`astro/cross_compare.py`): Unified planet positions across Western/Vedic/Chinese
- **Chart Export** (`astro/export.py`): Text summary, CSV, and PDF download
- **Session Store** (`astro/session_store.py`): Save/load/import/export chart parameters
- **Chart Theme** (`astro/chart_theme.py`): Unified colour palette + mobile CSS

### Changed
- **app.py**: Expanded from 13 to 15 tabs (added Hellenistic, Cross Compare)
- **Western tab**: Now has 4 sub-tabs (Natal, Transit, Solar Return, Synastry)
- **Vedic tab**: Now has 4 sub-tabs (Rashi, Dasha, Ashtakavarga, Yogas)
- **Chinese tab**: Added 擇日 (Electional) sub-tab
- **Sidebar**: Added chart save/load manager
- **Mobile CSS**: Responsive layout for tablets and phones
- **i18n**: Added translation keys for all new features
- **requirements.txt**: Added `fpdf2>=2.7.6`

### Tests
- Added 76 new tests in `tests/test_advanced_features.py` covering all 14 new modules
