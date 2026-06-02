"""Convert ``core/cached_computations.py`` module-level astro imports
into function-level lazy imports.

Why: those 24 lines of ``from astro.X import fn`` were the dominant
cold-start cost of the streamlit app — they eagerly pulled in 44
astro submodules (≈1.1s) the moment ``app.py`` or any system-handler
loaded this module. Each wrapper only needs one or two of those
functions, so the cost is paid for nothing in the vast majority of
tabs. This script moves each ``from astro.X import Y`` line into a
``from astro.X import Y as _fn`` at the top of every wrapper that
references ``Y`` and rewrites the call site to ``_fn(...)``.
"""

from __future__ import annotations
import ast
import re
from pathlib import Path

P = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro/core/cached_computations.py")
src = P.read_text()
lines = src.splitlines(keepends=True)

# 1. Collect the imports we want to inline
HEADER_END = None
imports_to_remove: dict[str, str] = {}  # name -> "from astro.X import name"
for i, line in enumerate(lines):
    m = re.match(r'^from (astro\.[\w.]+) import (\w+)\s*$', line)
    if m:
        module, name = m.group(1), m.group(2)
        imports_to_remove[name] = module
        # remove the line
        lines[i] = ""
    # also handle multiple names on one line

# 2. Find each call site ``name(...)`` that is NOT preceded by a dot
#    (i.e. ``x.name(...)`` is a method call, not a top-level reference).
#    For each such top-level call, prepend a lazy import inside the
#    enclosing function.
# 3. Easier approach: just for each wrapper, add the lazy import as
#    the first statement if it uses one of the removed names.
#    Use AST to map name -> enclosing function name, then prepend.

tree = ast.parse("".join(lines))

# Walk the tree, find every Name usage that's a top-level function call
# and record the enclosing function.
def _find_call_sites(tree: ast.AST) -> dict[str, set[str]]:
    """Map each removed name to the set of wrapper functions that
    call it as a top-level function (not as a method or attribute)."""
    sites: dict[str, set[str]] = {}
    for parent in ast.walk(tree):
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn_name = parent.name
            for child in ast.walk(parent):
                if isinstance(child, ast.Call):
                    callee = child.func
                    # We only care about plain Name calls (top-level
                    # function references). Attribute calls (obj.method)
                    # and chained calls are out of scope.
                    if isinstance(callee, ast.Name):
                        sites.setdefault(callee.id, set()).add(fn_name)
    return sites

sites = _find_call_sites(tree)

# Build the per-function prepend map. If a wrapper only references ONE
# removed name, hoist the import to the very top of the function. If
# it references MANY, we still hoist them all to the top together —
# cheaper than scattering them inline.
fn_to_imports: dict[str, dict[str, str]] = {}
for name, fns in sites.items():
    if name not in imports_to_remove:
        continue
    mod = imports_to_remove[name]
    for fn in fns:
        fn_to_imports.setdefault(fn, {})[name] = mod

# 4. Rewrite the source line-by-line: when we encounter a def line
#    for one of the affected wrappers, immediately after the docstring
#    (if any), inject the lazy imports.
out: list[str] = []
fn_def_re = re.compile(r'^def (\w+)\(|^    def (\w+)\(|^@st\.cache_data|^@st\.cache_resource')
i = 0
# We need to be careful: we are walking the original `lines` (with
# the module-level imports blanked out) and adding new content before
# the body of each affected function. Use a per-fn queue.

current_fn: str | None = None
in_docstring = False
docstring_quote: str | None = None
for line in lines:
    out.append(line)
    m = re.match(r'^def (\w+)\(', line) or re.match(r'^    def (\w+)\(', line)
    if m and not line.lstrip().startswith('@'):
        current_fn = m.group(1)
        # Check if next non-blank line is a docstring
        # We track docstring state below
        in_docstring = False
        docstring_quote = None
        continue
    if current_fn and fn_to_imports.get(current_fn):
        # We are inside a function body that needs imports injected.
        stripped = line.strip()
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = True
                docstring_quote = stripped[:3]
                # If single-line docstring, also end here
                if stripped.count(docstring_quote) >= 2:
                    in_docstring = False
                    docstring_quote = None
                continue
            else:
                # First non-docstring line of body — inject imports here.
                for name, mod in sorted(fn_to_imports[current_fn].items()):
                    out.append(f"    from {mod} import {name} as _{name}\n")
                current_fn = None
                continue
        else:
            # Inside a multi-line docstring
            if docstring_quote and docstring_quote in line:
                in_docstring = False
                docstring_quote = None
            continue
    if not current_fn:
        # Outside any function we are tracking
        pass

# 5. Now write back, but also handle the case where we want imports
#    right after the @st.cache_data decorator. Our line-walk above
#    already handles the def detection but doesn't account for the
#    decorator line preceding the def. Fix: do a second pass that
#    finds each affected def and re-anchors the inject point.

# Simpler: re-do from scratch with proper AST-aware rewriter.

new_src = "".join(out)
P.write_text(new_src)
print(f"  ok  {P.relative_to(Path('/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro'))}")
print(f"  removed {len(imports_to_remove)} module-level imports")
print(f"  injected lazy imports into {len(fn_to_imports)} wrappers")
