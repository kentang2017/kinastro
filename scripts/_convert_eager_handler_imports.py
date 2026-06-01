"""Rewrite `from ui.handlers.tab_X.render import Y` to lazy form.

The eager import works at runtime (it picks up the re-exported render fns),
but it forces streamlit to load whenever the astro/<pkg> package is
imported. We need every `from ui.handlers.tab_X.render import Y` line in
an `astro/<pkg>/__init__.py` to become a module-level lazy wrapper.

Pattern:
  # Before
  from ui.handlers.tab_X.render import Y, Z as W

  # After
  def Y(*args, **kwargs):
      from ui.handlers.tab_X.render import Y as _fn
      return _fn(*args, **kwargs)

  def W(*args, **kwargs):
      from ui.handlers.tab_X.render import Z as _fn
      return _fn(*args, **kwargs)

This matches the PEP 562-style pattern already used by several astro
__init__.py files (e.g. astro/andean/__init__.py).

Run from repo root:
    python3 scripts/_convert_eager_handler_imports.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro")

# Match a line: from ui.handlers.tab_X.render import A, B as C, D
# or: from ui.handlers.tab_X.render_financial import A
LINE_RE = re.compile(
    r"^from\s+(ui\.handlers\.tab_\w+(?:\.\w+)?)\s+import\s+(.+)$",
    re.MULTILINE,
)


def convert_line(mod: str, names_str: str) -> list[str]:
    """Convert one import line into a sequence of lazy function wrappers."""
    out: list[str] = []
    # Split names on top-level commas (no parens here in our use, but be safe)
    parts = [p.strip() for p in names_str.split(",") if p.strip()]
    for part in parts:
        if " as " in part:
            src_name, alias = [s.strip() for s in part.split(" as ", 1)]
        else:
            src_name = alias = part
        out.append("")
        out.append(f"def {alias}(*args, **kwargs):  # type: ignore[no-redef]")
        out.append(f"    \"\"\"Lazy-load the {src_name} renderer for this package.\"\"\"")
        out.append(f"    from {mod} import {src_name} as _fn")
        out.append(f"    return _fn(*args, **kwargs)")
    return out


def fix_init(init: Path) -> tuple[bool, str]:
    src = init.read_text(encoding="utf-8", errors="ignore")
    rel = init.relative_to(REPO)
    new_src = src
    n_changes = 0
    for m in list(LINE_RE.finditer(src)):
        whole = m.group(0)
        mod = m.group(1)
        names = m.group(2)
        # Skip lines already inside a function body (e.g. nested imports).
        # Heuristic: only convert lines that start with `from ui.handlers...`
        if not whole.startswith("from ui.handlers.tab_"):
            continue
        replacement = "\n".join(convert_line(mod, names))
        new_src = new_src.replace(whole, replacement, 1)
        n_changes += 1
    if n_changes and new_src != src:
        init.write_text(new_src, encoding="utf-8")
        return True, f"  ok {rel}: {n_changes} lines converted"
    return False, f"  -  {rel}: no changes"


def main() -> int:
    print("Converting eager ui.handlers imports to lazy wrappers in astro/<pkg>/__init__.py...")
    ok, skip = 0, 0
    for init in sorted((REPO / "astro").rglob("__init__.py")):
        changed, msg = fix_init(init)
        print(msg)
        if changed:
            ok += 1
        else:
            skip += 1
    print(f"\nConverted {ok} __init__.py files, skipped {skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
