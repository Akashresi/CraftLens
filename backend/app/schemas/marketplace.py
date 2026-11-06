from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    raw_url: str
    processed_url: Optional[str] = None
    background_type: str
    is_primary: bool
    quality_score: float


class ProductVariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sku: str
    title: str
    color: Optional[str] = None
    size: Optional[str] = None
    price_retail: float
    price_wholesale: float
    min_wholesale_qty: int
    stock_quantity: int


class ProductPublicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    summary: Optional[str] = None
    primary_material: Optional[str] = None
    technique: Optional[str] = None
    dimensions: Optional[str] = None
    status: str
    view_count: int
    category: CategoryOut
    variants: List[ProductVariantOut] = []
    images: List[ProductImageOut] = []
    artisan_name: Optional[str] = None
    artisan_city: Optional[str] = None
    artisan_verification_level: Optional[str] = None
    created_at: datetime


class CartItemIn(BaseModel):
    variant_id: str
    quantity: int = Field(..., ge=1)


class OrderCreateIn(BaseModel):
    items: List[CartItemIn]
    order_type: str = Field(default="RETAIL", description="RETAIL or WHOLESALE")
    delivery_address: Dict[str, Any]
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
    delivery_address: Dict[str, Any]
    items: List[OrderItemOut] = []
    created_at: datetime

