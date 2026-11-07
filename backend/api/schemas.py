"""
Pydantic request and response schemas for the ML Engineering Copilot API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.core.prompt_engine import CopilotMode


class ChatRequest(BaseModel):
    """Request payload for a regular or streaming chat."""

    query: str = Field(..., min_length=1, description="User's message")
    session_id: Optional[str] = Field(
        default=None,
        description="Existing session ID; if omitted, the server creates one",
    )
    mode: CopilotMode = Field(
        default=CopilotMode.GENERAL_ML,
        description="Copilot behavior mode",
    )
    use_rag: bool = Field(
        default=True,
        description="Whether to retrieve relevant knowledge-base documents",
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Maximum number of RAG results to retrieve",
    )


class ChatResponse(BaseModel):
    """Response payload for a non-streaming chat."""

    session_id: str
    answer: str
    model: str
    rag_used: bool = False
    sources: List[Dict[str, Any]] = Field(default_factory=list)


class SessionCreateRequest(BaseModel):
    """Request payload for creating a session."""

    title: str = Field(default="New ML Chat", min_length=1, max_length=200)


class SessionListResponse(BaseModel):
    """Session records returned by DatabaseManager."""

    sessions: List[Dict[str, Any]] = Field(default_factory=list)


class SessionHistoryResponse(BaseModel):
    """Messages and summary returned for a session."""

    session_id: str
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None


class HealthResponse(BaseModel):
    """Basic service health response."""

    status: str
    ollama_available: bool


class APIError(BaseModel):
    """Consistent API error payload."""

    detail: str
