"""Video summarization endpoint with SSE streaming."""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

from app.core.video_summary import get_video_summary_service

router = APIRouter(prefix="/api/video-summary", tags=["video-summary"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SummarizeRequest(BaseModel):
    video_id: str
    summary_type: Optional[str] = "detailed"  # detailed, quick
    session_id: Optional[str] = None
    force_regenerate: Optional[bool] = False


class ChapterSummarizeRequest(BaseModel):
    chapter: str
    session_id: Optional[str] = None


class VideoInfo(BaseModel):
    video_id: str
    title: str
    chapter: str
    video_url: str
    duration: str
    duration_seconds: int
    num_chunks: int


# ============================================================================
# SSE Helper
# ============================================================================

def format_sse(data: dict) -> str:
    """Format data as SSE event."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/summarize")
async def summarize_video(request: SummarizeRequest):
    """
    Summarize a specific video with streaming response.
    
    Returns SSE stream with events:
    - metadata: Video info
    - token: Content tokens
    - done: Final response with session_id
    - cached: Cached summary (if available)
    - error: Error message
    """
    service = get_video_summary_service()
    
    async def event_generator():
        try:
            async for event in service.summarize_video(
                video_id=request.video_id,
                summary_type=request.summary_type,
                session_id=request.session_id,
                force_regenerate=request.force_regenerate
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


@router.post("/summarize-chapter")
async def summarize_chapter(request: ChapterSummarizeRequest):
    """
    Summarize all videos in a chapter with streaming response.
    
    Returns SSE stream with events:
    - metadata: Chapter info with video count
    - token: Content tokens
    - done: Final response
    - error: Error message
    """
    service = get_video_summary_service()
    
    async def event_generator():
        try:
            async for event in service.summarize_chapter(
                chapter=request.chapter,
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


@router.get("/videos")
async def list_videos(
    chapter: Optional[str] = Query(None, description="Filter by chapter")
):
    """List available videos, optionally filtered by chapter."""
    service = get_video_summary_service()
    
    try:
        videos = await service.list_videos(chapter=chapter)
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapters")
async def list_chapters():
    """List all available chapters."""
    service = get_video_summary_service()
    
    try:
        chapters = await service.list_chapters()
        return {"chapters": chapters, "count": len(chapters)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
