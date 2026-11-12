import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    batch_code: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_materials_source: Mapped[str] = mapped_column(String(255), nullable=True)
    craft_technique_details: Mapped[str] = mapped_column(Text, nullable=True)
    maker_signature_hash: Mapped[str] = mapped_column(
        String(128), nullable=False
    )  # Cryptographic hash of maker authenticity
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    product: Mapped["Product"] = relationship("Product", back_populates="provenance_records")


class ProductQR(Base):
    __tablename__ = "product_qr"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    qr_code_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    public_url: Mapped[str] = mapped_column(String(500), nullable=False)
    scan_count: Mapped[int] = mapped_column(Integer, default=0)
    last_scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    product: Mapped["Product"] = relationship("Product", back_populates="qr_code")
