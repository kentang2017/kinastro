#!/usr/bin/env python3
"""Fix gender parameter issues in system handlers."""

import re
from pathlib import Path

HANDLERS_DIR = Path(__file__).parent.parent / "ui" / "system_handlers"

# Systems that don't use gender parameter (need fix)
NO_GENDER_SYSTEMS = {
    "amazigh", "andean", "arabic", "armenian", "astrocartography", "aztec",
    "babylonian", "bahre_hasab", "bazi", "beiji", "bintang", "brahma_jati",
    "burmese", "byzantine", "celtic", "cetian", "chinstar", "chunzi",
    "cosmobiology", "damo", "diqiyijue", "dogon", "draconic", "egyptian",
    "electional", "etruscan", "geomancy", "harmonic", "hellenistic", "horary",
    "kaiyuan", "kinketika", "kp", "laos", "liuyao_lifetime", "maya",
    "mundane", "nanji", "persian", "picatrix", "polynesian", "shanghan_qianfa",
    "sports", "tieban", "tojeong", "wariga", "wuyunliuqi", "zurkhai",
    "jewish_mazzalot", "kabbalistic", "mazzalot", "lal_kitab", "nadi",
}


def fix_handler(filepath: Path) -> bool:
    """Fix a single handler file. Returns True if modified."""
    content = filepath.read_text(encoding="utf-8")

    # Check if already fixed
    if "Remove gender parameter" in content:
        return False

    # Check if system uses gender (chinstar is the only one that does)
    system_name = filepath.stem.replace("build_", "")
    if system_name == "chinstar":
        # chinstar DOES use gender, skip
        return False

    # Pattern to fix _cached_compute
    old_cached = r'def _cached_compute\(params_payload: dict\[str, Any\], \*\*extra_kwargs\):\s+"""Pure compute wrapped for Streamlit caching."""\s+return compute_\w+\(\*\*params_payload, \*\*extra_kwargs\)'  # noqa: E501

    # Fix for _cached_compute - add gender filtering
    new_cached = '''def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        # Remove gender parameter - this system doesn't use it
        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}
        return compute_''' + system_name + '''_chart(**params_payload, **extra_kwargs)'''

    # Pattern to fix _compute
    old_compute = r'def _compute\(params: BirthChartParams, options: dict\[str, Any\]\) -> Any:\s+"""Compute chart from unified params."""\s+payload = params\.to_dict\(\)\s+# Add system-specific options here if needed'

    new_compute = '''def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Remove gender parameter - this system doesn't use it
        payload.pop("gender", None)
        # Add system-specific options here if needed'''

    modified = False
    new_content = content

    # Fix _cached_compute
    if re.search(r'def _cached_compute\(params_payload:', new_content):
        if "gender.*Remove" not in new_content and "gender.*Remove" not in new_content:
            new_content = re.sub(
                r'(def _cached_compute\(params_payload: dict\[str, Any\], \*\*extra_kwargs\):\s+"""Pure compute wrapped for Streamlit caching."""\s+)(return compute_\w+\(\*\*params_payload, \*\*extra_kwargs\))',
                r'\1# Remove gender parameter - this system doesn\'t use it\n        params_payload = {k: v for k, v in params_payload.items() if k != "gender"}\n        return compute_' + system_name + r'_chart(**params_payload, **extra_kwargs)',
                new_content
            )
            modified = True

    # Fix _compute
    if re.search(r'def _compute\(params: BirthChartParams', new_content):
        if "payload.pop.*gender" not in new_content:
            new_content = re.sub(
                r'(def _compute\(params: BirthChartParams, options: dict\[str, Any\]\) -> Any:\s+"""Compute chart from unified params."""\s+payload = params\.to_dict\(\)\s+)(# Add system-specific options here if needed)',
                r'\1# Remove gender parameter - this system doesn\'t use it\n        payload.pop("gender", None)\n        \2',
                new_content
            )
            modified = True

    if modified:
        filepath.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {filepath.name}")
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
