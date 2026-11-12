"""Phase 6 database performance indexes on hot filter and sort columns

Revision ID: f6b8d0e2c456
Revises: e5a7c9d1b345
Create Date: 2026-11-12 22:35:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "f6b8d0e2c456"
down_revision: str | Sequence[str] | None = "e5a7c9d1b345"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_products_status_created_at", "products", ["status", "created_at"], if_not_exists=True)
    op.create_index("ix_products_gi_verification_status", "products", ["gi_verification_status"], if_not_exists=True)
    op.create_index("ix_orders_buyer_created_at", "orders", ["buyer_id", "created_at"], if_not_exists=True)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], if_not_exists=True)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs", if_exists=True)
    op.drop_index("ix_orders_buyer_created_at", table_name="orders", if_exists=True)
    op.drop_index("ix_products_gi_verification_status", table_name="products", if_exists=True)
    op.drop_index("ix_products_status_created_at", table_name="products", if_exists=True)
