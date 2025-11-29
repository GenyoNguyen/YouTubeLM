"""Unit tests for VideoSummaryService."""
import pytest
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Set test environment variables before importing the service
os.environ["MAX_TRANSCRIPT_CHUNKS"] = "100"
os.environ["ENABLE_SUMMARY_CACHE"] = "true"

# Import service AFTER conftest has set up the mock modules
from app.core.video_summary.service import VideoSummaryService


class TestVideoSummaryServiceHelpers:
    """Tests for helper methods (synchronous, no external dependencies)."""
    
    @pytest.fixture
    def service(self, mock_retriever, mock_llm_client, mock_postgres):
        """Create service instance with mocked dependencies."""
        return VideoSummaryService(
            retriever=mock_retriever,
            llm_client=mock_llm_client,
            postgres=mock_postgres
        )
    
    # =========================================================================
    # Tests for _extract_video_info
    # =========================================================================
    
    @pytest.mark.unit
    def test_extract_video_info_basic(self, service, sample_chunks):
        """Test basic video info extraction."""
        result = service._extract_video_info(sample_chunks)
        
        assert result["video_id"] == "abc123"
        assert result["title"] == "CS431 - Chương 1: Giới thiệu Deep Learning"
        assert result["chapter"] == "Chương 1"
        assert result["video_url"] == "https://youtube.com/watch?v=abc123"
        assert result["num_chunks"] == 3
    
    @pytest.mark.unit
    def test_extract_video_info_duration_calculation(self, service, sample_chunks):
        """Test duration is calculated correctly from first and last chunk."""
        result = service._extract_video_info(sample_chunks)
        
        # First chunk: start_time=0, Last chunk: end_time=90
        assert result["duration_seconds"] == 90
        assert result["duration"] == "01:30"
    
    @pytest.mark.unit
    def test_extract_video_info_empty_chunks(self, service):
        """Test handling of empty chunk list."""
        result = service._extract_video_info([])
        assert result == {}
    
    @pytest.mark.unit
    def test_extract_video_info_single_chunk(self, service, sample_chunk):
        """Test extraction from single chunk."""
        result = service._extract_video_info([sample_chunk])
        
        assert result["video_id"] == "abc123"
        assert result["num_chunks"] == 1
        assert result["duration_seconds"] == 30  # end_time - start_time
    
    @pytest.mark.unit
    def test_extract_video_info_missing_metadata(self, service):
        """Test handling of chunks with missing metadata fields."""
        chunks = [
            {"id": "chunk_001", "metadata": {}},
            {"id": "chunk_002", "metadata": {"end_time": 60}}
        ]
        result = service._extract_video_info(chunks)
        
        assert result["video_id"] == ""
        assert result["title"] == "Unknown"
        assert result["chapter"] == ""
    
    @pytest.mark.unit
    def test_extract_video_info_negative_duration(self, service):
        """Test handling when end_time < start_time (edge case)."""
        chunks = [
            {"id": "1", "metadata": {"start_time": 100, "end_time": 50}}
        ]
        result = service._extract_video_info(chunks)
        
        # Should handle gracefully (duration = 0)
        assert result["duration_seconds"] == 0
    
    # =========================================================================
    # Tests for _build_transcript
    # =========================================================================
    
    @pytest.mark.unit
    def test_build_transcript_basic(self, service, sample_chunks):
        """Test basic transcript building."""
        result = service._build_transcript(sample_chunks)
        
        # Check all chunks are included
        assert "Xin chào các bạn" in result
        assert "Deep Learning là một nhánh" in result
        assert "Neural Networks là thành phần" in result
    
    @pytest.mark.unit
    def test_build_transcript_has_timestamps(self, service, sample_chunks):
        """Test transcript includes formatted timestamps."""
        result = service._build_transcript(sample_chunks)
        
        assert "[00:00]" in result
        assert "[00:30]" in result
        assert "[01:00]" in result
    
    @pytest.mark.unit
    def test_build_transcript_sorts_by_time(self, service, sample_unordered_chunks):
        """Test chunks are sorted by start_time regardless of input order."""
        result = service._build_transcript(sample_unordered_chunks)
        
        # Find positions of each segment in the transcript
        pos_first = result.find("First segment")
        pos_second = result.find("Second segment")
        pos_third = result.find("Third segment")
        
        # Verify correct ordering
        assert pos_first < pos_second < pos_third
    
    @pytest.mark.unit
    def test_build_transcript_empty_chunks(self, service):
        """Test handling of empty chunk list."""
        result = service._build_transcript([])
        assert result == ""
    
    @pytest.mark.unit
    def test_build_transcript_long_duration(self, service):
        """Test timestamp formatting for videos longer than 1 hour."""
        chunks = [
            {
                "id": "chunk_001",
                "metadata": {
                    "start_time": 3665,  # 1:01:05
                    "text": "This is after one hour."
                }
            }
        ]
        result = service._build_transcript(chunks)
        
        # Should format as [61:05] (minutes:seconds)
        assert "[61:05]" in result
    
    @pytest.mark.unit
    def test_build_transcript_with_empty_text(self, service):
        """Test handling chunks with empty text."""
        chunks = [
            {"id": "1", "metadata": {"start_time": 0, "text": ""}},
            {"id": "2", "metadata": {"start_time": 30, "text": "Valid text"}}
        ]
        result = service._build_transcript(chunks)
        
        # Should include both, even with empty text
        assert "[00:00]" in result
        assert "Valid text" in result
    
    # =========================================================================
    # Tests for _group_chunks_by_video
    # =========================================================================
    
    @pytest.mark.unit
    def test_group_chunks_by_video_basic(self, service, sample_chunks_multiple_videos):
        """Test grouping chunks by video_id."""
        result = service._group_chunks_by_video(sample_chunks_multiple_videos)
        
        assert len(result) == 2
        assert "video_1" in result
        assert "video_2" in result
        assert len(result["video_1"]) == 2
        assert len(result["video_2"]) == 2
    
    @pytest.mark.unit
    def test_group_chunks_by_video_sorts_within_groups(self, service):
        """Test chunks within each video are sorted by time."""
        chunks = [
            {"id": "2", "metadata": {"video_id": "v1", "start_time": 60}},
            {"id": "1", "metadata": {"video_id": "v1", "start_time": 0}},
            {"id": "3", "metadata": {"video_id": "v1", "start_time": 30}}
        ]
        result = service._group_chunks_by_video(chunks)
        
        # Check sorted order within video
        times = [c["metadata"]["start_time"] for c in result["v1"]]
        assert times == [0, 30, 60]
    
    @pytest.mark.unit
    def test_group_chunks_by_video_empty(self, service):
        """Test handling of empty chunk list."""
        result = service._group_chunks_by_video([])
        assert result == {}
    
    @pytest.mark.unit
    def test_group_chunks_by_video_missing_video_id(self, service):
        """Test chunks with missing video_id are grouped as 'unknown'."""
        chunks = [
            {"id": "1", "metadata": {}},
            {"id": "2", "metadata": {"start_time": 30}}
        ]
        result = service._group_chunks_by_video(chunks)
        
        assert "unknown" in result
        assert len(result["unknown"]) == 2
    
    # =========================================================================
    # Tests for _format_videos_content
    # =========================================================================
    
    @pytest.mark.unit
    def test_format_videos_content_basic(self, service, sample_chunks_multiple_videos):
        """Test formatting grouped videos for prompt."""
        grouped = service._group_chunks_by_video(sample_chunks_multiple_videos)
        result = service._format_videos_content(grouped)
        
        # Should contain video titles
        assert "CS431 - Bài 1.1" in result
        assert "CS431 - Bài 1.2" in result
        
        # Should contain separators
        assert "---" in result
        
        # Should contain duration
        assert "Thời lượng" in result
    
    @pytest.mark.unit
    def test_format_videos_content_truncates_long_transcripts(self, service):
        """Test that long transcripts are truncated."""
        # Create a chunk with very long text
        long_text = "A" * 3000
        chunks = [
            {
                "id": "1",
                "metadata": {
                    "video_id": "v1",
                    "video_title": "Long Video",
                    "start_time": 0,
                    "end_time": 30,
                    "text": long_text
                }
            }
        ]
        grouped = service._group_chunks_by_video(chunks)
        result = service._format_videos_content(grouped)
        
        # Should be truncated (2000 chars + "...")
        assert len(result) < len(long_text)
        assert "..." in result
    
    @pytest.mark.unit
    def test_format_videos_content_empty_groups(self, service):
        """Test handling of empty video groups."""
        result = service._format_videos_content({})
        assert result == ""
    
    @pytest.mark.unit
    def test_format_videos_content_skips_empty_chunk_lists(self, service):
        """Test that videos with no chunks are skipped."""
        grouped = {"video_1": [], "video_2": [{"id": "1", "metadata": {
            "video_id": "video_2",
            "video_title": "Valid Video",
            "start_time": 0,
            "end_time": 30,
            "text": "Content"
        }}]}
        result = service._format_videos_content(grouped)
        
        assert "Valid Video" in result


