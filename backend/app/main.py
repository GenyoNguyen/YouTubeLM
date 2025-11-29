# FastAPI application entry point

from fastapi import FastAPI
from app.api import (
    health,
    sessions,
    qa,
    text_summary,
    video_summary,
    quiz,
)

app = FastAPI(title="YouTubeLM API")

# Register routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(qa.router)
app.include_router(text_summary.router)
app.include_router(video_summary.router)
app.include_router(quiz.router)

