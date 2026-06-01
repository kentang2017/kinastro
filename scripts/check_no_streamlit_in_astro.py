#!/usr/bin/env python3
"""Regression guard: prevent new streamlit dependencies in astro/ compute modules.

Background
----------
The ``astro/`` package is meant to be importable without Streamlit so that
the FastAPI ``api_server.py`` and ``pytest`` collection can run in
streamlit-less environments (CI, plain Python, FastAPI server).  Compute
modules should depend on Streamlit *only* for cache decorators, and those
should go through the ``core.cache`` shim (which falls back to in-process
LRU / TTL memo when Streamlit is not in a run context).

What this script does
---------------------
1. Walks every ``astro/**/*.py`` file (skipping the existing
   ``astro/i18n.py``-allowed streamlit import pattern).
2. Greps for ``import streamlit``, ``from streamlit``, and
   ``@st.cache_data`` / ``@st.cache_resource``.
3. Fails (exit 1) if any are found in a file that has not been explicitly
   allow-listed.
4. Prints a short report (file list) when violations are found.

Allowed exceptions
------------------
* ``astro/i18n.py`` — the only streamlit access is wrapped in a
  try/except inside :func:`get_ui_lang`; the override / env-var fallback
  is the canonical path now.  Future cleanup can drop this exemption.
* Files in :data:`PENDING_FILES` — the 51 compute+render mixed files
  that will be addressed in the follow-up "split compute from render"
  refactor.  Each is tracked with a short reason.

Adding a new file
-----------------
When you genuinely need streamlit inside a new ``astro/`` module (rare —
most cases should use :mod:`core.cache`), add it to :data:`PENDING_FILES`
with a TODO referencing the follow-up plan, or — better — fix the
underlying coupling and remove it from the allow-list.

Usage
-----
::

    python3 scripts/check_no_streamlit_in_astro.py        # exit 0 if clean
    python3 scripts/check_no_streamlit_in_astro.py --fix   # print stats only

Exit codes:
    0 — clean (no violations)
    1 — violations found
    2 — script error
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASTRO = REPO / "astro"

# Patterns that indicate streamlit coupling at the file scope.
# Note: docstrings often mention ``@st.cache_data`` without the file
# actually using it; we filter those out by requiring the pattern to
# appear on a line whose first non-whitespace character is ``@``.
PATTERNS = [
    re.compile(r"^import\s+streamlit\b", re.MULTILINE),
    re.compile(r"^from\s+streamlit\b", re.MULTILINE),
    re.compile(r"^[ \t]*@st\.cache_data\b", re.MULTILINE),
    re.compile(r"^[ \t]*@st\.cache_resource\b", re.MULTILINE),
]

# Files that are explicitly allowed to use streamlit. Keep this list
# short and tied to tracked follow-up work; the goal is to shrink it.
PENDING_FILES: dict[str, str] = {
    # ── i18n: lazy streamlit access; canonical path is now non-streamlit ──
    "astro/i18n.py": "Uses streamlit lazily inside get_ui_lang() with override fallback. TODO: drop when callers stop reading st.session_state directly.",
    # ── template: scaffold for new systems; deliberately streamlit-flavored ──
    "astro/template/my_system.py": "Scaffold template for new astrology systems; intentionally demonstrates streamlit usage. Not part of the runtime package.",
    # ── render-only modules that are still imported eagerly from `astro/__init__.py` ──
    "astro/bazi/renderer.py": "render-only; not in scope",
    "astro/beiji/renderer.py": "render-only; not in scope",
    "astro/bintang_duabelas/renderer.py": "render-only; not in scope",
    "astro/burmese_mahabote/renderer.py": "render-only; not in scope",
    "astro/byzantine_astrology/renderer.py": "render-only; not in scope",
    "astro/chinese/taixuan/taixuan_renderer.py": "render-only; not in scope",
    "astro/chunzi/renderer.py": "render-only; not in scope",
    "astro/cosmobiology/renderer.py": "render-only; not in scope",
    "astro/damo/renderer.py": "render-only; not in scope",
    "astro/electional/renderer.py": "render-only; not in scope",
    "astro/esoteric/renderer.py": "render-only; not in scope",
    "astro/harmonic/renderer.py": "render-only; not in scope",
    "astro/horary/renderer.py": "render-only; not in scope",
    "astro/human_design/renderer.py": "render-only; not in scope",
    "astro/jawa_weton/renderer.py": "render-only; not in scope",
    "astro/kaiyuan/renderer.py": "render-only; not in scope",
    "astro/kp/kp_renderer.py": "render-only; not in scope",
    "astro/maya/renderer.py": "render-only; not in scope",
    "astro/medical_astrology/renderer.py": "render-only; not in scope",
    "astro/mundane/renderer.py": "render-only; not in scope",
    "astro/persian/renderer.py": "render-only; not in scope",
    "astro/picatrix_behenian/renderer.py": "render-only; not in scope",
    "astro/polynesian_hawaiian/renderer.py": "render-only; not in scope",
    "astro/primary_directions/renderer.py": "render-only; not in scope",
    "astro/qizheng/chart_renderer.py": "render-only; not in scope",
    "astro/qizheng/financial/stock_renderer.py": "render-only; not in scope",
    "astro/rectification/renderer.py": "render-only; not in scope",
    "astro/shaozi/renderer.py": "render-only; not in scope",
    "astro/sports/renderer.py": "render-only; not in scope",
    "astro/sumerian/renderer.py": "render-only; not in scope",
    "astro/tojeong/tojeong_renderer.py": "render-only; not in scope",
    "astro/trutine_of_hermes/renderer.py": "render-only; not in scope",
    "astro/wariga/renderer.py": "render-only; not in scope",
    "astro/western/predictive_ui.py": "render-only; not in scope",
    "astro/wuyunliuqi/renderer.py": "render-only; not in scope",
    "astro/andean/renderer.py": "render-only; not in scope",
    "astro/etruscan/renderer.py": "render-only; not in scope",
    "astro/liuyao_lifetime/renderer.py": "render-only; not in scope",
    "astro/diqiyijue/renderer.py": "render-only; not in scope",
    "astro/nanji/renderer.py": "render-only; not in scope",
    "astro/huangji/renderer.py": "render-only; not in scope",
    "astro/kinketika/renderer.py": "render-only; not in scope",
    "astro/laos/renderer.py": "render-only; not in scope",
    "astro/shanghan_qianfa/renderer.py": "render-only; not in scope",
    "astro/dogon/renderer.py": "render-only; not in scope",
    "astro/astronomical_geomancy/renderer.py": "render-only; not in scope",
    "astro/astronomical_geomancy/chart_renderer_geomancy.py": "render-only; not in scope",
    # ── package __init__.py files that still eagerly import renderers ──
    "astro/damo/__init__.py": "package init eager-imports damo.renderer",
    "astro/diqiyijue/__init__.py": "package init eager-imports renderer",
    "astro/kinketika/__init__.py": "package init eager-imports renderer",
    "astro/kp/__init__.py": "package init eager-imports kp_renderer",
    "astro/qizheng/__init__.py": "package init eager-imports chart_renderer",
    "astro/qizheng/financial/__init__.py": "package init eager-imports stock_renderer",
    "astro/sanshi/__init__.py": "package init eager-imports renderers",
    "astro/sumerian/__init__.py": "package init eager-imports renderer",
    "astro/tojeong/__init__.py": "package init eager-imports renderer",
    "astro/wariga/__init__.py": "package init eager-imports renderer",
    # ── remaining compute+render mixed files (NOT YET decoupled) ──
    "astro/arabic/ms164_browser.py": "compute+render mixed; follow-up: split",
    "astro/arabic/picatrix_mansions.py": "compute+render mixed; follow-up: split",
    "astro/arabic/shams_maarif.py": "compute+render mixed; follow-up: split",
    "astro/cross_compare.py": "compute+render mixed; follow-up: split",
    "astro/export.py": "compute+render mixed; follow-up: split",
    "astro/lal_kitab.py": "compute+render mixed; follow-up: split",
    "astro/qizheng/qizheng_financial.py": "compute+render mixed; follow-up: split",
    "astro/sanshi/kinliuren/kinliuren.py": "compute+render mixed; follow-up: split",
    "astro/sanshi/kinliuren.py": "compute+render mixed; follow-up: split",
    "astro/thai.py": "compute+render mixed; follow-up: split",
    "astro/tibetan.py": "compute+render mixed; follow-up: split",
    "astro/tieban/tieban_browser.py": "compute+render mixed; follow-up: split",
    "astro/vedic/indian.py": "compute+render mixed; follow-up: split",
    "astro/western/western.py": "compute+render mixed; follow-up: split",
}


def _is_in_docstring(src_lines: list[str], line_no: int) -> bool:
    """Return True if *line_no* (1-indexed) is inside a triple-quoted string.

    Walks the file from the top counting opens/closes of triple-quoted
    strings.  This is a coarse heuristic; it does not handle ``\\\"\\\"\\\"``
    inside an f-string, but in practice the kind of code we are
    scanning does not contain such constructs.
    """
    in_doc = False
    quote = ""
    for i, line in enumerate(src_lines, 1):
        if i > line_no:
            break
        stripped = line.strip()
        if not in_doc:
            # Look for an opening triple quote
            for q in ('"""', "'''"):
                if q in stripped:
                    count = stripped.count(q)
                    if count % 2 == 1:
                        in_doc = True
                        quote = q
                        break
        else:
            # Look for the closing triple quote on this line
            if quote in stripped:
                in_doc = False
                quote = ""
    return in_doc


