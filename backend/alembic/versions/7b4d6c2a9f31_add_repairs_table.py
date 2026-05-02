"""add_repairs_table

Revision ID: 7b4d6c2a9f31
Revises: 4d4e0ca9ef73
Create Date: 2026-05-02 12:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7b4d6c2a9f31"
down_revision = "4d4e0ca9ef73"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "repairs",
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("landlord_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("reopened_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.ForeignKeyConstraint(["landlord_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_repairs_contract_id"), "repairs", ["contract_id"], unique=False)
    op.create_index(op.f("ix_repairs_house_id"), "repairs", ["house_id"], unique=False)
    op.create_index(op.f("ix_repairs_landlord_id"), "repairs", ["landlord_id"], unique=False)
    op.create_index("ix_repairs_created_at", "repairs", ["created_at"], unique=False)
    op.create_index(op.f("ix_repairs_status"), "repairs", ["status"], unique=False)
    op.create_index(op.f("ix_repairs_tenant_id"), "repairs", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_repairs_tenant_id"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_status"), table_name="repairs")
    op.drop_index("ix_repairs_created_at", table_name="repairs")
    op.drop_index(op.f("ix_repairs_landlord_id"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_house_id"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_contract_id"), table_name="repairs")
    op.drop_table("repairs")
