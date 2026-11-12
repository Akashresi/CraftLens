import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artisan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), default="INSTAGRAM")  # INSTAGRAM, WHATSAPP, FESTIVAL_CATALOG
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    assets: Mapped[list["MarketingAsset"]] = relationship(
        "MarketingAsset", back_populates="campaign", cascade="all, delete-orphan"
    )


class MarketingAsset(Base):
    __tablename__ = "marketing_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("marketing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # POSTER, CAPTION, STORY_BANNER, CATALOG_PDF
    content_text: Mapped[str] = mapped_column(Text, nullable=True)
    media_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    campaign: Mapped["MarketingCampaign"] = relationship("MarketingCampaign", back_populates="assets")


class BusinessExpense(Base):
    __tablename__ = "business_expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artisan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expense_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # RAW_MATERIALS, TOOLS, DYE, LOGISTICS, WORKSHOP_RENT
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    region: Mapped[str] = mapped_column(String(100), default="National")
    predicted_growth_rate: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    confidence_interval: Mapped[dict] = mapped_column(JSON, default=dict)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
