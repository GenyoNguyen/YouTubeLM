# Database Setup Guide

This guide explains how to set up and initialize the databases for YouTubeLM.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with virtual environment
- PostgreSQL client tools (optional, for manual inspection)

## Step 1: Start Database Services

Start PostgreSQL and Qdrant using Docker Compose:

```bash
# From project root
docker-compose up -d
```

This will start:
- **PostgreSQL** on port `5432`
- **Qdrant** on ports `6333` (HTTP) and `6334` (gRPC)

Verify services are running:

```bash
docker-compose ps
```

You should see both `postgres` and `qdrant` services with status "Up".

## Step 2: Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and configure database settings:

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

# API Keys (required for ingestion)
GROQ_API_KEY=your_groq_api_key_here
```

## Step 3: Install Python Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

## Step 4: Run Database Migrations

Initialize the database schema using Alembic:

```bash
cd backend

# Run migrations
alembic upgrade head
```

This will create all necessary tables:
- `videos` - Video metadata
- `chunks` - Transcript chunks
- `chat_sessions` - Chat sessions
- `chat_messages` - Chat messages
- `quiz_questions` - Quiz questions

## Step 5: Verify Database Setup

Run the verification script:

```bash
# From project root
python scripts/verify_databases.py
```

Or manually verify:

### PostgreSQL

```bash
# Connect to PostgreSQL
docker exec -it youtubelm-postgres psql -U youtubelm -d youtubelm

# List tables
\dt

# Check videos table
SELECT COUNT(*) FROM videos;

# Exit
\q
```

### Qdrant

```bash
# Check Qdrant collections
curl http://localhost:6333/collections

# Check specific collection (after ingestion)
curl http://localhost:6333/collections/youtubelm_transcripts
```

## Step 6: Initialize Qdrant Collection

The Qdrant collection will be automatically created when you first ingest a video. However, you can also initialize it manually:

```python
from app.shared.database.qdrant import ensure_collection
ensure_collection()
```

## Database Schema

### PostgreSQL Tables

#### `videos`
- `id` (String, PK) - YouTube video ID
- `title` (String) - Video title
- `url` (String, Unique) - YouTube URL
- `duration` (Float) - Duration in seconds
- `transcript_path` (String) - Path to transcript file
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### `chunks`
- `id` (Integer, PK) - Auto-increment ID
- `video_id` (String, FK → videos.id) - Video reference
- `start_time` (Float) - Start time in seconds
- `end_time` (Float) - End time in seconds
- `text` (Text) - Chunk text content
- `qdrant_id` (String, Unique) - Qdrant point ID
- `created_at` (DateTime)

#### `chat_sessions`
- `id` (String, PK) - UUID
- `user_id` (String) - User identifier
- `task_type` (String) - qa, video_summary, quiz
- `title` (String) - Session title
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### `chat_messages`
- `id` (Integer, PK) - Auto-increment ID
- `session_id` (String, FK → chat_sessions.id) - Session reference
- `role` (String) - user, assistant
- `content` (Text) - Message content
- `sources` (JSON) - Source citations
- `created_at` (DateTime)

#### `quiz_questions`
- `id` (Integer, PK) - Auto-increment ID
- `session_id` (String) - Quiz session ID
- `video_id` (String, FK → videos.id) - Video reference
- `question_type` (String) - mcq, yes_no
- `question` (Text) - Question text
- `options` (JSON) - MCQ options
- `correct_answer` (String) - Correct answer
- `explanation` (Text) - Answer explanation
- `created_at` (DateTime)

### Qdrant Collection

**Collection Name**: `youtubelm_transcripts`

**Vector Configuration**:
- Dimension: 384 (sentence-transformers/all-MiniLM-L6-v2)
- Distance: Cosine

**Payload Schema**:
- `video_id` (String) - Video ID
- `video_title` (String) - Video title
- `video_url` (String) - Video URL
- `start_time` (Float) - Start time
- `end_time` (Float) - End time
- `text` (String) - Chunk text

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
docker-compose ps qdrant

# Check logs
docker-compose logs qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### Migration Issues

```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Rollback last migration (if needed)
alembic downgrade -1

# Re-run migrations
alembic upgrade head
```

### Reset Databases (Development Only)

⚠️ **Warning**: This will delete all data!

```bash
# Stop services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Restart services
docker-compose up -d

# Re-run migrations
cd backend
alembic upgrade head
```

## Data Persistence

Database data is persisted in local directories:
- PostgreSQL: `./postgres_data/`
- Qdrant: `./qdrant_data/`

These directories are mounted as Docker volumes and persist data between container restarts.

## Next Steps

After setting up the databases:

1. **Test the ingestion pipeline**: See `scripts/test_ingestion.py`
2. **Ingest your first video**: Use the `/api/ingestion/video` endpoint
3. **Verify data**: Check that videos and chunks are stored correctly

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

