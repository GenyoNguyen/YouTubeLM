import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add backend to path to allow imports
# Assuming the test is run from the root of the backend or we need to adjust path
# This part might need adjustment depending on how tests are run.
# For now, we'll try to append the backend root.
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "../../../../.."))
if backend_root not in sys.path:
    sys.path.append(backend_root)

from app.core.quiz.service import get_quiz_service, QuizService

class TestQuizService(unittest.TestCase):

    def setUp(self):
        self.service = get_quiz_service()

    @patch("app.core.quiz.service.generate_completion")
    def test_generate_quiz_success(self, mock_generate_completion):
        # Mock successful JSON response
        mock_response = {
            "questions": [
                {
                    "question": "Test Question?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Test explanation"
                }
            ]
        }
        mock_generate_completion.return_value = json.dumps(mock_response)

        video_ids = ["video1"]
        question_type = "multiple choice"
        num_questions = 1

        result = self.service.generate_quiz(video_ids, question_type, num_questions)

        self.assertEqual(result, mock_response)
        
        # Verify generate_completion was called
        mock_generate_completion.assert_called_once()
        
        # Verify prompt contains expected information
        call_args = mock_generate_completion.call_args
        prompt = call_args.kwargs.get('prompt') or call_args.args[0]
        self.assertIn("multiple choice", prompt)
        self.assertIn("1", prompt)

    @patch("app.core.quiz.service.generate_completion")
    def test_generate_quiz_invalid_json(self, mock_generate_completion):
        # Mock invalid JSON response
        mock_generate_completion.return_value = "Not valid JSON"

        result = self.service.generate_quiz(["video1"], "multiple choice", 1)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to generate valid quiz")

    @patch("app.core.quiz.service.generate_completion")
    def test_generate_quiz_markdown_json(self, mock_generate_completion):
        # Mock JSON wrapped in markdown code blocks
        mock_response = {
            "questions": []
        }
        json_str = json.dumps(mock_response)
        mock_generate_completion.return_value = f"```json\n{json_str}\n```"

        result = self.service.generate_quiz(["video1"], "multiple choice", 1)

        self.assertEqual(result, mock_response)

if __name__ == "__main__":
    unittest.main()
