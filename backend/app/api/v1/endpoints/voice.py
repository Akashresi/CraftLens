import uuid

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_role
from app.core.rate_limit import rate_limit
from app.core.upload_security import sanitize_text, validate_audio_upload
from app.db.session import get_db
from app.models import (
    AIJob,
    ArtisanProfile,
    Category,
    GeneratedDescription,
    IdempotencyRecord,
    Product,
    ProductTranslation,
    User,
)
from app.schemas.common import APIResponse
from app.schemas.voice import ApplyCatalogIn, GeneratedCatalogOut, VoiceCatalogGenerateIn, VoiceTranscribeOut
from app.services.voice_catalog import extract_and_generate_catalog, transcribe_regional_audio

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=APIResponse[VoiceTranscribeOut],
    dependencies=[Depends(rate_limit("voice_upload", max_requests=20, window_seconds=60))],
)
def transcribe_voice(
    file: UploadFile = File(...),
    language_code: str = Form("ta"),
    current_user: User = Depends(get_current_active_user),
):
    """Transcribes spoken regional audio in Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Marathi, or English."""
    contents = file.file.read()
    validate_audio_upload(contents)

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
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
):
    """Persists artisan-confirmed catalog data as a DRAFT product (never auto-published).
    Supports X-Idempotency-Key so offline mobile retries never duplicate drafts.
    """
    require_role("ARTISAN")(current_user)
    idem_key = x_idempotency_key.strip() if isinstance(x_idempotency_key, str) and x_idempotency_key.strip() else None
    if idem_key:
        existing_idem = (
            db.query(IdempotencyRecord)
            .filter(
                IdempotencyRecord.user_id == current_user.id,
                IdempotencyRecord.endpoint == "voice.apply_to_product",
                IdempotencyRecord.idempotency_key == idem_key,
            )
            .first()
        )
        if existing_idem:
            return APIResponse(
                success=True,
                message="Product draft already synced (idempotent replay)",
                data={**existing_idem.response_payload, "idempotent_replay": True},
            )

    if not payload.artisan_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Artisan review and explicit confirmation is required before creating a product listing.",
        )
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
        title=sanitize_text(payload.title) or payload.title,
        slug=slug,
        summary=sanitize_text(payload.summary) or payload.summary,
        primary_material=sanitize_text(payload.primary_material),
        technique=sanitize_text(payload.technique),
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

    result_data = {"product_id": product.id, "slug": product.slug, "idempotent_replay": False}
    if idem_key:
        db.add(
            IdempotencyRecord(
                user_id=current_user.id,
                endpoint="voice.apply_to_product",
                idempotency_key=idem_key,
                response_payload=result_data,
            )
        )
    db.commit()

    return APIResponse(
        success=True,
        message="Product listing created with multilingual descriptions",
        data=result_data,
    )
