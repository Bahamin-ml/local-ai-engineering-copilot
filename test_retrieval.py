import asyncio
from backend.config import Settings
from backend.core.ollama_client import OllamaClient
from backend.rag.vector_store import VectorStore

async def main():
    settings = Settings()
    client = OllamaClient(settings)
    vector_store = VectorStore(
        dimension=settings.EMBEDDING_DIM,
        index_path=settings.FAISS_INDEX_PATH,
        metadata_path=settings.FAISS_METADATA_PATH,
    )
    print(f"Total docs in store: {vector_store.total_documents}")

    test_queries = [
        "How to handle ZeroDivisionError in Python?",
        "Write a Python function to check if a string is palindrome",
    ]

    for q in test_queries:
        print(f"\n==================== Query: {q} ====================")
        query_embedding = await client.generate_embedding(q)
        results = vector_store.search(query_embedding=query_embedding, top_k=2)

        for i, (doc, score) in enumerate(results, 1):
            doc_type = doc.metadata.get("type", "unknown")
            print(f"[{i}] Cosine Similarity: {score:.4f} | Type: {doc_type}")
            print(f"    Metadata: {doc.metadata}")
            snippet = doc.content[:220].replace("\n", " ")
            print(f"    Snippet: {snippet}...\n")

if __name__ == "__main__":
    asyncio.run(main())
