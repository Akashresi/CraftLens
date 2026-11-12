from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_role
from app.core.config import settings
from app.core.upload_security import sanitize_text
from app.db.session import get_db
from app.models import (
    ArtisanApplication,
    ArtisanVerification,
    AuditLog,
    Buyer,
    ConsentRecord,
    GrievanceTicket,
    Order,
    Product,
    User,
)
from app.schemas.common import APIResponse

router = APIRouter()


class ConsentCreateIn(BaseModel):
    consent_type: str = Field(
        ...,
        description="TERMS_OF_SERVICE, DPDP_PRIVACY_POLICY, CULTURAL_HERITAGE_DISCLOSURE, DATA_PROCESSING, ANALYTICS",
    )
    granted: bool = True


class ConsentRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    consent_type: str
    granted: bool
    recorded_at: datetime
    withdrawn_at: datetime | None = None


class GrievanceCreateIn(BaseModel):
    subject: str = Field(..., min_length=4, max_length=255)
    description: str = Field(..., min_length=10, max_length=5000)


class GrievanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None = None
    subject: str
    description: str
    status: str
    created_at: datetime


@router.post("/consent", response_model=APIResponse[ConsentRecordOut])
def record_user_consent(
    consent_in: ConsentCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Records explicit informed consent in compliance with the DPDP Act 2023."""
    ip = request.client.host if request.client else "127.0.0.1"
    now = datetime.now(UTC)

    consent = ConsentRecord(
        user_id=current_user.id,
        consent_type=consent_in.consent_type,
        granted=consent_in.granted,
        ip_address=ip,
        recorded_at=now,
        withdrawn_at=None if consent_in.granted else now,
    )
    db.add(consent)

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="RECORD_CONSENT",
            resource="ConsentRecord",
            ip_address=ip,
            details={"consent_type": consent_in.consent_type, "granted": consent_in.granted},
        )
    )
    db.commit()
    db.refresh(consent)

    return APIResponse(
        success=True,
        message="Consent record registered",
        data=ConsentRecordOut.model_validate(consent),
    )


@router.post("/consent/{consent_type}/withdraw", response_model=APIResponse[ConsentRecordOut])
def withdraw_user_consent(
    consent_type: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Withdraws previously granted DPDP consent and creates an immutable audit record."""
    ip = request.client.host if request.client else "127.0.0.1"
    now = datetime.now(UTC)

    latest = (
        db.query(ConsentRecord)
        .filter(
            ConsentRecord.user_id == current_user.id,
            ConsentRecord.consent_type == consent_type,
        )
        .order_by(ConsentRecord.recorded_at.desc())
        .first()
    )
    if not latest:
        raise HTTPException(status_code=404, detail=f"No consent record found for '{consent_type}'")

    withdrawal = ConsentRecord(
        user_id=current_user.id,
        consent_type=consent_type,
        granted=False,
        ip_address=ip,
        recorded_at=now,
        withdrawn_at=now,
    )
    db.add(withdrawal)
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="WITHDRAW_CONSENT",
            resource=f"ConsentRecord:{consent_type}",
            ip_address=ip,
            details={"consent_type": consent_type, "granted": False},
        )
    )
    db.commit()
    db.refresh(withdrawal)

    return APIResponse(
        success=True,
        message=f"Consent '{consent_type}' withdrawn successfully",
        data=ConsentRecordOut.model_validate(withdrawal),
    )


