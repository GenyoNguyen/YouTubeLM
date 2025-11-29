# YouTubeLM - AI Assistant for YouTube Videos

A video course AI assistant that helps students interact with course content through 3 main capabilities:
1. **Q&A**: Ask questions and get answers with exact video timestamps
2. **Video Summarization**: Summarize content of specific course videos
3. **Quiz Generation**: Generate Yes/No and MCQ quizzes from video content

## Architecture

- **Backend**: Python with FastAPI (Modular Monolith)
- **Frontend**: React with TypeScript
- **Databases**: PostgreSQL (metadata) + Qdrant (vector embeddings)
- **Transcription**: Whisper large-v3
- **Embeddings**: HuggingFace sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: OpenAI GPT models

## Project Structure

```
youtubelm/
├── frontend/          # React/TypeScript Web UI
├── backend/           # Python FastAPI backend
├── ingestion/         # Video processing pipeline
├── evaluation/        # Task evaluation modules
└── scripts/           # Utility scripts
```

## Setup

1. Copy `.env.example` to `.env` and configure (see [Database Setup Guide](backend/DATABASE_SETUP.md))
2. Start databases: `docker-compose up -d`
3. Run database migrations: `cd backend && alembic upgrade head`
4. Verify setup: `python scripts/verify_databases.py`
5. Test ingestion: `python scripts/test_ingestion.py <youtube_url>`
6. Start backend: `cd backend && uvicorn app.main:app --reload`
7. Start frontend: `cd frontend && npm install && npm run dev`

## Quick Start

### Ingest a Video

```bash
# Test the ingestion pipeline
python scripts/test_ingestion.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

# Or use the API
curl -X POST "http://localhost:8000/api/ingestion/video" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"}'
```

## Documentation

- [`ARCHITECTURE_SAMPLE.md`](ARCHITECTURE_SAMPLE.md) - Detailed architecture documentation
- [`backend/DATABASE_SETUP.md`](backend/DATABASE_SETUP.md) - Database setup guide

