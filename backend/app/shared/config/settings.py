# Static configuration settings

import os

# Database settings
POSTGRES_DB = os.getenv("POSTGRES_DB", "tieplm")
POSTGRES_USER = os.getenv("POSTGRES_USER", "tieplm")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "tieplm")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Qdrant settings
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

