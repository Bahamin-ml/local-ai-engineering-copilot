"""
ML Engineering Copilot - Central Configuration Module
Path: backend/config.py
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # App Information
    APP_NAME: str = "ML Engineering Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Dynamic Base Paths (Relative to repository root)
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    BASE_DIR: Path = PROJECT_ROOT
    DATA_DIR: Path = PROJECT_ROOT / "data"
    STORAGE_DIR: Path = PROJECT_ROOT / "storage"
    DB_DIR: Path = STORAGE_DIR / "db"
    FAISS_DIR: Path = DATA_DIR

    # Database Paths
    DATABASE_PATH: Path = DB_DIR / "copilot_memory.db"
    DB_PATH: Path = DATABASE_PATH

    # Vector store paths
    FAISS_INDEX_PATH: Path = DATA_DIR / "faiss.index"
    FAISS_METADATA_PATH: Path = DATA_DIR / "metadata.json"

    # Ollama Local Service Configuration (Reads from ENV for Docker compatibility)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "qwen3:4b")
    FAST_LLM_MODEL: str = "qwen2.5:1.5b"
    FAST_SUMMARY_MODEL: str = "qwen2.5:1.5b"
    DEFAULT_EMBED_MODEL: str = "nomic-embed-text:latest"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    EMBEDDING_DIM: int = 768

    # Generation & RAG Parameters
    TEMPERATURE: float = 0.2
    CONTEXT_WINDOW: int = 8192
    TOP_K_RETRIEVAL: int = 4
    TOP_K_RESULTS: int = 4
    SIMILARITY_THRESHOLD: float = 0.35

    def ensure_directories(self) -> None:
        """Ensure necessary storage directories exist."""
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


# Singleton Instance
settings = Settings()
settings.ensure_directories()

# Aliases for backwards and forwards compatibility across codebase
Config = Settings
