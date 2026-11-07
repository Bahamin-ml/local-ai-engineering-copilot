"""
ML Engineering Copilot - FAISS Vector Store Wrapper
Handles index construction, cosine similarity search, and disk persistence.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple, Union

import faiss
import numpy as np

from backend.rag.preprocessor import KnowledgeDoc

logger = logging.getLogger(__name__)


class VectorStore:
    """
    High-performance vector database using FAISS IndexFlatIP (Cosine Similarity on L2-normalized vectors).
    Persists FAISS binary index alongside document metadata in JSON format.
    """

    def __init__(
        self,
        dimension: int = 768,
        index_path: Union[str, Path] = "storage/vector_store/faiss_index.bin",
        metadata_path: Union[str, Path] = "storage/vector_store/metadata.json",
    ):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        # Make sure storage directories exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

        self.documents: List[KnowledgeDoc] = []
        self.index: faiss.IndexFlatIP = faiss.IndexFlatIP(self.dimension)

        # Auto-load existing index if present
        if self.index_path.exists() and self.metadata_path.exists():
            self.load()

    def add_documents(self, docs: List[KnowledgeDoc], embeddings: List[List[float]]) -> None:
        """
        L2-normalizes vectors, appends them to FAISS index and stores doc objects.
        """
        if not docs or not embeddings:
            return

        if len(docs) != len(embeddings):
            raise ValueError(f"Mismatched count: {len(docs)} docs vs {len(embeddings)} embeddings")

        vectors = np.array(embeddings, dtype=np.float32)
        # L2-normalization ensures Inner Product == Cosine Similarity
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.documents.extend(docs)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[KnowledgeDoc, float]]:
        """
        Executes Cosine Similarity search and returns top_k (doc, score) pairs.
        """
        if self.index.ntotal == 0 or not self.documents:
            return []

        q_vec = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(q_vec)

        scores, indices = self.index.search(q_vec, min(top_k, self.index.ntotal))

        results: List[Tuple[KnowledgeDoc, float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if 0 <= idx < len(self.documents):
                results.append((self.documents[idx], float(score)))

        return results

    def save(self) -> None:
        """
        Persists FAISS binary index and document metadata.
        Uses dataclasses.asdict to reliably serialize KnowledgeDoc instances.
        """
        faiss.write_index(self.index, str(self.index_path))

        docs_data = []
        for doc in self.documents:
            if hasattr(doc, "to_dict"):
                docs_data.append(doc.to_dict())
            else:
                docs_data.append(asdict(doc))

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(docs_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved FAISS index ({self.index.ntotal} vectors) to {self.index_path}")

    def load(self) -> None:
        """
        Loads FAISS binary index and deserializes document metadata into KnowledgeDoc instances.
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            logger.warning("Index or metadata files do not exist. Skipping load.")
            return

        self.index = faiss.read_index(str(self.index_path))

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        self.documents = [
            KnowledgeDoc(
                doc_id=d.get("doc_id", ""),
                source=d.get("source", ""),
                content=d.get("content", ""),
                metadata=d.get("metadata", {}),
            )
            for d in raw_docs
        ]
        logger.info(f"Loaded {len(self.documents)} vectors from {self.index_path}")

    @property
    def total_documents(self) -> int:
        return len(self.documents)
