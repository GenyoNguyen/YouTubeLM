"""Main ingestion service."""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.shared.ingestion.downloader import download_video, extract_video_id
from app.shared.ingestion.transcriber import transcribe_audio
from app.shared.ingestion.chunker import chunk_transcript
from app.shared.ingestion.embedder import generate_embeddings
from app.shared.database.postgres import get_db
from app.shared.database.qdrant import upsert_points, ensure_collection
from app.shared.database.qdrant import PointStruct
from app.models import Video, Chunk


# Directories
VIDEOS_DIR = Path("ingestion/videos")
TRANSCRIPTS_DIR = Path("ingestion/transcripts")

# Ensure directories exist
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def process_video(
    video_url: str,
    groq_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process a YouTube video: download, transcribe, chunk, embed, and store.
    
    Args:
        video_url: YouTube video URL
        groq_api_key: Groq API key (if not in env)
    
    Returns:
        Dict with video_id and status
    """
    groq_key = groq_api_key or os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not provided")
    
    # Step 1: Download video
    video_info = download_video(video_url, str(VIDEOS_DIR))
    video_id = video_info['video_id']
    
    # Step 2: Transcribe audio
    transcript = transcribe_audio(
        video_info['audio_path'],
        api_key=groq_key,
        model="whisper-large-v3-turbo"
    )
    
    # Step 3: Chunk transcript
    chunks = chunk_transcript(transcript['segments'], window_size=60, overlap=10)
    
    # Step 4: Generate embeddings
    chunk_texts = [chunk['text'] for chunk in chunks]
    embeddings = generate_embeddings(chunk_texts)
    
    # Step 5: Store in databases
    with get_db() as db:
        # Check if video already exists
        existing_video = db.query(Video).filter(Video.id == video_id).first()
        
        if existing_video:
            # Update existing video
            existing_video.title = video_info['title']
            existing_video.duration = video_info['duration']
            existing_video.url = video_url
            video = existing_video
            
            # Delete existing chunks
            db.query(Chunk).filter(Chunk.video_id == video_id).delete()
        else:
            # Create new video
            video = Video(
                id=video_id,
                title=video_info['title'],
                url=video_url,
                duration=video_info['duration'],
            )
            db.add(video)
        
        db.flush()
        
        # Prepare Qdrant points
        qdrant_points = []
        
        # Create chunks and Qdrant points
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate a deterministic UUID from video_id and chunk index
            # This ensures the same chunk always gets the same ID
            unique_string = f"{video_id}_{i}_{chunk['start_time']}_{chunk['end_time']}"
            qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
            
            # Create chunk in PostgreSQL
            db_chunk = Chunk(
                video_id=video_id,
                start_time=chunk['start_time'],
                end_time=chunk['end_time'],
                text=chunk['text'],
                qdrant_id=qdrant_id,
            )
            db.add(db_chunk)
            
            # Prepare Qdrant point
            qdrant_points.append(
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload={
                        'video_id': video_id,
                        'video_title': video_info['title'],
                        'video_url': video_url,
                        'start_time': chunk['start_time'],
                        'end_time': chunk['end_time'],
                        'text': chunk['text'],
                    }
                )
            )
        
        db.commit()
    
    # Step 6: Upsert to Qdrant
    ensure_collection()
    if qdrant_points:
        upsert_points(qdrant_points)
    
    return {
        'video_id': video_id,
        'title': video_info['title'],
        'chunks_count': len(chunks),
        'status': 'success',
    }

