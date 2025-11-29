# YouTubeLM API Documentation

This document describes all available API endpoints for the YouTubeLM application.

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: Available at `http://localhost:8000/docs`
- **ReDoc**: Available at `http://localhost:8000/redoc`
- **OpenAPI Schema**: Available at `http://localhost:8000/openapi.json`

These interactive docs allow you to test endpoints directly from your browser.

## Base URL

All endpoints are prefixed with `/api` unless otherwise specified.

**Default Server**: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Response Format

### SSE (Server-Sent Events) Streaming

Several endpoints use Server-Sent Events (SSE) for streaming responses. These endpoints return `text/event-stream` content type with events formatted as:

```
event: <event_type>
data: <json_data>

```

### Standard JSON Responses

Non-streaming endpoints return standard JSON responses.

### Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error
- `501` - Not Implemented

---

## Health Check

### GET `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Video Ingestion

### POST `/api/ingestion/video`

Ingest a YouTube video: download, transcribe, generate embeddings, and store in databases.

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "video_id": "VIDEO_ID",
  "title": "Video Title",
  "chunks_count": 150,
  "status": "completed"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/ingestion/video" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Notes:**
- This endpoint processes the video synchronously
- Processing time depends on video length
- The video must be publicly accessible on YouTube

---

## Q&A (Question & Answer)

### POST `/api/qa/ask`

Ask a question and get a streaming answer with sources.

**Request Body:**
```json
{
  "query": "What is deep learning?",
  "session_id": "optional-session-id",
  "chapters": ["optional", "chapter", "filters"]
}
```

**Response:** SSE Stream

**Events:**
- `token` - Streaming text tokens
  ```json
  {
    "type": "token",
    "content": "Deep learning is..."
  }
  ```
- `sources` - Source references
  ```json
  {
    "type": "sources",
    "sources": [
      {
        "index": 1,
        "video_id": "VIDEO_ID",
        "video_title": "Video Title",
        "video_url": "https://youtube.com/watch?v=VIDEO_ID",
        "start_time": 120.5,
        "end_time": 145.0,
        "text": "Relevant text excerpt...",
        "score": 0.95
      }
    ]
  }
  ```
- `done` - Completion event
  ```json
  {
    "type": "done",
    "content": "Full response text...",
    "sources": [...],
    "session_id": "session-id"
  }
  ```
- `error` - Error event
  ```json
  {
    "type": "error",
    "content": "Error message"
  }
  ```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is deep learning?"}' \
  --no-buffer
```

**JavaScript Example:**
```javascript
const eventSource = new EventSource('http://localhost:8000/api/qa/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'What is deep learning?' })
});

eventSource.addEventListener('token', (e) => {
  const data = JSON.parse(e.data);
  console.log('Token:', data.content);
});

eventSource.addEventListener('done', (e) => {
  const data = JSON.parse(e.data);
  console.log('Done:', data.content);
  eventSource.close();
});
```

### POST `/api/qa/followup`

Ask a followup question in an existing session.

**Request Body:**
```json
{
  "query": "Can you explain more about that?",
  "session_id": "required-session-id",
  "chapters": ["optional", "chapter", "filters"]
}
```

**Response:** SSE Stream (same format as `/ask`)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/qa/followup" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can you explain more?",
    "session_id": "session-id-here"
  }' \
  --no-buffer
```

### GET `/api/qa/history/{session_id}`

Get chat history for a session.

**Response:**
```json
{
  "session_id": "session-id",
  "messages": [
    {
      "id": "message-id",
      "role": "user",
      "content": "User question",
      "sources": null,
      "created_at": "2024-01-01T12:00:00"
    },
    {
      "id": "message-id",
      "role": "assistant",
      "content": "Assistant response",
      "sources": [...],
      "created_at": "2024-01-01T12:00:01"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/qa/history/session-id-here"
```

---

## Video Summary

### POST `/api/video-summary/summarize`

Generate a summary for a specific video with streaming response.

**Request Body:**
```json
{
  "video_id": "VIDEO_ID",
  "summary_type": "detailed",
  "session_id": "optional-session-id",
  "force_regenerate": false
}
```

