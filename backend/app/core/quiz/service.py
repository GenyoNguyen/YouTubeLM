# Quiz generation service
import json
import os
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator
from ...shared.llm.client import LLMClient, get_llm_client
from ...shared.rag.retriever import RAGRetriever, get_rag_retriever
from .prompts import QUIZ_SYSTEM_PROMPT, QUIZ_USER_PROMPT

class QuizService:
    """Service for generating quizzes from video content."""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        retriever: Optional[RAGRetriever] = None
    ):
        """
        Initialize Quiz service.
        
        Args:
            llm_client: Optional LLM client instance (uses singleton if not provided)
            retriever: Optional RAG retriever instance
        """
        self.llm = llm_client or get_llm_client()
        self.retriever = retriever or get_rag_retriever()

    async def generate_quiz_stream(
        self,
        video_ids: list[str],
        question_type: str,
        num_questions: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate quiz questions for video(s) with streaming.
        
        Args:
            video_ids: List of video IDs to generate quiz for
            question_type: Type of questions (e.g., "multiple choice")
            num_questions: Number of questions to generate
        
        Yields:
            Dict events for SSE:
            - {"type": "progress", "message": str}
            - {"type": "token", "content": str}
            - {"type": "done", "quiz": dict, "quiz_id": str}
            - {"type": "error", "content": str}
        """
        quiz_id = str(uuid.uuid4())
        
        try:
            # Step 1: Fetch content
            yield {
                "type": "progress",
                "message": f"Retrieving content for {len(video_ids)} video(s)..."
            }
            content = await self._get_video_content(video_ids)
            
            # Step 2: Build prompt
            yield {
                "type": "progress",
                "message": "Building quiz prompt..."
            }
            prompt = QUIZ_USER_PROMPT.format(
                num_questions=num_questions,
                question_type=question_type,
                content=content
            )
            
            # Step 3: Stream LLM response
            yield {
                "type": "progress",
                "message": "Generating quiz questions..."
            }
            full_response = ""
            async for event in self.llm.stream(
                prompt=prompt,
                system_prompt=QUIZ_SYSTEM_PROMPT
            ):
                if event["type"] == "token":
                    full_response += event["content"]
                    yield event
                elif event["type"] == "done":
                    full_response = event["content"]
            
            # Step 4: Parse response
            yield {
                "type": "progress",
                "message": "Parsing quiz response..."
            }
            try:
                # Clean up response if it contains markdown code blocks
                cleaned_response = full_response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                quiz_data = json.loads(cleaned_response)
                
                # Yield done event with quiz data
                yield {
                    "type": "done",
                    "quiz": quiz_data,
                    "quiz_id": quiz_id
                }
            except (json.JSONDecodeError, AttributeError) as e:
                yield {
                    "type": "error",
                    "content": f"Failed to parse quiz response: {str(e)}",
                    "raw_response": full_response[:500]  # First 500 chars for debugging
                }
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error generating quiz: {str(e)}"
            }

    def generate_quiz(self, video_ids: list[str], question_type: str, num_questions: int) -> Dict[str, Any]:
        """
        Generate quiz questions for video(s) (non-streaming, for backward compatibility).
        
        Args:
            video_ids: List of video IDs to generate quiz for
            question_type: Type of questions (e.g., "multiple choice")
            num_questions: Number of questions to generate
            
        Returns:
            Dict containing the generated questions
        """
        # 1. Fetch content
        content = self._get_video_content_sync(video_ids)
        
        # 2. Build prompt
        prompt = QUIZ_USER_PROMPT.format(
            num_questions=num_questions,
            question_type=question_type,
            content=content
        )
        
        # 3. Call LLM
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=QUIZ_SYSTEM_PROMPT
        )
        
        # 4. Parse response
        try:
            # Clean up response if it contains markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except (json.JSONDecodeError, AttributeError) as e:
            # Handle cases where response is not valid JSON or None
            return {
                "error": "Failed to generate valid quiz",
                "raw_response": str(response),
                "parse_error": str(e)
            }

    async def _get_video_content(self, video_ids: list[str]) -> str:
        """
        Retrieve content for the given videos using RAG retriever.
        """
        all_chunks = []
        for video_id in video_ids:
            chunks = await self.retriever.retrieve_by_video(
                video_id=video_id,
                max_chunks=100  # Limit chunks per video
            )
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return f"Content placeholder for videos: {', '.join(video_ids)}. The video discusses Python programming concepts."
        
        # Sort chunks by video and timestamp
        sorted_chunks = sorted(
            all_chunks,
            key=lambda x: (
                x.get("metadata", {}).get("video_id", ""),
                x.get("metadata", {}).get("start_time", 0)
            )
        )
        
        # Format content
        content_parts = []
        current_video = None
        for chunk in sorted_chunks:
            metadata = chunk.get("metadata", {})
            video_id = metadata.get("video_id", "")
            video_title = metadata.get("video_title", "Unknown")
            text = metadata.get("text", "")
            start_time = metadata.get("start_time", 0)
            
            if video_id != current_video:
                if current_video is not None:
                    content_parts.append("")  # Empty line between videos
                content_parts.append(f"## Video: {video_title} ({video_id})")
                current_video = video_id
            
            # Format timestamp
            start_min, start_sec = divmod(int(start_time), 60)
            timestamp = f"[{start_min:02d}:{start_sec:02d}]"
            content_parts.append(f"{timestamp} {text}")
        
        return "\n".join(content_parts)

    def _get_video_content_sync(self, video_ids: list[str]) -> str:
        """
        Retrieve content synchronously (for backward compatibility).
        """
        # For sync version, return placeholder
        # TODO: Implement sync version if needed
        return f"Content placeholder for videos: {', '.join(video_ids)}. The video discusses Python programming concepts."

# Singleton instance
_quiz_service = None

def get_quiz_service() -> QuizService:
    """Get singleton Quiz service."""
    global _quiz_service
    if _quiz_service is None:
        _quiz_service = QuizService()
    return _quiz_service
