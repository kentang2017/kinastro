#!/usr/bin/env python3
"""Fix all handler compute function names."""

import re
from pathlib import Path

HANDLERS_DIR = Path(__file__).parent.parent / "ui" / "system_handlers"

# Map system name to actual compute function name
SYSTEM_TO_COMPUTE = {
    "amazigh": "compute_amazigh_chart",
    "arabic": "compute_arabic_chart",
    "astrocartography": "compute_astrocartography",
    "aztec": "compute_aztec_chart",
    "babylonian": "compute_babylonian_chart",
    "bahre_hasab": "analyze_bahre_hasab_date",
    "bazi": "compute_bazi_chart",
    "beiji": "compute_beiji_chart",
    "bintang": "compute_bintang_duabelas",
    "brahma_jati": "compute_brahma_jati",
    "burmese": "compute_mahabote_chart",
    "byzantine": "compute_byzantine_chart",
    "celtic": "compute_celtic_tree_chart",
    "cetian": "compute_cetian_ziwei_chart",
    "chunzi": "compute_chunzi_chart",
    "cosmobiology": "compute_cosmobiology_chart",
    "damo": "compute_damo_chart",
    "diqiyijue": "compute_diqiyijue_chart",
    "dogon": "compute_dogon_sirius_chart",
    "draconic": "compute_draconic_chart",
    "egyptian": "compute_decan_chart",
    "electional": "render_electional_chart",
    "etruscan": "compute_etruscan_chart",
    "geomancy": "compute_geomancy_chart",
    "harmonic": "compute_multi_harmonic",
    "hellenistic": "compute_hellenistic_chart",
    "horary": "render_horary_chart",
    "jaimini": "compute_jaimini_chart",
    "kaiyuan": "compute_kaiyuan_chart",
    "kinketika": "render_kinketika_chart",
    "lal_kitab": "compute_lal_kitab_chart",
    "laos": "compute_lao_chart",
    "liuren": "compute_liuren_chart",
    "liuyao_lifetime": "compute_lifetime_hexagram",
    "mazzalot": "compute_mazzalot_chart",
    "medical": "compute_medical_chart",
    "mundane": "render_mundane_chart",
    "nadi": "compute_nadi_chart",
    "nanji": "compute_nanji_chart",
    "nine_star_ki": "compute_nine_star_ki_chart",
    "persian": "render_deep_sassanian_chart",
    "picatrix": "render_picatrix_behenian",
    "polynesian": "compute_polynesian_chart",
    "qimen": "compute_taiyi_chart",
    "sabian": "compute_western_chart",
    "shanghan_qianfa": "compute_shanghan_qianfa",
    "sports": "render_sports_astrology_chart",
    "sukkayodo": "render_sukkayodo_chart",
    "taixuan": "render_taixuan_chart",
    "taiyi": "compute_taiyi_chart",
    "thai": "compute_thai_chart",
    "tibetan": "compute_tibetan_chart",
    "tieban": "render_tieban_chart_svg",
    "tojeong": "compute_tojeong_chart",
    "twelve_ci": "compute_twelve_ci_chart",
    "uranian": "compute_uranian_chart",
    "weton": "compute_weton",
    "wuyunliuqi": "compute_wuyunliuqi_chart",
    "yemeni": "compute_yemeni_chart",
    "zurkhai": "compute_zurkhai_chart",
}


def fix_handler(filepath: Path) -> bool:
    """Fix a single handler file. Returns True if modified."""
    content = filepath.read_text(encoding="utf-8")
    system_name = filepath.stem.replace("build_", "").replace("_handler", "")

    expected_func = SYSTEM_TO_COMPUTE.get(system_name)
    if not expected_func:
        # Try to get from register function
        reg_match = re.search(r'def register\([^)]+\):\s+([\s\S]+?)(?:handler = )', content)
        if reg_match:
            reg_text = reg_match.group(1)
            if "compute_" in reg_text:
                # Find the actual function name
                compute_match = re.search(r'compute_([^\s,)]+)', reg_text)
                if compute_match:
                    func_part = compute_match.group(1)
                    # Check if it's a chart function
                    if func_part.startswith("chart"):
                        expected_func = f"compute_{func_part}"
                    else:
                        expected_func = f"render_{func_part}"

    if not expected_func:
        return False

    # Fix the compute function name in _cached_compute
    wrong_name = f"compute_{system_name}_handler_chart"
    if wrong_name in content and expected_func:
        content = content.replace(wrong_name, expected_func)
        filepath.write_text(content, encoding="utf-8")
        print(f"Fixed: {filepath.name} -> {expected_func}")
        return True

    # Also fix the generic wrong pattern
    wrong_pattern = r"compute_\w+_handler_chart"
    if re.search(wrong_pattern, content):
        # Find the compute_XXX_chart from register function
        compute_func = re.search(r'compute_([a-z_]+)_chart', content)
        if compute_func:
            correct_name = f"compute_{compute_func.group(1)}_chart"
            wrong_name = f"compute_{system_name}_handler_chart"
            if wrong_name in content:
                content = content.replace(wrong_name, correct_name)
                filepath.write_text(content, encoding="utf-8")
                print(f"Fixed: {filepath.name} -> {correct_name}")
                return True

    return False


def main():
    count = 0
    for handler_file in HANDLERS_DIR.glob("build_*.py"):
        if fix_handler(handler_file):
            count += 1
    print(f"\nTotal fixed: {count} handlers")


if __name__ == "__main__":
    main()
