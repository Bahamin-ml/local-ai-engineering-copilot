"""
Service container and shared dependencies for FastAPI layer.
"""

from contextlib import asynccontextmanager
from typing import Optional
import uuid

from fastapi import FastAPI

from backend.config import Settings
from backend.core.memory_manager import MemoryManager
from backend.core.ollama_client import OllamaClient
from backend.core.prompt_engine import PromptEngine
from backend.database.models import DatabaseManager
from backend.rag.vector_store import VectorStore


class ServiceContainer:
    """Holds long-lived application state across the API lifecycle."""

    def __init__(self):
        self.settings: Settings = Settings()
        self.db_manager: DatabaseManager = DatabaseManager(str(self.settings.DB_PATH))
        self.ollama_client: OllamaClient = OllamaClient(self.settings)
        self.memory_manager: MemoryManager = MemoryManager(
            db_manager=self.db_manager,
            ollama_client=self.ollama_client,
        )
        self.prompt_engine: PromptEngine = PromptEngine()
        self.vector_store: VectorStore = VectorStore(
            dimension=self.settings.EMBEDDING_DIM,
            index_path=self.settings.FAISS_INDEX_PATH,
            metadata_path=self.settings.FAISS_METADATA_PATH,
        )

    def initialize(self):
        """Initialize database tables and load FAISS vector store into memory."""
        self.db_manager.init_db()
        try:
            self.vector_store.load()
        except Exception:
            # If vector store files are not found, start with empty index
            pass


container = ServiceContainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown."""
    container.initialize()
    yield


def generate_session_id() -> str:
    """Generate a clean unique session ID."""
    return f"sess_{uuid.uuid4().hex[:12]}"
