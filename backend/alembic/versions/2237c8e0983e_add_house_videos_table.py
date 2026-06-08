"""add_house_videos_table

Revision ID: 2237c8e0983e
Revises: d9f8e7c6b5a4
Create Date: 2026-06-07 16:55:38.993199

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2237c8e0983e'
down_revision = 'd9f8e7c6b5a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('house_videos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('house_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['house_id'], ['houses.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_house_videos_house_id'), 'house_videos', ['house_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_house_videos_house_id'), table_name='house_videos')
    op.drop_table('house_videos')
