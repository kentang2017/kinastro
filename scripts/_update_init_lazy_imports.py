"""Update astro/<pkg>/__init__.py to point renderer imports at ui/handlers/.

For each `from .renderer import <name> as <alias>` (or similar patterns) in
an `astro/<pkg>/__init__.py`, rewrite the import target to the new
`ui.handlers.tab_<id>.render` location. This keeps the existing public API
of the package intact while the actual renderer file has moved.

Run from repo root:
    python3 scripts/_update_init_lazy_imports.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro")

# Source renderer → tab id
TAB_MAP = {
    "andean": "tab_andean",
    "astronomical_geomancy": "tab_astro_geomancy",
    "bazi": "tab_bazi",
    "beiji": "tab_beiji",
    "bintang_duabelas": "tab_bintang_duabelas",
    "burmese": "tab_mahabote",  # burmese has mahabote renderer
    "burmese_mahabote": "tab_mahabote",
    "byzantine_astrology": "tab_byzantine_astrology",
    "chunzi": "tab_chunzi",
    "cosmobiology": "tab_cosmobiology",
    "diqiyijue": "tab_diqiyijue",
    "dogon": "tab_dogon_sirius",
    "electional": "tab_electional",
    "esoteric": "tab_esoteric",
    "etruscan": "tab_etruscan",
    "harmonic": "tab_harmonic",
    "horary": "tab_horary",
    "huangji": "tab_huangji",
    "human_design": "tab_human_design",
    "kinketika": "tab_kinketika",
    "laos": "tab_laos",
    "liuyao_lifetime": "tab_liuyao_lifetime",
    "maya": "tab_maya",
    "medical_astrology": "tab_medical_astrology",
    "mundane": "tab_mundane",
    "nanji": "tab_nanji",
    "persian": "tab_persian",
    "picatrix_behenian": "tab_picatrix_behenian",
    "primary_directions": "tab_primary_directions",
    "shanghan_qianfa": "tab_shanghan_qianfa",
    "sports": "tab_sports_astrology",
    "sumerian": "tab_sumerian",
    "trutine_of_hermes": "tab_trutine_of_hermes",
}


# In each astro/<pkg>/__init__.py, replace patterns like:
#   from .renderer import X as Y        → from ui.handlers.tab_<id>.render import X as Y
#   from .renderer import X             → from ui.handlers.tab_<id>.render import X
#   from . import renderer               → REMOVE (no longer exported)
#   import renderer                       → REMOVE

def fix_init(init_path: Path) -> tuple[bool, str]:
    """Update one __init__.py to use ui/handlers/ instead of .renderer."""
    rel = init_path.relative_to(REPO)
    parts = rel.parts
    # astro/<pkg>/__init__.py  → pkg = parts[1]
    # astro/qizheng/financial/__init__.py → pkg = qizheng.financial
    if "qizheng" in parts and "financial" in parts:
        # Special: stock_renderer is at ui/handlers/tab_chinese/render_financial.py
        tab_id = "tab_chinese"
        render_module = "ui.handlers.tab_chinese.render_financial"
    else:
        pkg = parts[1]
        if pkg not in TAB_MAP:
            return False, f"  skip: {rel} (pkg={pkg} not in TAB_MAP)"
        tab_id = TAB_MAP[pkg]
        render_module = f"ui.handlers.{tab_id}.render"

    src = init_path.read_text(encoding="utf-8", errors="ignore")
    new_src = src
    changed = False

    # 1. from .renderer import X as Y   (in lazy fn body)
    new_src, n1 = re.subn(
        r"from\s+\.renderer\s+import\s+",
        f"from {render_module} import ",
        new_src,
    )
    if n1:
        changed = True

    # 2. from . import renderer (module-level)
    new_src, n2 = re.subn(
        r"^from\s+\.\s+import\s+renderer\b[^\n]*\n",
        "",
        new_src,
        flags=re.MULTILINE,
    )
    if n2:
        changed = True

    # 3. import renderer (module-level)
    new_src, n3 = re.subn(
        r"^import\s+renderer\s*\n",
        "",
        new_src,
        flags=re.MULTILINE,
    )
    if n3:
        changed = True

    if changed and new_src != src:
        init_path.write_text(new_src, encoding="utf-8")
        return True, f"  ok {rel}: rewrote {n1} .renderer imports, removed {n2 + n3} module-level"
    return False, f"  -  {rel}: no changes"


def main() -> int:
    print("Updating astro/<pkg>/__init__.py to point at ui/handlers/...")
    ok, skip = 0, 0
    for init in sorted((REPO / "astro").rglob("__init__.py")):
        rel = init.relative_to(REPO)
        # Only top-level and second-level __init__.py in astro/
        parts = rel.parts
        if len(parts) > 3:
            # astro/<pkg>/<sub>/__init__.py  — e.g. astro/qizheng/financial/
            # We process these too if they're in TAB_MAP
            if "financial" not in parts:
                continue
        changed, msg = fix_init(init)
        print(msg)
        if changed:
            ok += 1
        else:
            skip += 1
    print(f"\nUpdated {ok} __init__.py files, skipped {skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
