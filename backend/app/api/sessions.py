"""Universal session management API endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.shared.database.postgres import get_postgres_client
from app.models import ChatSession, ChatMessage

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""
    task_type: str = "qa"  # "qa", "video_summary", "quiz"
    title: Optional[str] = None
    user_id: str = "default_user"


class SessionResponse(BaseModel):
    """Response model for session."""
    id: str
    task_type: str
    title: str
    user_id: str
    created_at: str
    updated_at: str
    message_count: int = 0


@router.post("/", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session."""
    import uuid
    
    postgres = get_postgres_client()
    
    try:
        with postgres.session_scope() as session:
            new_session = ChatSession(
                id=str(uuid.uuid4()),
                task_type=request.task_type,
                title=request.title or f"New {request.task_type} session",
                user_id=request.user_id
            )
            session.add(new_session)
            session.commit()
            session.refresh(new_session)
            
            return SessionResponse(
                id=new_session.id,
                task_type=new_session.task_type,
                title=new_session.title,
                user_id=new_session.user_id,
                created_at=new_session.created_at.isoformat() if new_session.created_at else "",
                updated_at=new_session.updated_at.isoformat() if new_session.updated_at else "",
                message_count=0
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details."""
    postgres = get_postgres_client()
    
    try:
        with postgres.session_scope() as session:
            chat_session = session.query(ChatSession).filter_by(id=session_id).first()
            
            if not chat_session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Count messages
            message_count = session.query(ChatMessage).filter_by(
                session_id=session_id
            ).count()
            
            return SessionResponse(
                id=chat_session.id,
                task_type=chat_session.task_type,
                title=chat_session.title,
                user_id=chat_session.user_id,
                created_at=chat_session.created_at.isoformat() if chat_session.created_at else "",
                updated_at=chat_session.updated_at.isoformat() if chat_session.updated_at else "",
                message_count=message_count
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    user_id: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 50
):
    """List sessions, optionally filtered by user_id and task_type."""
    postgres = get_postgres_client()
    
    try:
        with postgres.session_scope() as session:
            query = session.query(ChatSession)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            if task_type:
                query = query.filter_by(task_type=task_type)
            
            sessions = query.order_by(ChatSession.updated_at.desc()).limit(limit).all()
            
            result = []
            for chat_session in sessions:
                message_count = session.query(ChatMessage).filter_by(
                    session_id=chat_session.id
                ).count()
                
                result.append(SessionResponse(
                    id=chat_session.id,
                    task_type=chat_session.task_type,
                    title=chat_session.title,
                    user_id=chat_session.user_id,
                    created_at=chat_session.created_at.isoformat() if chat_session.created_at else "",
                    updated_at=chat_session.updated_at.isoformat() if chat_session.updated_at else "",
                    message_count=message_count
                ))
            
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages."""
    postgres = get_postgres_client()
    
    try:
        with postgres.session_scope() as session:
            chat_session = session.query(ChatSession).filter_by(id=session_id).first()
            
            if not chat_session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Delete all messages first
            session.query(ChatMessage).filter_by(session_id=session_id).delete()
            
            # Delete session
            session.delete(chat_session)
            session.commit()
            
            return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
