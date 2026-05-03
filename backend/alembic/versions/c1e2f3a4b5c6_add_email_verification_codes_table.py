"""add_email_verification_codes_table

Revision ID: c1e2f3a4b5c6
Revises: b5c4d3e2f1a0
Create Date: 2026-05-03 10:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1e2f3a4b5c6"
down_revision = "b5c4d3e2f1a0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_verification_codes",
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("biz_type", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_verification_codes_created_at", "email_verification_codes", ["created_at"], unique=False)
    op.create_index(op.f("ix_email_verification_codes_biz_type"), "email_verification_codes", ["biz_type"], unique=False)
    op.create_index(op.f("ix_email_verification_codes_email"), "email_verification_codes", ["email"], unique=False)

    op.execute("UPDATE users SET email = NULL WHERE email = ''")
    op.create_index("uq_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_users_email", table_name="users")
    op.drop_index(op.f("ix_email_verification_codes_email"), table_name="email_verification_codes")
    op.drop_index(op.f("ix_email_verification_codes_biz_type"), table_name="email_verification_codes")
    op.drop_index("ix_email_verification_codes_created_at", table_name="email_verification_codes")
    op.drop_table("email_verification_codes")
