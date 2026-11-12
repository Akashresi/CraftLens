"""Phase 2 security, Ed25519 provenance, lockout, and DPDP compliance tables

Revision ID: c3e5a7b9d123
Revises: b2d4f6e8a012
Create Date: 2026-11-12 19:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3e5a7b9d123"
down_revision: str | Sequence[str] | None = "b2d4f6e8a012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("is_anonymized", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("consent_records", sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "grievance_tickets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grievance_tickets_user_id"), "grievance_tickets", ["user_id"], unique=False)

    op.add_column("provenance_records", sa.Column("signed_payload", sa.Text(), nullable=True))
    op.add_column("provenance_records", sa.Column("signature_ed25519", sa.String(length=256), nullable=True))
    op.add_column("provenance_records", sa.Column("public_key_fingerprint", sa.String(length=64), nullable=True))
    op.add_column(
        "provenance_records", sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.add_column("provenance_records", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("provenance_records", sa.Column("revoked_reason", sa.String(length=255), nullable=True))

    op.add_column("product_qr", sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("product_qr", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("product_qr", sa.Column("revoked_reason", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("product_qr", "revoked_reason")
    op.drop_column("product_qr", "revoked_at")
    op.drop_column("product_qr", "is_revoked")

    op.drop_column("provenance_records", "revoked_reason")
    op.drop_column("provenance_records", "revoked_at")
    op.drop_column("provenance_records", "is_revoked")
    op.drop_column("provenance_records", "public_key_fingerprint")
    op.drop_column("provenance_records", "signature_ed25519")
    op.drop_column("provenance_records", "signed_payload")

    op.drop_index(op.f("ix_grievance_tickets_user_id"), table_name="grievance_tickets")
    op.drop_table("grievance_tickets")

    op.drop_column("consent_records", "withdrawn_at")

    op.drop_column("users", "is_anonymized")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")

