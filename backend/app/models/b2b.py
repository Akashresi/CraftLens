import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.buyer import Buyer


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )

    target_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    target_unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    required_delivery_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    specifications: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN")  # OPEN, RESPONDED, ACCEPTED, REJECTED, EXPIRED

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="purchase_requests")
    quotations: Mapped[list["Quotation"]] = relationship(
        "Quotation", back_populates="purchase_request", cascade="all, delete-orphan"
    )


class Quotation(Base):
    __tablename__ = "quotations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    purchase_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artisan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    quoted_unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=14)
    terms_conditions: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, ACCEPTED, REJECTED, EXPIRED

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    purchase_request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="quotations")
    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="quotation", uselist=False)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quotation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quotations.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    po_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(100), default="30% Advance, 70% on Dispatch")
    milestone_schedule: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(
        String(50), default="DRAFT"
    )  # DRAFT, ISSUED, IN_PRODUCTION, FULFILLED, CANCELLED

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="purchase_order")
