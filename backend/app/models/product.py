import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artisan_id: Mapped[str] = mapped_column(String(36), ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    craft_origin_id: Mapped[str] = mapped_column(String(36), ForeignKey("craft_origins.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    primary_material: Mapped[str] = mapped_column(String(100), nullable=True)
    technique: Mapped[str] = mapped_column(String(100), nullable=True)
    dimensions: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g., "12x8x4 inches"
    weight_grams: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", index=True)  # DRAFT, PENDING_REVIEW, ACTIVE, ARCHIVED
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    artisan: Mapped["ArtisanProfile"] = relationship("ArtisanProfile", back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    craft_origin: Mapped["CraftOrigin"] = relationship("CraftOrigin", back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    translations: Mapped[list["ProductTranslation"]] = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")
    generated_descriptions: Mapped[list["GeneratedDescription"]] = relationship("GeneratedDescription", back_populates="product", cascade="all, delete-orphan")
    cost_component: Mapped["CostComponent"] = relationship("CostComponent", back_populates="product", uselist=False, cascade="all, delete-orphan")
    pricing_estimates: Mapped[list["PricingEstimate"]] = relationship("PricingEstimate", back_populates="product", cascade="all, delete-orphan")
    provenance_records: Mapped[list["ProvenanceRecord"]] = relationship("ProvenanceRecord", back_populates="product", cascade="all, delete-orphan")
    qr_code: Mapped["ProductQR"] = relationship("ProductQR", back_populates="product", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=True)
    size: Mapped[str] = mapped_column(String(50), nullable=True)
    price_retail: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    price_wholesale: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    min_wholesale_qty: Mapped[int] = mapped_column(Integer, default=10)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    inventory_record: Mapped["Inventory"] = relationship("Inventory", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="variant")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_url: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_url: Mapped[str] = mapped_column(String(500), nullable=True)
    background_type: Mapped[str] = mapped_column(String(50), default="ORIGINAL")  # ORIGINAL, WHITE, LIFESTYLE
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)  # Blur / lighting analysis score (0.0 to 10.0)

    product: Mapped["Product"] = relationship("Product", back_populates="images")


class ProductTranslation(Base):
    __tablename__ = "product_translations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # ta, hi, en, te, kn, ml
    translated_title: Mapped[str] = mapped_column(String(255), nullable=False)
    translated_description: Mapped[str] = mapped_column(Text, nullable=False)
    seo_keywords: Mapped[list] = mapped_column(JSON, default=list)

    product: Mapped["Product"] = relationship("Product", back_populates="translations")


class GeneratedDescription(Base):
    __tablename__ = "generated_descriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    source_language: Mapped[str] = mapped_column(String(10), default="ta")
    raw_speech_transcript: Mapped[str] = mapped_column(Text, nullable=True)
    generated_en: Mapped[str] = mapped_column(Text, nullable=False)
    generated_hi: Mapped[str] = mapped_column(Text, nullable=True)
    detected_tags: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship("Product", back_populates="generated_descriptions")

