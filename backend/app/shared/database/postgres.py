"""PostgreSQL database client."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator

from app.shared.config.settings import (
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
)

# Create database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_connection():
    """Get PostgreSQL connection."""
    return engine.connect()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)


# Class-based wrapper for compatibility with services
class PostgresClient:
    """Wrapper class for PostgreSQL database operations."""
    
    @contextmanager
    def session_scope(self):
        """Get database session context manager."""
        with get_db() as db:
            yield db


# Singleton instance
_postgres_client = None

def get_postgres_client() -> PostgresClient:
    """Get singleton PostgreSQL client instance."""
    global _postgres_client
    if _postgres_client is None:
        _postgres_client = PostgresClient()
    return _postgres_client
