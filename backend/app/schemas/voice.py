from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class VoiceTranscribeOut(BaseModel):
    transcript: str
    detected_language: str
    confidence: float


class VoiceCatalogGenerateIn(BaseModel):
    transcript: str = Field(..., min_length=5)
    source_language: str = Field(default="ta", description="ta, hi, en, te, kn, ml")
    craft_context: Optional[str] = None


class GeneratedCatalogOut(BaseModel):
    title_en: str
    title_hi: str
    description_en: str
    description_hi: str
    primary_material: str
    technique: str
    seo_keywords: List[str]
    suggested_category_slug: str


class ApplyCatalogIn(BaseModel):
    product_id: Optional[str] = None
    title: str
    summary: str
    primary_material: str
    technique: str
    category_slug: str
    title_hi: Optional[str] = None
    description_hi: Optional[str] = None
    seo_keywords: List[str] = []
    source_transcript: Optional[str] = None
    source_language: str = "ta"
