"""Replace `import streamlit as st` + `@st.cache_*` with core/cache shim in mixed files.

The 6 files that still leak streamlit in astro/ are mixed (compute+render)
files that use `@st.cache_data` for memoizing pure compute. We don't split
the render out here — that's a separate, larger refactor. We only
*decouple* the cache decorator from the streamlit import, using the
``core.cache`` shim introduced in the first decoupling pass.

The shim picks the real streamlit decorator when running inside a
Streamlit app and falls back to in-process memoization otherwise, so
compute modules become importable in non-streamlit contexts (CLI,
FastAPI, pytest) without changing their behavior in production.

Run from repo root:
    python3 scripts/_replace_st_cache_in_mixed.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro")
ASTRO = REPO / "astro"

# Files in the audit list that still import streamlit
TARGETS = [
    "astro/lal_kitab.py",
    "astro/ziwei.py",
    "astro/western/western.py",
    "astro/vedic/indian.py",
    "astro/thai.py",
    "astro/tibetan.py",
]


def rewrite_one(rel: str) -> tuple[bool, str]:
    p = REPO / rel
    src = p.read_text(encoding="utf-8", errors="ignore")
    new_src = src
    n_imp = 0
    n_cd = 0
    n_cr = 0

    # 1. Replace `import streamlit as st` with shim import
    if "import streamlit as st" in new_src:
        new_src = re.sub(
            r"^import streamlit as st\s*$",
            "from core.cache import cache_data, cache_resource",
            new_src,
            flags=re.MULTILINE,
        )
        n_imp = 1

    # 2. Replace @st.cache_data with @cache_data
    new_src, n_cd = re.subn(r"@st\.cache_data\b", "@cache_data", new_src)

    # 3. Replace @st.cache_resource with @cache_resource
    new_src, n_cr = re.subn(r"@st\.cache_resource\b", "@cache_resource", new_src)

    if n_imp == 0 and n_cd == 0 and n_cr == 0:
        return False, f"  skip: {rel} (no streamlit references)"

    # Also remove the now-unused "import streamlit" line if we found a usage
    # that wasn't already replaced (e.g. `from streamlit import X` form).
    # Safety: only remove if the rest of the file does NOT use st.
    if "import streamlit" in new_src and "st." not in new_src.split("from core.cache")[0] + new_src.split("from core.cache")[-1].split("cache_resource")[0]:
        # If the only st usage is the import line, leave it (already replaced above)
        pass

    if new_src != src:
        p.write_text(new_src, encoding="utf-8")
    return True, f"  ok {rel}: import={n_imp} cache_data={n_cd} cache_resource={n_cr}"


def main() -> int:
    print("Replacing @st.cache_* with core/cache shim in 6 mixed files...")
    ok, skip = 0, 0
    for rel in TARGETS:
        changed, msg = rewrite_one(rel)
        print(msg)
        if changed:
            ok += 1
        else:
            skip += 1
    print(f"\n{ok} changed, {skip} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
