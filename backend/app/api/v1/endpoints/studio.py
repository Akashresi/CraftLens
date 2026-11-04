import os
import uuid
import time
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, ImageProcessingJob
from app.schemas.studio import QualityAnalysisOut, StudioProcessResult
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role
from app.services.image_studio import (
    analyze_image_quality,
    remove_product_background,
    correct_lighting_and_color,
    generate_studio_white_background,
    generate_lifestyle_background,
)

router = APIRouter()

UPLOAD_BASE = "./uploads"
os.makedirs(f"{UPLOAD_BASE}/original", exist_ok=True)
os.makedirs(f"{UPLOAD_BASE}/processed", exist_ok=True)


@router.post("/analyze", response_model=APIResponse[QualityAnalysisOut])
def analyze_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """Analyzes photo quality, blur (Laplacian variance), and exposure before catalog creation."""
    contents = file.file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    analysis = analyze_image_quality(contents)
    return APIResponse(
        success=True,
        message="Image quality analysis completed",
        data=QualityAnalysisOut(**analysis),
    )


@router.post("/process", response_model=APIResponse[StudioProcessResult])
def process_product_photo(
    file: UploadFile = File(...),
    lifestyle_theme: str = Form("wood"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Processes product image through studio pipeline: quality analysis, background removal,
    lighting correction, pure white drop shadow generation, and lifestyle staging.
    """
    start_time = time.time()
    raw_bytes = file.file.read()
    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"

    # Save original image
    orig_path = f"{UPLOAD_BASE}/original/{file_id}.{ext}"
    with open(orig_path, "wb") as f:
        f.write(raw_bytes)
    original_url = f"/uploads/original/{file_id}.{ext}"

    # 1. Quality analysis
    quality_result = analyze_image_quality(raw_bytes)
    quality_score = quality_result["quality_score"]

    # 2. Lighting correction
    lit_bytes = correct_lighting_and_color(raw_bytes)

    # 3. Background removal
    transparent_png_bytes = remove_product_background(lit_bytes)
    trans_path = f"{UPLOAD_BASE}/processed/{file_id}_transparent.png"
    with open(trans_path, "wb") as f:
        f.write(transparent_png_bytes)
    transparent_url = f"/uploads/processed/{file_id}_transparent.png"

    # 4. White studio background with drop shadow
    white_bg_bytes = generate_studio_white_background(transparent_png_bytes)
    white_path = f"{UPLOAD_BASE}/processed/{file_id}_white.jpg"
    with open(white_path, "wb") as f:
        f.write(white_bg_bytes)
    white_url = f"/uploads/processed/{file_id}_white.jpg"

    # 5. Lifestyle background
    lifestyle_bytes = generate_lifestyle_background(transparent_png_bytes, theme=lifestyle_theme)
    lifestyle_path = f"{UPLOAD_BASE}/processed/{file_id}_lifestyle.jpg"
    with open(lifestyle_path, "wb") as f:
        f.write(lifestyle_bytes)
    lifestyle_url = f"/uploads/processed/{file_id}_lifestyle.jpg"

    elapsed_ms = int((time.time() - start_time) * 1000)

    # Record job in database
    job = ImageProcessingJob(
        id=file_id,
        user_id=current_user.id,
        original_image_url=original_url,
        processed_image_url=white_url,
        operation="STUDIO_FULL_PIPELINE",
        status="COMPLETED",
        latency_ms=elapsed_ms,
    )
    db.add(job)
    db.commit()

    return APIResponse(
        success=True,
        message="Product photo studio processing complete",
        data=StudioProcessResult(
            job_id=file_id,
            original_url=original_url,
            white_bg_url=white_url,
            lifestyle_url=lifestyle_url,
            transparent_png_url=transparent_url,
            quality_score=quality_score,
            latency_ms=elapsed_ms,
            status="COMPLETED",
        ),
    )
