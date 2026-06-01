"""Move 45 astro/<pkg>/renderer.py files to ui/handlers/tab_<id>/render.py.

For each renderer:
  1. Create ui/handlers/tab_<id>/ directory
  2. Copy file contents to ui/handlers/tab_<id>/render.py
  3. Fix relative imports (from .module import X → from astro.<pkg>.module import X)
  4. Keep `import streamlit as st` (UI layer)
  5. Write ui/handlers/tab_<id>/__init__.py with re-exports

Run from repo root:
    python3 scripts/_apply_renderer_moves.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro")
ASTRO = REPO / "astro"
HANDLERS = REPO / "ui" / "handlers"
LEGACY = REPO / "core" / "legacy_bridge.py"

# (source renderer path, target tab_id, target render file)
MOVES = [
    ("astro/andean/renderer.py", "tab_andean", "ui/handlers/tab_andean/render.py"),
    ("astro/astronomical_geomancy/renderer.py", "tab_astro_geomancy", "ui/handlers/tab_astro_geomancy/render.py"),
    ("astro/bazi/renderer.py", "tab_bazi", "ui/handlers/tab_bazi/render.py"),
    ("astro/beiji/renderer.py", "tab_beiji", "ui/handlers/tab_beiji/render.py"),
    ("astro/bintang_duabelas/renderer.py", "tab_bintang_duabelas", "ui/handlers/tab_bintang_duabelas/render.py"),
    ("astro/burmese_mahabote/renderer.py", "tab_mahabote", "ui/handlers/tab_mahabote/render.py"),
    ("astro/byzantine_astrology/renderer.py", "tab_byzantine_astrology", "ui/handlers/tab_byzantine_astrology/render.py"),
    ("astro/chinese/taixuan/taixuan_renderer.py", "tab_taixuan", "ui/handlers/tab_taixuan/render.py"),
    ("astro/chunzi/renderer.py", "tab_chunzi", "ui/handlers/tab_chunzi/render.py"),
    ("astro/cosmobiology/renderer.py", "tab_cosmobiology", "ui/handlers/tab_cosmobiology/render.py"),
    ("astro/damo/renderer.py", "tab_damo", "ui/handlers/tab_damo/render.py"),
    ("astro/diqiyijue/renderer.py", "tab_diqiyijue", "ui/handlers/tab_diqiyijue/render.py"),
    ("astro/dogon/renderer.py", "tab_dogon_sirius", "ui/handlers/tab_dogon_sirius/render.py"),
    ("astro/electional/renderer.py", "tab_electional", "ui/handlers/tab_electional/render.py"),
    ("astro/esoteric/renderer.py", "tab_esoteric", "ui/handlers/tab_esoteric/render.py"),
    ("astro/etruscan/renderer.py", "tab_etruscan", "ui/handlers/tab_etruscan/render.py"),
    ("astro/harmonic/renderer.py", "tab_harmonic", "ui/handlers/tab_harmonic/render.py"),
    ("astro/horary/renderer.py", "tab_horary", "ui/handlers/tab_horary/render.py"),
    ("astro/huangji/renderer.py", "tab_huangji", "ui/handlers/tab_huangji/render.py"),
    ("astro/human_design/renderer.py", "tab_human_design", "ui/handlers/tab_human_design/render.py"),
    ("astro/jawa_weton/renderer.py", "tab_jawa_weton", "ui/handlers/tab_jawa_weton/render.py"),
    ("astro/kaiyuan/renderer.py", "tab_kaiyuan", "ui/handlers/tab_kaiyuan/render.py"),
    ("astro/kinketika/renderer.py", "tab_kinketika", "ui/handlers/tab_kinketika/render.py"),
    ("astro/kp/kp_renderer.py", "tab_kp", "ui/handlers/tab_kp/render.py"),
    ("astro/laos/renderer.py", "tab_laos", "ui/handlers/tab_laos/render.py"),
    ("astro/liuyao_lifetime/renderer.py", "tab_liuyao_lifetime", "ui/handlers/tab_liuyao_lifetime/render.py"),
    ("astro/maya/renderer.py", "tab_maya", "ui/handlers/tab_maya/render.py"),
    ("astro/medical_astrology/renderer.py", "tab_medical_astrology", "ui/handlers/tab_medical_astrology/render.py"),
    ("astro/mundane/renderer.py", "tab_mundane", "ui/handlers/tab_mundane/render.py"),
    ("astro/nanji/renderer.py", "tab_nanji", "ui/handlers/tab_nanji/render.py"),
    ("astro/persian/renderer.py", "tab_persian", "ui/handlers/tab_persian/render.py"),
    ("astro/picatrix_behenian/renderer.py", "tab_picatrix_behenian", "ui/handlers/tab_picatrix_behenian/render.py"),
    ("astro/polynesian_hawaiian/renderer.py", "tab_polynesian", "ui/handlers/tab_polynesian/render.py"),
    ("astro/primary_directions/renderer.py", "tab_primary_directions", "ui/handlers/tab_primary_directions/render.py"),
    ("astro/qizheng/chart_renderer.py", "tab_chinese", "ui/handlers/tab_chinese/render.py"),
    ("astro/qizheng/financial/stock_renderer.py", "tab_chinese", "ui/handlers/tab_chinese/render_financial.py"),
    ("astro/rectification/renderer.py", "tab_rectification", "ui/handlers/tab_rectification/render.py"),
    ("astro/shanghan_qianfa/renderer.py", "tab_shanghan_qianfa", "ui/handlers/tab_shanghan_qianfa/render.py"),
    ("astro/shaozi/renderer.py", "tab_shaozi", "ui/handlers/tab_shaozi/render.py"),
    ("astro/sports/renderer.py", "tab_sports_astrology", "ui/handlers/tab_sports_astrology/render.py"),
    ("astro/sumerian/renderer.py", "tab_sumerian", "ui/handlers/tab_sumerian/render.py"),
    ("astro/tojeong/tojeong_renderer.py", "tab_tojeong", "ui/handlers/tab_tojeong/render.py"),
    ("astro/trutine_of_hermes/renderer.py", "tab_trutine_of_hermes", "ui/handlers/tab_trutine_of_hermes/render.py"),
    ("astro/wariga/renderer.py", "tab_wariga", "ui/handlers/tab_wariga/render.py"),
    ("astro/wuyunliuqi/renderer.py", "tab_wuyunliuqi", "ui/handlers/tab_wuyunliuqi/render.py"),
]


def make_absolute_imports(src: str, source_rel: str) -> str:
    """Rewrite `from .module import X` to `from astro.<pkg>.module import X`."""
    pkg_dir = Path(source_rel).parent
    pkg_root = str(pkg_dir).replace("/", ".")

    def rewrite(m: re.Match) -> str:
        prefix = m.group(1)
        module = m.group(2)
        suffix = m.group(3)
        if module:
            new_mod = pkg_root + "." + module
        else:
            new_mod = pkg_root
        return prefix + new_mod + suffix

    pattern = re.compile(
        r"^(from\s+)(\.[\w.]*|)(\s+import\s+.*)$",
        re.MULTILINE,
    )
    return pattern.sub(rewrite, src)


def make_init(pkg: str, tab_id: str, render_fns: list[str]) -> str:
    """Generate ui/handlers/tab_<id>/__init__.py content."""
    imports = ",\n    ".join(render_fns)
    alls = ", ".join('"' + fn + '"' for fn in render_fns)
    return (
        '"""UI handler for system **' + tab_id + '**.\n\n'
        'Render layer for ' + pkg + '. The compute logic stays in astro/;\n'
        'this package is the streamlit-side dispatcher.\n"""\n'
        '\nfrom __future__ import annotations\n'
        '\nfrom .render import (\n    ' + imports + ',\n)\n'
        '\n__all__ = [\n    ' + alls + ',\n]\n'
    )


