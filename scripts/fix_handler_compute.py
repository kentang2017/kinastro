#!/usr/bin/env python3
"""Fix handler compute function names."""

import re
from pathlib import Path

HANDLERS_DIR = Path(__file__).parent.parent / "ui" / "system_handlers"

# Map handler system names to actual compute function names
COMPUTE_NAME_MAP = {
    "armenian": "compute_armenian_chart",
    "maya": "compute_maya_chart",
    "kabbalistic": "compute_kabbalistic_chart",
    "chinstar": "compute_chinstar_chart",
    "kp": "compute_kp_chart",
    "thai": "compute_thai_chart",
    "laos": "compute_lao_chart",
    "lal_kitab": "compute_lal_kitab_chart",
    "yemeni": "compute_yemeni_chart",
    "picatrix": "compute_picatrix_behenian_chart",
    "persian": "compute_deep_sassanian_chart",
    "mazzalot": "compute_mazzalot_chart",
    "arabic": "compute_arabic_chart",
    "ahman": "compute_amazigh_chart",
    "bahre_hasab": "analyze_bahre_hasab_date",
    "aztec": "compute_aztec_chart",
    "mahabote": "compute_mahabote_chart",
    "decans": "compute_decan_chart",
    "nadi": "compute_nadi_chart",
    "jaimini": "compute_jaimini_chart",
    "zurkhai": "compute_zurkhai_chart",
    "tibetan": "compute_tibetan_chart",
    "nine_star_ki": "compute_nine_star_ki_chart",
    "celtic_tree": "compute_celtic_tree_chart",
    "hellenistic": "compute_hellenistic_chart",
    "babylonian": "compute_babylonian_chart",
    "sumerian": "compute_sumerian_chart",
    "damo": "compute_damo_chart",
    "diqiyijue": "compute_diqiyijue_chart",
    "twelve_ci": "compute_twelve_ci_chart",
    "liuren": "compute_liuren_chart",
    "fendjing": "compute_qimen_luming",
    "tojeong": "compute_tojeong_chart",
    "khmer": "compute_khmer_chart",
    "taiyi": "compute_taiyi_chart",
    "qimen_luming": "compute_qimen_luming",
    "acg": "compute_astrocartography",
    "uranian": "compute_uranian_chart",
    "cosmobiology": "compute_cosmobiology_chart",
    "harmonic": "compute_multi_harmonic",
    "primary_directions": "compute_primary_directions_chart",
    "wariga": "compute_wariga",
    "weton": "compute_weton",
    "bintang": "compute_bintang_duabelas",
    "kinketika": "compute_kinketika",
    "cetian": "compute_cetian_ziwei_chart",
    "chunzi": "compute_chunzi_chart",
    "kaiyuan": "compute_kaiyuan_chart",
    "sukkayodo": "compute_sukkayodo_chart",
    "taixuan": "compute_taixuan_chart",
    "diqiyijue": "compute_diqiyijue_chart",
    "beiji": "compute_beiji_chart",
    "nanji": "compute_nanji_chart",
    "wuyunliuqi": "compute_wuyunliuqi_chart",
    "tieban": "compute_tieban_chart",
    "bazi": "compute_bazi_chart",
    "damo": "compute_damo_chart",
    "cetian_ziwei": "compute_cetian_ziwei_chart",
    "western": "compute_western_chart",
    "vedic": "compute_vedic_chart",
    "sabian": "compute_western_chart",
    "astrocartography": "compute_astrocartography",
}


def fix_handler(filepath: Path) -> bool:
    """Fix a single handler file. Returns True if modified."""
    content = filepath.read_text(encoding="utf-8")

    system_name = filepath.stem.replace("build_", "")
    expected_func = COMPUTE_NAME_MAP.get(system_name)

    if not expected_func:
        # Try to infer from register function
        register_match = re.search(r'def register\(.*?\):[\s\S]*?compute_([^,]+)', content)
        if register_match:
            expected_func = f"compute_{register_match.group(1)}"
        else:
            return False

    # Fix the _cached_compute function
    old_pattern = rf'return compute_{system_name}_chart\(\*\*params_payload'
    new_pattern = f"return {expected_func}(**params_payload"

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        filepath.write_text(content, encoding="utf-8")
        print(f"Fixed: {filepath.name} -> {expected_func}")
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