@router.get("/consent", response_model=APIResponse[list[ConsentRecordOut]])
def get_user_consents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves all consent history records for the authenticated user."""
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


@router.get("/export-my-data", response_model=APIResponse[dict])
def export_my_personal_data(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """DPDP Act 2023 Right to Access: exports all personal data held for the user."""
    ip = request.client.host if request.client else "127.0.0.1"
    consents = db.query(ConsentRecord).filter(ConsentRecord.user_id == current_user.id).all()
    apps = db.query(ArtisanApplication).filter(ArtisanApplication.user_id == current_user.id).all()
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    orders = db.query(Order).filter(Order.buyer_id == buyer.id).all() if buyer else []
    grievances = db.query(GrievanceTicket).filter(GrievanceTicket.user_id == current_user.id).all()

    export_bundle = {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "phone": current_user.phone,
            "full_name": current_user.full_name,
            "preferred_language": current_user.preferred_language,
            "roles": [r.code for r in current_user.roles],
            "created_at": current_user.created_at.isoformat(),
        },
        "consents": [
            {
                "consent_type": c.consent_type,
                "granted": c.granted,
                "recorded_at": c.recorded_at.isoformat(),
                "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None,
            }
            for c in consents
        ],
        "artisan_applications": [
            {
                "id": a.id,
                "craft_specialization": a.craft_specialization,
                "status": a.status,
                "created_at": a.created_at.isoformat(),
            }
            for a in apps
        ],
        "orders": [
            {
                "order_number": o.order_number,
                "total_amount": float(o.total_amount),
                "status": o.status,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ],
        "grievances": [
            {"id": g.id, "subject": g.subject, "status": g.status, "created_at": g.created_at.isoformat()}
            for g in grievances
        ],
    }

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="EXPORT_PERSONAL_DATA",
            resource=f"user:{current_user.id}",
            ip_address=ip,
            details={"records_exported": len(consents) + len(apps) + len(orders)},
        )
    )
    db.commit()

    return APIResponse(
        success=True,
        message="Personal data export generated",
        data=export_bundle,
    )


@router.post("/erase-my-data", response_model=APIResponse[dict[str, str]])
def erase_my_personal_data(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """DPDP Act 2023 Right to Erasure: anonymizes user PII and deactivates the account
    while preserving immutable statutory accounting/audit trails.
    """
    ip = request.client.host if request.client else "127.0.0.1"
    anon_suffix = current_user.id[:8]
    current_user.email = f"erased-{anon_suffix}@anonymized.craftlens.invalid"
    current_user.phone = None
    current_user.full_name = f"Erased User {anon_suffix}"
    current_user.is_active = False
    current_user.is_anonymized = True

    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if buyer:
        buyer.default_shipping_address = {}
        buyer.default_billing_address = {}

    for app_rec in db.query(ArtisanApplication).filter(ArtisanApplication.user_id == current_user.id).all():
        app_rec.full_name = f"Erased User {anon_suffix}"
        app_rec.portfolio_url = None
        app_rec.supporting_documents_url = None

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="ERASE_PERSONAL_DATA",
            resource=f"user:{current_user.id}",
            ip_address=ip,
            details={"anonymized": True},
        )
    )
    db.commit()

    return APIResponse(
        success=True,
        message="Personal data anonymized and account deactivated under DPDP Act 2023",
        data={"user_id": current_user.id, "status": "ANONYMIZED"},
    )


@router.get("/grievance-contact", response_model=APIResponse[dict[str, str]])
def get_grievance_officer_contact():
    """Returns statutory DPDP Act 2023 Data Protection & Grievance Officer contact details."""
    return APIResponse(
        success=True,
        message="Grievance officer contact details",
        data={
            "officer_name": settings.DPDP_GRIEVANCE_OFFICER_NAME,
            "email": settings.DPDP_GRIEVANCE_OFFICER_EMAIL,
            "phone": settings.DPDP_GRIEVANCE_OFFICER_PHONE,
            "sla_hours": "72",
        },
    )


@router.post("/grievance", response_model=APIResponse[GrievanceOut])
def submit_grievance(
    grievance_in: GrievanceCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Files a data protection or platform grievance ticket."""
    ip = request.client.host if request.client else "127.0.0.1"
    ticket = GrievanceTicket(
        user_id=current_user.id,
        subject=sanitize_text(grievance_in.subject) or grievance_in.subject,
        description=sanitize_text(grievance_in.description) or grievance_in.description,
        status="OPEN",
    )
    db.add(ticket)
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="SUBMIT_GRIEVANCE",
            resource="GrievanceTicket",
            ip_address=ip,
            details={"subject": ticket.subject},
        )
    )
    db.commit()
    db.refresh(ticket)
    return APIResponse(
        success=True,
        message="Grievance ticket submitted to Data Protection Officer",
        data=GrievanceOut.model_validate(ticket),
    )


@router.get("/grievance", response_model=APIResponse[list[GrievanceOut]])
def list_my_grievances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists grievance tickets filed by the authenticated user."""
    tickets = (
        db.query(GrievanceTicket)
        .filter(GrievanceTicket.user_id == current_user.id)
        .order_by(GrievanceTicket.created_at.desc())
        .all()
    )
    return APIResponse(
        success=True,
        message="Grievance tickets retrieved",
        data=[GrievanceOut.model_validate(t) for t in tickets],
    )


@router.get("/admin/overview", response_model=APIResponse[dict])
def get_admin_compliance_and_analytics_overview(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Live Admin analytics + DPDP audit log feed (paginated)."""
    p = max(1, page)
    ps = min(100, max(1, page_size))

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_gmv = float(db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0.0)
    pending_apps = (
        db.query(func.count(ArtisanApplication.id)).filter(ArtisanApplication.status == "PENDING").scalar() or 0
    )
    pending_kyc = (
        db.query(func.count(ArtisanVerification.id)).filter(ArtisanVerification.status == "PENDING").scalar() or 0
    )
    pending_gi = db.query(func.count(Product.id)).filter(Product.gi_verification_status == "PENDING").scalar() or 0
    open_grievances = db.query(func.count(GrievanceTicket.id)).filter(GrievanceTicket.status == "OPEN").scalar() or 0

    audit_total = db.query(func.count(AuditLog.id)).scalar() or 0
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset((p - 1) * ps).limit(ps).all()

    return APIResponse(
        success=True,
        message="Admin compliance & platform analytics retrieved",
        data={
            "metrics": {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders,
                "total_gmv_inr": round(total_gmv, 2),
                "pending_applications": pending_apps,
                "pending_kyc": pending_kyc,
                "pending_gi_claims": pending_gi,
                "open_grievances": open_grievances,
            },
            "audit_logs": {
                "total": audit_total,
                "page": p,
                "page_size": ps,
                "items": [
                    {
                        "id": log.id,
                        "user_id": log.user_id,
                        "action": log.action,
                        "resource": log.resource,
                        "ip_address": log.ip_address,
                        "details": log.details,
                        "created_at": log.created_at.isoformat(),
                    }
                    for log in logs
                ],
            },
        },
    )
