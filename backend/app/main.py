# FastAPI application entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    health,
    sessions,
    qa,
    video_summary,
    quiz,
    ingestion,
)

app = FastAPI(title="YouTubeLM API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(qa.router)
app.include_router(video_summary.router)
app.include_router(quiz.router)
app.include_router(ingestion.router)

