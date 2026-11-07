# tests/test_rag_core.py

from types import SimpleNamespace

import numpy as np

from backend.rag.vector_store import VectorStore


def test_vector_store_add_and_search():
    """Check that documents can be indexed and retrieved by vector similarity."""

    dimension = 768
    store = VectorStore(dimension=dimension)

    rng = np.random.default_rng(42)
    vectors = rng.standard_normal((3, dimension)).astype(np.float32)

    docs = [
        SimpleNamespace(
            doc_id="test_1",
            doc_type="synthetic",
            content="PyTorch tensor operations",
            metadata={"category": "ml"},
        ),
        SimpleNamespace(
            doc_id="test_2",
            doc_type="synthetic",
            content="Docker deployment instructions",
            metadata={"category": "devops"},
        ),
        SimpleNamespace(
            doc_id="test_3",
            doc_type="synthetic",
            content="FastAPI async endpoints",
            metadata={"category": "backend"},
        ),
    ]

    embeddings = vectors.tolist()

    store.add_documents(docs, embeddings)

    assert store.total_documents == len(docs)

    
    results = store.search(query_embedding=embeddings[0], top_k=1)

    assert len(results) == 1

    matched_doc, score = results[0]
    assert matched_doc.doc_id == "test_1"
    assert isinstance(score, (int, float, np.floating))
