from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.upload_security import sanitize_text
from app.db.session import get_db
from app.models import ArtisanProfile, ArtisanVerification, AuditLog, Product, User
from app.schemas.artisan import (
    ArtisanProfileOut,
    ArtisanProfileUpdate,
    ArtisanVerificationCreate,
    ArtisanVerificationOut,
    GIClaimOut,
    GIClaimReviewIn,
    GIClaimSubmitIn,
    KYCReviewIn,
)
from app.schemas.common import APIResponse
from app.services.commerce_providers import notification_provider, run_kyc_verification_hook

router = APIRouter()


@router.get("/me", response_model=APIResponse[ArtisanProfileOut])
def get_my_artisan_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Retrieves profile and verification history for the authenticated artisan."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
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
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
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
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
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


@router.post("/me/kyc-hook", response_model=APIResponse[dict])
def submit_seller_kyc_hook(
    verification_in: ArtisanVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Runs Indian craft KYC format check (PAN/Masked Aadhaar/GSTIN/Pehchan) and queues Admin review."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artisan profile not found")

    hook_result = run_kyc_verification_hook(verification_in.document_type, verification_in.document_number)
    verification = ArtisanVerification(
        artisan_profile_id=profile.id,
        document_type=verification_in.document_type.upper(),
        document_number=verification_in.document_number,
        document_url=verification_in.document_url,
        status="PENDING",
        reviewer_notes=hook_result["message"],
    )
    db.add(verification)
    profile.verification_level = "SUBMITTED"
    db.commit()
    db.refresh(verification)
    return APIResponse(
        success=True,
        message=hook_result["message"],
        data={"verification": ArtisanVerificationOut.model_validate(verification), "kyc_hook": hook_result},
    )


@router.get("/admin/verifications", response_model=APIResponse[list[ArtisanVerificationOut]])
def admin_list_kyc_verifications(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Admin endpoint listing artisan KYC verification submissions."""
    query = db.query(ArtisanVerification)
    if status_filter:
        query = query.filter(ArtisanVerification.status == status_filter.upper())
    items = query.order_by(ArtisanVerification.created_at.desc()).all()
    return APIResponse(
        success=True,
        message="KYC verifications retrieved",
        data=[ArtisanVerificationOut.model_validate(v) for v in items],
    )


@router.post("/admin/verifications/{verification_id}/review", response_model=APIResponse[ArtisanVerificationOut])
def admin_review_kyc_verification(
    verification_id: str,
    payload: KYCReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Admin approves or rejects artisan seller KYC document."""
    ver = db.query(ArtisanVerification).filter(ArtisanVerification.id == verification_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="Verification record not found")
    decision = payload.status.strip().upper()
    if decision not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Status must be APPROVED or REJECTED")

    ver.status = decision
    ver.reviewer_notes = sanitize_text(payload.reviewer_notes) or ""
    ver.verified_by_user_id = current_user.id
    ver.verified_at = datetime.now(UTC)

    profile = db.query(ArtisanProfile).filter(ArtisanProfile.id == ver.artisan_profile_id).first()
    if profile and decision == "APPROVED":
        profile.verification_level = "GOVT_ID_VERIFIED"

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="ARTISAN_KYC_REVIEWED",
            resource=f"verification:{ver.id}",
            details={"decision": decision, "notes": ver.reviewer_notes},
        )
    )
    db.commit()
    db.refresh(ver)
    return APIResponse(
        success=True,
        message=f"Artisan KYC {decision.lower()}",
        data=ArtisanVerificationOut.model_validate(ver),
    )


@router.post("/products/{product_id}/gi-claim", response_model=APIResponse[GIClaimOut])
def submit_product_gi_claim(
    product_id: str,
    payload: GIClaimSubmitIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Artisan attaches a Geographical Indication (GI) claim to their product for admin verification."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if "ADMIN" not in [r.code for r in current_user.roles] and (
        not product.artisan or product.artisan.user_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Only product owner can submit GI claims")

    product.gi_claim_code = sanitize_text(payload.gi_claim_code)
    product.gi_verification_status = "PENDING"
    product.gi_reviewer_notes = sanitize_text(payload.notes) if payload.notes else None
    db.commit()
    db.refresh(product)

    artisan_name = product.artisan.user.full_name if product.artisan and product.artisan.user else "Artisan"
    return APIResponse(
        success=True,
        message="GI claim submitted for verification",
        data=GIClaimOut(
            product_id=product.id,
            product_title=product.title,
            artisan_name=artisan_name,
            gi_claim_code=product.gi_claim_code,
            gi_verification_status=product.gi_verification_status,
            gi_reviewer_notes=product.gi_reviewer_notes,
        ),
    )


@router.get("/admin/gi-claims", response_model=APIResponse[list[GIClaimOut]])
def admin_list_gi_claims(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Lists product GI-tag claims awaiting or completed Admin verification."""
    query = db.query(Product).filter(Product.gi_verification_status != "NONE")
    if status_filter:
        query = query.filter(Product.gi_verification_status == status_filter.upper())
    prods = query.order_by(Product.updated_at.desc()).all()
    items = [
        GIClaimOut(
            product_id=p.id,
            product_title=p.title,
            artisan_name=p.artisan.user.full_name if p.artisan and p.artisan.user else "Artisan",
            gi_claim_code=p.gi_claim_code,
            gi_verification_status=p.gi_verification_status,
            gi_reviewer_notes=p.gi_reviewer_notes,
        )
        for p in prods
    ]
    return APIResponse(success=True, message="GI claims retrieved", data=items)


@router.post("/admin/gi-claims/{product_id}/review", response_model=APIResponse[GIClaimOut])
def admin_review_gi_claim(
    product_id: str,
    payload: GIClaimReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Admin approves or rejects a product's Geographical Indication claim and notifies the artisan."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    decision = payload.status.strip().upper()
    if decision not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Status must be APPROVED or REJECTED")

    product.gi_verification_status = decision
    product.gi_reviewer_notes = sanitize_text(payload.reviewer_notes) if payload.reviewer_notes else None
    if product.artisan and product.artisan.user:
        notification_provider.dispatch(
            db=db,
            user_id=product.artisan.user.id,
            language=product.artisan.user.preferred_language,
            event="GI_STATUS_UPDATED",
            ref=product.title,
            extra=decision,
        )
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="GI_CLAIM_REVIEWED",
            resource=f"product:{product.id}",
            details={"decision": decision, "gi_claim_code": product.gi_claim_code, "notes": product.gi_reviewer_notes},
        )
    )
    db.commit()
    db.refresh(product)

    artisan_name = product.artisan.user.full_name if product.artisan and product.artisan.user else "Artisan"
    return APIResponse(
        success=True,
        message=f"GI claim {decision.lower()}",
        data=GIClaimOut(
            product_id=product.id,
            product_title=product.title,
            artisan_name=artisan_name,
            gi_claim_code=product.gi_claim_code,
            gi_verification_status=product.gi_verification_status,
            gi_reviewer_notes=product.gi_reviewer_notes,
        ),
    )


@router.get("/{artisan_id}", response_model=APIResponse[ArtisanProfileOut])
def get_public_artisan_profile(
    artisan_id: str,
    db: Session = Depends(get_db),
):
    """Public storefront view of an artisan's profile, craft background, and verified status."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.id == artisan_id).first()
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
