"""Phase 7 followup: route the 5 __init__.py modules that still
``from .renderer import ...`` at module load time through the new
ui/handlers/tab_<id>/render.py location, so deleting the orphan
astro/<pkg>/renderer.py files (which were re-created by an earlier
``git checkout`` mistake and still ``import streamlit as st``) doesn't
break the import chain.
"""

from __future__ import annotations
import re
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")

# (path, package, ui_handler_module, names_to_re_export)
JOBS = [
    (
        "astro/primary_directions/__init__.py",
        "astro.primary_directions",
        "ui.handlers.tab_primary_directions.render",
        ["render_primary_directions", "render_primary_directions_svg"],
    ),
    (
        "astro/shanghan_qianfa/__init__.py",
        "astro.shanghan_qianfa",
        "ui.handlers.tab_shanghan_qianfa.render",
        ["render_streamlit"],
    ),
    (
        "astro/picatrix_behenian/__init__.py",
        "astro.picatrix_behenian",
        "ui.handlers.tab_picatrix_behenian.render",
        ["render_streamlit"],
    ),
    (
        "astro/trutine_of_hermes/__init__.py",
        "astro.trutine_of_hermes",
        "ui.handlers.tab_trutine_of_hermes.render",
        ["render_streamlit"],
    ),
    (
        "astro/tojeong/__init__.py",
        "astro.tojeong",
        "ui.handlers.tab_tojeong.render",
        ["render_tojeong_chart"],
    ),
]

LAZY_BLOCK_TEMPLATE = """\

# Lazy re-export: the renderer module moved to ``{ui_module}`` during
# the phase-7 compute/render split, but legacy callers still expect to
# find the names at ``{pkg_full}.<name>``. PEP 562 __getattr__ keeps
# ``import astro.{pkg_full}`` free of streamlit until a caller actually
# accesses the symbol.
_NEW_HOME = "{ui_module}"
_NAMES = {names!r}
_LEGACY = "{legacy_attr}"


def __getattr__(name):
    if name in _NAMES:
        try:
            import importlib
            mod = importlib.import_module(_NEW_HOME)
            value = getattr(mod, name)
        except (ImportError, AttributeError):
            try:
                import importlib
                legacy = importlib.import_module(_LEGACY, __name__)
                value = getattr(legacy, name)
            except (ImportError, AttributeError):
                raise AttributeError(
                    "module %r has no attribute %r" % (__name__, name)
                )
        globals()[name] = value
        return value
    raise AttributeError("module %r has no attribute %r" % (__name__, name))
"""

for rel, pkg_full, ui_module, names in JOBS:
    pkg_short = pkg_full.split(".")[-1]
    legacy_attr = pkg_short + ".renderer"
    p = REPO / rel
    if not p.exists():
        print(f"  SKIP (missing) {rel}")
        continue
    src = p.read_text()
    lines = src.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "from .renderer import" in line or "from .tojeong_renderer import" in line:
            # Collect the whole import block.
            block = [line]
            j = i + 1
            if "(" in line and ")" not in line:
                while j < len(lines):
                    block.append(lines[j])
                    if ")" in lines[j]:
                        j += 1
                        break
                    j += 1
            block_text = "".join(block)
            if any(name in block_text for name in names):
                i = j  # skip block
                continue
        out.append(line)
        i += 1

    out_text = "".join(out)
    new_block = LAZY_BLOCK_TEMPLATE.format(
        ui_module=ui_module,
        names=names,
        legacy_attr=legacy_attr,
        pkg_full=pkg_full,
    )
    if "__all__" in out_text:
        out_text = out_text.replace("\n__all__", "\n" + new_block + "\n__all__", 1)
    else:
        out_text = out_text.rstrip() + "\n" + new_block
    p.write_text(out_text)
    print(f"  ok  {rel}")
