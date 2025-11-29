"""Universal session management endpoint."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.shared.database.postgres import get_db
from app.models import ChatSession, ChatMessage

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SessionCreate(BaseModel):
    task_type: str  # qa, video_summary, quiz
    title: Optional[str] = None
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    task_type: str
    title: Optional[str]
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[dict]]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    messages: List[MessageResponse]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=SessionResponse)
def create_session(request: SessionCreate):
    """Create a new chat session."""
    with get_db() as db:
        session = ChatSession(
            id=str(uuid.uuid4()),
            task_type=request.task_type,
            title=request.title or f"New {request.task_type} session",
            user_id=request.user_id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return SessionResponse.model_validate(session)


@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all sessions with optional filters."""
    with get_db() as db:
        query = db.query(ChatSession)
        
        if task_type:
            query = query.filter(ChatSession.task_type == task_type)
        if user_id:
            query = query.filter(ChatSession.user_id == user_id)
        
        sessions = query.order_by(
            ChatSession.updated_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str):
    """Get session details with messages."""
    with get_db() as db:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        return SessionDetailResponse(
            id=session.id,
            task_type=session.task_type,
            title=session.title,
            user_id=session.user_id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            messages=[MessageResponse.model_validate(m) for m in messages]
        )


@router.delete("/{session_id}")
def delete_session(session_id: str):
    """Delete a session and all its messages."""
    with get_db() as db:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        db.delete(session)
        db.commit()
        
        return {"status": "deleted", "session_id": session_id}


@router.patch("/{session_id}")
def update_session(session_id: str, title: str = Query(...)):
    """Update session title."""
    with get_db() as db:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.title = title
        db.commit()
        
        return SessionResponse.model_validate(session)
