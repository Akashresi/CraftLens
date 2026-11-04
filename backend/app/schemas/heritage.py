from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


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
    raw_materials_source: Optional[str] = None
    craft_technique_details: Optional[str] = None
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
    last_scanned_at: Optional[datetime] = None


class PublicHeritageStoryOut(BaseModel):
    product_title: str
    category_name: str
    primary_material: Optional[str] = None
    technique: Optional[str] = None
    craft_origin_name: Optional[str] = None
    geographical_indication_code: Optional[str] = None
    artisan_name: str
    artisan_city: Optional[str] = None
    artisan_state: Optional[str] = None
    artisan_experience_years: int
    artisan_bio: Optional[str] = None
    verification_level: str
    batch_code: Optional[str] = None
    maker_signature_hash: Optional[str] = None
    verified_genuine: bool = True
    scan_count: int
