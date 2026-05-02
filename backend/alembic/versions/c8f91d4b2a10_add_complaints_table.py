"""add_complaints_table

Revision ID: c8f91d4b2a10
Revises: 7b4d6c2a9f31
Create Date: 2026-05-02 15:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c8f91d4b2a10"
down_revision = "7b4d6c2a9f31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "complaints",
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("landlord_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.ForeignKeyConstraint(["landlord_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_complaints_contract_id"), "complaints", ["contract_id"], unique=False)
    op.create_index(op.f("ix_complaints_house_id"), "complaints", ["house_id"], unique=False)
    op.create_index(op.f("ix_complaints_landlord_id"), "complaints", ["landlord_id"], unique=False)
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"], unique=False)
    op.create_index(op.f("ix_complaints_status"), "complaints", ["status"], unique=False)
    op.create_index(op.f("ix_complaints_tenant_id"), "complaints", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_complaints_tenant_id"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_status"), table_name="complaints")
    op.drop_index("ix_complaints_created_at", table_name="complaints")
    op.drop_index(op.f("ix_complaints_landlord_id"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_house_id"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_contract_id"), table_name="complaints")
    op.drop_table("complaints")
