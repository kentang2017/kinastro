# -*- coding: utf-8 -*-
"""
Encoding Fixer for astro/qizheng/calculator.py

This script fixes the common Traditional Chinese Windows legacy encoding problem
(cp950 / big5) that causes SyntaxError when a # -*- coding: utf-8 -*- declaration is present.

Usage (run from the project root in the (tf) environment):
    & "C:\Users\hooki\anaconda3\envs\tf\python.exe" scripts/fix_qizheng_encoding.py

Or simply (if the tf env is activated):
    python scripts/fix_qizheng_encoding.py
"""

from pathlib import Path
import py_compile
import sys

TARGET = Path("astro/qizheng/calculator.py")

def main():
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found from current directory.")
        print("Please run this script from the project root (the folder containing app.py).")
        sys.exit(1)

    print(f"Reading {TARGET} ...")
    raw = TARGET.read_bytes()

    # Most common encodings on Traditional Chinese Windows
    encodings_to_try = ["cp950", "big5", "utf-8"]

    decoded = None
    used_encoding = None

    for enc in encodings_to_try:
        try:
            decoded = raw.decode(enc)
            used_encoding = enc
            print(f"  Successfully decoded using {enc}")
            break
        except UnicodeDecodeError:
            continue

    if decoded is None:
        print("  Could not decode cleanly with cp950/big5/utf-8.")
        print("  Falling back to utf-8 with error replacement (may lose some characters).")
        decoded = raw.decode("utf-8", errors="replace")
        used_encoding = "utf-8 (replace)"

    print(f"  Original file was encoded as: {used_encoding}")

    # Clean any existing coding declaration at the top
    lines = decoded.splitlines(keepends=True)
    cleaned_lines = []
    header_found = False
    for line in lines:
        stripped_lower = line.strip().lower()
        if not header_found and (
            stripped_lower.startswith("# -*- coding")
            or stripped_lower.startswith("# coding")
            or stripped_lower.startswith("#!python")
        ):
            header_found = True
            continue
        cleaned_lines.append(line)

    content = "".join(cleaned_lines).lstrip("\ufeff")  # remove possible BOM

    # Always force the correct UTF-8 declaration as the very first line
    final_content = "# -*- coding: utf-8 -*-\n" + content

    # Write back as real UTF-8
    TARGET.write_text(final_content, encoding="utf-8")
    print(f"  File successfully rewritten as UTF-8.")

    # Verify syntax
    print("Verifying syntax with py_compile ...")
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("  SUCCESS: No more SyntaxError!")
        print("")
        print("You can now run:  python app.py")
    except py_compile.PyCompileError as e:
        print(f"  STILL HAS ERROR: {e}")
        print("")
        print("Please also delete any cached .pyc files:")
        print("  Remove-Item -Recurse -Force astro/qizheng/__pycache__ -ErrorAction SilentlyContinue")
        sys.exit(1)

if __name__ == "__main__":
    main()
