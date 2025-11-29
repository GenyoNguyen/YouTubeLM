# Quiz generation endpoint

from fastapi import APIRouter

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/generate")
def generate_quiz():
    """Generate quiz for video(s)"""
    pass


@router.get("/{quiz_id}")
def get_quiz(quiz_id: str):
    """Retrieve generated quiz"""
    pass


@router.post("/validate")
def validate_answers():
    """Validate user answers"""
    pass

