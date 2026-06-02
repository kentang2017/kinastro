"""Replace any leftover `import streamlit as st` + `@st.cache_data` /
`@st.cache_resource` in astro/qizheng/ with the core.cache shim.

Phase 6 missed these compute modules. The streamlit direct use means
that when a test injects a stub streamlit module into sys.modules,
core/cache.py flips to "in streamlit context" mode and tries to
decorate with the real @st.cache_data, which fails with
UnserializableReturnValueError because the stub lacks a ScriptRunContext.
"""

from __future__ import annotations
import re
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")
TARGETS = [
    "astro/qizheng/qizheng_transit.py",
    "astro/qizheng/shensha.py",
    "astro/qizheng/zhangguo.py",
    "astro/qizheng/qizheng_dasha.py",
    "astro/qizheng/ming_gong_interp.py",
    "astro/qizheng/calculator.py",
    "astro/qizheng/qizheng_financial.py",
]

RE_IMPORT = re.compile(r"^import streamlit as st\s*$", re.MULTILINE)
RE_CACHE_DATA = re.compile(r"@st\.cache_data\b")
RE_CACHE_RESOURCE = re.compile(r"@st\.cache_resource\b")
NEW_IMPORT = "from core.cache import cache_data, cache_resource"

for rel in TARGETS:
    p = REPO / rel
    if not p.exists():
        print(f"  SKIP (missing) {rel}")
        continue
    src = p.read_text()
    if "import streamlit" not in src:
        print(f"  SKIP (no streamlit) {rel}")
        continue
    new = RE_IMPORT.sub(NEW_IMPORT, src)
    new = RE_CACHE_DATA.sub("@cache_data", new)
    new = RE_CACHE_RESOURCE.sub("@cache_resource", new)
    if new != src:
        p.write_text(new)
        print(f"  ok  {rel}")
    else:
        print(f"  no change {rel}")
