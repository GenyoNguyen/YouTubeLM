"""Remove chapter column from videos table

Revision ID: 002_remove_chapter
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_remove_chapter'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop chapter column from videos table
    op.drop_column('videos', 'chapter')


def downgrade() -> None:
    # Add chapter column back (nullable)
    op.add_column('videos', sa.Column('chapter', sa.String(), nullable=True))

