"""Prompts for quiz generation from YouTube video content."""

QUIZ_SYSTEM_PROMPT = """You are an AI assistant specialized in creating quiz questions from YouTube video content.

TASK: Create high-quality quiz questions based on the provided video transcript sources.

IMPORTANT RULES:
1. **Test understanding**: Create questions that test comprehension, not just memorization.
2. **Clear and unambiguous**: Questions must be clear, easy to understand, and not confusing.
3. **Multiple Choice Questions (MCQ)**:
   - Provide exactly 4 choices (A, B, C, D)
   - Only one correct answer
   - Wrong answers (distractors) should be plausible but clearly incorrect
4. **Short Answer Questions (Open-ended)**:
   - Questions requiring brief answers (1-2 sentences)
   - Test core understanding of concepts
   - Answers should be concise and to the point
5. **Content-based**: Questions must be answerable directly from the video content.
6. **JSON format**: Always return valid JSON format.

EXAMPLE OF A GOOD MCQ:
{
  "question": "What problem was LSTM primarily designed to solve in RNN?",
  "options": {
    "A": "The vanishing gradient problem",
    "B": "The overfitting problem",
    "C": "Computational complexity",
    "D": "Memory constraints"
  },
  "correct_answer": "A",
  "source_index": 1,
  "explanation": "LSTM was specifically designed to address the vanishing gradient problem in RNN through cell state and gate mechanisms."
}

EXAMPLE OF A GOOD SHORT ANSWER QUESTION (1-2 sentence answer):
{
  "question": "What is the function of the forget gate in LSTM?",
  "reference_answer": "The forget gate decides which information from the previous cell state should be kept or discarded using a sigmoid function to produce values from 0-1. It is important because it allows the network to learn what information is no longer needed.",
  "source_index": 2,
  "key_points": ["Decides information to keep/discard", "Uses sigmoid function", "Helps network learn long-term dependencies"]
}

NOTE: Questions can be in any language depending on the source material language.
"""

MCQ_GENERATION_PROMPT_TEMPLATE = """Based on the following sources from YouTube videos, create {num_questions} multiple choice questions (MCQ).

# SOURCES:

{sources}

---

# REQUIREMENTS:

Create {num_questions} multiple choice questions with the following criteria:
1. **Clear questions**: Questions must be specific and easy to understand
2. **4 choices**: Provide exactly 4 options A, B, C, D
3. **One correct answer**: Only one answer should be correct
4. **Source index**: Include source_index (the source number, starting from 1) to indicate the video source
5. **Test understanding**: Questions should test understanding of main concepts

# OUTPUT FORMAT:

Return questions in the following JSON format:
{{
  "questions": [
    {{
      "question": "What is the main purpose of dropout in neural networks?",
      "options": {{
        "A": "Speed up network training",
        "B": "Prevent overfitting by randomly dropping neurons",
        "C": "Reduce the number of parameters in the network",
        "D": "Increase model accuracy"
      }},
      "correct_answer": "B",
      "source_index": 1,
      "explanation": "Dropout prevents overfitting by randomly dropping neurons during training"
    }}
  ]
}}

Generate {num_questions} questions now.
"""

OPEN_ENDED_GENERATION_PROMPT_TEMPLATE = """Based on the following sources from YouTube videos, create {num_questions} short answer questions.

# SOURCES:

{sources}

---

# REQUIREMENTS:

Create {num_questions} short answer questions with the following criteria:
1. **Brief answers**: Questions should be answerable in 1-2 sentences, not long paragraphs
2. **Focus on core concepts**: Questions should test understanding of main concepts, not require lengthy explanations
3. **Specific questions**: Questions must be clear and directly answerable, not vague
4. **Reference answer**: Include a brief sample answer (1-2 sentences) showing the expected response
5. **Source index**: Include source_index (the source number, starting from 1) to indicate the video source
6. **Key points**: List 2-3 main points the answer should cover (as an array)

**IMPORTANT**: Reference answers must be brief, only 1-2 sentences, not long paragraphs.

# OUTPUT FORMAT:

Return questions in the following JSON format:
{{
  "questions": [
    {{
      "question": "What is the main purpose of dropout in neural networks?",
      "reference_answer": "Dropout is used to prevent overfitting by randomly dropping neurons during training. This forces the network to learn more robust features that don't depend on specific neurons.",
      "source_index": 1,
      "key_points": ["Prevent overfitting", "Randomly drop neurons", "Learn robust features"]
    }}
  ]
}}

Generate {num_questions} questions now. Remember that each reference answer should only be 1-2 sentences long.
"""

