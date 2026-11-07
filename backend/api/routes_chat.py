"""
API endpoints for synchronous chat and SSE streaming chat with RAG augmentation.
Path: backend/api/routes_chat.py
"""

import json
from typing import AsyncGenerator, Dict, List, Tuple

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.api.deps import container, generate_session_id
from backend.api.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


async def _resolve_rag_context(query: str, top_k: int) -> Tuple[str, List[Dict], bool]:
    """
    Search the knowledge base and build a formatted RAG context block.
    Returns:
        rag_context: str
        sources: List[Dict]
        rag_used: bool
    """
    rag_context = ""
    sources: List[Dict] = []
    rag_used = False

    try:
        query_emb = await container.ollama_client.generate_embedding(query)
        search_results = container.vector_store.search(query_emb, top_k=top_k)

        filtered = [
            (doc, score)
            for doc, score in search_results
            if score >= container.settings.SIMILARITY_THRESHOLD
        ]

        if filtered:
            rag_used = True
            context_blocks = []

            for rank, (doc, score) in enumerate(filtered, start=1):
                metadata = getattr(doc, "metadata", {}) or {}
                doc_type = metadata.get("type", "unknown")
                content = getattr(doc, "content", "") or ""
                preview = content[:1200].strip()

                context_blocks.append(
                    f"--- Reference Document {rank} "
                    f"[Type: {doc_type} | Score: {score:.3f}] ---\n"
                    f"{preview}"
                )

                sources.append(
                    {
                        "doc_id": getattr(doc, "doc_id", ""),
                        "type": doc_type,
                        "score": round(float(score), 4),
                        "metadata": metadata,
                    }
                )

            rag_context = "\n\n".join(context_blocks)

    except Exception:
        # Graceful fallback if embedding/search fails
        rag_used = False
        rag_context = ""
        sources = []

    return rag_context, sources, rag_used


@router.post("", response_model=ChatResponse)
async def chat_sync(request: ChatRequest):
    """Standard non-streaming chat with RAG and persistent memory."""
    session_id = request.session_id or generate_session_id()
    container.memory_manager.ensure_session(session_id=session_id)

    # 1) RAG retrieval
    top_k = request.top_k or container.settings.TOP_K_RESULTS
    rag_context = ""
    sources: List[Dict] = []
    rag_used = False

    if request.use_rag:
        rag_context, sources, rag_used = await _resolve_rag_context(request.query, top_k)

    # 2) Conversation history + summary
    history = container.memory_manager.get_context_history(session_id=session_id, limit=6)
    summary = container.db_manager.get_session_summary(session_id=session_id)

    # 3) Prompt assembly
    payload_messages = container.prompt_engine.assemble_conversation_payload(
        user_query=request.query,
        mode=request.mode,
        history=history,
        rag_context=rag_context if rag_used else None,
        summary_context=summary,
    )

    # 4) LLM generation
    answer_tokens: List[str] = []
    async for chunk in container.ollama_client.stream_chat(payload_messages):
        answer_tokens.append(chunk)

    full_answer = "".join(answer_tokens).strip()

    # 5) Persist memory
    container.memory_manager.append_interaction(
        session_id=session_id,
        user_query=request.query,
        assistant_reply=full_answer,
        model=container.settings.DEFAULT_LLM_MODEL,
        rag_used=rag_used,
    )

    return ChatResponse(
        session_id=session_id,
        answer=full_answer,
        model=container.settings.DEFAULT_LLM_MODEL,
        rag_used=rag_used,
        sources=sources,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Server-Sent Events (SSE) streaming chat endpoint."""
    session_id = request.session_id or generate_session_id()
    container.memory_manager.ensure_session(session_id=session_id)

    # 1) RAG retrieval
    top_k = request.top_k or container.settings.TOP_K_RESULTS
    rag_context = ""
    sources: List[Dict] = []
    rag_used = False

    if request.use_rag:
        rag_context, sources, rag_used = await _resolve_rag_context(request.query, top_k)

    # 2) Conversation history + summary
    history = container.memory_manager.get_context_history(session_id=session_id, limit=6)
    summary = container.db_manager.get_session_summary(session_id=session_id)

    # 3) Prompt assembly
    payload_messages = container.prompt_engine.assemble_conversation_payload(
        user_query=request.query,
        mode=request.mode,
        history=history,
        rag_context=rag_context if rag_used else None,
        summary_context=summary,
    )

    async def sse_event_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'event': 'start', 'session_id': session_id, 'rag_used': rag_used, 'sources': sources})}\n\n"

        accumulated_chunks: List[str] = []

        try:
            async for chunk in container.ollama_client.stream_chat(payload_messages):
                accumulated_chunks.append(chunk)
                payload = json.dumps({"event": "chunk", "content": chunk})
                yield f"data: {payload}\n\n"
        except Exception as e:
            err_payload = json.dumps({"event": "error", "message": str(e)})
            yield f"data: {err_payload}\n\n"
            return

        full_reply = "".join(accumulated_chunks).strip()

        container.memory_manager.append_interaction(
            session_id=session_id,
            user_query=request.query,
            assistant_reply=full_reply,
            model=container.settings.DEFAULT_LLM_MODEL,
            rag_used=rag_used,
        )

        yield f"data: {json.dumps({'event': 'end', 'session_id': session_id})}\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")
