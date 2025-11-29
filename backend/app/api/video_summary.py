"""Video summarization API endpoint with SSE streaming."""

import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.core.video_summary.service import get_video_summary_service

router = APIRouter(prefix="/api/video-summary", tags=["video-summary"])


class SummarizeRequest(BaseModel):
    """Request model for video summarization."""
    video_id: str
    summary_type: str = "detailed"  # "detailed" or "quick"
    session_id: Optional[str] = None
    force_regenerate: bool = False


def format_sse_event(event_type: str, data: dict) -> str:
    """Format a dict as SSE event."""
    data_str = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {data_str}\n\n"


@router.post("/summarize")
async def summarize_video(request: SummarizeRequest):
    """
    Summarize a specific video with streaming response.
    
    Returns SSE stream with events:
    - metadata: Video information
    - token: Streaming text tokens
    - cached: Cached summary (if available)
    - done: Completion event
    - error: Error event
    """
    if request.summary_type not in ["detailed", "quick"]:
        raise HTTPException(
            status_code=400,
            detail="summary_type must be 'detailed' or 'quick'"
        )
    
    service = get_video_summary_service()
    
    async def generate():
        try:
            async for event in service.summarize_video(
                video_id=request.video_id,
                summary_type=request.summary_type,
                session_id=request.session_id,
                force_regenerate=request.force_regenerate
            ):
                event_type = event.get("type", "message")
                yield format_sse_event(event_type, event)
        except Exception as e:
            error_event = {
                "type": "error",
                "content": f"Error generating summary: {str(e)}"
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


@router.get("/videos")
async def list_videos(chapter: Optional[str] = Query(None, description="Filter by chapter")):
    """List available videos."""
    service = get_video_summary_service()
    
    try:
        videos = await service.list_videos(chapter=chapter)
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing videos: {str(e)}")


@router.get("/chapters")
async def list_chapters():
    """List available chapters."""
    service = get_video_summary_service()
    
    try:
        chapters = await service.list_chapters()
        return {"chapters": chapters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing chapters: {str(e)}")
