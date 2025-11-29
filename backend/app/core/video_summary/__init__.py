"""Video summarization core module."""

from .service import VideoSummaryService, get_video_summary_service
from .prompts import (
    VIDEO_SUMMARY_SYSTEM_PROMPT,
    VIDEO_SUMMARY_USER_PROMPT_TEMPLATE,
    CHAPTER_SUMMARY_USER_PROMPT_TEMPLATE,
    QUICK_SUMMARY_USER_PROMPT_TEMPLATE
)

__all__ = [
    "VideoSummaryService",
    "get_video_summary_service",
    "VIDEO_SUMMARY_SYSTEM_PROMPT",
    "VIDEO_SUMMARY_USER_PROMPT_TEMPLATE",
    "CHAPTER_SUMMARY_USER_PROMPT_TEMPLATE",
    "QUICK_SUMMARY_USER_PROMPT_TEMPLATE"
]
