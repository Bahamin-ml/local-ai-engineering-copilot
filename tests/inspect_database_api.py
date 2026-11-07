"""
Read-only inspection of database and memory APIs for Phase 6.
"""

import inspect
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.models import DatabaseManager
from backend.core.memory_manager import MemoryManager


def inspect_public_methods(cls):
    print(f"\n--- {cls.__name__} ---")
    try:
        print("Constructor:", inspect.signature(cls))
    except (TypeError, ValueError) as exc:
        print("Constructor: unavailable:", exc)

    for name in dir(cls):
        if name.startswith("_"):
            continue
        member = getattr(cls, name)
        if callable(member):
            try:
                print(f"{name}{inspect.signature(member)}")
            except (TypeError, ValueError):
                print(name)


def main():
    print("=" * 60)
    print("DATABASE AND MEMORY API AUDIT")
    print("=" * 60)

    inspect_public_methods(DatabaseManager)
    inspect_public_methods(MemoryManager)


if __name__ == "__main__":
    main()
