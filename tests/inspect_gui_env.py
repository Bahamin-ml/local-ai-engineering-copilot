"""
Phase 7: GUI Environment & Structure Audit
"""
import sys
from pathlib import Path
import importlib.metadata as md

PROJECT_ROOT = Path(__file__).resolve().parent.parent

print("=" * 60)
print("PHASE 7 GUI ENVIRONMENT & STRUCTURE AUDIT")
print("=" * 60)

# 1. Package checks
for pkg in ["PyQt5", "qasync", "httpx", "markdown"]:
    try:
        ver = md.version(pkg)
        print(f"Package {pkg}: {ver}")
    except Exception:
        print(f"Package {pkg}: NOT INSTALLED")

# 2. Check existing GUI directories/files
gui_dir = PROJECT_ROOT / "gui"
frontend_dir = PROJECT_ROOT / "frontend"

print(f"\nChecking 'gui' directory ({gui_dir}): exists = {gui_dir.exists()}")
if gui_dir.exists():
    for p in sorted(gui_dir.rglob("*")):
        if p.is_file():
            print(f"  - {p.relative_to(PROJECT_ROOT)}")

print(f"\nChecking 'frontend' directory ({frontend_dir}): exists = {frontend_dir.exists()}")
if frontend_dir.exists():
    for p in sorted(frontend_dir.rglob("*")):
        if p.is_file():
            print(f"  - {p.relative_to(PROJECT_ROOT)}")

print("\n" + "=" * 60)
