"""
RAG retrieval utilities for ML Engineering Copilot
Path: backend/rag/retrieval.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional

from backend.core.ollama_client import OllamaClient
from backend.rag.vector_store import VectorStore, KnowledgeDoc


@dataclass(frozen=True)
class RetrievedChunk:
    doc: KnowledgeDoc
    score: float


class RagRetriever:
    """
    Async retriever:
    1) embeds query via OllamaClient (async)
    2) searches FAISS via VectorStore (sync, in-memory)
    3) formats retrieved docs into compact context text
    """

    def __init__(self, vector_store: VectorStore, ollama_client: OllamaClient):
        self.vector_store = vector_store
        self.ollama_client = ollama_client

    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        query = (query or "").strip()
        if not query:
            return []

        query_embedding = await self.ollama_client.generate_embedding(query)
        hits = self.vector_store.search(query_embedding=query_embedding, top_k=top_k)
        return [RetrievedChunk(doc=d, score=float(s)) for (d, s) in hits]

    @staticmethod
    def _safe_meta(meta: Optional[Dict]) -> Dict:
        return meta or {}

    def build_rag_context(self, chunks: List[RetrievedChunk], max_chars: int = 2200) -> str:
        """
        Compact context builder with caps to prevent prompt bloat.
        """
        if not chunks:
            return ""

        parts: List[str] = []
        used = 0

        for i, ch in enumerate(chunks, start=1):
            meta = self._safe_meta(ch.doc.metadata)
            doc_type = meta.get("type", "unknown")
            header = f"[{i}] type={doc_type} score={ch.score:.4f}\n"

            body = (ch.doc.content or "").strip()
            if not body:
                continue

            body = body[:900]  # per-doc cap
            block = header + body + "\n"

            if used + len(block) > max_chars:
                break

            parts.append(block)
            used += len(block)

        return "\n".join(parts).strip()
