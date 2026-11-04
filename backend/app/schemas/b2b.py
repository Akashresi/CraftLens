from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PurchaseRequestCreate(BaseModel):
    product_id: str
    target_quantity: int = Field(..., ge=5, description="Minimum B2B order quantity")
    target_unit_price: Optional[float] = None
    required_delivery_date: Optional[datetime] = None
    specifications: Optional[str] = None


class QuotationCreate(BaseModel):
    purchase_request_id: str
    quoted_unit_price: float = Field(..., gt=0)
    lead_time_days: int = Field(default=14, ge=1)
    terms_conditions: Optional[str] = None


class QuotationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    purchase_request_id: str
    artisan_id: str
    quoted_unit_price: float
    total_amount: float
    lead_time_days: int
    terms_conditions: Optional[str] = None
    status: str
    created_at: datetime


class PurchaseOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    quotation_id: str
    po_number: str
    payment_terms: str
    milestone_schedule: List[Any] = []
    status: str
    created_at: datetime


class PurchaseRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    buyer_id: str
    product_id: str
    target_quantity: int
    target_unit_price: Optional[float] = None
    required_delivery_date: Optional[datetime] = None
    specifications: Optional[str] = None
    status: str
    created_at: datetime
    quotations: List[QuotationOut] = []
