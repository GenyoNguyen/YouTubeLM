#!/usr/bin/env python3
"""Test script for the ingestion pipeline."""

import sys
import os
from pathlib import Path

# Try to load .env file from project root
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Also try backend/.env
        backend_env = Path(__file__).parent.parent / "backend" / ".env"
        if backend_env.exists():
            load_dotenv(dotenv_path=backend_env)
        else:
            load_dotenv()  # Try current directory
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")
    print("Install it with: pip install python-dotenv")

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.shared.ingestion.service import process_video
from app.shared.database.postgres import get_db, init_db
from app.shared.database.qdrant import ensure_collection, get_client
from app.models import Video, Chunk
from app.shared.config.settings import GROQ_API_KEY


def test_database_connection():
    """Test database connections."""
    print("=" * 60)
    print("Testing Database Connections")
    print("=" * 60)
    
    # Test PostgreSQL
    try:
        from sqlalchemy import text
        with get_db() as db:
            result = db.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ PostgreSQL connection: OK")
            else:
                print("❌ PostgreSQL connection: FAILED")
                return False
    except Exception as e:
        print(f"❌ PostgreSQL connection: FAILED - {e}")
        return False
    
    # Test Qdrant
    try:
        client = get_client()
        collections = client.get_collections()
        print("✅ Qdrant connection: OK")
        print(f"   Found {len(collections.collections)} collection(s)")
    except Exception as e:
        print(f"❌ Qdrant connection: FAILED - {e}")
        return False
    
    return True


def test_ingestion_pipeline(video_url: str):
    """Test the full ingestion pipeline."""
    print("\n" + "=" * 60)
    print("Testing Ingestion Pipeline")
    print("=" * 60)
    print(f"Video URL: {video_url}")
    print()
    
    # Check API keys
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set in environment")
        return False
    
    print("✅ API keys: OK")
    print()
    
    try:
        # Step 1: Download
        print("Step 1: Downloading video...")
        # This will be done inside process_video
        
        # Step 2-6: Process video
        print("Step 2-6: Processing video (transcribe, chunk, embed, store)...")
        result = process_video(
            video_url=video_url,
            groq_api_key=GROQ_API_KEY,
        )
        
        print("\n✅ Ingestion completed successfully!")
        print(f"   Video ID: {result['video_id']}")
        print(f"   Title: {result['title']}")
        print(f"   Chunks: {result['chunks_count']}")
        print(f"   Status: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_data_storage(video_id: str):
    """Verify that data was stored correctly."""
    print("\n" + "=" * 60)
    print("Verifying Data Storage")
    print("=" * 60)
    
    # Check PostgreSQL
    try:
        with get_db() as db:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                print(f"✅ Video found in PostgreSQL:")
                print(f"   ID: {video.id}")
                print(f"   Title: {video.title}")
                print(f"   Duration: {video.duration}s")
                
                chunks = db.query(Chunk).filter(Chunk.video_id == video_id).all()
                print(f"   Chunks: {len(chunks)}")
                
                if chunks:
                    print(f"   First chunk: {chunks[0].text[:100]}...")
                    print(f"   Last chunk: {chunks[-1].text[:100]}...")
            else:
                print(f"❌ Video {video_id} not found in PostgreSQL")
                return False
    except Exception as e:
        print(f"❌ PostgreSQL verification failed: {e}")
        return False
    
    # Check Qdrant
    try:
        client = get_client()
        ensure_collection()
        
        # Search for points with this video_id
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        search_result = client.scroll(
            collection_name="youtubelm_transcripts",
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="video_id",
                        match=MatchValue(value=video_id)
                    )
                ]
            ),
            limit=10,
        )
        
        points = search_result[0]
        if points:
            print(f"\n✅ Found {len(points)} point(s) in Qdrant for video {video_id}")
            print(f"   First point ID: {points[0].id}")
            print(f"   First point payload: {points[0].payload.get('text', '')[:100]}...")
        else:
            print(f"❌ No points found in Qdrant for video {video_id}")
            return False
            
    except Exception as e:
        print(f"❌ Qdrant verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main test function."""
    print("YouTubeLM Ingestion Pipeline Test")
    print("=" * 60)
    
    # Check if video URL provided
    if len(sys.argv) < 2:
        print("\nUsage: python scripts/test_ingestion.py <youtube_url>")
        print("\nExample:")
        print("  python scripts/test_ingestion.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
        sys.exit(1)
    
    video_url = sys.argv[1]
    
    # Test 1: Database connections
    if not test_database_connection():
        print("\n❌ Database connection test failed. Please check your setup.")
        sys.exit(1)
    
    # Test 2: Ingestion pipeline
    if not test_ingestion_pipeline(video_url):
        print("\n❌ Ingestion pipeline test failed.")
        sys.exit(1)
    
    # Extract video ID for verification
    from app.shared.ingestion.downloader import extract_video_id
    try:
        video_id = extract_video_id(video_url)
    except:
        print("\n⚠️  Could not extract video ID for verification")
        sys.exit(0)
    
    # Test 3: Verify data storage
    if not verify_data_storage(video_id):
        print("\n❌ Data storage verification failed.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print(f"\nYou can now query the video with ID: {video_id}")


if __name__ == "__main__":
    main()

