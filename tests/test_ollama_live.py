"""
ML Engineering Copilot - Live Ollama Client Verification
Path: tests/test_ollama_live.py
"""
import sys
import asyncio
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.core.ollama_client import OllamaClient


async def run_verification():
    print("=" * 60)
    print("Testing Live Connection to Ollama Service")
    print("=" * 60)

    client = OllamaClient()

    # 1. Test listing models
    print("\n[1] Verifying active models list via API...")
    models = await client.list_models()
    print(f"  Available models in API: {models}")
    assert settings.DEFAULT_LLM_MODEL in models or any(settings.DEFAULT_LLM_MODEL in m for m in models), \
        f"Default model {settings.DEFAULT_LLM_MODEL} not found in Ollama!"
    print("  [✓] Model presence confirmed.")

    # 2. Test Embedding Generation (nomic-embed-text)
    print(f"\n[2] Generating embedding vector with '{settings.DEFAULT_EMBED_MODEL}'...")
    sample_text = "PyTorch AdamW optimizer with cosine learning rate scheduler"
    emb = await client.get_embedding(sample_text)
    print(f"  Vector dimension received: {len(emb)}")
    assert len(emb) == settings.EMBEDDING_DIM, f"Expected {settings.EMBEDDING_DIM}, got {len(emb)}"
    print("  [✓] Embedding dimension matches 768.")

    # 3. Test Text Generation (Stream)
    print(f"\n[3] Testing streaming generation with '{settings.DEFAULT_LLM_MODEL}'...")
    prompt = "Write a 1-line Python code snippet using PyTorch to check if CUDA is available."
    print("  Response: ", end="", flush=True)
    async for chunk in client.stream_response(prompt=prompt):
        print(chunk, end="", flush=True)
    print("\n  [✓] Streaming generation passed successfully.")

    print("\n" + "=" * 60)
    print("ALL OLLAMA CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_verification())
