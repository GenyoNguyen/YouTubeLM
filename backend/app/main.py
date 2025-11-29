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

app = FastAPI(
    title="YouTubeLM API",
    description="API for YouTube video interaction - Q&A, Summarization, Quiz",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Vite default
        "http://localhost:5173",      # Vite alternative
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

