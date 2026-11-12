import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ImageProcessingJob(Base):
    __tablename__ = "image_processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    operation: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # BG_REMOVAL, LIGHTING_ENHANCE, UPSCALING, LIFESTYLE_GEN
    status: Mapped[str] = mapped_column(
        String(50), default="QUEUED", index=True
    )  # QUEUED, PROCESSING, COMPLETED, FAILED
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # VOICE_CATALOG, PRICING_CALC, MARKETING_COPY, DEMAND_PREDICT
    status: Mapped[str] = mapped_column(
        String(50), default="QUEUED", index=True
    )  # QUEUED, PROCESSING, COMPLETED, FAILED
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
