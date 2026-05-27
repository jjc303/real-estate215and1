"""add_house_images_and_user_avatars

Revision ID: d9f8e7c6b5a4
Revises: c1e2f3a4b5c6
Create Date: 2026-05-27 21:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d9f8e7c6b5a4"
down_revision = "c1e2f3a4b5c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "house_images",
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("object_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_cover", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_house_images_house_id"), "house_images", ["house_id"], unique=False)
    op.create_index("ix_house_images_house_status", "house_images", ["house_id", "status"], unique=False)
    op.create_index("ix_house_images_house_cover", "house_images", ["house_id", "is_cover"], unique=False)

    op.create_table(
        "user_avatars",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("object_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_avatars_user_id"), "user_avatars", ["user_id"], unique=False)
    op.create_index("ix_user_avatars_user_current", "user_avatars", ["user_id", "is_current"], unique=False)
    op.create_index("ix_user_avatars_user_status", "user_avatars", ["user_id", "status"], unique=False)

    op.drop_column("users", "avatar")


def downgrade() -> None:
    op.add_column("users", sa.Column("avatar", sa.String(length=255), nullable=True))

    op.drop_index("ix_user_avatars_user_status", table_name="user_avatars")
    op.drop_index("ix_user_avatars_user_current", table_name="user_avatars")
    op.drop_index(op.f("ix_user_avatars_user_id"), table_name="user_avatars")
    op.drop_table("user_avatars")

    op.drop_index("ix_house_images_house_cover", table_name="house_images")
    op.drop_index("ix_house_images_house_status", table_name="house_images")
    op.drop_index(op.f("ix_house_images_house_id"), table_name="house_images")
    op.drop_table("house_images")
