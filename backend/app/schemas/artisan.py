from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ArtisanVerificationCreate(BaseModel):
    document_type: str = Field(..., description="PEHCHAN_CARD, AADHAAR, WEAVER_ID, COOP_CERTIFICATE")
    document_number: Optional[str] = None
    document_url: str


class ArtisanVerificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_type: str
    document_number: Optional[str] = None
    document_url: str
    status: str
    reviewer_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime


class ArtisanProfileUpdate(BaseModel):
    craft_specialization: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=80)
    studio_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    profile_image_url: Optional[str] = None
    group_id: Optional[str] = None
    bank_account_configured: Optional[bool] = None


class ArtisanProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    group_id: Optional[str] = None
    craft_specialization: str
    bio: Optional[str] = None
    experience_years: int
    studio_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    verification_level: str
    profile_image_url: Optional[str] = None
    bank_account_configured: bool
    created_at: datetime
    updated_at: datetime
    verifications: List[ArtisanVerificationOut] = []

