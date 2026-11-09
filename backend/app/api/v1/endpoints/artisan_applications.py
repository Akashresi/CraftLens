from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, Role, ArtisanProfile, ArtisanApplication, AuditLog
from app.schemas.artisan_application import (
    ArtisanApplicationCreate,
    ArtisanApplicationReviewIn,
    ArtisanApplicationOut,
)
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role

router = APIRouter()


def _format_application_out(app: ArtisanApplication) -> ArtisanApplicationOut:
    return ArtisanApplicationOut(
        id=app.id,
        user_id=app.user_id,
        applicant_email=app.user.email if app.user else None,
        applicant_phone=app.user.phone if app.user else None,
        full_name=app.full_name,
        craft_specialization=app.craft_specialization,
        experience_years=app.experience_years,
        city=app.city,
        state=app.state,
        portfolio_url=app.portfolio_url,
        craft_description=app.craft_description,
        supporting_documents_url=app.supporting_documents_url,
        status=app.status,
        reviewer_notes=app.reviewer_notes,
        reviewed_by_user_id=app.reviewed_by_user_id,
        reviewed_at=app.reviewed_at,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


@router.post("/me", response_model=APIResponse[ArtisanApplicationOut])
def submit_artisan_application(
    app_in: ArtisanApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submits a new application to become a verified artisan.
    - User must not already be an artisan.
    - Prevents duplicate pending applications.
    - Submitting does NOT automatically grant the artisan role.
    """
    user_role_codes = [r.code for r in current_user.roles]
    if "ARTISAN" in user_role_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already an approved artisan on CraftLens.",
        )

    # Check for existing pending application
    existing_pending = (
        db.query(ArtisanApplication)
        .filter(
            ArtisanApplication.user_id == current_user.id,
            ArtisanApplication.status == "PENDING",
        )
        .first()
    )
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending artisan application under review.",
        )

    new_app = ArtisanApplication(
        user_id=current_user.id,
        full_name=app_in.full_name,
        craft_specialization=app_in.craft_specialization,
        experience_years=app_in.experience_years,
        city=app_in.city,
        state=app_in.state,
        portfolio_url=app_in.portfolio_url,
        craft_description=app_in.craft_description,
        supporting_documents_url=app_in.supporting_documents_url,
        status="PENDING",
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return APIResponse(
        success=True,
        message="Artisan application submitted successfully and is pending review.",
        data=_format_application_out(new_app),
    )


@router.get("/me", response_model=APIResponse[Optional[ArtisanApplicationOut]])
def get_my_artisan_application(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves the latest artisan application status for the current user."""
    latest_app = (
        db.query(ArtisanApplication)
        .filter(ArtisanApplication.user_id == current_user.id)
        .order_by(ArtisanApplication.created_at.desc())
        .first()
    )
    if not latest_app:
        return APIResponse(
            success=True,
            message="No artisan applications found for current user.",
            data=None,
        )

    return APIResponse(
        success=True,
        message="Application status retrieved.",
        data=_format_application_out(latest_app),
    )


@router.get("/admin", response_model=APIResponse[List[ArtisanApplicationOut]])
def list_artisan_applications_admin(
    status_filter: Optional[str] = Query(None, alias="status", description="PENDING, APPROVED, REJECTED"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Admin endpoint to list and filter all artisan applications."""
    require_role("ADMIN")(current_user)
    query = db.query(ArtisanApplication)
    if status_filter and isinstance(status_filter, str):
        query = query.filter(ArtisanApplication.status == status_filter.upper())
    
    applications = query.order_by(ArtisanApplication.created_at.desc()).all()
    out_list = [_format_application_out(app) for app in applications]

    return APIResponse(
        success=True,
        message=f"Retrieved {len(out_list)} artisan applications",
        data=out_list,
    )


@router.post("/admin/{application_id}/approve", response_model=APIResponse[ArtisanApplicationOut])
def approve_artisan_application(
    application_id: str,
    review_in: Optional[ArtisanApplicationReviewIn] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Approves an artisan application within an atomic database transaction:
    1. Verifies application is still pending.
    2. Updates status to APPROVED and records review metadata.
    3. Replaces buyer role with ARTISAN role.
    4. Creates or updates the applicant's ArtisanProfile.
    5. Writes an immutable audit log entry.
    """
    require_role("ADMIN")(current_user)
    app_record = (
        db.query(ArtisanApplication)
        .filter(ArtisanApplication.id == application_id)
        .first()
    )
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan application not found.",
        )

    if app_record.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve application that is already {app_record.status.lower()}.",
        )

    # 1. Update application status
    app_record.status = "APPROVED"
    app_record.reviewer_notes = review_in.reviewer_notes if review_in else None
    app_record.reviewed_by_user_id = current_user.id
    app_record.reviewed_at = datetime.now(timezone.utc)

    # 2. Convert applicant role
    applicant = db.query(User).filter(User.id == app_record.user_id).first()
    if applicant:
        # Remove buyer role (exclusive conversion rule)
        applicant.roles = [
            r for r in applicant.roles if r.code not in ["RETAIL_BUYER", "WHOLESALE_BUYER"]
        ]
        
        artisan_role = db.query(Role).filter(Role.code == "ARTISAN").first()
        if artisan_role and artisan_role not in applicant.roles:
            applicant.roles.append(artisan_role)

        # 3. Create or update ArtisanProfile
        artisan_profile = (
            db.query(ArtisanProfile)
            .filter(ArtisanProfile.user_id == applicant.id)
            .first()
        )
        if not artisan_profile:
            artisan_profile = ArtisanProfile(
                user_id=applicant.id,
                craft_specialization=app_record.craft_specialization,
                experience_years=app_record.experience_years,
                city=app_record.city,
                state=app_record.state,
                bio=app_record.craft_description,
                verification_level="SUBMITTED",
            )
            db.add(artisan_profile)
        else:
            artisan_profile.craft_specialization = app_record.craft_specialization
            artisan_profile.experience_years = app_record.experience_years
            artisan_profile.city = app_record.city
            artisan_profile.state = app_record.state
            artisan_profile.bio = app_record.craft_description

    # 4. Record audit log
    audit_entry = AuditLog(
        user_id=current_user.id,
        action="ARTISAN_APPLICATION_APPROVED",
        resource=f"artisan_application:{app_record.id}",
        details={
            "applicant_id": app_record.user_id,
            "application_id": app_record.id,
            "craft": app_record.craft_specialization,
            "reviewer_notes": app_record.reviewer_notes,
        },
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(app_record)

    return APIResponse(
        success=True,
        message="Artisan application approved. User has been converted to Artisan.",
        data=_format_application_out(app_record),
    )


@router.post("/admin/{application_id}/reject", response_model=APIResponse[ArtisanApplicationOut])
def reject_artisan_application(
    application_id: str,
    review_in: Optional[ArtisanApplicationReviewIn] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Rejects an artisan application:
    - Status set to REJECTED.
    - Saves reviewer note.
    - User's Buyer role remains unchanged.
    - Audit log entry recorded.
    """
    require_role("ADMIN")(current_user)
    app_record = (
        db.query(ArtisanApplication)
        .filter(ArtisanApplication.id == application_id)
        .first()
    )
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan application not found.",
        )

    if app_record.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject application that is already {app_record.status.lower()}.",
        )

    app_record.status = "REJECTED"
    app_record.reviewer_notes = review_in.reviewer_notes if review_in else None
    app_record.reviewed_by_user_id = current_user.id
    app_record.reviewed_at = datetime.now(timezone.utc)

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="ARTISAN_APPLICATION_REJECTED",
        resource=f"artisan_application:{app_record.id}",
        details={
            "applicant_id": app_record.user_id,
            "application_id": app_record.id,
            "reviewer_notes": app_record.reviewer_notes,
        },
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(app_record)

    return APIResponse(
        success=True,
        message="Artisan application has been rejected. Buyer role preserved.",
        data=_format_application_out(app_record),
    )

