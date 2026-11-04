from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BuyerBusinessProfileUpdate(BaseModel):
    company_name: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    trade_license_url: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None


class BuyerBusinessProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    trade_license_url: Optional[str] = None
    verified_status: str
    credit_limit: float
    website: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class BuyerProfileUpdate(BaseModel):
    buyer_type: Optional[str] = Field(None, description="RETAIL or WHOLESALE")
    default_shipping_address: Optional[Dict[str, Any]] = None
    default_billing_address: Optional[Dict[str, Any]] = None


class BuyerProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    buyer_type: str
    default_shipping_address: Dict[str, Any]
    default_billing_address: Dict[str, Any]
    business_profile: Optional[BuyerBusinessProfileOut] = None
    created_at: datetime
    updated_at: datetime
