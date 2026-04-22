# Changelog

All notable changes to Kin Astro (堅占星) will be documented in this file.

## [Unreleased]

### Added

#### New Astrology Systems
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
