from pydantic import BaseModel, Field


class VoiceTranscribeOut(BaseModel):
    transcript: str
    detected_language: str
    confidence: float
    provider: str = "fallback"
    fallback_used: bool = False
    needs_confirmation: bool = True


class VoiceCatalogGenerateIn(BaseModel):
    transcript: str = Field(..., min_length=3)
    source_language: str = "ta"
    product_category_hint: str | None = None


class GeneratedCatalogOut(BaseModel):
    title_en: str
    title_hi: str
    title_local: str = ""
    description_en: str
    description_hi: str
    description_local: str = ""
    source_language: str = "ta"
    primary_material: str
    technique: str
    seo_keywords: list[str]
    suggested_category_slug: str
    requires_artisan_confirmation: bool = True
    listing_status: str = "DRAFT_PREVIEW"


class ApplyCatalogIn(BaseModel):
    title: str
    summary: str
    primary_material: str
    technique: str
    category_slug: str
    title_hi: str | None = None
    description_hi: str | None = None
    seo_keywords: list[str] = []
    source_transcript: str | None = None
    source_language: str = "ta"
    artisan_confirmed: bool = True
