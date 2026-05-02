"""add_news_table

Revision ID: a4b3c2d1e0f9
Revises: f1a7b92d4c33
Create Date: 2026-05-02 20:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4b3c2d1e0f9"
down_revision = "f1a7b92d4c33"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news",
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_news_created_at", "news", ["created_at"], unique=False)
    op.create_index(op.f("ix_news_author_id"), "news", ["author_id"], unique=False)
    op.create_index(op.f("ix_news_status"), "news", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_news_status"), table_name="news")
    op.drop_index(op.f("ix_news_author_id"), table_name="news")
    op.drop_index("ix_news_created_at", table_name="news")
    op.drop_table("news")
