from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None


class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    raw_url: str
    processed_url: str | None = None
    background_type: str
    is_primary: bool
    quality_score: float


class ProductVariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sku: str
    title: str
    color: str | None = None
    size: str | None = None
    price_retail: float
    price_wholesale: float
    min_wholesale_qty: int
    stock_quantity: int


class ProductPublicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    summary: str | None = None
    primary_material: str | None = None
    technique: str | None = None
    dimensions: str | None = None
    status: str
    view_count: int
    category: CategoryOut
    variants: list[ProductVariantOut] = []
    images: list[ProductImageOut] = []
    artisan_name: str | None = None
    artisan_city: str | None = None
    artisan_verification_level: str | None = None
    created_at: datetime


class CartItemIn(BaseModel):
    variant_id: str
    quantity: int = Field(..., ge=1)


class OrderCreateIn(BaseModel):
    items: list[CartItemIn]
    order_type: str = Field(default="RETAIL", description="RETAIL or WHOLESALE")
    delivery_address: dict[str, Any]
    payment_method: str = Field(default="SANDBOX", description="SANDBOX, RAZORPAY, COD")


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_variant_id: str
    artisan_id: str
    quantity: int
    unit_price: float
    total_price: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_number: str
    buyer_id: str
    order_type: str
    subtotal: float
    discount: float
    tax: float
    shipping_fee: float
    total_amount: float
    status: str
    delivery_address: dict[str, Any]
    items: list[OrderItemOut] = []
    created_at: datetime
