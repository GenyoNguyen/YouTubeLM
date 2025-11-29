"""Quiz generation endpoint with SSE streaming."""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid

from app.shared.database.postgres import get_db
from app.models import QuizQuestion

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


# ============================================================================
# Request/Response Models
# ============================================================================

class QuizGenerateRequest(BaseModel):
    video_ids: List[str]
    question_type: str = "mcq"  # mcq, true_false, fill_blank
    num_questions: int = 5
    difficulty: Optional[str] = "medium"  # easy, medium, hard


class QuizSubmitRequest(BaseModel):
    question_id: int
    answer: str


class QuestionResponse(BaseModel):
    id: int
    question_type: str
    question: str
    options: Optional[List[str]]
    video_id: Optional[str]

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[QuestionResponse]
    total_questions: int


class AnswerResult(BaseModel):
    correct: bool
    correct_answer: str
    explanation: Optional[str]


# ============================================================================
# SSE Helper
# ============================================================================

def format_sse(data: dict) -> str:
    """Format data as SSE event."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/generate")
async def generate_quiz(request: QuizGenerateRequest):
    """
    Generate quiz questions with streaming response.
    
    Returns SSE stream with events:
    - progress: Generation progress
    - question: Individual question generated
    - done: All questions with quiz_id
    - error: Error message
    """
    # TODO: Implement with QuizService when ready
    # For now, return a placeholder implementation
    
    quiz_id = str(uuid.uuid4())
    
    async def event_generator():
        try:
            # Placeholder: In production, this would use QuizService
            yield format_sse({
                "type": "progress",
                "content": f"Generating {request.num_questions} questions..."
            })
            
            # Generate placeholder questions
            questions = []
            for i in range(request.num_questions):
                question = {
                    "index": i + 1,
                    "question_type": request.question_type,
                    "question": f"Sample question {i + 1} about the video content?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"] if request.question_type == "mcq" else None,
                    "video_id": request.video_ids[0] if request.video_ids else None
                }
                questions.append(question)
                yield format_sse({"type": "question", **question})
            
            yield format_sse({
                "type": "done",
                "quiz_id": quiz_id,
                "questions": questions,
                "total": len(questions)
            })
            
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


@router.get("/{quiz_id}")
def get_quiz(quiz_id: str):
    """Retrieve a generated quiz by ID."""
    with get_db() as db:
        questions = db.query(QuizQuestion).filter(
            QuizQuestion.session_id == quiz_id
        ).all()
        
        if not questions:
            raise HTTPException(
                status_code=404,
                detail=f"Quiz {quiz_id} not found"
            )
        
        return QuizResponse(
            quiz_id=quiz_id,
            questions=[QuestionResponse.model_validate(q) for q in questions],
            total_questions=len(questions)
        )


@router.post("/submit", response_model=AnswerResult)
def submit_answer(request: QuizSubmitRequest):
    """Submit and validate a quiz answer."""
    with get_db() as db:
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == request.question_id
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=404,
                detail=f"Question {request.question_id} not found"
            )
        
        is_correct = request.answer.upper() == question.correct_answer.upper()
        
        return AnswerResult(
            correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation
        )


@router.get("/history")
def get_quiz_history(
    user_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Get quiz history for a user."""
    with get_db() as db:
        query = db.query(QuizQuestion)
        
        # Group by session_id to get unique quizzes
        quiz_sessions = db.query(
            QuizQuestion.session_id
        ).distinct().limit(limit).all()
        
        quizzes = []
        for (session_id,) in quiz_sessions:
            questions = db.query(QuizQuestion).filter(
                QuizQuestion.session_id == session_id
            ).all()
            
            if questions:
                quizzes.append({
                    "quiz_id": session_id,
                    "question_count": len(questions),
                    "created_at": questions[0].created_at.isoformat()
                })
        
        return {"quizzes": quizzes, "count": len(quizzes)}
