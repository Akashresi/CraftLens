from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArtisanApplicationCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    craft_specialization: str = Field(..., min_length=2, max_length=255)
    experience_years: int = Field(default=1, ge=0, le=100)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    portfolio_url: str | None = Field(None, max_length=500)
    craft_description: str = Field(..., min_length=10, max_length=5000)
    supporting_documents_url: str | None = Field(None, max_length=500)


class ArtisanApplicationReviewIn(BaseModel):
    reviewer_notes: str | None = Field(None, max_length=2000)


class ArtisanApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    applicant_email: str | None = None
    applicant_phone: str | None = None
    full_name: str
    craft_specialization: str
    experience_years: int
    city: str
    state: str
    portfolio_url: str | None = None
    craft_description: str
    supporting_documents_url: str | None = None
    status: str
    reviewer_notes: str | None = None
    reviewed_by_user_id: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
