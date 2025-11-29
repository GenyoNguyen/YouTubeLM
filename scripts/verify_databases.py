#!/usr/bin/env python3
"""Verify database setup and connectivity."""

import sys
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
    # python-dotenv not installed, continue without it
    pass

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.shared.database.postgres import get_db, engine
from app.shared.database.qdrant import get_client, ensure_collection, COLLECTION_NAME
from app.models import Base


def verify_postgres():
    """Verify PostgreSQL connection and schema."""
    print("=" * 60)
    print("PostgreSQL Verification")
    print("=" * 60)
    
    try:
        # Test connection
        from sqlalchemy import text
        with get_db() as db:
            result = db.execute(text("SELECT version()")).scalar()
            print(f"✅ Connection: OK")
            print(f"   PostgreSQL version: {result.split(',')[0]}")
        
        # Check tables
        print("\nChecking tables...")
        tables = Base.metadata.tables.keys()
        expected_tables = {'videos', 'chunks', 'chat_sessions', 'chat_messages', 'quiz_questions'}
        
        with get_db() as db:
            existing_tables = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).fetchall()
            existing_table_names = {row[0] for row in existing_tables}
        
        for table in expected_tables:
            if table in existing_table_names:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (missing)")
                return False
        
        # Check row counts
        print("\nRow counts:")
        with get_db() as db:
            from app.models import Video, Chunk, ChatSession, ChatMessage, QuizQuestion
            
            video_count = db.query(Video).count()
            chunk_count = db.query(Chunk).count()
            session_count = db.query(ChatSession).count()
            message_count = db.query(ChatMessage).count()
            quiz_count = db.query(QuizQuestion).count()
            
            print(f"   Videos: {video_count}")
            print(f"   Chunks: {chunk_count}")
            print(f"   Chat Sessions: {session_count}")
            print(f"   Chat Messages: {message_count}")
            print(f"   Quiz Questions: {quiz_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_qdrant():
    """Verify Qdrant connection and collection."""
    print("\n" + "=" * 60)
    print("Qdrant Verification")
    print("=" * 60)
    
    try:
        # Test connection
        client = get_client()
        collections = client.get_collections()
        print(f"✅ Connection: OK")
        print(f"   Found {len(collections.collections)} collection(s)")
        
        # Ensure collection exists
        ensure_collection()
        print(f"✅ Collection '{COLLECTION_NAME}': OK")
        
        # Get collection info
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"\nCollection info:")
        print(f"   Points count: {collection_info.points_count}")
        print(f"   Vector size: {collection_info.config.params.vectors.size}")
        print(f"   Distance: {collection_info.config.params.vectors.distance}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main verification function."""
    print("YouTubeLM Database Verification")
    print("=" * 60)
    print()
    
    postgres_ok = verify_postgres()
    qdrant_ok = verify_qdrant()
    
    print("\n" + "=" * 60)
    if postgres_ok and qdrant_ok:
        print("✅ All databases verified successfully!")
        return 0
    else:
        print("❌ Some verifications failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

