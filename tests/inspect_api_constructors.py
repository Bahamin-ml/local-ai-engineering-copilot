"""
Read-only audit of constructors and runtime settings for Phase 6.
"""

import inspect
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Settings
from backend.core.memory_manager import MemoryManager
from backend.core.ollama_client import OllamaClient
from backend.core.prompt_engine import PromptEngine
from backend.rag.indexer import KnowledgeIndexer
from backend.rag.vector_store import VectorStore


def show_signature(label, obj):
    try:
        print(f"{label}{inspect.signature(obj)}")
    except (TypeError, ValueError) as exc:
        print(f"{label}<signature unavailable: {exc}>")


def main():
    print("=" * 60)
    print("PHASE 6 CONSTRUCTOR AND CONFIG AUDIT")
    print("=" * 60)

    print("\n--- SETTINGS INSTANCE ---")
    settings = Settings()
    fields = getattr(Settings, "model_fields", {})
    for name in fields:
        try:
            value = getattr(settings, name)
            print(f"{name} = {value!r}")
        except Exception as exc:
            print(f"{name} = <error: {exc}>")

    classes = [
        OllamaClient,
        MemoryManager,
        PromptEngine,
        KnowledgeIndexer,
        VectorStore,
    ]

    print("\n--- CONSTRUCTORS ---")
    for cls in classes:
        print(f"\n{cls.__name__}")
        show_signature("  class ", cls)
        show_signature("  __init__ ", cls.__init__)

    print("\n--- VECTOR STORE METHODS ---")
    for name in ("load", "save", "search", "add_documents"):
        method = getattr(VectorStore, name, None)
        if method is not None:
            show_signature(f"  {name}", method)

    print("\n--- MEMORY MANAGER METHODS ---")
    for name in (
        "ensure_session",
        "append_interaction",
        "get_context_history",
        "summarize_and_compress",
    ):
        method = getattr(MemoryManager, name, None)
        if method is not None:
            show_signature(f"  {name}", method)


if __name__ == "__main__":
    main()
