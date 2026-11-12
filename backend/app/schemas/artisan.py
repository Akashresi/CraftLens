from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArtisanVerificationCreate(BaseModel):
    document_type: str = Field(..., description="PEHCHAN_CARD, AADHAAR, WEAVER_ID, COOP_CERTIFICATE")
    document_number: str | None = None
    document_url: str


class ArtisanVerificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_type: str
    document_number: str | None = None
    document_url: str
    status: str
    reviewer_notes: str | None = None
    verified_at: datetime | None = None
    created_at: datetime


class ArtisanProfileUpdate(BaseModel):
    craft_specialization: str | None = None
    bio: str | None = None
    experience_years: int | None = Field(None, ge=0, le=80)
    studio_address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    profile_image_url: str | None = None
    group_id: str | None = None
    bank_account_configured: bool | None = None


class ArtisanProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    group_id: str | None = None
    craft_specialization: str
    bio: str | None = None
    experience_years: int
    studio_address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    verification_level: str
    profile_image_url: str | None = None
    bank_account_configured: bool
    created_at: datetime
    updated_at: datetime
    verifications: list[ArtisanVerificationOut] = []


class KYCReviewIn(BaseModel):
    status: str = Field(..., description="APPROVED or REJECTED")
    reviewer_notes: str | None = None


class GIClaimSubmitIn(BaseModel):
    gi_claim_code: str = Field(..., min_length=3, max_length=100)
    notes: str | None = None


class GIClaimReviewIn(BaseModel):
    status: str = Field(..., description="APPROVED or REJECTED")
    reviewer_notes: str | None = None


class GIClaimOut(BaseModel):
    product_id: str
    product_title: str
    artisan_name: str
    gi_claim_code: str | None = None
    gi_verification_status: str
    gi_reviewer_notes: str | None = None
