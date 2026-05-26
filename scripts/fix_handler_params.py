#!/usr/bin/env python3
"""
Fix generated handler files to use uniform compute_fn/render_fn parameter names.
"""

import re
from pathlib import Path


def fix_handler_file(filepath: Path) -> bool:
    """Fix a single handler file. Returns True if modified."""
    content = filepath.read_text(encoding="utf-8")

    # Pattern 1: Replace function signature parameters
    # From: def build_xxx_handler(*, compute_xxx_chart, render_xxx_chart, ai_button_sink)
    # To:   def build_xxx_handler(*, compute_fn, render_fn, ai_button_sink)
    signature_pattern = r'def (build_\w+_handler)\(\s*\*,\s*compute_\w+(?:_chart)?,\s*render_\w+(?:_chart)?,\s*ai_button_sink,\s*\)'
    new_signature = r'def \1(\n    *,\n    compute_fn,\n    render_fn,\n    ai_button_sink,\n)'

    # Pattern 2: Replace compute_fn usage in _cached_compute
    # From: return compute_xxx_chart(**params_payload, **extra_kwargs)
    # To:   return compute_fn(**params_payload, **extra_kwargs)
    compute_call_pattern = r'return compute_\w+(?:_chart)?\(\*\*params_payload'
    new_compute_call = 'return compute_fn(**params_payload'

    # Pattern 3: Replace render_fn usage
    # From: render_xxx_chart(\n    result,\n    after_chart_hook=lambda: ai_button_sink(
    # To:   render_fn(\n    result,\n    after_chart_hook=lambda: ai_button_sink(
    render_call_pattern = r'render_\w+(?:_chart)?\(\s*result,'
    new_render_call = 'render_fn(\n            result,'

    modified = False

    # Apply fixes
    new_content, n = re.subn(signature_pattern, new_signature, content)
    if n > 0:
        modified = True
        content = new_content

    new_content, n = re.subn(compute_call_pattern, new_compute_call, content)
    if n > 0:
        modified = True
        content = new_content

    new_content, n = re.subn(render_call_pattern, new_render_call, content)
    if n > 0:
        modified = True
        content = new_content

    if modified:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    """Fix all generated handler files."""
    handler_dir = Path("ui/system_handlers")
    fixed_count = 0
    skipped_count = 0

    # Skip Phase 1-3 handlers (they have custom implementations)
    skip_files = {
        "phase1_handlers.py",
        "build_andean_handler.py",
        "build_western_handler.py",
        "build_vedic_handler.py",
        "build_chinese_handler.py",
    }

    for handler_file in handler_dir.glob("build_*_handler.py"):
        if handler_file.name in skip_files:
            skipped_count += 1
            continue

        if fix_handler_file(handler_file):
            fixed_count += 1
            print(f"[FIXED] {handler_file.name}")

    print(f"\n{'='*60}")
    print(f"Fixed: {fixed_count} files")
    print(f"Skipped: {skipped_count} files (custom implementations)")


if __name__ == "__main__":
    main()