def get_top_level_defs(src: str) -> list[str]:
    return re.findall(r"^def\s+(\w+)", src, re.M)


def move_one(src_rel: str, tab_id: str, dst_rel: str) -> tuple[bool, str]:
    src = REPO / src_rel
    dst = REPO / dst_rel

    if not src.exists():
        return False, f"missing: {src_rel}"
    if dst.exists():
        return False, f"already exists: {dst_rel}"

    src_content = src.read_text(encoding="utf-8", errors="ignore")
    new_content = make_absolute_imports(src_content, src_rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new_content, encoding="utf-8")

    defs = get_top_level_defs(new_content)
    public_defs = sorted(set(d for d in defs if not d.startswith("_")))
    init_path = dst.parent / "__init__.py"
    init_path.write_text(make_init(Path(src_rel).parent.name, tab_id, public_defs), encoding="utf-8")

    return True, f"  ok: {src_rel} -> {dst_rel} ({len(public_defs)} public fns)"


def main() -> int:
    ok, skip = 0, 0
    print(f"Moving {len(MOVES)} renderer files...")
    for src_rel, tab_id, dst_rel in MOVES:
        changed, msg = move_one(src_rel, tab_id, dst_rel)
        print(msg)
        if changed:
            ok += 1
        else:
            skip += 1
    print(f"\nPhase 1 (move): {ok} moved, {skip} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
