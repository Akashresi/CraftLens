from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ArtisanApplicationCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    craft_specialization: str = Field(..., min_length=2, max_length=255)
    experience_years: int = Field(default=1, ge=0, le=100)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    craft_description: str = Field(..., min_length=10, max_length=5000)
    supporting_documents_url: Optional[str] = Field(None, max_length=500)


class ArtisanApplicationReviewIn(BaseModel):
    reviewer_notes: Optional[str] = Field(None, max_length=2000)


class ArtisanApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    applicant_email: Optional[str] = None
    applicant_phone: Optional[str] = None
    full_name: str
    craft_specialization: str
    experience_years: int
    city: str
    state: str
    portfolio_url: Optional[str] = None
    craft_description: str
    supporting_documents_url: Optional[str] = None
    status: str
    reviewer_notes: Optional[str] = None
    reviewed_by_user_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
