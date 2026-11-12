from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BuyerBusinessProfileUpdate(BaseModel):
    company_name: str
    gst_number: str | None = None
    pan_number: str | None = None
    trade_license_url: str | None = None
    website: str | None = None
    notes: str | None = None


class BuyerBusinessProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    gst_number: str | None = None
    pan_number: str | None = None
    trade_license_url: str | None = None
    verified_status: str
    credit_limit: float
    website: str | None = None
    notes: str | None = None
    created_at: datetime


class BuyerProfileUpdate(BaseModel):
    buyer_type: str | None = Field(None, description="RETAIL or WHOLESALE")
    default_shipping_address: dict[str, Any] | None = None
    default_billing_address: dict[str, Any] | None = None


class BuyerProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    buyer_type: str
    default_shipping_address: dict[str, Any]
    default_billing_address: dict[str, Any]
    business_profile: BuyerBusinessProfileOut | None = None
    created_at: datetime
    updated_at: datetime
