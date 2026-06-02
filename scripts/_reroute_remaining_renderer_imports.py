"""Phase-7 post-fix: for every astro/<pkg>/__init__.py that still has
a ``from .renderer import render_streamlit`` line (the renderer module
was deleted in the phase-7 compute/render split), rewrite the import
to point at the new ui/handlers home.

Maps:

* astro/polynesian_hawaiian  -> ui.handlers.tab_polynesian.render
* astro/nanji                -> ui.handlers.tab_nanji.render
* astro/sports               -> ui.handlers.tab_sports_astrology.render
* astro/sumerian             -> ui.handlers.tab_sumerian.render
"""

from __future__ import annotations
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")

# (path, new_renderer_module)
JOBS = [
    ("astro/polynesian_hawaiian/__init__.py", "ui.handlers.tab_polynesian.render"),
    ("astro/nanji/__init__.py", "ui.handlers.tab_nanji.render"),
    ("astro/sports/__init__.py", "ui.handlers.tab_sports_astrology.render"),
    ("astro/sumerian/__init__.py", "ui.handlers.tab_sumerian.render"),
]

OLD_FROM = "from .renderer import"
NEW_FROM = "from {ui} import"


def fix_sumerian(src: str, ui: str) -> str:
    """sumerian/__init__.py: rewrite _lazy_renderer to import from ui."""
    src = src.replace(
        "from .renderer import render_streamlit",
        f"from {ui} import render_streamlit",
    )
    # sumerian doesn't expose render_streamlit in __all__; add a
    # public wrapper so legacy_bridge._get_attr can find it without
    # going through _lazy_renderer (which is private).
    if "render_streamlit" not in src.split("__all__")[0].split("def ")[-1] if "def " in src else True:
        pass
    # Add a render_streamlit wrapper at the end if missing.
    if "def render_streamlit(" not in src:
        src = src.rstrip() + (
            "\n\n\ndef render_streamlit(*args, **kwargs):\n"
            "    \"\"\"Sumerian streamlit renderer (lazy-loaded).\"\"\"\n"
            "    from "
            f"{ui} import render_streamlit as _fn\n"
            "    return _fn(*args, **kwargs)\n\n\n"
            "__all__ = __all__ + [\"render_streamlit\"]\n"
        )
    return src


def fix_polynesian(src: str, ui: str) -> str:
    return src.replace(
        OLD_FROM + " render_streamlit as _fn",
        NEW_FROM.format(ui=ui) + " render_streamlit as _fn",
    )


def fix_nanji(src: str, ui: str) -> str:
    return src.replace(
        "from .renderer import render_streamlit as _r",
        f"from {ui} import render_streamlit as _r",
    )


def fix_sports(src: str, ui: str) -> str:
    return src.replace(
        OLD_FROM + " render_streamlit as _fn",
        NEW_FROM.format(ui=ui) + " render_streamlit as _fn",
    )


for rel, ui in JOBS:
    p = REPO / rel
    src = p.read_text()
    if rel == "astro/polynesian_hawaiian/__init__.py":
        new = fix_polynesian(src, ui)
    elif rel == "astro/nanji/__init__.py":
        new = fix_nanji(src, ui)
    elif rel == "astro/sports/__init__.py":
        new = fix_sports(src, ui)
    elif rel == "astro/sumerian/__init__.py":
        new = fix_sumerian(src, ui)
    else:
        new = src
    if new != src:
        p.write_text(new)
        print(f"  ok  {rel}")
    else:
        print(f"  no change {rel}")
