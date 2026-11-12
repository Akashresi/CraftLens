import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class ArtisanGroup(Base):
    __tablename__ = "artisan_groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    group_type: Mapped[str] = mapped_column(String(100), default="SHG")  # SHG, COOPERATIVE, WEAVER_CLUSTER
    contact_person: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    artisans: Mapped[list["ArtisanProfile"]] = relationship("ArtisanProfile", back_populates="group")


class ArtisanProfile(Base):
    __tablename__ = "artisan_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_groups.id", ondelete="SET NULL"), nullable=True
    )

    craft_specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=1)
    studio_address: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str] = mapped_column(String(16), nullable=True)
    verification_level: Mapped[str] = mapped_column(
        String(50), default="UNVERIFIED"
    )  # UNVERIFIED, SUBMITTED, PEER_VERIFIED, GOVT_ID_VERIFIED, MASTER_ARTISAN
    profile_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bank_account_configured: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="artisan_profile")
    group: Mapped["ArtisanGroup"] = relationship("ArtisanGroup", back_populates="artisans")
    verifications: Mapped[list["ArtisanVerification"]] = relationship(
        "ArtisanVerification", back_populates="artisan_profile"
    )
    stories: Mapped[list["ArtisanStory"]] = relationship("ArtisanStory", back_populates="artisan_profile")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="artisan")


class ArtisanVerification(Base):
    __tablename__ = "artisan_verifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artisan_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # PEHCHAN_CARD, AADHAAR, WEAVER_ID, COOP_CERTIFICATE
    document_number: Mapped[str] = mapped_column(String(100), nullable=True)
    document_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    reviewer_notes: Mapped[str] = mapped_column(Text, nullable=True)
    verified_by_user_id: Mapped[str] = mapped_column(String(36), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    artisan_profile: Mapped["ArtisanProfile"] = relationship("ArtisanProfile", back_populates="verifications")


class ArtisanStory(Base):
    __tablename__ = "artisan_stories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artisan_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    story_body: Mapped[str] = mapped_column(Text, nullable=False)
    audio_clip_url: Mapped[str] = mapped_column(String(500), nullable=True)
    video_clip_url: Mapped[str] = mapped_column(String(500), nullable=True)
    is_heritage_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    artisan_profile: Mapped["ArtisanProfile"] = relationship("ArtisanProfile", back_populates="stories")
