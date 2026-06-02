"""Bisect failing tests by running in two halves.

Goal: find the test file that, when run earlier, causes the later
twelve_ci / talismanic / sassanian_chart tests to fail.
"""

from __future__ import annotations
import subprocess
import sys
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")
PROBE = [
    "tests/test_twelve_ci.py::TestComputeChart::test_chart_basic",
    "tests/test_twelve_ci.py::TestComputeChart::test_chart_planet_names",
    "tests/test_twelve_ci.py::TestFormatChart::test_format_contains_key_info",
    "tests/test_twelve_ci.py::TestBuildSvg::test_svg_basic",
    "tests/test_talismanic_magic.py::TestSVGGeneration::test_svg_generation_all_planets",
    "tests/test_talismanic_magic.py::TestSVGGeneration::test_svg_contains_planet_sigil",
    "tests/test_talismanic_magic.py::TestSVGGeneration::test_svg_custom_size",
    "tests/test_talismanic_magic.py::TestSVGGeneration::test_svg_with_moon_phase",
    "tests/test_talismanic_magic.py::TestSVGGeneration::test_svg_without_kamea",
    # Note: test_sassanian_ayanamsa_historical is a real pre-existing
    # bug (the formula returns 1.05° for 500 CE where the spec expects
    # ~21.5°), not a phase-6/7 regression. Excluded from PROBE so the
    # bisect focuses on test-isolation failures.
]

# Get all test files in collection order
result = subprocess.run(
    [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header"],
    capture_output=True, text=True, cwd=REPO,
)
files: list[str] = []
for line in result.stdout.splitlines():
    if "::" in line and line.startswith("tests/"):
        f = line.split("::")[0]
        if f not in files:
            files.append(f)

print(f"Total test files: {len(files)}", file=sys.stderr)

def runs_clean(probe_args: list[str], prefix: list[str]) -> bool:
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", *prefix, *probe_args]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    out = p.stdout + p.stderr
    if " 0 failed" in out and " passed" in out:
        return True
    return False

# Binary search: which test file's inclusion makes the probe fail?
# We bisect on the prefix list.
# Test the empty case first.
if not runs_clean(PROBE, []):
    print("Even empty prefix makes PROBE fail — isolated to the probe itself or collection state.")
    # Try without collection of any other test files
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", *PROBE]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    print(p.stdout[-500:])
    sys.exit(0)

lo, hi = 0, len(files)
print(f"Bisect among {len(files)} files (empty verified CLEAN)", file=sys.stderr)
while hi - lo > 1:
    mid = (lo + hi) // 2
    prefix = files[:mid]
    if runs_clean(PROBE, prefix):
        lo = mid
        print(f"  prefix {mid} ({prefix[-1] if prefix else 'EMPTY'}) -> CLEAN", file=sys.stderr)
    else:
        hi = mid
        print(f"  prefix {mid} ({prefix[-1] if prefix else 'EMPTY'}) -> FAILS", file=sys.stderr)

polluter = files[hi - 1] if hi > 0 else "<EMPTY>"
print(f"\nPoluter test file: {polluter}")
# Confirm the polluter alone is enough
print(f"  - Running just {polluter} before PROBE:")
if runs_clean(PROBE, [polluter]):
    print("    polluter alone IS enough to make PROBE fail")
else:
    print("    polluter alone is NOT enough — needs combination with earlier files")
