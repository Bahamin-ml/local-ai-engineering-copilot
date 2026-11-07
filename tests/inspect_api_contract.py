"""
ML Engineering Copilot - Inspect Signatures and Dependencies for Phase 6 API
"""

import importlib.metadata as md
import inspect
from pathlib import Path
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config, Settings
from backend.core.memory_manager import MemoryManager
from backend.core.ollama_client import OllamaClient
from backend.core.prompt_engine import CopilotMode, PromptEngine
from backend.rag.indexer import KnowledgeIndexer
from backend.rag.vector_store import VectorStore


def inspect_all():
    print("=" * 60)
    print("PHASE 6 API DEPENDENCIES & SIGNATURES AUDIT")
    print("=" * 60)

    # Check packages
    for pkg in ["fastapi", "uvicorn"]:
        try:
            ver = md.version(pkg)
            print(f"Package {pkg}: {ver}")
        except Exception:
            print(f"Package {pkg}: NOT INSTALLED")

    # Settings fields
    print("\n--- SETTINGS FIELDS ---")
    fields = list(getattr(Settings, "model_fields", getattr(Settings, "__fields__", {})))
    print(fields)

    # PromptEngine modes
    print("\n--- COPILOT MODES ---")
    print([m.value for m in CopilotMode])

    # Class signatures
    classes = [
        OllamaClient,
        MemoryManager,
        PromptEngine,
        KnowledgeIndexer,
        VectorStore,
    ]

    for cls in classes:
        print(f"\n--- CLASS: {cls.__name__} ---")
        for name in dir(cls):
            if not name.startswith("_"):
                member = getattr(cls, name)
                if callable(member):
                    try:
                        sig = inspect.signature(member)
                        print(f"  def {name}{sig}")
                    except Exception as e:
                        print(f"  {name}: <unable to inspect signature: {e}>")


if __name__ == "__main__":
    inspect_all()
