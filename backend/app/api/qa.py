"""Q&A endpoint with SSE streaming."""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

from app.core.qa import get_qa_service
from app.shared.database.postgres import get_db
from app.models import ChatMessage

router = APIRouter(prefix="/api/qa", tags=["qa"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AskRequest(BaseModel):
    query: str
    chapters: Optional[List[str]] = None
    session_id: Optional[str] = None


class FollowupRequest(BaseModel):
    session_id: str
    query: str
    chapters: Optional[List[str]] = None


class SourceResponse(BaseModel):
    index: int
    video_id: str
    video_title: str
    video_url: str
    chapter: str
    start_time: int
    end_time: int
    text: str
    score: float


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[dict]]
    created_at: str

    class Config:
        from_attributes = True


# ============================================================================
# SSE Helper
# ============================================================================

def format_sse(data: dict) -> str:
    """Format data as SSE event."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/ask")
async def ask_question(request: AskRequest):
    """
    Ask a question with streaming response.
    
    Returns SSE stream with events:
    - token: Content tokens
    - sources: Source citations
    - done: Final response with session_id
    - error: Error message
    """
    service = get_qa_service()
    
    async def event_generator():
        try:
            async for event in service.answer(
                query=request.query,
                chapters=request.chapters,
                session_id=request.session_id
            ):
                yield format_sse(event)
        except Exception as e:
            yield format_sse({"type": "error", "content": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/followup")
async def followup_question(request: FollowupRequest):
    """
    Ask a followup question in an existing session.
    
    Returns SSE stream with events:
    - token: Content tokens
    - sources: Source citations
    - done: Final response
    - error: Error message
    """
    service = get_qa_service()
    
    async def event_generator():
        try:
            async for event in service.followup(
                session_id=request.session_id,
                query=request.query,
                chapters=request.chapters
            ):
                yield format_sse(event)
        except ValueError as e:
            yield format_sse({"type": "error", "content": str(e)})
        except Exception as e:
            yield format_sse({"type": "error", "content": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history/{session_id}")
def get_history(session_id: str):
    """Get chat history for a session."""
    with get_db() as db:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        if not messages:
            raise HTTPException(
                status_code=404, 
                detail=f"No history found for session {session_id}"
            )
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "sources": m.sources,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ],
            "count": len(messages)
        }
