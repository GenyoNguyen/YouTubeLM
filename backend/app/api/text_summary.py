# Text summarization endpoint

from fastapi import APIRouter

router = APIRouter(prefix="/api/text-summary", tags=["text-summary"])


@router.post("/summarize")
def summarize_topic():
    """Summarize a specific topic"""
    pass


@router.post("/filter")
def filter_videos():
    """Get relevant videos for a topic"""
    pass

