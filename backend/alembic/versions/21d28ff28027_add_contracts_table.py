"""add_contracts_table

Revision ID: 21d28ff28027
Revises: 8599342798d7
Create Date: 2026-04-26 21:30:39.573309

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '21d28ff28027'
down_revision = '8599342798d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'contracts',
        sa.Column('house_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('landlord_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('monthly_rent', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('deposit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id']),
        sa.ForeignKeyConstraint(['house_id'], ['houses.id']),
        sa.ForeignKeyConstraint(['landlord_id'], ['users.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_contracts_appointment_id'), 'contracts', ['appointment_id'], unique=False)
    op.create_index(op.f('ix_contracts_house_id'), 'contracts', ['house_id'], unique=False)
    op.create_index(op.f('ix_contracts_landlord_id'), 'contracts', ['landlord_id'], unique=False)
    op.create_index(op.f('ix_contracts_status'), 'contracts', ['status'], unique=False)
    op.create_index(op.f('ix_contracts_tenant_id'), 'contracts', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_contracts_tenant_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_status'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_landlord_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_house_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_appointment_id'), table_name='contracts')
    op.drop_table('contracts')
