#!/usr/bin/env python3
"""Build the existing static site, then stage only its public files."""
from pathlib import Path
import shutil, subprocess, sys
root = Path(__file__).resolve().parent.parent
subprocess.run([sys.executable, str(root / "build.py")], check=True)
out = root / "dist"
if out.exists(): shutil.rmtree(out)
out.mkdir()
for extension in ("*.html", "*.css", "*.js"):
    for source in root.glob(extension):
        if source.name != "preview.html": shutil.copy2(source, out / source.name)
shutil.copytree(root / "assets", out / "assets", ignore=shutil.ignore_patterns("*.tmp"))
for source in (out / "assets/img").glob("*.png"): source.unlink()
print("Static output:", out)
