import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_role
from app.db.session import get_db
from app.models import AIJob, ArtisanProfile, Category, GeneratedDescription, Product, ProductTranslation, User
from app.schemas.common import APIResponse
from app.schemas.voice import ApplyCatalogIn, GeneratedCatalogOut, VoiceCatalogGenerateIn, VoiceTranscribeOut
from app.services.voice_catalog import extract_and_generate_catalog, transcribe_regional_audio

router = APIRouter()


@router.post("/transcribe", response_model=APIResponse[VoiceTranscribeOut])
def transcribe_voice(
    file: UploadFile = File(...),
    language_code: str = Form("ta"),
    current_user: User = Depends(get_current_active_user),
):
    """Transcribes spoken regional audio in Tamil, Hindi, Telugu, Kannada, Malayalam, or English."""
    contents = file.file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    result = transcribe_regional_audio(contents, language_code=language_code)
    return APIResponse(
        success=True,
        message="Voice speech transcribed successfully",
        data=VoiceTranscribeOut(**result),
    )


@router.post("/generate-catalog", response_model=APIResponse[GeneratedCatalogOut])
def generate_catalog_from_speech(
    catalog_in: VoiceCatalogGenerateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Processes regional transcript and produces professional multilingual titles,
    descriptions, craft materials, techniques, and SEO keywords.
    """
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    context = profile.craft_specialization if profile else None

    catalog = extract_and_generate_catalog(
        transcript=catalog_in.transcript,
        source_language=catalog_in.source_language,
        artisan_craft_specialization=context,
    )

    # Track AI Job record in database
    ai_job = AIJob(
        user_id=current_user.id,
        job_type="VOICE_CATALOG",
        status="COMPLETED",
        payload={"transcript": catalog_in.transcript, "language": catalog_in.source_language},
        result=catalog,
    )
    db.add(ai_job)
    db.commit()

    return APIResponse(
        success=True,
        message="AI catalog listing generated successfully",
        data=GeneratedCatalogOut(**catalog),
    )


@router.post("/apply-to-product", response_model=APIResponse[dict])
def apply_catalog_to_product(
    payload: ApplyCatalogIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Persists verified catalog data into a new or existing Product entity,
    creating translation records in English, Hindi, and regional languages.
    """
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Artisan profile not found")

    category = db.query(Category).filter(Category.slug == payload.category_slug).first()
    if not category:
        category = db.query(Category).first()
    if not category:
        raise HTTPException(status_code=400, detail="No craft categories configured")

    slug = payload.title.lower().replace(" ", "-")[:80] + "-" + str(uuid.uuid4())[:8]

    # Create Product
    product = Product(
        artisan_id=profile.id,
        category_id=category.id,
        title=payload.title,
        slug=slug,
        summary=payload.summary,
        primary_material=payload.primary_material,
        technique=payload.technique,
        status="DRAFT",
    )
    db.add(product)
    db.flush()

    # Store Speech & Generated Description record
    gen_desc = GeneratedDescription(
        product_id=product.id,
        source_language=payload.source_language,
        raw_speech_transcript=payload.source_transcript,
        generated_en=payload.summary,
        generated_hi=payload.description_hi or "",
        detected_tags={"keywords": payload.seo_keywords},
    )
    db.add(gen_desc)

    # Store English Translation
    trans_en = ProductTranslation(
        product_id=product.id,
        language_code="en",
        translated_title=payload.title,
        translated_description=payload.summary,
        seo_keywords=payload.seo_keywords,
    )
    db.add(trans_en)

    # Store Hindi Translation if provided
    if payload.title_hi and payload.description_hi:
        trans_hi = ProductTranslation(
            product_id=product.id,
            language_code="hi",
            translated_title=payload.title_hi,
            translated_description=payload.description_hi,
            seo_keywords=payload.seo_keywords,
        )
        db.add(trans_hi)

    db.commit()

    return APIResponse(
        success=True,
        message="Product listing created with multilingual descriptions",
        data={"product_id": product.id, "slug": product.slug},
    )
