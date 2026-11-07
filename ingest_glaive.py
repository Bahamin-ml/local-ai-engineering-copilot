import asyncio
from pathlib import Path

from backend.rag.indexer import KnowledgeIndexer


async def main():
    indexer = KnowledgeIndexer()
    before = indexer.vector_store.total_documents

    print(f"Before ingestion: {before}")

    added = await indexer.ingest_glaive_qa(
        Path(r"D:\resume\10 - chatbot\DATA\Glaive Python Code QA Dataset\train.csv"),
        max_rows=300,
    )

    after = indexer.vector_store.total_documents

    print(f"Added: {added}")
    print(f"After ingestion: {after}")


if __name__ == "__main__":
    asyncio.run(main())
