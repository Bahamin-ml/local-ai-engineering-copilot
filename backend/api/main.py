"""
ML Engineering Copilot - FastAPI Main Application Entrypoint
"""

from pathlib import Path
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.deps import container, lifespan
from backend.api.routes_chat import router as chat_router
from backend.api.routes_sessions import router as sessions_router
from backend.api.schemas import HealthResponse

app = FastAPI(
    title="ML Engineering Copilot API",
    description="High-performance backend API for local ML coding assistant with RAG and Memory.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local desktop & web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Sub-routers
app.include_router(chat_router)
app.include_router(sessions_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """System health check and Ollama connectivity verification."""
    ollama_ok = await container.ollama_client.check_health()
    status_str = "healthy" if ollama_ok else "degraded"
    return HealthResponse(
        status=status_str,
        ollama_available=ollama_ok,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api.main:app", host="127.0.0.1", port=8000, reload=False)
