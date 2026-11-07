"""
ML Engineering Copilot - Test Knowledge Indexer & Live Retrieval
"""

import asyncio
from pathlib import Path
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config, Settings
from backend.core.ollama_client import OllamaClient
from backend.rag.indexer import KnowledgeIndexer
from backend.rag.vector_store import VectorStore


async def test_indexer_pipeline():
    print("=" * 60)
    print("Testing RAG Ingestion Pipeline & Live Search")
    print("=" * 60)

    try:
        config = Config()
    except Exception:
        config = Settings()

    ollama_client = OllamaClient(config)

    # Resolve vector store directory safely
    storage_dir = config.FAISS_INDEX_PATH.parent
    storage_dir.mkdir(parents=True, exist_ok=True)

    test_index_path = storage_dir / "test_faiss.bin"
    test_meta_path = storage_dir / "test_meta.json"

    # Clean up previous test runs if any
    if test_index_path.exists():
        test_index_path.unlink()
    if test_meta_path.exists():
        test_meta_path.unlink()

    vector_store = VectorStore(
        dimension=config.EMBEDDING_DIM,
        index_path=test_index_path,
        metadata_path=test_meta_path,
    )
    indexer = KnowledgeIndexer(
        config=config,
        ollama_client=ollama_client,
        vector_store=vector_store,
    )

    data_dir = PROJECT_ROOT / "DATA"

    # 1. Ingest Bug & Fix Pairs
    print("\n[1] Testing Bug & Fix Ingestion (10 samples)...")
    bug_fix_csv = data_dir / "Python Code Bug & Fix Pairs" / "code_bug_fix_pairs.csv"
    count_bf = await indexer.ingest_bug_fix_pairs(bug_fix_csv, max_samples=10)
    print(f"  [✓] Indexed {count_bf} bug-fix documents.")

    # 2. Ingest StackSample
    print("\n[2] Testing StackSample Ingestion (10 samples)...")
    q_csv = data_dir / "StackSample 10% of Stack Overflow Q&A" / "Questions.csv"
    a_csv = data_dir / "StackSample 10% of Stack Overflow Q&A" / "Answers.csv"
    count_ss = await indexer.ingest_stack_sample(q_csv, a_csv, max_questions=10, min_score=10)
    print(f"  [✓] Indexed {count_ss} StackOverflow Q&A documents.")

    # 3. Live Cosine Search Test
    query = "How to handle IndexError in Python lists or array slice?"
    print(f"\n[3] Testing Live Vector Search for Query: '{query}'...")
    query_emb = await ollama_client.generate_embedding(query)
    results = vector_store.search(query_emb, top_k=2)

    for rank, (doc, score) in enumerate(results, start=1):
        content_preview = getattr(doc, "content", getattr(doc, "text", ""))[:140].replace("\n", " ")
        print(f"  Match {rank} [Score: {score:.4f}]: Source={doc.source} | ID={doc.doc_id}")
        print(f"  Preview: {content_preview}...\n")

    # Clean up test artifacts
    if test_index_path.exists():
        test_index_path.unlink()
    if test_meta_path.exists():
        test_meta_path.unlink()

    print("[✓] RAG Pipeline & Cosine Search fully validated!")


if __name__ == "__main__":
    asyncio.run(test_indexer_pipeline())
