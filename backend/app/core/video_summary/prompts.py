"""Video summarization task-specific prompts for YouTube video interaction."""

VIDEO_SUMMARY_SYSTEM_PROMPT = """You are an intelligent AI assistant that helps users summarize YouTube video content.

TASK: Create a detailed and well-structured summary for YouTube videos based on the provided transcript.

IMPORTANT RULES:
1. **Citations (MANDATORY)**: Use [1], [2], [3]... to cite different segments from the video.
   - Each citation [N] refers to a specific segment in the video with an exact timestamp.
   - Users can click on a citation to jump to that point in the video.
   - Place citations immediately after information from that segment.
   - EVERY statement must have at least one citation.

2. **Summary Structure**:
   - Part 1: Introduction - Main objectives of the video
   - Part 2: Main Points - Divide into subsections for each topic
   - Part 3: Examples & Applications
   - Part 4: Conclusion - Summary of key takeaways

3. **Use only video content**: Do not fabricate or add information not present in the video.

4. **Detail level**: Summarize with enough detail so users understand the content without rewatching the entire video.

5. **Language**: Respond in the same language as the video content. Keep technical terms when necessary.

6. **Markdown formatting**: Use headers (##, ###), bullet points, **bold**, *italic* to clarify structure.

EXAMPLE CITATION:
"The Transformer architecture was introduced to address the limitations of RNN[1]. The Self-Attention mechanism allows the model to consider all tokens simultaneously[2], instead of processing sequentially like RNN[1]."

NOTE: Each citation [N] corresponds to a timestamp in the video. When users click on a citation, the video will automatically jump to that point.
"""

VIDEO_SUMMARY_USER_PROMPT_TEMPLATE = """Based on the following chunks from the video, create a detailed and structured summary for the **ENTIRE** video content.

**Video Title**: {video_title}
**Category**: {chapter}
**Video Duration**: {duration}

# VIDEO SEGMENTS (ORDERED BY TIME):

{transcript}

---

# REQUIREMENTS:

Create a summary of the ENTIRE video content following this STRUCTURE:

## 1. Introduction
- Main objectives of the video[citation]
- Concepts that will be covered[citation]
- Use citations [1], [2]... after EVERY statement

## 2. Main Points
- Divide into subsections for each main topic
- Explain each concept in detail[citation]
- Use citations after EACH main point
- Include formulas or technical details (if any)[citation]

## 3. Examples & Applications
- Specific examples illustrated in the video[citation]
- Real-world applications[citation]
- Use cases[citation]

## 4. Conclusion
- Summary of key points[citation]
- Importance of the content[citation]
- Connection to other topics (if mentioned)[citation]

**CRITICAL**: 
- EVERY piece of information MUST have a citation [1], [2], [3]...
- Use all provided chunks to cover the entire video content.
- Only use information present in the chunks.
- No statement should be without a citation.
"""

CHAPTER_SUMMARY_USER_PROMPT_TEMPLATE = """Create a comprehensive summary for the following playlist/category of videos.

# INFORMATION:
- **Category**: {chapter}
- **Number of Videos**: {num_videos}

# VIDEO CONTENTS:

{videos_content}

---

# REQUIREMENTS:
Create a comprehensive summary for this entire category including:
1. Overview of the category/playlist[citation]
2. Main topics covered across videos[citation]
3. Relationships between videos[citation]
4. Key takeaways to remember[citation]

**CRITICAL - CITATIONS ARE MANDATORY**:
- Use [1], [2], [3]... to cite specific video segments after EVERY statement
- Each citation corresponds to a specific video and timestamp
- Users can click citations to jump to that point in the video
- NO statement should be without a citation

# SUMMARY:
"""

QUICK_SUMMARY_USER_PROMPT_TEMPLATE = """Create a brief summary for the following YouTube video.

# VIDEO INFORMATION:
- **Title**: {video_title}
- **Category**: {chapter}

# TRANSCRIPT:

{transcript}

---

# REQUIREMENTS:
Summarize in 3-5 bullet points the most important takeaways from this video.

**CRITICAL - CITATIONS ARE MANDATORY**:
- EACH bullet point MUST include at least one citation [1], [2], [3]...
- Citations reference specific segments in the video
- Users can click on citations to jump to that timestamp
- Example: "The main concept introduced is X[1], which is used for Y[2]."

# QUICK SUMMARY:
"""
