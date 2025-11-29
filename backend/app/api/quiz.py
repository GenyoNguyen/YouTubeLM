"""Quiz generation API endpoint with SSE streaming."""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

from app.core.quiz.service import get_quiz_service

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


class GenerateQuizRequest(BaseModel):
    """Request model for quiz generation."""
    video_ids: List[str]
    question_type: str = "multiple choice"
    num_questions: int = 5


def format_sse_event(event_type: str, data: dict) -> str:
    """Format a dict as SSE event."""
    data_str = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {data_str}\n\n"


@router.post("/generate")
async def generate_quiz(request: GenerateQuizRequest):
    """
    Generate quiz for video(s) with streaming response.
    
    Returns SSE stream with events:
    - progress: Progress updates
    - token: Streaming text tokens
    - done: Completion event with quiz data
    - error: Error event
    """
    if request.num_questions < 1 or request.num_questions > 20:
        raise HTTPException(
            status_code=400,
            detail="num_questions must be between 1 and 20"
        )
    
    if not request.video_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one video_id is required"
        )
    
    service = get_quiz_service()
    
    async def generate():
        try:
            async for event in service.generate_quiz_stream(
                video_ids=request.video_ids,
                question_type=request.question_type,
                num_questions=request.num_questions
            ):
                event_type = event.get("type", "message")
                yield format_sse_event(event_type, event)
        except Exception as e:
            error_event = {
                "type": "error",
                "content": f"Error generating quiz: {str(e)}"
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


@router.get("/{quiz_id}")
async def get_quiz(quiz_id: str):
    """
    Retrieve generated quiz by ID.
    
    Note: This is a placeholder. In a full implementation, quizzes would be
    stored in the database and retrieved here.
    """
    # TODO: Implement quiz storage and retrieval
    raise HTTPException(
        status_code=501,
        detail="Quiz storage and retrieval not yet implemented"
    )


@router.post("/validate")
async def validate_answers(request: dict):
    """
    Validate user answers for a quiz.
    
    Note: This is a placeholder. In a full implementation, this would
    compare user answers with correct answers and return results.
    """
    # TODO: Implement answer validation
    raise HTTPException(
        status_code=501,
        detail="Answer validation not yet implemented"
    )
