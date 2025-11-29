"""Video summarization task-specific prompts."""

VIDEO_SUMMARY_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh giúp người dùng tóm tắt nội dung video YouTube.

NHIỆM VỤ: Tóm tắt nội dung video dựa trên transcript được cung cấp.

QUY TẮC QUAN TRỌNG:
1. **Toàn diện**: Nắm bắt tất cả các điểm quan trọng trong video, không bỏ sót ý chính.
2. **Cấu trúc rõ ràng**: Tổ chức bản tóm tắt theo các phần/chủ đề chính trong video.
3. **Súc tích**: Tóm tắt ngắn gọn nhưng đầy đủ ý nghĩa, tránh lặp lại.
4. **Ngôn ngữ**: Sử dụng ngôn ngữ phù hợp với nội dung video. Giữ thuật ngữ chuyên ngành khi cần thiết.
5. **Định dạng**: Sử dụng bullet points, **bold**, markdown để làm rõ ý.
6. **Timestamps**: Đề cập khoảng thời gian khi cần thiết để người dùng có thể tìm kiếm nhanh.

CẤU TRÚC TÓM TẮT:
1. **Tổng quan**: 2-3 câu mô tả nội dung chính của video
2. **Các điểm chính**: Liệt kê các khái niệm/chủ đề quan trọng
3. **Chi tiết từng phần**: Giải thích ngắn gọn từng điểm chính
4. **Kết luận**: Tóm tắt những điều quan trọng cần nhớ

LƯU Ý: Bản tóm tắt nên giúp người dùng nắm được toàn bộ nội dung video mà không cần xem lại từ đầu.
"""

VIDEO_SUMMARY_USER_PROMPT_TEMPLATE = """Hãy tóm tắt nội dung video YouTube sau.

# THÔNG TIN VIDEO:
- **Tiêu đề**: {video_title}
- **Danh mục**: {chapter}
- **Thời lượng**: {duration}

# TRANSCRIPT VIDEO:

{transcript}

---

# YÊU CẦU:
Tạo bản tóm tắt chi tiết và có cấu trúc cho video này. Bao gồm:
1. Tổng quan ngắn gọn (2-3 câu)
2. Các điểm chính được trình bày
3. Giải thích chi tiết từng điểm
4. Những điều quan trọng cần nhớ

# TÓM TẮT:
"""

CHAPTER_SUMMARY_USER_PROMPT_TEMPLATE = """Hãy tóm tắt tổng hợp nội dung của playlist/danh mục video sau.

# THÔNG TIN:
- **Danh mục**: {chapter}
- **Số video**: {num_videos}

# NỘI DUNG CÁC VIDEO:

{videos_content}

---

# YÊU CẦU:
Tạo bản tóm tắt tổng hợp cho toàn bộ danh mục này. Bao gồm:
1. Tổng quan về danh mục/playlist
2. Các chủ đề chính được đề cập
3. Mối liên hệ giữa các video
4. Điểm quan trọng cần nắm vững

# TÓM TẮT:
"""

QUICK_SUMMARY_USER_PROMPT_TEMPLATE = """Hãy tạo bản tóm tắt ngắn gọn cho video YouTube sau.

# THÔNG TIN VIDEO:
- **Tiêu đề**: {video_title}
- **Danh mục**: {chapter}

# TRANSCRIPT:

{transcript}

---

# YÊU CẦU:
Tóm tắt trong 3-5 bullet points những điểm quan trọng nhất của video này.

# TÓM TẮT NHANH:
"""
