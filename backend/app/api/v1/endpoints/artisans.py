from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models import User, ArtisanProfile, ArtisanVerification
from app.schemas.artisan import (
    ArtisanProfileOut,
    ArtisanProfileUpdate,
    ArtisanVerificationCreate,
    ArtisanVerificationOut,
)
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role

router = APIRouter()


@router.get("/me", response_model=APIResponse[ArtisanProfileOut])
def get_my_artisan_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Retrieves profile and verification history for the authenticated artisan."""
    profile = (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        profile = ArtisanProfile(
            user_id=current_user.id,
            craft_specialization="Handmade Crafts",
            experience_years=1,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return APIResponse(
        success=True,
        message="Artisan profile loaded",
        data=ArtisanProfileOut.model_validate(profile),
    )


@router.put("/me", response_model=APIResponse[ArtisanProfileOut])
def update_my_artisan_profile(
    profile_in: ArtisanProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Updates studio location, experience, craft specialization, and bank details."""
    profile = (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        profile = ArtisanProfile(user_id=current_user.id, craft_specialization="")
        db.add(profile)

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return APIResponse(
        success=True,
        message="Artisan profile updated successfully",
        data=ArtisanProfileOut.model_validate(profile),
    )


@router.post("/me/verify", response_model=APIResponse[ArtisanVerificationOut])
def submit_artisan_verification(
    verification_in: ArtisanVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Submits government or craft ID (Pehchan card, Weaver ID, Aadhaar) for artisan verification."""
    profile = (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan profile not found",
        )

    verification = ArtisanVerification(
        artisan_profile_id=profile.id,
        document_type=verification_in.document_type,
        document_number=verification_in.document_number,
        document_url=verification_in.document_url,
        status="PENDING",
    )
    db.add(verification)
    profile.verification_level = "SUBMITTED"
    db.commit()
    db.refresh(verification)

    return APIResponse(
        success=True,
        message="Verification document submitted for review",
        data=ArtisanVerificationOut.model_validate(verification),
    )


@router.get("/{artisan_id}", response_model=APIResponse[ArtisanProfileOut])
def get_public_artisan_profile(
    artisan_id: str,
    db: Session = Depends(get_db),
):
    """Public storefront view of an artisan's profile, craft background, and verified status."""
    profile = (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.id == artisan_id)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan not found",
        )

    return APIResponse(
        success=True,
        message="Public artisan profile loaded",
        data=ArtisanProfileOut.model_validate(profile),
    )

