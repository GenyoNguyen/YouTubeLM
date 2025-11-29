# Q&A endpoint

from fastapi import APIRouter

router = APIRouter(prefix="/api/qa", tags=["qa"])


@router.post("/ask")
def ask_question():
    """Ask a question and get answer with timestamps"""
    pass


@router.get("/history")
def get_history():
    """Get chat history"""
    pass

