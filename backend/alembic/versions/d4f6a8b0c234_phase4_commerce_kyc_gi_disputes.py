"""Phase 4 commerce completeness: Razorpay UPI, refunds, disputes, shipping, GI claims, and B2B GST invoicing

Revision ID: d4f6a8b0c234
Revises: c3e5a7b9d123
Create Date: 2026-11-12 19:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4f6a8b0c234"
down_revision: str | Sequence[str] | None = "c3e5a7b9d123"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("dispute_reason", sa.Text(), nullable=True))
    op.add_column("orders", sa.Column("dispute_resolution", sa.Text(), nullable=True))
    op.add_column("orders", sa.Column("payout_status", sa.String(length=50), nullable=False, server_default="PENDING"))
    op.add_column("orders", sa.Column("payout_released_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("gst_invoice_number", sa.String(length=80), nullable=True))

    op.add_column("payments", sa.Column("gateway_order_id", sa.String(length=120), nullable=True))
    op.add_column("payments", sa.Column("gateway_payment_id", sa.String(length=120), nullable=True))
    op.add_column("payments", sa.Column("upi_vpa", sa.String(length=120), nullable=True))
    op.add_column("payments", sa.Column("refund_ref", sa.String(length=120), nullable=True))
    op.add_column("payments", sa.Column("refund_amount", sa.Numeric(12, 2), nullable=True))
    op.add_column("payments", sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("payments", sa.Column("webhook_event_ids", sa.JSON(), nullable=True))
    op.create_index(op.f("ix_payments_gateway_order_id"), "payments", ["gateway_order_id"], unique=True)
    op.create_index(op.f("ix_payments_gateway_payment_id"), "payments", ["gateway_payment_id"], unique=True)

    op.add_column(
        "shipments",
        sa.Column("shipping_provider", sa.String(length=64), nullable=False, server_default="SHIPROCKET_SANDBOX"),
    )
    op.add_column("shipments", sa.Column("label_url", sa.String(length=500), nullable=True))

    op.add_column("products", sa.Column("gi_claim_code", sa.String(length=100), nullable=True))
    op.add_column(
        "products",
        sa.Column("gi_verification_status", sa.String(length=50), nullable=False, server_default="NONE"),
    )
    op.add_column("products", sa.Column("gi_reviewer_notes", sa.Text(), nullable=True))

    op.add_column("purchase_orders", sa.Column("buyer_gstin", sa.String(length=32), nullable=True))
    op.add_column("purchase_orders", sa.Column("seller_gstin", sa.String(length=32), nullable=True))
    op.add_column(
        "purchase_orders",
        sa.Column("gst_rate_percent", sa.Numeric(5, 2), nullable=False, server_default="5.00"),
    )
    op.add_column(
        "purchase_orders",
        sa.Column("hsn_code", sa.String(length=32), nullable=False, server_default="5007"),
    )


def downgrade() -> None:
    op.drop_column("purchase_orders", "hsn_code")
    op.drop_column("purchase_orders", "gst_rate_percent")
    op.drop_column("purchase_orders", "seller_gstin")
    op.drop_column("purchase_orders", "buyer_gstin")

    op.drop_column("products", "gi_reviewer_notes")
    op.drop_column("products", "gi_verification_status")
    op.drop_column("products", "gi_claim_code")

    op.drop_column("shipments", "label_url")
    op.drop_column("shipments", "shipping_provider")

    op.drop_index(op.f("ix_payments_gateway_payment_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_gateway_order_id"), table_name="payments")
    op.drop_column("payments", "webhook_event_ids")
    op.drop_column("payments", "refunded_at")
    op.drop_column("payments", "refund_amount")
    op.drop_column("payments", "refund_ref")
    op.drop_column("payments", "upi_vpa")
    op.drop_column("payments", "gateway_payment_id")
    op.drop_column("payments", "gateway_order_id")

    op.drop_column("orders", "gst_invoice_number")
    op.drop_column("orders", "payout_released_at")
    op.drop_column("orders", "payout_status")
    op.drop_column("orders", "dispute_resolution")
    op.drop_column("orders", "dispute_reason")

