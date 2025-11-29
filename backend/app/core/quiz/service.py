# Quiz generation service
import json
from typing import List, Dict, Any
from ...shared.llm.client import generate_completion
from .prompts import QUIZ_SYSTEM_PROMPT, QUIZ_USER_PROMPT

class QuizService:
    """Service for generating quizzes from video content."""

    def generate_quiz(self, video_ids: list[str], question_type: str, num_questions: int) -> Dict[str, Any]:
        """
        Generate quiz questions for video(s).
        
        Args:
            video_ids: List of video IDs to generate quiz for
            question_type: Type of questions (e.g., "multiple choice")
            num_questions: Number of questions to generate
            
        Returns:
            Dict containing the generated questions
        """
        # 1. Fetch content
        # TODO: Implement actual content fetching from DB or RAG
        content = self._get_video_content(video_ids)
        
        # 2. Build prompt
        prompt = QUIZ_USER_PROMPT.format(
            num_questions=num_questions,
            question_type=question_type,
            content=content
        )
        
        # 3. Call LLM
        # Note: generate_completion is a function in the current codebase
        response = generate_completion(
            prompt=prompt,
            system_prompt=QUIZ_SYSTEM_PROMPT
        )
        
        # 4. Parse response
        try:
            # Clean up response if it contains markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response)
        except (json.JSONDecodeError, AttributeError):
            # Handle cases where response is not valid JSON or None
            return {
                "error": "Failed to generate valid quiz",
                "raw_response": str(response)
            }

    def _get_video_content(self, video_ids: list[str]) -> str:
        """
        Retrieve content for the given videos.
        Currently a stub.
        """
        # TODO: Integrate with RAGRetriever or Database to get actual transcripts
        return f"Content placeholder for videos: {', '.join(video_ids)}. The video discusses Python programming concepts."

# Singleton instance
_quiz_service = None

def get_quiz_service() -> QuizService:
    """Get singleton Quiz service."""
    global _quiz_service
    if _quiz_service is None:
        _quiz_service = QuizService()
    return _quiz_service
