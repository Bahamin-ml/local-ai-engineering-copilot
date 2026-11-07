"""
ML Engineering Copilot - Knowledge Base Indexer

Loads dataset rows, converts them to KnowledgeDoc objects,
generates embeddings, and stores the documents in the vector store.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import List, Optional

from backend.config import Settings
from backend.core.ollama_client import OllamaClient
from backend.rag.preprocessor import KnowledgeDoc, TextPreprocessor
from backend.rag.vector_store import VectorStore


logger = logging.getLogger(__name__)


class KnowledgeIndexer:
    """Ingest datasets and index their documents."""

    def __init__(
        self,
        config: Optional[Settings] = None,
        ollama_client: Optional[OllamaClient] = None,
        vector_store: Optional[VectorStore] = None,
    ) -> None:
        self.config = config or Settings()
        self.client = ollama_client or OllamaClient(self.config)
        self.preprocessor = TextPreprocessor()

        self.vector_store = vector_store or VectorStore(
            dimension=self.config.EMBEDDING_DIM,
            index_path=self.config.FAISS_INDEX_PATH,
            metadata_path=self.config.FAISS_METADATA_PATH,
        )

    async def ingest_bug_fix_pairs(
        self,
        dataset_path: Path,
        max_samples: int = 1000,
    ) -> int:
        """
        Ingest bug/fix CSV rows.

        Expected columns: id, buggy, fixed, message
        """
        dataset_path = Path(dataset_path)
        logger.info("Ingesting Bug & Fix Pairs (max=%s)...", max_samples)

        if not dataset_path.exists():
            logger.warning("Bug & Fix dataset not found: %s", dataset_path)
            return 0

        docs: List[KnowledgeDoc] = []

        with dataset_path.open(
            mode="r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            for row_number, row in enumerate(reader):
                if row_number >= max_samples:
                    break

                doc = self.preprocessor.format_bug_fix_doc(
                    row_id=str(row.get("id") or row_number + 1),
                    buggy=row.get("buggy") or "",
                    fixed=row.get("fixed") or "",
                    message=row.get("message") or "",
                )
                docs.append(doc)

        logger.info(
            "Built %s KnowledgeDocs from Bug & Fix dataset.",
            len(docs),
        )
        return await self._embed_and_index_docs(docs)

    async def ingest_stack_sample(
        self,
        questions_path: Path,
        answers_path: Path,
        max_questions: int = 500,
        min_score: int = 5,
    ) -> int:
        """
        Ingest StackSample questions and their highest-scoring answers.

        Expected question columns include: Id, Title, Body, Score
        Expected answer columns include: ParentId, Body, Score
        """
        questions_path = Path(questions_path)
        answers_path = Path(answers_path)

        logger.info(
            "Ingesting StackSample (max_questions=%s, min_score=%s)...",
            max_questions,
            min_score,
        )

        if not questions_path.exists():
            logger.warning("StackSample questions file not found: %s", questions_path)
            return 0

        questions = {}

        with questions_path.open(
            mode="r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                try:
                    score = int(row.get("Score") or 0)
                except (TypeError, ValueError):
                    score = 0

                if score < min_score:
                    continue

                question_id = row.get("Id")
                if not question_id:
                    continue

                questions[str(question_id)] = {
                    "title": row.get("Title") or "",
                    "body": row.get("Body") or "",
                    "score": score,
                }

                if len(questions) >= max_questions:
                    break

        answers = {}

        if answers_path.exists():
            with answers_path.open(
                mode="r",
                encoding="utf-8-sig",
                errors="replace",
                newline="",
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                for row in reader:
                    parent_id = row.get("ParentId")
                    if parent_id not in questions:
                        continue

                    try:
                        answer_score = int(row.get("Score") or 0)
                    except (TypeError, ValueError):
                        answer_score = 0

                    current_answer = answers.get(parent_id)
                    if (
                        current_answer is None
                        or answer_score > current_answer["score"]
                    ):
                        answers[parent_id] = {
                            "body": row.get("Body") or "",
                            "score": answer_score,
                        }
        else:
            logger.warning(
                "StackSample answers file not found; indexing questions without answers: %s",
                answers_path,
            )

        docs: List[KnowledgeDoc] = []

        for question_id, question in questions.items():
            answer = answers.get(question_id, {}).get("body")

            # Actual TextPreprocessor signature:
            # format_stack_doc(question_id, title, body, answer=None)
            doc = self.preprocessor.format_stack_doc(
                question_id=question_id,
                title=question["title"],
                body=question["body"],
                answer=answer,
            )
            docs.append(doc)

        logger.info(
            "Built %s KnowledgeDocs from StackSample.",
            len(docs),
        )
        return await self._embed_and_index_docs(docs)

    async def _embed_and_index_docs(
        self,
        docs: List[KnowledgeDoc],
        batch_size: int = 32,
    ) -> int:
        """Generate embeddings in batches, add documents, and save the index."""
        if not docs:
            logger.info("No documents to index.")
            return 0

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        total_indexed = 0

        for start in range(0, len(docs), batch_size):
            batch = docs[start : start + batch_size]
            texts = [(doc.content[:1200] if len(doc.content) > 1200 else doc.content) for doc in batch]
            try:
                embeddings = await self.client.generate_embeddings_batch(texts)
                self.vector_store.add_documents(batch, embeddings)
                total_indexed += len(batch)
            except Exception as e:
                logger.warning(f"Skipping batch {start} due to error: {e}")
            logger.info(
                "Indexed %s/%s documents in this run.",
                total_indexed,
                len(docs),
            )

        self.vector_store.save()
        return total_indexed
    async def ingest_glaive_qa(
        self,
        csv_path: Path,
        max_rows: int = 500,
        min_question_len: int = 15,
        min_answer_len: int = 20,
    ) -> int:
        """
        Ingest Glaive Python Code QA dataset.

        Expected columns:
            - question
            - answer
        """
        csv_path = Path(csv_path)

        logger.info(
            "Ingesting Glaive Python QA (max_rows=%s)...",
            max_rows,
        )

        if not csv_path.exists():
            logger.warning("Glaive QA file not found: %s", csv_path)
            return 0

        docs: List[KnowledgeDoc] = []

        with csv_path.open(
            mode="r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            for idx, row in enumerate(reader, start=1):
                question = (row.get("question") or "").strip()
                answer = (row.get("answer") or "").strip()

                if not question or not answer:
                    continue

                if len(question) < min_question_len or len(answer) < min_answer_len:
                    continue

                doc = self.preprocessor.format_glaive_qa_doc(
                    row_id=str(idx),
                    question=question,
                    answer=answer,
                )
                docs.append(doc)

                if len(docs) >= max_rows:
                    break

        logger.info(
            "Built %s KnowledgeDocs from Glaive Python QA.",
            len(docs),
        )

        return await self._embed_and_index_docs(docs)