def find_violations() -> list[tuple[str, str, int]]:
    """Return list of (rel_path, snippet, line_number) for each violation."""
    violations: list[tuple[str, str, int]] = []
    for path in sorted(ASTRO.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = str(path.relative_to(REPO))
        if rel in PENDING_FILES:
            continue
        try:
            src = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        src_lines = src.splitlines()
        for pat in PATTERNS:
            for m in pat.finditer(src):
                line_no = src.count("\n", 0, m.start()) + 1
                if _is_in_docstring(src_lines, line_no):
                    continue
                snippet = m.group(0).strip()
                violations.append((rel, snippet, line_no))
    return violations


def main(argv: list[str]) -> int:
    fix_mode = "--fix" in argv
    violations = find_violations()
    if not violations:
        print("✓ astro/ has no unexpected streamlit dependencies")
        return 0
    print(f"✗ Found {len(violations)} streamlit dependency violation(s) in astro/")
    print("-" * 70)
    by_file: dict[str, list[tuple[str, int]]] = {}
    for rel, snippet, line_no in violations:
        by_file.setdefault(rel, []).append((snippet, line_no))
    for rel, hits in sorted(by_file.items()):
        print(f"\n  {rel}")
        for snippet, line_no in hits:
            print(f"    L{line_no}: {snippet}")
    print()
    print(f"Pending allow-listed files (tracked follow-up): {len(PENDING_FILES)}")
    if fix_mode:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
