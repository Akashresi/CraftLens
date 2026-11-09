"""Add artisan_applications table

Revision ID: b2d4f6e8a012
Revises: a8c298840ad8
Create Date: 2026-11-09 14:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2d4f6e8a012'
down_revision: Union[str, Sequence[str], None] = 'a8c298840ad8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'artisan_applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('craft_specialization', sa.String(length=255), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('craft_description', sa.Text(), nullable=False),
        sa.Column('supporting_documents_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artisan_applications_user_id'), 'artisan_applications', ['user_id'], unique=False)
    op.create_index(op.f('ix_artisan_applications_status'), 'artisan_applications', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_artisan_applications_status'), table_name='artisan_applications')
    op.drop_index(op.f('ix_artisan_applications_user_id'), table_name='artisan_applications')
    op.drop_table('artisan_applications')
