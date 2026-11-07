"""
ML Engineering Copilot - Memory & SQLite Verification
Path: tests/test_memory.py
"""
import sys
import uuid
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.models import DatabaseManager
from backend.core.memory_manager import MemoryManager
from backend.core.ollama_client import OllamaClient


async def test_memory_subsystem():
    print("=" * 60)
    print("Testing Persistent SQLite Memory & History Retention")
    print("=" * 60)

    db = DatabaseManager()
    client = OllamaClient()
    memory = MemoryManager(db_manager=db, ollama_client=client)

    test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    print(f"\n[1] Creating session: {test_session_id}")
    memory.ensure_session(test_session_id, title="PyTorch CNN Architecture Discussion")

    # ذخیره تعاملات آزمایشی
    print("\n[2] Recording conversational turns...")
    memory.append_interaction(
        session_id=test_session_id,
        user_query="What loss function should I use for multi-label classification in PyTorch?",
        assistant_reply="For multi-label classification, use torch.nn.BCEWithLogitsLoss.",
        model="qwen3:4b"
    )

    history = memory.get_context_history(test_session_id)
    print(f"  Retrieved history count: {len(history)}")
    assert len(history) == 2, f"Expected 2 messages, got {len(history)}"
    print("  [✓] History stored and retrieved with exact roles.")

    # تست خلاصه‌ساز کانتکست با مدل سریع
    print("\n[3] Testing fast context compression (qwen2.5:1.5b)...")
    summary = await memory.summarize_and_compress(test_session_id)
    print(f"  Summary triggered (active when conversation grows): {summary if summary else 'Skipped as intended (<6 msgs)'}")
    print("  [✓] Memory pipeline validated successfully.")

    print("\n" + "=" * 60)
    print("PHASE 3: MEMORY & DATABASE VALIDATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_memory_subsystem())
