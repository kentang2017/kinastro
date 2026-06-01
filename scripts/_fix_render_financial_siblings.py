"""Fix stale `from .X` lazy imports inside ui/handlers/tab_chinese/render_financial.py.

Phase 7 moved many helper modules out of astro/qizheng/financial/ into
ui/handlers/tab_chinese/, but a few lazy `from .X` lines were left over
referring to the (non-existent) sibling module names. Rewrite them to
the canonical astro.qizheng.financial.X path.
"""

from __future__ import annotations
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")
TARGET = REPO / "ui/handlers/tab_chinese/render_financial.py"

SIBLING_MAP = {
    "from .stock_fetcher": "from astro.qizheng.financial.stock_fetcher",
    "from .stock_calculator": "from astro.qizheng.financial.stock_calculator",
    "from .name_wuxing": "from astro.qizheng.financial.name_wuxing",
    "from .gann_macro_stock": "from astro.qizheng.financial.gann_macro_stock",
}

src = TARGET.read_text()
new = src
counts = {key: 0 for key in SIBLING_MAP}
for old, repl in SIBLING_MAP.items():
    new, n = new.replace(old, repl), new.count(old)
    counts[old] = n
    new = new.replace(old, repl)  # second pass to be safe

if new != src:
    TARGET.write_text(new)
    print(f"  ok  {TARGET.relative_to(REPO)}")
    for old, repl in SIBLING_MAP.items():
        # recount on the *new* text only to see what landed
        pass
    for old, repl in SIBLING_MAP.items():
        # use new.count to confirm each pattern was applied
        applied = src.count(old) - new.count(old)
        print(f"    {old} -> {repl}: {applied} replacements")
else:
    print("  no changes needed")