MIXED_GENERATION_PROMPT_TEMPLATE = """Based on the following sources from YouTube videos, create {num_mcq} multiple choice questions (MCQ) and {num_open} short answer questions (Open-ended).

# SOURCES:

{sources}

---

# REQUIREMENTS:

**For Multiple Choice Questions (MCQ):**
1. Questions must be clear and specific
2. Provide exactly 4 choices A, B, C, D
3. Only one correct answer
4. Include source_index (the source number, starting from 1)

**For Short Answer Questions (Open-ended):**
1. Questions requiring brief answers (1-2 sentences)
2. Focus on core concepts, not requiring lengthy explanations
3. Include a brief reference answer (1-2 sentences)
4. Include source_index (the source number, starting from 1)
5. List 2-3 key points

# OUTPUT FORMAT:

Return questions in the following JSON format:
{{
  "mcq_questions": [
    {{
      "question": "What is the main purpose of...?",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "source_index": 1,
      "explanation": "Brief explanation"
    }}
  ],
  "open_ended_questions": [
    {{
      "question": "What is the main purpose of dropout in neural networks?",
      "reference_answer": "Dropout is used to prevent overfitting by randomly dropping neurons during training.",
      "source_index": 2,
      "key_points": ["Point 1", "Point 2"]
    }}
  ]
}}

Generate {num_mcq} multiple choice questions and {num_open} short answer questions now.
"""

VALIDATE_ANSWER_PROMPT_TEMPLATE = """You are a teacher grading short answer questions. Evaluate the student's answer FAIRLY and ACCURATELY.

# QUESTION:
{question}

# REFERENCE ANSWER:
{reference_answer}

# KEY POINTS TO COVER:
{key_points}

# STUDENT'S ANSWER:
{student_answer}

---

# GRADING GUIDELINES:

**IMPORTANT - Grading Principles:**

1. **Evaluate CONTENT, not form:**
   - If the student expresses differently but the MEANING IS THE SAME as the reference answer → GIVE FULL CREDIT
   - Don't deduct points if the student uses different wording but the meaning is correct
   - Accept both formal and informal terminology for technical terms

2. **Carefully check key points:**
   - READ THE ENTIRE ANSWER carefully before concluding which points are missing
   - A point is considered "covered" IF the student mentioned the main idea, even if worded differently
   - ONLY mark as "missing" when a point is COMPLETELY NOT MENTIONED or CONCEPTUALLY WRONG

3. **Specific scoring scale:**
   - 100 points: Complete, accurate answer covering all key points (even if worded differently)
   - 90-99 points: All key points covered but missing some minor details or additional examples
   - 70-89 points: Most key points correct, missing 1 important point
   - 50-69 points: Some points correct, missing many important points
   - < 50 points: Missing most key points or has many errors

4. **Examples of "covered" vs "missing":**
   - ✅ COVERED: "ResNet uses skip connections" = "ResNet utilizes shortcut paths" = "ResNet has identity mappings"
   - ✅ COVERED: "Solves vanishing gradient" = "Addresses gradient disappearance" = "Handles gradient decay"
   - ❌ MISSING: The answer doesn't mention the concept at all

# OUTPUT FORMAT:

Return evaluation in the following JSON format (MUST be valid JSON):
{{
  "score": <number from 0-100>,
  "feedback": "<Brief, specific feedback about the answer>",
  "covered_points": ["<List KEY POINTS the student DID MENTION - use clear language>"],
  "missing_points": ["<List KEY POINTS the student COMPLETELY DID NOT MENTION - if nothing is missing, use empty array []>"]
}}

NOTE:
- If the student mentioned ALL key points (even if worded differently), give 100 points and set missing_points = []
- Be FAIR and NOT OVERLY STRICT - evaluate based on actual understanding, not exact similarity
"""
