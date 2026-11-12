import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import ProductVariant


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="inventory_record")
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement", back_populates="inventory", cascade="all, delete-orphan"
    )


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inventory_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity_change: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # positive for restock, negative for deduction
    movement_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PURCHASE_RECEIPT, SALE_DEDUCT, RETURN_RESTOCK, MANUAL_ADJUST
    reference_id: Mapped[str] = mapped_column(String(100), nullable=True)  # order_id or batch_number
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="movements")
