"""Add `import streamlit as st` to every astro/ file that uses
``st.`` but forgot to import it.

Background: the phase-6 decoupling pass replaced
``import streamlit as st`` + ``@st.cache_data`` with
``from core.cache import cache_data, cache_resource`` in qizheng/
files, but it was over-eager and also dropped the import for
single-file (non-package) modules that still need ``st.markdown`` /
``st.error`` / etc. for streamlit-side rendering.

This script is a surgical post-fix: for every file that references
``st`` (as a Name node) but does NOT import streamlit, inject
``import streamlit as st`` right after the ``from __future__ import
annotations`` header.
"""

from __future__ import annotations
import ast
import os
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")


def fix(p: Path) -> bool:
    src = p.read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    has_st_ref = False
    has_st_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "st":
            has_st_ref = True
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name == "streamlit":
                    has_st_import = True
        if isinstance(node, ast.ImportFrom) and node.module == "streamlit":
            has_st_import = True
    if not has_st_ref or has_st_import:
        return False
    # Find the right place to inject the import. Prefer right after
    # ``from __future__ import annotations`` if present, else at top.
    lines = src.splitlines(keepends=True)
    inject_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from __future__ import annotations"):
            inject_at = i + 1
            break
    # Skip a blank line if present, so we keep formatting tidy.
    if inject_at < len(lines) and lines[inject_at].strip() == "":
        inject_at += 1
    lines.insert(inject_at, "import streamlit as st\n")
    p.write_text("".join(lines))
    return True


count = 0
for root, dirs, files in os.walk(REPO / "astro"):
    if "__pycache__" in root:
        continue
    for f in files:
        if not f.endswith(".py"):
            continue
        p = Path(root) / f
        if fix(p):
            print(f"  ok  {p.relative_to(REPO)}")
            count += 1
print(f"  {count} files updated")
