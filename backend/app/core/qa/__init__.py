"""Q&A core module."""

from .service import QAService, get_qa_service
from .prompts import (
    QA_SYSTEM_PROMPT,
    QA_USER_PROMPT_TEMPLATE,
    FOLLOWUP_QA_PROMPT_TEMPLATE
)

__all__ = [
    "QAService",
    "get_qa_service",
    "QA_SYSTEM_PROMPT",
    "QA_USER_PROMPT_TEMPLATE",
    "FOLLOWUP_QA_PROMPT_TEMPLATE"
]
