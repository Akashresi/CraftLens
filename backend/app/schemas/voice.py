from pydantic import BaseModel, Field


class VoiceTranscribeOut(BaseModel):
    transcript: str
    detected_language: str
    confidence: float


class VoiceCatalogGenerateIn(BaseModel):
    transcript: str = Field(..., min_length=5)
    source_language: str = Field(default="ta", description="ta, hi, en, te, kn, ml")
    craft_context: str | None = None


class GeneratedCatalogOut(BaseModel):
    title_en: str
    title_hi: str
    description_en: str
    description_hi: str
    primary_material: str
    technique: str
    seo_keywords: list[str]
    suggested_category_slug: str


class ApplyCatalogIn(BaseModel):
    product_id: str | None = None
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
