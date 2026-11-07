"""
API endpoints for session and history management.
"""

from fastapi import APIRouter

from backend.api.deps import container, generate_session_id
from backend.api.schemas import (
    SessionCreateRequest,
    SessionHistoryResponse,
    SessionListResponse,
)

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=SessionListResponse)
def list_sessions():
    """Retrieve all chat sessions, mapping database `id` to API `session_id`."""
    raw_sessions = container.db_manager.get_all_sessions()

    sessions = [
        {
            "session_id": row.get("session_id") or row.get("id"),
            "title": row.get("title") or "New ML Chat",
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
            "summary": row.get("summary") or "",
        }
        for row in raw_sessions
    ]

    return SessionListResponse(sessions=sessions)


@router.post("", status_code=201)
def create_session(request: SessionCreateRequest):
    """Create a new chat session."""
    session_id = generate_session_id()

    container.memory_manager.ensure_session(
        session_id=session_id,
        title=request.title,
    )

    return {
        "session_id": session_id,
        "title": request.title,
        "message": "Session created successfully",
    }


@router.get("/{session_id}", response_model=SessionHistoryResponse)
def get_session_history(session_id: str, limit: int = 50):
    """Get a session's message history and latest summary."""
    messages = container.db_manager.get_session_messages(
        session_id=session_id,
        limit=limit,
    )
    summary = container.db_manager.get_session_summary(session_id)

    return SessionHistoryResponse(
        session_id=session_id,
        messages=messages,
        summary=summary,
    )