class TestVideoSummaryServiceAsync:
    """Tests for async methods with mocked dependencies."""
    
    @pytest.fixture
    def service(self, mock_retriever, mock_llm_client, mock_postgres):
        """Create service instance with mocked dependencies."""
        return VideoSummaryService(
            retriever=mock_retriever,
            llm_client=mock_llm_client,
            postgres=mock_postgres
        )
    
    # =========================================================================
    # Tests for summarize_video
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_summarize_video_success(self, service, sample_chunks, mock_retriever):
        """Test successful video summarization flow."""
        mock_retriever.retrieve_by_video = AsyncMock(return_value=sample_chunks)
        
        events = []
        async for event in service.summarize_video(video_id="abc123"):
            events.append(event)
        
        # Should have metadata, tokens, and done events
        event_types = [e["type"] for e in events]
        assert "metadata" in event_types
        assert "token" in event_types
        assert "done" in event_types
    
    @pytest.mark.asyncio
    async def test_summarize_video_no_chunks_found(self, service, mock_retriever):
        """Test handling when no chunks are found for video."""
        mock_retriever.retrieve_by_video = AsyncMock(return_value=[])
        
        events = []
        async for event in service.summarize_video(video_id="nonexistent"):
            events.append(event)
        
        assert len(events) == 1
        assert events[0]["type"] == "error"
        assert "Không tìm thấy video" in events[0]["content"]
    
    @pytest.mark.asyncio
    async def test_summarize_video_returns_cached(
        self, mock_retriever, mock_llm_client, mock_postgres_with_cached_summary
    ):
        """Test that cached summary is returned when available."""
        service = VideoSummaryService(
            retriever=mock_retriever,
            llm_client=mock_llm_client,
            postgres=mock_postgres_with_cached_summary
        )
        service.enable_caching = True
    
        events = []
        async for event in service.summarize_video(video_id="cached_video"):
            events.append(event)
    
        assert len(events) == 1
        assert events[0]["type"] == "cached"
        assert events[0]["content"] == "Cached summary content"
    
    @pytest.mark.asyncio
    async def test_summarize_video_force_regenerate_ignores_cache(
        self, mock_retriever, mock_llm_client, mock_postgres_with_cached_summary, sample_chunks
    ):
        """Test force_regenerate bypasses cache."""
        mock_retriever.retrieve_by_video = AsyncMock(return_value=sample_chunks)
        
        service = VideoSummaryService(
            retriever=mock_retriever,
            llm_client=mock_llm_client,
            postgres=mock_postgres_with_cached_summary
        )
    
        events = []
        async for event in service.summarize_video(
            video_id="cached_video",
            force_regenerate=True
        ):
            events.append(event)
    
        # Should not return cached, should have metadata and streaming events
        event_types = [e["type"] for e in events]
        assert "cached" not in event_types
        assert "metadata" in event_types
    
    @pytest.mark.asyncio
    async def test_summarize_video_quick_summary_type(self, service, sample_chunks, mock_retriever):
        """Test quick summary uses correct prompt template."""
        mock_retriever.retrieve_by_video = AsyncMock(return_value=sample_chunks)
        
        events = []
        async for event in service.summarize_video(
            video_id="abc123",
            summary_type="quick"
        ):
            events.append(event)
        
        # Should complete successfully
        assert any(e["type"] == "done" for e in events)
    
    @pytest.mark.asyncio
    async def test_summarize_video_metadata_event_first(self, service, sample_chunks, mock_retriever):
        """Test that metadata event is yielded before tokens."""
        mock_retriever.retrieve_by_video = AsyncMock(return_value=sample_chunks)
        
        events = []
        async for event in service.summarize_video(video_id="abc123"):
            events.append(event)
        
        # Find indices
        metadata_idx = next(i for i, e in enumerate(events) if e["type"] == "metadata")
        token_idx = next(i for i, e in enumerate(events) if e["type"] == "token")
        
        assert metadata_idx < token_idx
    
    @pytest.mark.asyncio
    async def test_summarize_video_done_contains_session_id(self, service, sample_chunks, mock_retriever):
        """Test done event contains session_id."""
        mock_retriever.retrieve_by_video = AsyncMock(return_value=sample_chunks)
        
        events = []
        async for event in service.summarize_video(video_id="abc123"):
            events.append(event)
        
        done_event = next(e for e in events if e["type"] == "done")
        assert "session_id" in done_event
        assert done_event["session_id"] is not None
    
    # =========================================================================
    # Tests for summarize_chapter
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_summarize_chapter_success(
        self, service, sample_chunks_multiple_videos, mock_retriever
    ):
        """Test successful chapter summarization."""
        mock_retriever.retrieve_by_chapter = AsyncMock(return_value=sample_chunks_multiple_videos)
        
        events = []
        async for event in service.summarize_chapter(chapter="Chương 1"):
            events.append(event)
        
        event_types = [e["type"] for e in events]
        assert "metadata" in event_types
        assert "done" in event_types
    
    @pytest.mark.asyncio
    async def test_summarize_chapter_no_chunks_found(self, service, mock_retriever):
        """Test handling when no chunks found for chapter."""
        mock_retriever.retrieve_by_chapter = AsyncMock(return_value=[])
        
        events = []
        async for event in service.summarize_chapter(chapter="Nonexistent"):
            events.append(event)
        
        assert len(events) == 1
        assert events[0]["type"] == "error"
        assert "Không tìm thấy chapter" in events[0]["content"]
    
    @pytest.mark.asyncio
    async def test_summarize_chapter_metadata_includes_num_videos(
        self, service, sample_chunks_multiple_videos, mock_retriever
    ):
        """Test chapter metadata includes number of videos."""
        mock_retriever.retrieve_by_chapter = AsyncMock(return_value=sample_chunks_multiple_videos)
        
        events = []
        async for event in service.summarize_chapter(chapter="Chương 1"):
            events.append(event)
        
        metadata_event = next(e for e in events if e["type"] == "metadata")
        assert metadata_event["num_videos"] == 2  # video_1 and video_2
    
    # =========================================================================
    # Tests for list_videos and list_chapters
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_list_videos(self, service, mock_retriever):
        """Test listing videos."""
        expected_videos = [
            {"video_id": "v1", "title": "Video 1"},
            {"video_id": "v2", "title": "Video 2"}
        ]
        mock_retriever.list_videos = AsyncMock(return_value=expected_videos)
        
        result = await service.list_videos()
        
        assert result == expected_videos
        mock_retriever.list_videos.assert_called_once_with(chapter_filter=None)
    
    @pytest.mark.asyncio
    async def test_list_videos_with_chapter_filter(self, service, mock_retriever):
        """Test listing videos with chapter filter."""
        mock_retriever.list_videos = AsyncMock(return_value=[])
        
        await service.list_videos(chapter="Chương 1")
        
        mock_retriever.list_videos.assert_called_once_with(chapter_filter="Chương 1")
    
    @pytest.mark.asyncio
    async def test_list_chapters(self, service, mock_retriever):
        """Test listing chapters."""
        expected_chapters = [
            {"name": "Chương 1", "video_count": 5},
            {"name": "Chương 2", "video_count": 3}
        ]
        mock_retriever.list_chapters = AsyncMock(return_value=expected_chapters)
        
        result = await service.list_chapters()
        
        assert result == expected_chapters


