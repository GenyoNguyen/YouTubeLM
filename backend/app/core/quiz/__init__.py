"""Quiz generation core module."""

from .service import generate_quiz
from .prompts import QUIZ_SYSTEM_PROMPT

__all__ = [
    "generate_quiz",
    "QUIZ_SYSTEM_PROMPT"
]
