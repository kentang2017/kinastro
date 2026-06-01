"""Batch-replace `import streamlit as st` + `@st.cache_*` decorators in
the 28 audited astro/ easy-win files.

For each file we:
  1. Replace `import streamlit as st` with
     `from core.cache import cache_data, cache_resource`
  2. Replace `@st.cache_data(...)` with `@cache_data(...)`
  3. Replace `@st.cache_resource(...)` with `@cache_resource(...)`

This keeps the call signature identical at the call site, but the
module no longer imports streamlit. The shim picks the real decorator
inside a Streamlit run, or the in-process fallback otherwise.

Run from repo root:
    python3 scripts/_apply_decouple_batch.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro")

EASY_WINS = [
    "astro/arabic/picatrix_data.py",
    "astro/astrocartography.py",
    "astro/burmese_mahabote/calculator.py",
    "astro/chinstar/chinstar.py",
    "astro/damo/calculator.py",
    "astro/interpretations_base.py",
    "astro/medical_astrology/calculator.py",
    "astro/qizheng/calculator.py",
    "astro/qizheng/financial/data_loader.py",
    "astro/qizheng/financial/stock_calculator.py",
    "astro/qizheng/financial/stock_fetcher.py",
    "astro/qizheng/ming_gong_interp.py",
    "astro/qizheng/qizheng_dasha.py",
    "astro/qizheng/qizheng_transit.py",
    "astro/qizheng/shensha.py",
    "astro/qizheng/zhangguo.py",
    "astro/sumerian/calculator.py",
    "astro/swe_init.py",
    "astro/systems/obscure/armenian.py",
    "astro/tojeong/tojeong_calculator.py",
    "astro/vedic/ashtakavarga.py",
    "astro/vedic/bphs_engine.py",
    "astro/vedic/vedic_dasha.py",
    "astro/vedic/vedic_yogas.py",
    "astro/western/predictive.py",
    "astro/western/western_return.py",
    "astro/western/western_synastry.py",
    "astro/western/western_transit.py",
]

NEW_IMPORT = "from core.cache import cache_data, cache_resource"

# Match `import streamlit as st` and `from streamlit import ...` (whole line, possibly with leading whitespace)
RE_STREAMLIT_IMPORT = re.compile(
    r"^[ \t]*(?:import streamlit as st|from streamlit[^\n]*)\s*$",
    re.MULTILINE,
)
# Match @st.cache_data(...) with whatever balanced-ish parens
RE_ST_CACHE_DATA = re.compile(r"@st\.cache_data\b")
RE_ST_CACHE_RESOURCE = re.compile(r"@st\.cache_resource\b")


def patch_file(rel: str) -> tuple[bool, str]:
    """Apply the 3 rewrites. Returns (changed, status_message)."""
    p = REPO / rel
    if not p.exists():
        return False, f"missing: {rel}"
    src = p.read_text(encoding="utf-8", errors="ignore")

    # Sanity: file should currently import streamlit
    if "import streamlit" not in src and "from streamlit" not in src:
        return False, f"no streamlit import found, skipped: {rel}"

    new_src = src
    new_src, n_imp = RE_STREAMLIT_IMPORT.subn(NEW_IMPORT, new_src)
    new_src, n_cd = RE_ST_CACHE_DATA.subn("@cache_data", new_src)
    new_src, n_cr = RE_ST_CACHE_RESOURCE.subn("@cache_resource", new_src)

    if n_imp == 0 and n_cd == 0 and n_cr == 0:
        return False, f"no replacements made: {rel}"

    if new_src != src:
        p.write_text(new_src, encoding="utf-8")

    msg = f"  ok {rel}: import={n_imp} cache_data={n_cd} cache_resource={n_cr}"
    return True, msg


def main() -> int:
    ok, skip = 0, 0
    for rel in EASY_WINS:
        changed, msg = patch_file(rel)
        print(msg)
        if changed:
            ok += 1
        else:
            skip += 1
    print(f"\nSummary: {ok} changed, {skip} skipped, {len(EASY_WINS)} total")
    return 0 if ok + skip == len(EASY_WINS) else 1


if __name__ == "__main__":
    sys.exit(main())
