# YouTubeLM Backend

FastAPI-based backend for the YouTubeLM AI assistant application. Provides RESTful APIs with Server-Sent Events (SSE) streaming for Q&A, video summarization, and quiz generation.

## Features

- **Q&A System**: Ask questions and get answers with exact video timestamps using RAG (Retrieval-Augmented Generation)
- **Video Summarization**: Generate detailed or quick summaries of video content
- **Quiz Generation**: Create multiple-choice quizzes from video content
- **Session Management**: Universal session management for all AI tasks
- **Video Ingestion**: Download, transcribe, and embed YouTube videos
- **Streaming Responses**: Real-time streaming via Server-Sent Events (SSE)
- **Hybrid Search**: Combines BM25 (PostgreSQL) and vector search (Qdrant) for better retrieval

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (metadata) + Qdrant (vector embeddings)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Transcription**: GroqCloud Whisper API (whisper-large-v3-turbo)
- **Embeddings**: HuggingFace sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Groq (llama-3.1-70b-versatile)
- **Reranking**: Cross-encoder (ms-marco-MiniLM-L-6-v2)

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── health.py     # Health check
│   │   ├── ingestion.py  # Video ingestion
│   │   ├── qa.py         # Q&A endpoints
│   │   ├── quiz.py       # Quiz generation
│   │   ├── sessions.py   # Session management
│   │   └── video_summary.py  # Video summarization
│   ├── core/             # Business logic
│   │   ├── qa/           # Q&A service
│   │   ├── quiz/         # Quiz service
│   │   └── video_summary/  # Video summary service
│   ├── models.py         # SQLAlchemy models
│   ├── main.py           # FastAPI app entry point
│   └── shared/           # Shared utilities
│       ├── config/       # Configuration
│       ├── database/     # Database clients
│       ├── ingestion/    # Ingestion pipeline
│       ├── llm/          # LLM client
│       └── rag/          # RAG components
├── alembic/              # Database migrations
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── alembic.ini           # Alembic configuration
├── pytest.ini            # Pytest configuration
├── API_DOCUMENTATION.md  # Complete API documentation
└── DATABASE_SETUP.md     # Database setup guide
```

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ (via Docker)
- Qdrant (via Docker)
- Groq API key (for transcription and LLM)
- Docker and Docker Compose (for databases)

## Installation

### 1. Clone the Repository

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Databases

See [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) for detailed database setup instructions.

Quick setup:

```bash
# From project root
docker-compose up -d

# Run migrations
cd backend
alembic upgrade head
```

### 5. Configure Environment Variables

Create a `.env` file in the project root (not in `backend/`):

```env
# Database Configuration
POSTGRES_DB=youtubelm
POSTGRES_USER=youtubelm
POSTGRES_PASSWORD=youtubelm
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Groq API (Required)
GROQ_API_KEY=your_groq_api_key_here

# LLM Configuration
LLM_MODEL=llama-3.1-70b-versatile
LLM_TEMPERATURE=1.0
LLM_MAX_COMPLETION_TOKENS=3000
LLM_MAX_RETRIES=3
LLM_TIMEOUT=60

# RAG Configuration
ENABLE_RERANKING=true
RETRIEVAL_INITIAL_K=150
FINAL_CONTEXT_CHUNKS=10

# Video Summary Configuration
MAX_TRANSCRIPT_CHUNKS=200
ENABLE_SUMMARY_CACHE=true
```

## Running the Server

### Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run with auto-reload
uvicorn app.main:app --reload --port 8000
```

The server will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Environment Variable for Port

```bash
# Set port in .env
BACKEND_PORT=8000

# Run with port from env
uvicorn app.main:app --reload --port ${BACKEND_PORT:-8000}
```

## API Documentation

Complete API documentation is available in [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md).

### Quick API Examples

#### Health Check

```bash
curl http://localhost:8000/api/health
```

#### Ingest a Video

```bash
curl -X POST "http://localhost:8000/api/ingestion/video" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

#### Ask a Question (SSE Stream)

```bash
curl -X POST "http://localhost:8000/api/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is deep learning?"}' \
  --no-buffer
