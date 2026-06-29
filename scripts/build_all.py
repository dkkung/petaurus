"""
Run all build scripts in scripts/build/ (globbed in sorted order).
Palette-authoring scripts live in scripts/palettes/ and are not run here.

Usage (from project root):
    uv run python scripts/build_all.py
"""

import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).parent / "build"

scripts = sorted(BUILD_DIR.glob("*.py"))
failures = []

for path in scripts:
    print(f"  {path.name} ...", end=" ", flush=True)
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    if result.returncode == 0:
        print("ok")
    else:
        print("FAILED")
        if result.stderr.strip():
            print(result.stderr.strip())
        failures.append(path.name)

print()
if failures:
    print(f"{len(failures)} script(s) failed: {', '.join(failures)}")
    sys.exit(1)
else:
    print(f"All {len(scripts)} build scripts completed successfully.")
