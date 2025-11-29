# Video summarization endpoint

from fastapi import APIRouter

router = APIRouter(prefix="/api/video-summary", tags=["video-summary"])


@router.post("/summarize")
def summarize_video():
    """Summarize a specific video"""
    pass


@router.get("/videos")
def list_videos():
    """List available videos"""
    pass

