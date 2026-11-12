import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.buyer import Buyer
    from app.models.product import ProductVariant


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    buyer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("buyers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    order_type: Mapped[str] = mapped_column(String(50), default="RETAIL")  # RETAIL, WHOLESALE

    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    tax: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    shipping_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), default="PLACED", index=True
    )  # PLACED, PAID/CONFIRMED, PACKED, SHIPPED, DELIVERED, CANCELLED, RETURNED, DISPUTED
    delivery_address: Mapped[dict] = mapped_column(JSON, nullable=False)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispute_resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    payout_status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, ELIGIBLE, RELEASED, HELD
    payout_released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gst_invoice_number: Mapped[str | None] = mapped_column(String(80), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment: Mapped["Payment"] = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    shipment: Mapped["Shipment"] = relationship(
        "Shipment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False
    )
    artisan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_profiles.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="order_items")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    payment_gateway: Mapped[str] = mapped_column(String(50), default="SANDBOX")  # RAZORPAY_UPI, RAZORPAY, SANDBOX, COD
    transaction_ref: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    gateway_order_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    gateway_payment_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    upi_vpa: Mapped[str | None] = mapped_column(String(120), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    status: Mapped[str] = mapped_column(String(50), default="INITIATED")  # INITIATED, SUCCESS, FAILED, REFUNDED
    refund_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    refund_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    webhook_event_ids: Mapped[list] = mapped_column(JSON, default=list)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    order: Mapped["Order"] = relationship("Order", back_populates="payment")


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    shipping_provider: Mapped[str] = mapped_column(String(64), default="SHIPROCKET_SANDBOX")
    carrier: Mapped[str] = mapped_column(String(100), nullable=True)  # India Post, Delhivery, BlueDart, Ekart
    tracking_number: Mapped[str] = mapped_column(String(100), nullable=True)
    label_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="MANIFESTED"
    )  # MANIFESTED, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED
    shipped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    order: Mapped["Order"] = relationship("Order", back_populates="shipment")
