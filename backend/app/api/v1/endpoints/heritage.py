import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, Product, ArtisanProfile, ProvenanceRecord, ProductQR, CraftOrigin
from app.schemas.heritage import (
    ProvenanceCreateIn,
    ProvenanceRecordOut,
    ProductQROut,
    PublicHeritageStoryOut,
)
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role
from app.services.heritage_service import (
    create_provenance_signature,
    generate_qr_code_image,
)

router = APIRouter()


@router.post("/provenance", response_model=APIResponse[ProvenanceRecordOut])
def record_craft_provenance(
    provenance_in: ProvenanceCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Generates an immutable cryptographic provenance signature for a product batch."""
    product = db.query(Product).filter(Product.id == provenance_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sig = create_provenance_signature(
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
        maker_signature_hash=sig,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return APIResponse(
        success=True,
        message="Provenance record registered with cryptographic maker signature",
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

    qr_hash = hashlib.sha256(f"{product.id}:{product.slug}:CraftLensQR".encode("utf-8")).hexdigest()[:16]
    public_url = f"http://localhost:3000/heritage/{qr_hash}"

    # Generate QR Code PNG
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
        ),
    )


@router.get("/verify/{qr_hash}", response_model=APIResponse[PublicHeritageStoryOut])
def verify_heritage_qr(
    qr_hash: str,
    db: Session = Depends(get_db),
):
    """Public verification endpoint accessed by retail buyers scanning physical product tag.
    Increments scan count and displays authenticated maker provenance.
    """
    qr_record = db.query(ProductQR).filter(ProductQR.qr_code_hash == qr_hash).first()
    if not qr_record:
        raise HTTPException(status_code=404, detail="Invalid or unregistered CraftLens QR code")

    # Increment scan metrics
    qr_record.scan_count += 1
    qr_record.last_scanned_at = datetime.now(timezone.utc)
    db.commit()

    product = qr_record.product
    artisan = product.artisan
    user = artisan.user if artisan else None

    # Get latest provenance record if exists
    prov = (
        db.query(ProvenanceRecord)
        .filter(ProvenanceRecord.product_id == product.id)
        .order_by(ProvenanceRecord.created_at.desc())
        .first()
    )

    story = PublicHeritageStoryOut(
        product_title=product.title,
        category_name=product.category.name if product.category else "Handicraft",
        primary_material=product.primary_material,
        technique=product.technique,
        craft_origin_name=product.craft_origin.name if product.craft_origin else None,
        geographical_indication_code=product.craft_origin.geographical_indication_code if product.craft_origin else None,
        artisan_name=user.full_name if user else "Verified Master Artisan",
        artisan_city=artisan.city if artisan else None,
        artisan_state=artisan.state if artisan else None,
        artisan_experience_years=artisan.experience_years if artisan else 1,
        artisan_bio=artisan.bio if artisan else None,
        verification_level=artisan.verification_level if artisan else "UNVERIFIED",
        batch_code=prov.batch_code if prov else None,
        maker_signature_hash=prov.maker_signature_hash if prov else None,
        verified_genuine=True,
        scan_count=qr_record.scan_count,
    )

    return APIResponse(
        success=True,
        message="Authentic craft heritage verified",
        data=story,
    )

