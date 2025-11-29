# Static configuration settings

import os
from pathlib import Path

# Try to load .env file from project root or backend directory
try:
    from dotenv import load_dotenv
    
    # settings.py is at: backend/app/shared/config/settings.py
    # Try project root first (4 levels up), then backend directory (2 levels up)
    project_root_env = Path(__file__).parent.parent.parent.parent.parent / ".env"
    backend_env = Path(__file__).parent.parent.parent.parent / ".env"
    
    if project_root_env.exists():
        load_dotenv(dotenv_path=project_root_env)
    elif backend_env.exists():
        load_dotenv(dotenv_path=backend_env)
    else:
        # Try loading from current directory as fallback
        load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables must be set manually
    pass

# Database settings
POSTGRES_DB = os.getenv("POSTGRES_DB", "youtubelm")
POSTGRES_USER = os.getenv("POSTGRES_USER", "youtubelm")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "youtubelm")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Qdrant settings
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")

# Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