**Parameters:**
- `video_id` (required): YouTube video ID
- `summary_type` (optional): `"detailed"` or `"quick"` (default: `"detailed"`)
- `session_id` (optional): Existing session ID
- `force_regenerate` (optional): Force regeneration even if cached (default: `false`)

**Response:** SSE Stream

**Events:**
- `metadata` - Video information
  ```json
  {
    "type": "metadata",
    "video_info": {
      "video_id": "VIDEO_ID",
      "title": "Video Title",
      "video_url": "https://youtube.com/watch?v=VIDEO_ID",
      "duration": "15:30",
      "duration_seconds": 930,
      "num_chunks": 150
    }
  }
  ```
- `token` - Streaming text tokens
  ```json
  {
    "type": "token",
    "content": "Summary text..."
  }
  ```
- `cached` - Cached summary (if available and not forced)
  ```json
  {
    "type": "cached",
    "content": "Cached summary...",
    "video_id": "VIDEO_ID",
    "video_info": {...}
  }
  ```
- `done` - Completion event
  ```json
  {
    "type": "done",
    "content": "Full summary...",
    "video_id": "VIDEO_ID",
    "video_info": {...},
    "session_id": "session-id"
  }
  ```
- `error` - Error event
  ```json
  {
    "type": "error",
    "content": "Error message"
  }
  ```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/video-summary/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "VIDEO_ID",
    "summary_type": "detailed"
  }' \
  --no-buffer
