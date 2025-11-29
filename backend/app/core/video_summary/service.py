"""Video summarization service - orchestration logic."""
import os
import uuid
from typing import AsyncGenerator, Dict, Any, List, Optional
from datetime import datetime

from ...shared.rag.retriever import RAGRetriever, get_rag_retriever
from ...shared.llm.client import LLMClient, get_llm_client
from ...shared.database.postgres import PostgresClient, get_postgres_client
from ...models import ChatSession, ChatMessage

from .prompts import (
    VIDEO_SUMMARY_SYSTEM_PROMPT,
    VIDEO_SUMMARY_USER_PROMPT_TEMPLATE,
    CHAPTER_SUMMARY_USER_PROMPT_TEMPLATE,
    QUICK_SUMMARY_USER_PROMPT_TEMPLATE
)


class VideoSummaryService:
    """
    Service for video summarization.
    
    Pipeline:
    1. Retrieve all chunks for a video (ordered by timestamp)
    2. Build transcript from chunks
    3. Generate summary with LLM
    4. Stream response and save to database
    """
    
    def __init__(
        self,
        retriever: RAGRetriever = None,
        llm_client: LLMClient = None,
        postgres: PostgresClient = None
    ):
        self.retriever = retriever or get_rag_retriever()
        self.llm = llm_client or get_llm_client()
        self.postgres = postgres or get_postgres_client()
        
        # Load configuration
        self.max_transcript_chunks = int(os.getenv("MAX_TRANSCRIPT_CHUNKS", "200"))
        self.enable_caching = os.getenv("ENABLE_SUMMARY_CACHE", "true").lower() == "true"
    
    async def summarize_video(
        self,
        video_id: str,
        summary_type: str = "detailed",
        session_id: Optional[str] = None,
        force_regenerate: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate summary for a specific video.
        
        Args:
            video_id: YouTube video ID
            summary_type: Type of summary ("detailed", "quick")
            session_id: Optional existing session ID
            force_regenerate: Force regeneration even if cached
        
        Yields:
            Dict events for SSE:
            - {"type": "token", "content": str}
            - {"type": "metadata", "video_info": dict}
            - {"type": "done", "content": str, "video_id": str, "session_id": str}
        """
        # Step 0: Check cache if enabled
        if self.enable_caching and not force_regenerate:
            cached_summary = await self._get_cached_summary(video_id, summary_type)
            if cached_summary:
                yield {
                    "type": "cached",
                    "content": cached_summary["content"],
                    "video_id": video_id,
                    "video_info": cached_summary.get("video_info", {})
                }
                return
        
        # Step 1: Create or get session
        created_session_id = await self._create_or_get_session(
            session_id=session_id,
            video_id=video_id
        )
        
        # Step 2: Retrieve all chunks for the video
        print(f"📚 Retrieving chunks for video: {video_id}...")
        video_chunks = await self.retriever.retrieve_by_video(
            video_id=video_id,
            max_chunks=self.max_transcript_chunks
        )
        print(f"✅ Retrieved {len(video_chunks)} chunks")
        
        if not video_chunks:
            yield {
                "type": "error",
                "content": f"Không tìm thấy video với ID: {video_id}"
            }
            return
        
        # Step 3: Extract video info and build transcript
        video_info = self._extract_video_info(video_chunks)
        transcript = self._build_transcript(video_chunks)
        
        # Yield video metadata first
        yield {
            "type": "metadata",
            "video_info": video_info
        }
        
        # Step 4: Build prompt based on summary type
        if summary_type == "quick":
            prompt = QUICK_SUMMARY_USER_PROMPT_TEMPLATE.format(
                video_title=video_info["title"],
                transcript=transcript
            )
        else:
            # For detailed summary, use sources format
            prompt = VIDEO_SUMMARY_USER_PROMPT_TEMPLATE.format(
                video_title=video_info["title"],
                duration=video_info["duration"],
                sources=transcript  # Use transcript as sources
            )
        
        # Step 5: Stream LLM response
        print("🤖 Generating video summary with LLM...")
        full_response = ""
        async for event in self.llm.stream(
            prompt=prompt,
            system_prompt=VIDEO_SUMMARY_SYSTEM_PROMPT
        ):
            if event["type"] == "token":
                full_response += event["content"]
                yield event
            elif event["type"] == "done":
                yield {
                    "type": "done",
                    "content": full_response,
                    "video_id": video_id,
                    "video_info": video_info,
                    "session_id": created_session_id
                }
        
        # Step 6: Save to database and cache
        await self._save_summary(
            video_id=video_id,
            video_info=video_info,
            summary=full_response,
            summary_type=summary_type,
            session_id=created_session_id
        )
        
        print("✅ Video summary generated and saved")
    
    async def summarize_chapter(
        self,
        chapter: str,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate summary for all videos in a chapter.
        
        Args:
            chapter: Chapter name/identifier
            session_id: Optional existing session ID
        
        Yields:
            SSE events
        """
        # Step 1: Create session
        created_session_id = await self._create_or_get_session(
            session_id=session_id,
            chapter=chapter
        )
        
        # Step 2: Retrieve all chunks for the chapter
        print(f"📚 Retrieving chunks for chapter: {chapter}...")
        chapter_chunks = await self.retriever.retrieve_by_chapter(
            chapter=chapter,
            max_chunks=self.max_transcript_chunks * 3  # More chunks for chapter
        )
        print(f"✅ Retrieved {len(chapter_chunks)} chunks")
        
        if not chapter_chunks:
            yield {
                "type": "error",
                "content": f"Không tìm thấy chapter: {chapter}"
            }
            return
        
        # Step 3: Group chunks by video and build content
        videos_content = self._group_chunks_by_video(chapter_chunks)
        
        yield {
            "type": "metadata",
            "chapter": chapter,
            "num_videos": len(videos_content)
        }
        
        # Step 4: Build prompt
        formatted_videos = self._format_videos_content(videos_content)
        prompt = CHAPTER_SUMMARY_USER_PROMPT_TEMPLATE.format(
            chapter=chapter,
            num_videos=len(videos_content),
            videos_content=formatted_videos
        )
        
        # Step 5: Stream response
        print("🤖 Generating chapter summary with LLM...")
        full_response = ""
        async for event in self.llm.stream(
            prompt=prompt,
            system_prompt=VIDEO_SUMMARY_SYSTEM_PROMPT
        ):
            if event["type"] == "token":
                full_response += event["content"]
                yield event
            elif event["type"] == "done":
                yield {
                    "type": "done",
                    "content": full_response,
                    "chapter": chapter,
                    "session_id": created_session_id
                }
        
        # Step 6: Save to database
        await self._save_chapter_summary(
            chapter=chapter,
            summary=full_response,
            session_id=created_session_id
        )
        
        print("✅ Chapter summary generated and saved")
    
    async def list_videos(
        self,
        chapter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available videos, optionally filtered by chapter.
        
        Args:
            chapter: Optional chapter filter
        
        Returns:
            List of video info dicts
        """
        return await self.retriever.list_videos(chapter_filter=chapter)
    
    async def list_chapters(self) -> List[Dict[str, Any]]:
        """
        List all available chapters.
        
        Returns:
            List of chapter info dicts
        """
        return await self.retriever.list_chapters()
    
    def _extract_video_info(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract video metadata from chunks."""
        if not chunks:
            return {}
        
        first_chunk = chunks[0]
        last_chunk = chunks[-1]
        metadata = first_chunk.get("metadata", {})
        
        # Calculate duration from first and last chunk
        start_time = metadata.get("start_time", 0)
        end_time = last_chunk.get("metadata", {}).get("end_time", 0)
        duration_secs = end_time - start_time if end_time > start_time else 0
        
        # Format duration
        duration_min, duration_sec = divmod(duration_secs, 60)
        duration_str = f"{duration_min:02d}:{duration_sec:02d}"
        
        return {
            "video_id": metadata.get("video_id", ""),
            "title": metadata.get("video_title", "Unknown"),
            "video_url": metadata.get("video_url", ""),
            "duration": duration_str,
            "duration_seconds": duration_secs,
            "num_chunks": len(chunks)
        }
    
    def _build_transcript(self, chunks: List[Dict[str, Any]]) -> str:
        """Build ordered transcript from chunks."""
        # Sort chunks by start_time
        sorted_chunks = sorted(
            chunks,
            key=lambda x: x.get("metadata", {}).get("start_time", 0)
        )
        
        transcript_parts = []
        for chunk in sorted_chunks:
            metadata = chunk.get("metadata", {})
            start_time = metadata.get("start_time", 0)
            text = metadata.get("text", "")
            
            # Format timestamp
            start_min, start_sec = divmod(start_time, 60)
            timestamp = f"[{start_min:02d}:{start_sec:02d}]"
            
            transcript_parts.append(f"{timestamp} {text}")
        
        return "\n\n".join(transcript_parts)
    
    def _group_chunks_by_video(
        self,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group chunks by video_id."""
        videos = {}
        for chunk in chunks:
            video_id = chunk.get("metadata", {}).get("video_id", "unknown")
            if video_id not in videos:
                videos[video_id] = []
            videos[video_id].append(chunk)
        
        # Sort chunks within each video
        for video_id in videos:
            videos[video_id] = sorted(
                videos[video_id],
                key=lambda x: x.get("metadata", {}).get("start_time", 0)
            )
        
        return videos
    
    def _format_videos_content(
        self,
        videos: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Format grouped videos for chapter summary prompt."""
        formatted_parts = []
        
        for video_id, chunks in videos.items():
            if not chunks:
                continue
            
            video_info = self._extract_video_info(chunks)
            transcript = self._build_transcript(chunks)
            
            formatted_parts.append(
                f"## Video: {video_info['title']}\n"
                f"**Thời lượng**: {video_info['duration']}\n\n"
                f"{transcript[:2000]}..."  # Truncate for context limit
            )
        
        return "\n\n---\n\n".join(formatted_parts)
    
    async def _get_cached_summary(
        self,
        video_id: str,
        summary_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached summary from database if exists."""
        # TODO: Implement caching if needed
        # For now, return None to always regenerate
        return None
    
    async def _create_or_get_session(
        self,
        session_id: Optional[str],
        video_id: str = None,
        chapter: str = None
    ) -> str:
        """
        Create new session or validate existing one.
        
        Returns:
            session_id (str): ID of created or validated session
        """
        with self.postgres.session_scope() as session:
            if session_id:
                # Validate existing session
                chat_session = session.query(ChatSession).filter_by(id=session_id).first()
                if not chat_session:
                    raise ValueError(f"Session {session_id} not found")
                
                # Update timestamp
                chat_session.updated_at = datetime.utcnow()
                return chat_session.id
            else:
                # Create new session
                title = f"Video Summary: {video_id}" if video_id else f"Chapter Summary: {chapter}"
                new_session = ChatSession(
                    id=str(uuid.uuid4()),
                    task_type="video_summary",
                    title=title[:100],
                    user_id="default_user"
                )
                session.add(new_session)
                session.commit()
                return new_session.id
    
    async def _save_summary(
        self,
        video_id: str,
        video_info: Dict[str, Any],
        summary: str,
        summary_type: str,
        session_id: str
    ):
        """Save video summary to database."""
        from ...models import ChatMessage
        
        with self.postgres.session_scope() as session:
            # Save to chat messages for history
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="assistant",
                content=summary,
                sources=[{"video_id": video_id, **video_info}]
            )
            session.add(assistant_message)
    
    async def _save_chapter_summary(
        self,
        chapter: str,
        summary: str,
        session_id: str
    ):
        """Save chapter summary to database."""
        with self.postgres.session_scope() as session:
            # Save to chat messages
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="assistant",
                content=summary,
                sources=[{"chapter": chapter}]
            )
            session.add(assistant_message)


# Singleton instance
_video_summary_service = None


def get_video_summary_service() -> VideoSummaryService:
    """Get singleton video summary service."""
    global _video_summary_service
    if _video_summary_service is None:
        _video_summary_service = VideoSummaryService()
    return _video_summary_service