class TestVideoSummaryServiceConfig:
    """Tests for service configuration."""
    
    @pytest.mark.unit
    def test_service_config_from_env(self, mock_retriever, mock_llm_client, mock_postgres):
        """Test service loads configuration from environment."""
        with patch.dict(os.environ, {
            "MAX_TRANSCRIPT_CHUNKS": "50",
            "ENABLE_SUMMARY_CACHE": "false"
        }):
            service = VideoSummaryService(
                retriever=mock_retriever,
                llm_client=mock_llm_client,
                postgres=mock_postgres
            )
        
            assert service.max_transcript_chunks == 50
            assert service.enable_caching is False
    
    @pytest.mark.unit
    def test_service_default_config(self, mock_retriever, mock_llm_client, mock_postgres):
        """Test service uses default configuration."""
        # Clear env vars to test defaults
        with patch.dict(os.environ, {}, clear=True):
            service = VideoSummaryService(
                retriever=mock_retriever,
                llm_client=mock_llm_client,
                postgres=mock_postgres
            )
        
            assert service.max_transcript_chunks == 200
            assert service.enable_caching is True


class TestVideoSummaryServiceSingleton:
    """Tests for singleton pattern."""
    
    def test_get_video_summary_service_returns_singleton(
        self, mock_retriever, mock_llm_client, mock_postgres
    ):
        """Test that get_video_summary_service returns same instance."""
        import app.core.video_summary.service as service_module
        
        # Reset singleton
        service_module._video_summary_service = None
        
        # Patch the dependency getters
        with patch.object(service_module, 'get_rag_retriever', return_value=mock_retriever), \
             patch.object(service_module, 'get_llm_client', return_value=mock_llm_client), \
             patch.object(service_module, 'get_postgres_client', return_value=mock_postgres):
            
            service1 = service_module.get_video_summary_service()
            service2 = service_module.get_video_summary_service()
            
            assert service1 is service2