```

#### Generate Video Summary (SSE Stream)

```bash
curl -X POST "http://localhost:8000/api/video-summary/summarize" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "VIDEO_ID", "summary_type": "detailed"}' \
  --no-buffer
```

## Development

### Code Structure

The backend follows a modular monolith architecture:

- **API Layer** (`app/api/`): FastAPI route handlers
- **Core Services** (`app/core/`): Business logic for each feature
- **Shared Components** (`app/shared/`): Reusable utilities
  - `config/`: Configuration management
  - `database/`: Database clients (PostgreSQL, Qdrant)
  - `ingestion/`: Video processing pipeline
  - `llm/`: LLM client wrapper
  - `rag/`: RAG retrieval and reranking

### Adding a New Endpoint

1. Create route handler in `app/api/`
2. Create service in `app/core/` if needed
3. Register router in `app/main.py`

Example:

```python
# app/api/my_feature.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/my-feature", tags=["my-feature"])

@router.get("/")
def my_endpoint():
    return {"message": "Hello"}
```

```python
# app/main.py
from app.api import my_feature
app.include_router(my_feature.router)
```

### Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Review the generated migration file in `alembic/versions/`, then apply:

```bash
alembic upgrade head
```

Rollback:

```bash
alembic downgrade -1
```

### Environment Variables

The backend loads environment variables from:
1. `.env` file in the project root
2. `.env` file in the `backend/` directory (fallback)
3. System environment variables

See `app/shared/config/settings.py` for all available configuration options.

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/core/test_video_summary_service.py

# Run with verbose output
pytest -v
```

### Test Configuration

Test configuration is in `pytest.ini`. Tests use mocks for external services (databases, APIs).

## Database Schema

### Tables

- **videos**: Video metadata (id, title, url, duration)
- **chunks**: Transcript chunks (id, video_id, start_time, end_time, text, qdrant_id)
- **chat_sessions**: Chat sessions (id, task_type, title, user_id, timestamps)
- **chat_messages**: Chat messages (id, session_id, role, content, sources, timestamps)
- **quiz_questions**: Quiz questions (id, session_id, question, options, correct_answer, etc.)

### Vector Database

- **Qdrant Collection**: `youtubelm_transcripts`
- **Vector Dimension**: 384 (HuggingFace all-MiniLM-L6-v2)
- **Payload**: video_id, video_title, video_url, start_time, end_time, text

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker exec -it youtubelm-postgres psql -U youtubelm -d youtubelm
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
docker-compose ps

# Check Qdrant logs
docker-compose logs qdrant

# Test Qdrant API
curl http://localhost:6333/collections
```

### Import Errors

Make sure you're in the `backend/` directory and the virtual environment is activated:

```bash
cd backend
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Environment Variables Not Loading

1. Ensure `.env` file exists in project root
2. Check that `python-dotenv` is installed: `pip install python-dotenv`
3. Verify variable names match those in `app/shared/config/settings.py`

### Migration Issues

```bash
# Check current migration status
alembic current

# Show migration history
alembic history

# If migrations are out of sync, reset (WARNING: data loss)
# alembic downgrade base
# alembic upgrade head
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

## Performance Considerations

### Streaming Responses

SSE endpoints stream responses in real-time. For best performance:
- Use proper SSE client libraries
- Handle connection errors gracefully
- Implement reconnection logic

### Database Queries

- RAG retrieval uses hybrid search (BM25 + vector)
- Reranking is optional but improves quality
- Adjust `RETRIEVAL_INITIAL_K` and `FINAL_CONTEXT_CHUNKS` based on needs

### LLM Configuration

- Adjust `LLM_MAX_COMPLETION_TOKENS` based on expected response length
- Lower `LLM_TEMPERATURE` for more deterministic responses
- Increase `LLM_TIMEOUT` for longer videos

## Security Notes

- **CORS**: Currently allows all origins (`*`). Update in `app/main.py` for production
- **API Keys**: Store securely in `.env` file (never commit to git)
- **Database**: Use strong passwords in production
- **Input Validation**: All endpoints use Pydantic models for validation

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update API documentation
4. Run linters and tests before committing

## License

See project root LICENSE file.

## Support

For issues or questions:
- Check [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) for API details
- Check [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) for database setup
- Review project root README for overall architecture

