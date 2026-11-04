from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, Buyer, BuyerBusinessProfile
from app.schemas.buyer import (
    BuyerProfileOut,
    BuyerProfileUpdate,
    BuyerBusinessProfileOut,
    BuyerBusinessProfileUpdate,
)
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role

router = APIRouter()


@router.get("/me", response_model=APIResponse[BuyerProfileOut])
def get_my_buyer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves authenticated retail or wholesale buyer profile."""
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        buyer = Buyer(user_id=current_user.id, buyer_type="RETAIL")
        db.add(buyer)
        db.commit()
        db.refresh(buyer)

    return APIResponse(
        success=True,
        message="Buyer profile loaded",
        data=BuyerProfileOut.model_validate(buyer),
    )


@router.put("/me", response_model=APIResponse[BuyerProfileOut])
def update_my_buyer_profile(
    profile_in: BuyerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates shipping and billing address information."""
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        buyer = Buyer(user_id=current_user.id)
        db.add(buyer)

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(buyer, field, value)

    db.commit()
    db.refresh(buyer)

    return APIResponse(
        success=True,
        message="Buyer profile updated successfully",
        data=BuyerProfileOut.model_validate(buyer),
    )


@router.put("/me/business", response_model=APIResponse[BuyerBusinessProfileOut])
def update_my_business_profile(
    business_in: BuyerBusinessProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("WHOLESALE_BUYER")),
):
    """Configures corporate B2B wholesale verification details (GST, PAN, Trade License)."""
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        buyer = Buyer(user_id=current_user.id, buyer_type="WHOLESALE")
        db.add(buyer)
        db.flush()

    business = (
        db.query(BuyerBusinessProfile)
        .filter(BuyerBusinessProfile.buyer_id == buyer.id)
        .first()
    )
    if not business:
        business = BuyerBusinessProfile(
            buyer_id=buyer.id,
            company_name=business_in.company_name,
            gst_number=business_in.gst_number,
            pan_number=business_in.pan_number,
            trade_license_url=business_in.trade_license_url,
            website=business_in.website,
            notes=business_in.notes,
        )
        db.add(business)
    else:
        for field, value in business_in.model_dump(exclude_unset=True).items():
            setattr(business, field, value)

    db.commit()
    db.refresh(business)

    return APIResponse(
        success=True,
        message="B2B Wholesale business profile updated",
        data=BuyerBusinessProfileOut.model_validate(business),
    )
