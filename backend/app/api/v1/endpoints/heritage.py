import hashlib
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.config import settings
from app.db.session import get_db
from app.models import AuditLog, Product, ProductQR, ProvenanceRecord, User
from app.schemas.common import APIResponse
from app.schemas.heritage import (
    ProductQROut,
    ProvenanceCreateIn,
    ProvenanceRecordOut,
    ProvenanceRevokeIn,
    PublicHeritageStoryOut,
)
from app.services.heritage_service import (
    create_signed_provenance,
    generate_qr_code_image,
    get_public_key_info,
    verify_provenance_signature,
)

router = APIRouter()


def _assert_product_owner_or_admin(product: Product, current_user: User) -> None:
    roles = [r.code for r in current_user.roles]
    if "ADMIN" in roles:
        return
    if not product.artisan or product.artisan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not own this product.",
        )


@router.get("/public-key", response_model=APIResponse[dict[str, str]])
def get_heritage_public_key():
    """Returns the platform Ed25519 public key for independent offline provenance verification."""
    return APIResponse(
        success=True,
        message="Ed25519 provenance public key retrieved",
        data=get_public_key_info(),
    )


@router.post("/provenance", response_model=APIResponse[ProvenanceRecordOut])
def record_craft_provenance(
    provenance_in: ProvenanceCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Generates an Ed25519 digitally signed provenance record for a product batch."""
    product = db.query(Product).filter(Product.id == provenance_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    _assert_product_owner_or_admin(product, current_user)

    signed = create_signed_provenance(
        artisan_id=product.artisan_id,
        product_id=product.id,
        batch_code=provenance_in.batch_code,
        raw_material_source=provenance_in.raw_materials_source,
    )

    record = ProvenanceRecord(
        product_id=product.id,
        batch_code=provenance_in.batch_code,
        raw_materials_source=provenance_in.raw_materials_source,
        craft_technique_details=provenance_in.craft_technique_details,
        maker_signature_hash=signed["maker_signature_hash"],
        signed_payload=signed["signed_payload"],
        signature_ed25519=signed["signature_ed25519"],
        public_key_fingerprint=signed["public_key_fingerprint"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return APIResponse(
        success=True,
        message="Provenance record registered with Ed25519 maker signature",
        data=ProvenanceRecordOut.model_validate(record),
    )


@router.post("/generate-qr/{product_id}", response_model=APIResponse[ProductQROut])
def generate_product_qr(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Generates a tamper-evident QR code embedding public provenance story link."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    _assert_product_owner_or_admin(product, current_user)

    qr_hash = hashlib.sha256(f"{product.id}:{product.slug}:CraftLensQR".encode()).hexdigest()[:16]
    base_url = settings.PUBLIC_WEB_BASE_URL.rstrip("/")
    public_url = f"{base_url}/heritage/{qr_hash}"

    qr_img_url = generate_qr_code_image(public_url=public_url, qr_hash=qr_hash)

    qr_record = db.query(ProductQR).filter(ProductQR.product_id == product.id).first()
    if not qr_record:
        qr_record = ProductQR(
            product_id=product.id,
            qr_code_hash=qr_hash,
            public_url=public_url,
            scan_count=0,
        )
        db.add(qr_record)
    else:
        qr_record.qr_code_hash = qr_hash
        qr_record.public_url = public_url
        qr_record.is_revoked = False
        qr_record.revoked_at = None
        qr_record.revoked_reason = None

    db.commit()
    db.refresh(qr_record)

    return APIResponse(
        success=True,
        message="Cryptographic heritage QR code generated successfully",
        data=ProductQROut(
            id=qr_record.id,
            product_id=qr_record.product_id,
            qr_code_hash=qr_record.qr_code_hash,
            public_url=qr_record.public_url,
            qr_image_url=qr_img_url,
            scan_count=qr_record.scan_count,
            last_scanned_at=qr_record.last_scanned_at,
            is_revoked=qr_record.is_revoked,
        ),
    )


@router.post("/revoke/{product_id}", response_model=APIResponse[dict[str, str]])
def revoke_heritage_provenance(
    product_id: str,
    revoke_in: ProvenanceRevokeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Revokes provenance records and QR verification for a product (owner artisan or admin)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    _assert_product_owner_or_admin(product, current_user)

    now = datetime.now(UTC)
    records = db.query(ProvenanceRecord).filter(ProvenanceRecord.product_id == product.id).all()
    for rec in records:
        rec.is_revoked = True
        rec.revoked_at = now
        rec.revoked_reason = revoke_in.reason

    qr_record = db.query(ProductQR).filter(ProductQR.product_id == product.id).first()
    if qr_record:
        qr_record.is_revoked = True
        qr_record.revoked_at = now
        qr_record.revoked_reason = revoke_in.reason

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="REVOKE_HERITAGE_PROVENANCE",
            resource=f"product:{product.id}",
            details={"reason": revoke_in.reason},
        )
    )
    db.commit()

    return APIResponse(
        success=True,
        message="Product provenance and QR code revoked",
        data={"product_id": product.id, "status": "REVOKED"},
    )


@router.get("/verify/{qr_hash}", response_model=APIResponse[PublicHeritageStoryOut])
def verify_heritage_qr(
    qr_hash: str,
    db: Session = Depends(get_db),
):
    """Public verification endpoint verifying Ed25519 signature and revocation status."""
    qr_record = db.query(ProductQR).filter(ProductQR.qr_code_hash == qr_hash).first()
    if not qr_record:
        raise HTTPException(status_code=404, detail="Invalid or unregistered CraftLens QR code")

    qr_record.scan_count += 1
    qr_record.last_scanned_at = datetime.now(UTC)
    db.commit()

    product = qr_record.product
    artisan = product.artisan
    user = artisan.user if artisan else None

    prov = (
        db.query(ProvenanceRecord)
        .filter(ProvenanceRecord.product_id == product.id)
        .order_by(ProvenanceRecord.created_at.desc())
        .first()
    )

    sig_valid = verify_provenance_signature(prov.signed_payload, prov.signature_ed25519) if prov else False
    is_revoked = bool(qr_record.is_revoked or (prov and prov.is_revoked))
    revoked_reason = qr_record.revoked_reason or (prov.revoked_reason if prov else None)
    verified_genuine = bool(sig_valid and not is_revoked)

    story = PublicHeritageStoryOut(
        product_title=product.title,
        category_name=product.category.name if product.category else "Handicraft",
        primary_material=product.primary_material,
        technique=product.technique,
        craft_origin_name=product.craft_origin.name if product.craft_origin else None,
        geographical_indication_code=(
            product.craft_origin.geographical_indication_code if product.craft_origin else None
        ),
        artisan_name=user.full_name if user else "Verified Master Artisan",
        artisan_city=artisan.city if artisan else None,
        artisan_state=artisan.state if artisan else None,
        artisan_experience_years=artisan.experience_years if artisan else 1,
        artisan_bio=artisan.bio if artisan else None,
        verification_level=artisan.verification_level if artisan else "UNVERIFIED",
        batch_code=prov.batch_code if prov else None,
        maker_signature_hash=prov.maker_signature_hash if prov else None,
        signature_ed25519=prov.signature_ed25519 if prov else None,
        signed_payload=prov.signed_payload if prov else None,
        public_key_fingerprint=prov.public_key_fingerprint if prov else None,
        signature_valid=sig_valid,
        revoked=is_revoked,
        revoked_reason=revoked_reason,
        verified_genuine=verified_genuine,
        scan_count=qr_record.scan_count,
    )

    msg = (
        "Provenance verification FAILED: record revoked"
        if is_revoked
        else ("Authentic craft heritage verified (Ed25519)" if sig_valid else "Provenance signature invalid or missing")
    )
    return APIResponse(
        success=True,
        message=msg,
        data=story,
    )
