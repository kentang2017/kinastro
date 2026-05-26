# KinAstro Architecture Overview (2026)

**Goal**: Support 84+ astrology systems with high fidelity while keeping the codebase maintainable, testable, and extensible.

## Three-Layer Model (Current Direction)

1. **Descriptive Layer** — `astro/system_registry.py`
   - Single source of truth for all 84 systems.
   - `System` dataclass: id, names (i18n keys), category, sub_tabs, feature flags, AI persona, accent color, etc.
   - Used by sidebar selector (`ui/components/system_selector.py`), metadata lookups, and future auto-generation.

2. **Execution Layer** — `ui/system_engine.py` + `SystemHandler`
   - `SystemEngine` + `EXECUTION_REGISTRY` (singleton).
   - `SystemHandler(system_id, compute, render, options_schema)`.
   - `run_system(...)` handles spinner, error boundary, and calls the pair.
   - Handlers live in `ui/system_handlers/`.
   - **Phase 1**: only `tab_ziwei` registered (see `phase1_handlers.py`).
   - Legacy fallback still exists in `app.py` for everything else.

3. **Legacy Monolith** — `app.py` (6.3k LOC)
   - Giant top-level if/elif dispatch on `_selected_system`.
   - ~87 branches, heavy duplication of `st.tabs`, `st.spinner`, try/except + AI hook, session_state param extraction.
   - **Migration invariant**: `if EXECUTION_REGISTRY.run_system(...)` succeeds → skip legacy branch. Never remove the fallback until 100% coverage + full test sign-off.

## Compute vs Render Separation (Critical Rule)

- **Pure compute** (`*calculator.py`, `core.py`, many root `*.py`): **NO `import streamlit`**.
  - Must accept primitive args or `BirthChartParams`.
  - Return plain dataclasses / dicts / primitives (JSON-serializable for API).
  - Use `@st.cache_data` only via thin wrappers in handlers or `ui/` layer when needed.
- **Render** (`*renderer.py`, `frontend/*`): may import `streamlit`, call `st.*`, build SVG/Plotly, etc.
- **Why**: Enables:
  - FastAPI reuse (`api_server.py`)
  - Pure unit tests (no Streamlit runtime)
  - Future headless / CLI / batch use

**Current reality** (Phase 0 audit): 53 compute-layer files still touch Streamlit (baseline established by `scripts/audit_st_imports.py`).

## Key Shared Utilities (Under-adopted)

- `astro/i18n.py` — `t(key)`, `auto_cn`, bilingual.
- `astro/chart_theme.py` — colors, `svg_header/footer`, `apply_chart_theme`.
- `astro/systems/base.py` — `BaseChart` (minimal adoption so far).
- `astro/export.py`, `cache_keys.py`, `interpretations_base.py`.

New systems should use these. Linter rules + template will enforce over time.

## Adding a New System (2026 Recommended Flow)

1. Create package under `astro/<slug>/`:
   - `calculator.py` (pure)
   - `renderer.py` (st allowed)
   - `constants.py`, `models.py` optional
   - `__init__.py` with lazy re-exports (see `andean/`, `maya/` as exemplars)
2. Declare in `astro/system_registry.py` (add `System(...)` + `_reg`).
3. (Optional but recommended) Create `ui/system_handlers/build_<slug>_handler.py` returning a `SystemHandler`.
4. In `app.py` (or central init): register the handler if you want to bypass legacy branch.
5. Add i18n keys.
6. Add tests under `tests/test_<slug>*.py`.
7. Update wiki/ + docs if culturally significant.

See `astro/template/` (being modernized in Phase 1) and `CONTRIBUTING.md`.

## Current State & Migration Status

- **Metadata**: Excellent (84 systems fully described).
- **Execution**: Early (1/84 handlers).
- **app.py**: The main technical debt (dispatch hell + duplication).
- **Purity**: Partial (newer packages better than legacy flats).
- **Tests**: Good volume (~40 files), variable depth.

## References

- Full optimization plan: see the plan.md generated during exploration (or ask maintainer).
- Audit tool: `python scripts/audit_st_imports.py`
- Phase 1 goal: app.py < 5k LOC, ≥3 handlers, measurable drop in compute-layer st imports.
- Long-term: declarative registration, scaffold CLI, >80% core test coverage, single source of truth for versions.

**Never break existing users.** All changes preserve the legacy fallback path until proven.

---

*Last updated: Phase 0 (initial docs + audit baseline).*
