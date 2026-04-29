"""add_bills_table

Revision ID: e196c0dcb397
Revises: 21d28ff28027
Create Date: 2026-04-28 12:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e196c0dcb397"
down_revision = "21d28ff28027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bills",
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("landlord_id", sa.Integer(), nullable=False),
        sa.Column("bill_type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="unpaid", nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.ForeignKeyConstraint(["landlord_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bills_bill_type"), "bills", ["bill_type"], unique=False)
    op.create_index(op.f("ix_bills_contract_id"), "bills", ["contract_id"], unique=False)
    op.create_index(op.f("ix_bills_due_date"), "bills", ["due_date"], unique=False)
    op.create_index(op.f("ix_bills_house_id"), "bills", ["house_id"], unique=False)
    op.create_index(op.f("ix_bills_landlord_id"), "bills", ["landlord_id"], unique=False)
    op.create_index(op.f("ix_bills_status"), "bills", ["status"], unique=False)
    op.create_index(op.f("ix_bills_tenant_id"), "bills", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_bills_tenant_id"), table_name="bills")
    op.drop_index(op.f("ix_bills_status"), table_name="bills")
    op.drop_index(op.f("ix_bills_landlord_id"), table_name="bills")
    op.drop_index(op.f("ix_bills_house_id"), table_name="bills")
    op.drop_index(op.f("ix_bills_due_date"), table_name="bills")
    op.drop_index(op.f("ix_bills_contract_id"), table_name="bills")
    op.drop_index(op.f("ix_bills_bill_type"), table_name="bills")
    op.drop_table("bills")