```

### GET `/api/video-summary/videos`

List available videos.

**Query Parameters:**
- `chapter` (optional): Filter by chapter name

**Response:**
```json
{
  "videos": [
    {
      "id": "VIDEO_ID",
      "title": "Video Title",
      "url": "https://youtube.com/watch?v=VIDEO_ID",
      "duration": 930
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/video-summary/videos"
curl "http://localhost:8000/api/video-summary/videos?chapter=Chapter1"
```

### GET `/api/video-summary/chapters`

List available chapters.

**Response:**
```json
{
  "chapters": [
    {
      "name": "Chapter1",
      "video_count": 5
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/video-summary/chapters"
```

---

## Quiz Generation

### POST `/api/quiz/generate`

Generate quiz questions for video(s) with streaming response.

**Request Body:**
```json
{
  "video_ids": ["VIDEO_ID1", "VIDEO_ID2"],
  "question_type": "multiple choice",
  "num_questions": 5
}
```

**Parameters:**
- `video_ids` (required): List of video IDs (at least one)
- `question_type` (optional): Type of questions (default: `"multiple choice"`)
- `num_questions` (optional): Number of questions (1-20, default: 5)

**Response:** SSE Stream

**Events:**
- `progress` - Progress updates
  ```json
  {
    "type": "progress",
    "message": "Retrieving content for 2 video(s)..."
  }
  ```
- `token` - Streaming text tokens
  ```json
  {
    "type": "token",
    "content": "Quiz generation text..."
  }
  ```
- `done` - Completion event with quiz data
  ```json
  {
    "type": "done",
    "quiz": {
      "questions": [
        {
          "id": 1,
          "question": "What is deep learning?",
          "type": "multiple_choice",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_answer": 0,
          "explanation": "Explanation text..."
        }
      ]
    },
    "quiz_id": "quiz-uuid"
  }
  ```
- `error` - Error event
  ```json
  {
    "type": "error",
    "content": "Error message"
  }
  ```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/quiz/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "video_ids": ["VIDEO_ID"],
    "question_type": "multiple choice",
    "num_questions": 5
  }' \
  --no-buffer
```

### GET `/api/quiz/{quiz_id}`

Retrieve generated quiz by ID.

**Status:** Not yet implemented (returns 501)

### POST `/api/quiz/validate`

Validate user answers for a quiz.

**Status:** Not yet implemented (returns 501)

---

## Session Management

### POST `/api/sessions/`

Create a new chat session.

**Request Body:**
```json
{
  "task_type": "qa",
  "title": "Optional session title",
  "user_id": "default_user"
}
```

**Parameters:**
- `task_type` (optional): `"qa"`, `"video_summary"`, or `"quiz"` (default: `"qa"`)
- `title` (optional): Session title
- `user_id` (optional): User ID (default: `"default_user"`)

**Response:**
```json
{
  "id": "session-uuid",
  "task_type": "qa",
  "title": "Session Title",
  "user_id": "default_user",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "message_count": 0
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "qa",
    "title": "My Q&A Session"
  }'
```

### GET `/api/sessions/{session_id}`

Get session details.

**Response:**
```json
{
  "id": "session-uuid",
  "task_type": "qa",
  "title": "Session Title",
  "user_id": "default_user",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:01",
  "message_count": 5
}
```

**Example:**
```bash
curl "http://localhost:8000/api/sessions/session-id-here"
```

### GET `/api/sessions/`

List sessions with optional filters.

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `task_type` (optional): Filter by task type
- `limit` (optional): Maximum number of results (default: 50)

**Response:**
```json
[
  {
    "id": "session-uuid",
    "task_type": "qa",
    "title": "Session Title",
    "user_id": "default_user",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:01",
    "message_count": 5
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/sessions/"
curl "http://localhost:8000/api/sessions/?user_id=user123&task_type=qa&limit=10"
```

### DELETE `/api/sessions/{session_id}`

Delete a session and all its messages.

**Response:**
```json
{
  "message": "Session deleted successfully",
  "session_id": "session-uuid"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/sessions/session-id-here"
```

---

## Environment Variables

The following environment variables can be configured:

```bash
# Database
POSTGRES_DB=youtubelm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Groq API
GROQ_API_KEY=your-groq-api-key

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

---

## Error Handling

All endpoints follow consistent error handling:

1. **400 Bad Request**: Invalid request parameters
   ```json
   {
     "detail": "num_questions must be between 1 and 20"
   }
   ```

2. **404 Not Found**: Resource not found
   ```json
   {
     "detail": "Session not found"
   }
   ```

3. **500 Internal Server Error**: Server-side error
   ```json
   {
     "detail": "Error processing question: ..."
   }
   ```

4. **501 Not Implemented**: Feature not yet implemented
   ```json
   {
     "detail": "Quiz storage and retrieval not yet implemented"
   }
   ```

---

## SSE Event Handling

When consuming SSE streams, handle events as follows:

```javascript
const eventSource = new EventSource(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestData)
});

// Handle token events
eventSource.addEventListener('token', (e) => {
  const data = JSON.parse(e.data);
  appendToUI(data.content);
});

// Handle sources
eventSource.addEventListener('sources', (e) => {
  const data = JSON.parse(e.data);
  displaySources(data.sources);
});

// Handle completion
eventSource.addEventListener('done', (e) => {
  const data = JSON.parse(e.data);
  finalizeResponse(data);
  eventSource.close();
});

// Handle errors
eventSource.addEventListener('error', (e) => {
  const data = JSON.parse(e.data);
  showError(data.content);
  eventSource.close();
});

// Handle generic message events
eventSource.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Event:', data);
};
```

---

## Rate Limiting

Currently, there are no rate limits implemented. This may change in future versions.

---

## CORS

CORS is configured to allow requests from the frontend. Update CORS settings in `main.py` if needed.

---

## Examples

### Complete Q&A Flow

```bash
# 1. Create a session
SESSION_ID=$(curl -X POST "http://localhost:8000/api/sessions/" \
  -H "Content-Type: application/json" \
  -d '{"task_type": "qa", "title": "My Q&A"}' \
  | jq -r '.id')

# 2. Ask a question
curl -X POST "http://localhost:8000/api/qa/ask" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is deep learning?\", \"session_id\": \"$SESSION_ID\"}" \
  --no-buffer

# 3. Ask a followup
curl -X POST "http://localhost:8000/api/qa/followup" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Can you explain more?\", \"session_id\": \"$SESSION_ID\"}" \
  --no-buffer

# 4. Get history
curl "http://localhost:8000/api/qa/history/$SESSION_ID"
```

### Video Summary Flow

```bash
# 1. Ingest a video (if not already ingested)
curl -X POST "http://localhost:8000/api/ingestion/video" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# 2. Generate summary
curl -X POST "http://localhost:8000/api/video-summary/summarize" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "VIDEO_ID", "summary_type": "detailed"}' \
  --no-buffer
```

---

## Support

For issues or questions, please refer to the project repository or contact the development team.

