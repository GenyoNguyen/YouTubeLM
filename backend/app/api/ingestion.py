"""Video ingestion API endpoint."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.shared.ingestion.service import process_video
from app.shared.config.settings import GROQ_API_KEY

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


class VideoIngestionRequest(BaseModel):
    """Request model for video ingestion."""
    video_url: HttpUrl


class VideoIngestionResponse(BaseModel):
    """Response model for video ingestion."""
    video_id: str
    title: str
    chunks_count: int
    status: str


@router.post("/video", response_model=VideoIngestionResponse)
async def ingest_video(
    request: VideoIngestionRequest,
    background_tasks: BackgroundTasks,
):
    """
    Ingest a YouTube video: download, transcribe, embed, and store.
    
    This endpoint processes the video asynchronously in the background.
    """
    try:
        # Process video (synchronous for now, can be made async later)
        result = process_video(
            video_url=str(request.video_url),
            groq_api_key=GROQ_API_KEY,
        )
        return VideoIngestionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

