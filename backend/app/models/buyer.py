import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.b2b import PurchaseRequest
    from app.models.order import Order
    from app.models.user import User


class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    buyer_type: Mapped[str] = mapped_column(String(50), default="RETAIL")  # RETAIL, WHOLESALE
    default_shipping_address: Mapped[dict] = mapped_column(JSON, default=dict)
    default_billing_address: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship("User", back_populates="buyer_profile")
    business_profile: Mapped["BuyerBusinessProfile"] = relationship(
        "BuyerBusinessProfile", back_populates="buyer", uselist=False
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="buyer")
    purchase_requests: Mapped[list["PurchaseRequest"]] = relationship("PurchaseRequest", back_populates="buyer")


class BuyerBusinessProfile(Base):
    __tablename__ = "buyer_business_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("buyers.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gst_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    pan_number: Mapped[str] = mapped_column(String(50), nullable=True)
    trade_license_url: Mapped[str] = mapped_column(String(500), nullable=True)
    verified_status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, VERIFIED, REJECTED
    credit_limit: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    website: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="business_profile")
