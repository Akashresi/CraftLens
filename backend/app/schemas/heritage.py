from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceCreateIn(BaseModel):
    product_id: str
    batch_code: str = Field(..., min_length=3)
    raw_materials_source: str
    craft_technique_details: str


class ProvenanceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    batch_code: str
    raw_materials_source: str | None = None
    craft_technique_details: str | None = None
    maker_signature_hash: str
    created_at: datetime


class ProductQROut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    qr_code_hash: str
    public_url: str
    qr_image_url: str
    scan_count: int
    last_scanned_at: datetime | None = None


class PublicHeritageStoryOut(BaseModel):
    product_title: str
    category_name: str
    primary_material: str | None = None
    technique: str | None = None
    craft_origin_name: str | None = None
    geographical_indication_code: str | None = None
    artisan_name: str
    artisan_city: str | None = None
    artisan_state: str | None = None
    artisan_experience_years: int
    artisan_bio: str | None = None
    verification_level: str
    batch_code: str | None = None
    maker_signature_hash: str | None = None
    verified_genuine: bool = True
    scan_count: int
