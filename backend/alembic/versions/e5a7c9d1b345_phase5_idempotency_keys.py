"""Phase 5 mobile offline sync idempotency table

Revision ID: e5a7c9d1b345
Revises: d4f6a8b0c234
Create Date: 2026-11-12 21:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5a7c9d1b345"
down_revision: str | Sequence[str] | None = "d4f6a8b0c234"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("endpoint", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "endpoint", "idempotency_key", name="uq_user_endpoint_idem_key"),
    )
    op.create_index(op.f("ix_idempotency_records_idempotency_key"), "idempotency_records", ["idempotency_key"])


def downgrade() -> None:
    op.drop_index(op.f("ix_idempotency_records_idempotency_key"), table_name="idempotency_records")
    op.drop_table("idempotency_records")
