"""add_payments_table

Revision ID: 4d4e0ca9ef73
Revises: e196c0dcb397
Create Date: 2026-04-28 18:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d4e0ca9ef73"
down_revision = "e196c0dcb397"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("bill_id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("landlord_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="success", nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["bill_id"], ["bills.id"]),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.ForeignKeyConstraint(["landlord_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bill_id", name="uq_payments_bill_id"),
    )
    op.create_index("ix_payments_created_at", "payments", ["created_at"], unique=False)
    op.create_index("ix_payments_landlord_id", "payments", ["landlord_id"], unique=False)
    op.create_index("ix_payments_payment_method", "payments", ["payment_method"], unique=False)
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index("ix_payments_tenant_id", "payments", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payments_tenant_id", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_payment_method", table_name="payments")
    op.drop_index("ix_payments_landlord_id", table_name="payments")
    op.drop_index("ix_payments_created_at", table_name="payments")
    op.drop_table("payments")
