"""Batch-fix 19 remaining mixed astro/* files.

For each file:
  1. Replace top-level `import streamlit as st` with
     `from core.streamlit_lazy import lazy_streamlit as st`.
  2. Replace `@st.cache_data(...)` with `@cache_data(...)` (importing
     `from core.cache import cache_data` if not already present).
  3. Leave function-body `st.xxx(...)` calls untouched — the lazy
     proxy resolves them on first use at runtime.
  4. Leave any `import streamlit.components.v1 as components` /
     `from streamlit import X` lines alone (they are inside function
     bodies in the audit; handled later in the components sweep).

Run from repo root:
    /usr/bin/python3 scripts/_decouple_streamlit_in_mixed.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro")

# 19 files remaining (yemeni was the demo; fix it idempotently too)
TARGETS = [
    "astro/aztec.py",
    "astro/babylonian.py",
    "astro/brahma_jati.py",
    "astro/celtic/celtic_tree_graves.py",
    "astro/cetian_ziwei.py",
    "astro/fendjing/fendjing_calculator.py",
    "astro/jaimini.py",
    "astro/jewish_mazzalot.py",
    "astro/kabbalistic.py",
    "astro/mahabote.py",
    "astro/nine_star_ki.py",
    "astro/sanshi/liuren.py",
    "astro/sanshi/qimen.py",
    "astro/sanshi/qimen_luming.py",
    "astro/sanshi/taiyi.py",
    "astro/sukkayodo.py",
    "astro/twelve_ci.py",
    "astro/vedic/financial.py",
    "astro/vedic/nadi.py",
    "astro/wariga/calculator.py",
    "astro/western/draconic.py",
    "astro/western/harmonic.py",
    "astro/western/hellenistic.py",
    "astro/western/uranian.py",
    "astro/world_map.py",
    "astro/yemeni.py",
    "astro/zurkhai.py",
]

# Other files in the audit that contain `import streamlit` only inside
# function bodies — those are streamlit.components.v1 imports and
# require manual review (see fendjing_calculator:223, hellenistic:744,1347,1371).
# We deliberately do NOT touch them in this pass.


def fix_one(rel: str) -> tuple[bool, str]:
    p = REPO / rel
    src = p.read_text(encoding="utf-8", errors="ignore")
    new = src
    n_imp, n_cd, n_shim_add = 0, 0, 0

    # 1. top-level `import streamlit as st`
    if re.search(r"^import streamlit as st\s*$", new, flags=re.MULTILINE):
        new = re.sub(
            r"^import streamlit as st\s*$",
            "from core.streamlit_lazy import lazy_streamlit as st",
            new,
            flags=re.MULTILINE,
        )
        n_imp = 1

    # 2. @st.cache_data / @st.cache_resource → @cache_data / @cache_resource
    new, n_cd = re.subn(r"@st\.cache_data\b", "@cache_data", new)
    new, n_cr = re.subn(r"@st\.cache_resource\b", "@cache_resource", new)
    n_cd += n_cr

    # 3. If we replaced a cache decorator but the file doesn't import the
    # shim yet, inject it once at the top-level import block.
    # Correct insertion point: immediately AFTER the last top-level
    # ``import X`` or ``from X import Y`` statement at column 0, so the
    # shim import sits with the other top-level imports and never lands
    # between a decorator and its target, or in the middle of a
    # multi-line ``from X import (a, b, c)`` block (which would be a
    # SyntaxError).
    needs_shim_import = (n_cd > 0) and "from core.cache import" not in new
    if needs_shim_import:
        lines = new.split("\n")
        # Walk forward through contiguous top-level imports (including
        # their continuation lines that are indented one level, e.g.
        # items inside a parenthesised import block).
        i = 0
        n = len(lines)
        last_in_block = -1
        while i < n:
            line = lines[i]
            stripped = line.strip()
            is_top_import = (
                (stripped.startswith("import ") or stripped.startswith("from "))
                and not line.startswith((" ", "\t"))
            )
            if is_top_import:
                # Consume the import statement + any indented continuation
                last_in_block = i
                i += 1
                # Continuation lines are indented (paren-wrapped imports)
                # OR they are bare identifiers / commas that follow an
                # import on its own line. We treat "indented" or
                # "starts with bare word/comma" as continuation until we
                # hit something that looks like a new top-level statement.
                paren_depth = stripped.count("(") - stripped.count(")")
                while i < n:
                    nxt = lines[i]
                    nxt_strip = nxt.strip()
                    if paren_depth > 0:
                        paren_depth += nxt_strip.count("(") - nxt_strip.count(")")
                        last_in_block = i
                        i += 1
                        continue
                    # No unclosed paren — is this still part of the import?
                    # A backslash line continuation, or an indented
                    # continuation line.
                    if nxt.startswith((" ", "\t")) and nxt_strip:
                        last_in_block = i
                        i += 1
                        continue
                    if nxt_strip.endswith("\\"):
                        last_in_block = i
                        i += 1
                        continue
                    break
            else:
                i += 1
        if last_in_block >= 0:
            insert_at = last_in_block + 1
            # Skip ONE blank line after the import block so the new line
            # lands inside the block visually. If the next line is not
            # blank, we still insert (better to be in the import block
            # than to break a decorator or class body).
            if insert_at < len(lines) and lines[insert_at].strip() == "":
                insert_at += 1
            lines.insert(insert_at, "from core.cache import cache_data, cache_resource")
        else:
            lines.insert(0, "from core.cache import cache_data, cache_resource")
        new = "\n".join(lines)
        n_shim_add = 1

    if n_imp == 0 and n_cd == 0 and n_shim_add == 0:
        return False, f"  skip: {rel} (no changes needed)"

    p.write_text(new, encoding="utf-8")
    return True, f"  ok   {rel}: import={n_imp} cache={n_cd} shim_added={n_shim_add}"


def main() -> int:
    print(f"Decoupling {len(TARGETS)} mixed files from streamlit import graph...")
    ok = skip = 0
    for rel in TARGETS:
        changed, msg = fix_one(rel)
        print(msg)
        if changed:
            ok += 1
        else:
            skip += 1
    print(f"\n{ok} changed, {skip} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
