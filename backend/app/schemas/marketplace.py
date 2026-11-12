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
    payment_method: str = Field(default="SANDBOX", description="SANDBOX, RAZORPAY_UPI, RAZORPAY, COD")
    upi_vpa: str | None = None


class PaymentSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_gateway: str
    transaction_ref: str | None = None
    gateway_order_id: str | None = None
    gateway_payment_id: str | None = None
    upi_vpa: str | None = None
    status: str
    refund_ref: str | None = None
    refund_amount: float | None = None


class ShipmentSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shipping_provider: str = "SHIPROCKET_SANDBOX"
    carrier: str | None = None
    tracking_number: str | None = None
    label_url: str | None = None
    status: str


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
    dispute_reason: str | None = None
    dispute_resolution: str | None = None
    payout_status: str = "PENDING"
    gst_invoice_number: str | None = None
    upi_intent_uri: str | None = None
    payment: PaymentSummaryOut | None = None
    shipment: ShipmentSummaryOut | None = None
    items: list[OrderItemOut] = []
    created_at: datetime


class OrderTransitionIn(BaseModel):
    target_status: str = Field(
        ..., description="PLACED, PAID, PACKED, SHIPPED, DELIVERED, CANCELLED, RETURNED, DISPUTED"
    )
    carrier: str | None = None
    notes: str | None = None


class OrderRefundIn(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    reason: str = Field(default="Customer cancellation / return", max_length=500)


class OrderDisputeIn(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)


class DisputeResolveIn(BaseModel):
    resolution_status: str = Field(..., description="CANCELLED, RETURNED, DELIVERED, or PAID")
    resolution_notes: str = Field(..., min_length=3, max_length=1000)


class OrderReviewCreateIn(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    buyer_id: str
    rating: int
    comment: str | None = None
    is_verified_purchase: bool
    created_at: datetime
