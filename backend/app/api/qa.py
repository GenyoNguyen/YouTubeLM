"""Q&A API endpoint with SSE streaming."""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

from app.core.qa.service import get_qa_service

router = APIRouter(prefix="/api/qa", tags=["qa"])


class QARequest(BaseModel):
    """Request model for Q&A."""
    query: str
    session_id: Optional[str] = None
    chapters: Optional[List[str]] = None


class FollowupRequest(BaseModel):
    """Request model for followup question."""
    query: str
    session_id: str
    chapters: Optional[List[str]] = None


def format_sse_event(event_type: str, data: dict) -> str:
    """Format a dict as SSE event."""
    data_str = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {data_str}\n\n"


@router.post("/ask")
async def ask_question(request: QARequest):
    """
    Ask a question and get streaming answer with sources.
    
    Returns SSE stream with events:
    - token: Streaming text tokens
    - sources: Source references
    - done: Completion event with full response
    - error: Error event
    """
    service = get_qa_service()
    
    async def generate():
        try:
            async for event in service.answer(
                query=request.query,
                session_id=request.session_id,
                chapters=request.chapters
            ):
                event_type = event.get("type", "message")
                yield format_sse_event(event_type, event)
        except Exception as e:
            error_event = {
                "type": "error",
                "content": f"Error processing question: {str(e)}"
            }
            yield format_sse_event("error", error_event)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for nginx
        }
    )


@router.post("/followup")
async def followup_question(request: FollowupRequest):
    """
    Ask a followup question in an existing session.
    
    Returns SSE stream with events similar to /ask.
    """
    service = get_qa_service()
    
    async def generate():
        try:
            async for event in service.followup(
                session_id=request.session_id,
                query=request.query,
                chapters=request.chapters
            ):
                event_type = event.get("type", "message")
                yield format_sse_event(event_type, event)
        except Exception as e:
            error_event = {
                "type": "error",
                "content": f"Error processing followup: {str(e)}"
            }
            yield format_sse_event("error", error_event)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get chat history for a session."""
    from app.shared.database.postgres import get_postgres_client
    from app.models import ChatMessage
    
    postgres = get_postgres_client()
    
    try:
        with postgres.session_scope() as session:
            messages = session.query(ChatMessage).filter_by(
                session_id=session_id
            ).order_by(ChatMessage.created_at).all()
            
            return {
                "session_id": session_id,
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "sources": msg.sources,
                        "created_at": msg.created_at.isoformat() if msg.created_at else None
                    }
                    for msg in messages
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")
