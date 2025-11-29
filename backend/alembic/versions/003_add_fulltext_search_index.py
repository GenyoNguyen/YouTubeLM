"""Add full-text search index for BM25 search

Revision ID: 003_add_fulltext
Revises: 002_remove_chapter
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_fulltext'
down_revision = '002_remove_chapter'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create GIN index on text column for full-text search
    # This enables fast BM25-style search using PostgreSQL's full-text search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_text_fts 
        ON chunks USING GIN (to_tsvector('english', text))
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chunks_text_fts")

