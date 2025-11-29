"""Database models for YouTubeLM."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, ForeignKey, 
    Boolean, JSON, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Video(Base):
    """Video metadata model."""
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True)  # YouTube video ID
    title = Column(String, nullable=False)  # Video title
    url = Column(String, nullable=False, unique=True)  # YouTube URL
    duration = Column(Float, nullable=True)  # Duration in seconds
    transcript_path = Column(String, nullable=True)  # Path to transcript file
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="video", cascade="all, delete-orphan")


class Chunk(Base):
    """Transcript chunk model."""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(Float, nullable=False)  # Start time in seconds
    end_time = Column(Float, nullable=False)  # End time in seconds
    text = Column(Text, nullable=False)  # Chunk text content
    qdrant_id = Column(String, nullable=True, unique=True)  # Qdrant point ID
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    video = relationship("Video", back_populates="chunks")


class ChatSession(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, nullable=True)  # User identifier (optional)
    task_type = Column(String, nullable=False)  # qa, video_summary, quiz
    title = Column(String, nullable=True)  # Session title
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message model."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)  # Message content
    sources = Column(JSON, nullable=True)  # List of source citations
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class QuizQuestion(Base):
    """Quiz question model."""
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)  # Quiz session ID
    video_id = Column(String, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)
    question_type = Column(String, nullable=False)  # mcq, yes_no
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For MCQ: ["A) ...", "B) ..."]
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
