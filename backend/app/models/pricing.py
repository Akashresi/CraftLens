import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CostComponent(Base):
    __tablename__ = "cost_components"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    material_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    labor_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0.00, nullable=False)
    labor_hourly_rate: Mapped[float] = mapped_column(Numeric(10, 2), default=150.00, nullable=False)  # Fair wage baseline
    packaging_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    transportation_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    overhead_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    total_production_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    product: Mapped["Product"] = relationship("Product", back_populates="cost_component")
    estimates: Mapped[list["PricingEstimate"]] = relationship("PricingEstimate", back_populates="cost_component")


class PricingEstimate(Base):
    __tablename__ = "pricing_estimates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    cost_component_id: Mapped[str] = mapped_column(String(36), ForeignKey("cost_components.id", ondelete="CASCADE"), nullable=False)

    min_selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    recommended_retail_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    recommended_wholesale_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    premium_export_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    profit_margin_percent: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 2), default=0.85)  # 0.00 to 1.00
    explanation_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship("Product", back_populates="pricing_estimates")
    cost_component: Mapped["CostComponent"] = relationship("CostComponent", back_populates="estimates")


class PricingHistory(Base):
    __tablename__ = "pricing_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    old_retail_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    new_retail_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MarketComparable(Base):
    __tablename__ = "market_comparables"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    source_platform: Mapped[str] = mapped_column(String(100), nullable=False)  # Amazon Karigar, Etsy, Fabindia, ONDC
    sample_title: Mapped[str] = mapped_column(String(255), nullable=False)
    price_range_min: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    price_range_max: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    recorded_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

