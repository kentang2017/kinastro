#!/usr/bin/env python3
"""
KinAstro Architecture Audit Tool - Phase 0
Scans astro/ for Streamlit imports inside compute/calculator modules.
Reports violations of the "pure compute layer" rule.

Usage:
    python scripts/audit_st_imports.py [--json] [--fail-on-violation]

Exit code 1 if violations found and --fail-on-violation used (for CI).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASTRO_DIR = ROOT / "astro"

# Patterns that strongly indicate "compute layer" (should be pure)
COMPUTE_MARKERS = [
    "calculator",
    "compute",
    "core",
    "engine",
]

# Files/patterns we allow st in (renderers, CLI demos, etc.)
RENDER_ALLOWED = ["renderer", "render", "ui", "frontend", "browser", "demo", "visuals"]

# Root-level files that are known mixed/legacy (we still flag but note)
LEGACY_FLAT_ALLOWLIST: set[str] = set()  # populate as we migrate


def is_compute_file(path: Path) -> bool:
    name = path.name.lower()
    if any(m in name for m in RENDER_ALLOWED):
        return False
    if any(m in name for m in COMPUTE_MARKERS):
        return True
    # Root-level .py under astro/ that are not obviously render-only
    if path.parent == ASTRO_DIR and path.suffix == ".py":
        if not any(m in name for m in RENDER_ALLOWED):
            return True
    return False


def scan_file(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return {"path": str(path.relative_to(ROOT)), "error": str(exc)}

    lines = text.splitlines()
    st_imports: list[int] = []
    st_uses: list[int] = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip().lower()
        if "import streamlit" in stripped or "from streamlit" in stripped:
            st_imports.append(i)
        # crude usage detection (st. or streamlit.)
        if ("st." in line or "streamlit." in line) and not stripped.startswith("#"):
            st_uses.append(i)

    if not st_imports and not st_uses:
        return None

    return {
        "path": str(path.relative_to(ROOT)),
        "is_compute": is_compute_file(path),
        "st_import_lines": st_imports,
        "st_use_lines": st_uses[:10],  # cap for readability
        "total_uses": len(st_uses),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--fail-on-violation", action="store_true", help="Exit 1 if any compute-layer violations")
    args = parser.parse_args()

    violations: list[dict[str, Any]] = []
    all_findings: list[dict[str, Any]] = []

    for py in sorted(ASTRO_DIR.rglob("*.py")):
        if py.name.startswith("__") or "test" in str(py).lower():
            continue
        finding = scan_file(py)
        if finding:
            all_findings.append(finding)
            if finding["is_compute"]:
                violations.append(finding)

    summary = {
        "total_files_with_st": len(all_findings),
        "compute_layer_violations": len(violations),
        "violation_paths": [v["path"] for v in violations],
    }

    if args.json:
        print(json.dumps({"summary": summary, "violations": violations, "findings": all_findings}, indent=2))
    else:
        print("=== KinAstro Streamlit Import Audit (Phase 0) ===\n")
        print(f"Scanned: {ASTRO_DIR}")
        print(f"Files importing/using streamlit: {summary['total_files_with_st']}")
        print(f"**Compute-layer violations (should be pure)**: {summary['compute_layer_violations']}\n")

        if violations:
            print("VIOLATIONS (compute/calculator files with st):")
            for v in violations[:30]:
                print(f"  - {v['path']} (imports at {v['st_import_lines']})")
            if len(violations) > 30:
                print(f"  ... and {len(violations)-30} more")
        else:
            print("✅ No compute-layer Streamlit imports detected. Great!")

        print("\n(Full list available with --json)")

    if args.fail_on_violation and violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
