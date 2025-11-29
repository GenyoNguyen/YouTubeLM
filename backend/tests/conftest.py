"""Pytest configuration and fixtures for backend tests."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from contextlib import contextmanager

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# ============================================================================
# Mock Classes for Shared Modules (so we don't modify them)
# ============================================================================

class MockRAGRetriever:
    """Mock RAG Retriever."""
    async def retrieve(self, query, top_k=5, chapter_filter=None, use_bm25=True):
        return []
    
    async def retrieve_by_video(self, video_id, max_chunks=200):
        return []
    
    async def retrieve_by_chapter(self, chapter, max_chunks=600):
        return []
    
    async def list_videos(self, chapter_filter=None):
        return []
    
    async def list_chapters(self):
        return []


class MockLLMClient:
    """Mock LLM Client."""
    async def stream(self, prompt, system_prompt=None, **kwargs):
        yield {"type": "done"}
    
    async def stream_with_sources(self, prompt, system_prompt=None, sources=None, **kwargs):
        yield {"type": "done", "sources": sources or []}


class MockPostgresClient:
    """Mock Postgres Client."""
    @contextmanager
    def session_scope(self):
        yield MagicMock()


class MockChatSession:
    """Mock ChatSession model."""
    def __init__(self, id=None, task_type=None, title=None, user_id=None, **kwargs):
        self.id = id
        self.task_type = task_type
        self.title = title
        self.user_id = user_id
        self.created_at = None
        self.updated_at = None


class MockChatMessage:
    """Mock ChatMessage model."""
    def __init__(self, id=None, session_id=None, role=None, content=None, sources=None, **kwargs):
        self.id = id
        self.session_id = session_id
        self.role = role
        self.content = content
        self.sources = sources or []


class MockVideoSummary:
    """Mock VideoSummary model."""
    def __init__(self, id=None, video_id=None, video_info=None, content=None, summary_type=None, **kwargs):
        self.id = id
        self.video_id = video_id
        self.video_info = video_info
        self.content = content
        self.summary_type = summary_type


# ============================================================================
# Setup Mock Modules BEFORE importing the service
# ============================================================================

# Create mock modules
mock_retriever_module = MagicMock()
mock_retriever_module.RAGRetriever = MockRAGRetriever
mock_retriever_module.get_rag_retriever = lambda: MockRAGRetriever()

mock_llm_module = MagicMock()
mock_llm_module.LLMClient = MockLLMClient
mock_llm_module.get_llm_client = lambda: MockLLMClient()

mock_postgres_module = MagicMock()
mock_postgres_module.PostgresClient = MockPostgresClient
mock_postgres_module.get_postgres_client = lambda: MockPostgresClient()

mock_models_module = MagicMock()
mock_models_module.ChatSession = MockChatSession
mock_models_module.ChatMessage = MockChatMessage
mock_models_module.VideoSummary = MockVideoSummary

# Inject mocks into sys.modules
sys.modules['app.shared.rag.retriever'] = mock_retriever_module
sys.modules['app.shared.llm.client'] = mock_llm_module
sys.modules['app.shared.database.postgres'] = mock_postgres_module
sys.modules['app.shared.database.models'] = mock_models_module


# ============================================================================
# Pytest Imports (after mock setup)
# ============================================================================
import pytest


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_chunk():
    """Single sample chunk with metadata."""
    return {
        "id": "chunk_001",
        "metadata": {
            "video_id": "abc123",
            "video_title": "CS431 - Chương 1: Giới thiệu Deep Learning",
            "chapter": "Chương 1",
            "video_url": "https://youtube.com/watch?v=abc123",
            "start_time": 0,
            "end_time": 30,
            "text": "Xin chào các bạn, hôm nay chúng ta sẽ học về Deep Learning."
        },
        "score": 0.95
    }


@pytest.fixture
def sample_chunks():
    """List of sample chunks for a video."""
    return [
        {
            "id": "chunk_001",
            "metadata": {
                "video_id": "abc123",
                "video_title": "CS431 - Chương 1: Giới thiệu Deep Learning",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=abc123",
                "start_time": 0,
                "end_time": 30,
                "text": "Xin chào các bạn, hôm nay chúng ta sẽ học về Deep Learning."
            },
            "score": 0.95
        },
        {
            "id": "chunk_002",
            "metadata": {
                "video_id": "abc123",
                "video_title": "CS431 - Chương 1: Giới thiệu Deep Learning",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=abc123",
                "start_time": 30,
                "end_time": 60,
                "text": "Deep Learning là một nhánh của Machine Learning."
            },
            "score": 0.90
        },
        {
            "id": "chunk_003",
            "metadata": {
                "video_id": "abc123",
                "video_title": "CS431 - Chương 1: Giới thiệu Deep Learning",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=abc123",
                "start_time": 60,
                "end_time": 90,
                "text": "Neural Networks là thành phần cốt lõi của Deep Learning."
            },
            "score": 0.85
        }
    ]


@pytest.fixture
def sample_chunks_multiple_videos():
    """Chunks from multiple videos for chapter testing."""
    return [
        {
            "id": "chunk_001",
            "metadata": {
                "video_id": "video_1",
                "video_title": "CS431 - Bài 1.1",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=video_1",
                "start_time": 0,
                "end_time": 30,
                "text": "Nội dung video 1 phần 1."
            }
        },
        {
            "id": "chunk_002",
            "metadata": {
                "video_id": "video_1",
                "video_title": "CS431 - Bài 1.1",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=video_1",
                "start_time": 30,
                "end_time": 60,
                "text": "Nội dung video 1 phần 2."
            }
        },
        {
            "id": "chunk_003",
            "metadata": {
                "video_id": "video_2",
                "video_title": "CS431 - Bài 1.2",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=video_2",
                "start_time": 0,
                "end_time": 45,
                "text": "Nội dung video 2 phần 1."
            }
        },
        {
            "id": "chunk_004",
            "metadata": {
                "video_id": "video_2",
                "video_title": "CS431 - Bài 1.2",
                "chapter": "Chương 1",
                "video_url": "https://youtube.com/watch?v=video_2",
                "start_time": 45,
                "end_time": 90,
                "text": "Nội dung video 2 phần 2."
            }
        }
    ]


@pytest.fixture
def sample_unordered_chunks():
    """Chunks in non-chronological order to test sorting."""
    return [
        {
            "id": "chunk_003",
            "metadata": {
                "video_id": "abc123",
                "video_title": "Test Video",
                "chapter": "Chapter 1",
                "start_time": 120,
                "end_time": 150,
                "text": "Third segment of the video."
            }
        },
        {
            "id": "chunk_001",
            "metadata": {
                "video_id": "abc123",
                "video_title": "Test Video",
                "chapter": "Chapter 1",
                "start_time": 0,
                "end_time": 30,
                "text": "First segment of the video."
            }
        },
        {
            "id": "chunk_002",
            "metadata": {
                "video_id": "abc123",
                "video_title": "Test Video",
                "chapter": "Chapter 1",
                "start_time": 60,
                "end_time": 90,
                "text": "Second segment of the video."
            }
        }
    ]


# ============================================================================
# Mock Fixtures for Tests
# ============================================================================

@pytest.fixture
def mock_retriever():
    """Mock RAG retriever with configurable async methods."""
    retriever = MagicMock()
    retriever.retrieve_by_video = AsyncMock(return_value=[])
    retriever.retrieve_by_chapter = AsyncMock(return_value=[])
    retriever.list_videos = AsyncMock(return_value=[])
    retriever.list_chapters = AsyncMock(return_value=[])
    return retriever


@pytest.fixture
def mock_llm_client():
    """Mock LLM client with streaming support."""
    client = MagicMock()
    
    async def mock_stream(*args, **kwargs):
        """Mock streaming response."""
        yield {"type": "token", "content": "This is "}
        yield {"type": "token", "content": "a test "}
        yield {"type": "token", "content": "summary."}
        yield {"type": "done"}
    
    client.stream = mock_stream
    return client


@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL client."""
    postgres = MagicMock()
    
    # Create a mock session context manager
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    
    @contextmanager
    def mock_session_scope():
        yield mock_session
    
    postgres.session_scope = mock_session_scope
    return postgres


@pytest.fixture
def mock_postgres_with_cached_summary():
    """Mock PostgreSQL client that returns a cached summary."""
    postgres = MagicMock()
    
    # Create a mock cached summary
    mock_cached = MagicMock()
    mock_cached.content = "Cached summary content"
    mock_cached.video_info = {"title": "Cached Video", "chapter": "Chapter 1"}
    
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_cached
    
    @contextmanager
    def mock_session_scope():
        yield mock_session
    
    postgres.session_scope = mock_session_scope
    return postgres


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
