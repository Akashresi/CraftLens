from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models import AuditLog, ConsentRecord, User
from app.schemas.common import APIResponse

router = APIRouter()


class ConsentCreateIn(BaseModel):
    consent_type: str = Field(
        ...,
        description="TERMS_OF_SERVICE, DPDP_PRIVACY_POLICY, CULTURAL_HERITAGE_DISCLOSURE, DATA_PROCESSING",
    )
    granted: bool = True


class ConsentRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    consent_type: str
    granted: bool
    recorded_at: datetime


@router.post("/consent", response_model=APIResponse[ConsentRecordOut])
def record_user_consent(
    consent_in: ConsentCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Records explicit informed consent in compliance with the Digital Personal Data Protection (DPDP) Act 2023."""
    ip = request.client.host if request.client else "127.0.0.1"

    consent = ConsentRecord(
        user_id=current_user.id,
        consent_type=consent_in.consent_type,
        granted=consent_in.granted,
        ip_address=ip,
        recorded_at=datetime.now(UTC),
    )
    db.add(consent)

    # Log to audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="RECORD_CONSENT",
        resource="ConsentRecord",
        ip_address=ip,
        details={"consent_type": consent_in.consent_type, "granted": consent_in.granted},
    )
    db.add(audit)
    db.commit()
    db.refresh(consent)

    return APIResponse(
        success=True,
        message="Consent record registered",
        data=ConsentRecordOut.model_validate(consent),
    )


@router.get("/consent", response_model=APIResponse[list[ConsentRecordOut]])
def get_user_consents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves all active consents granted by the authenticated user."""
    consents = (
        db.query(ConsentRecord)
        .filter(ConsentRecord.user_id == current_user.id)
        .order_by(ConsentRecord.recorded_at.desc())
        .all()
    )
    return APIResponse(
        success=True,
        message="Active consents retrieved",
        data=[ConsentRecordOut.model_validate(c) for c in consents],
    )
