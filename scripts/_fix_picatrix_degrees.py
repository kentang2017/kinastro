"""Replace all start_degree / end_degree formulas in picatrix_data.py
with literal floats computed by Python.

Walk the file in order, tracking the current mansion index by
parsing the "index" line that precedes each dict. Rewrite start/end
as soon as we see them, so each entry gets its own value.
"""

from __future__ import annotations
import re
from pathlib import Path

REPO = Path("/mnt/c/Users/hooki/OneDrive/pastword/文件/GitHub/kinastro")
TARGET = REPO / "astro/arabic/picatrix_data.py"

WIDTH = 360.0 / 28.0

src = TARGET.read_text()
lines = src.splitlines(keepends=True)
out = []
cur_index = None
for line in lines:
    if '"index":' in line:
        m = re.search(r'"index":\s*(\d+)', line)
        if m:
            cur_index = int(m.group(1))
    if cur_index is None:
        out.append(line)
        continue
    if '"start_degree":' in line:
        new_val = f"{cur_index * WIDTH!r}"
        line = re.sub(r'("start_degree":\s*)([^,\n]+)(,)',
                      rf'\g<1>{new_val}\g<3>', line, count=1)
    if '"end_degree":' in line:
        new_val = f"{(cur_index + 1) * WIDTH!r}"
        line = re.sub(r'("end_degree":\s*)([^,\n]+)(,)',
                      rf'\g<1>{new_val}\g<3>', line, count=1)
    out.append(line)

new_src = ''.join(out)
if new_src != src:
    TARGET.write_text(new_src)
    print(f"  ok rewrote {TARGET.relative_to(REPO)}")
else:
    print("  no changes")
