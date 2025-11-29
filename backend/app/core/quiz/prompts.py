"""Quiz generation task-specific prompts."""

QUIZ_SYSTEM_PROMPT = """
You are a helpful AI assistant for a video course.
Generate quiz questions based on the provided video content.
"""

QUIZ_USER_PROMPT = """
Based on the following video content, generate {num_questions} {question_type} questions.

Content:
{content}

Return the output in JSON format with the following structure:
{{
    "questions": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Explanation for the answer"
        }}
    ]
}}
"""
