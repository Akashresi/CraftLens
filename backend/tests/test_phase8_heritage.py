import pytest
from app.models import User, Product, ProductQR, ProvenanceRecord
from app.api.v1.endpoints.auth import register_user
from app.schemas.user import UserRegister
from app.api.v1.endpoints.voice import apply_catalog_to_product
from app.schemas.voice import ApplyCatalogIn
from app.schemas.heritage import ProvenanceCreateIn
from app.api.v1.endpoints.heritage import record_craft_provenance, generate_product_qr, verify_heritage_qr


def test_heritage_provenance_and_qr_verification_flow(db):
    # 1. Register Master Artisan
    artisan_reg = register_user(
        user_in=UserRegister(
            email="heritage.master@craftlens.org",
            password="HeritagePass#123",
            full_name="Padma Shri Artisan",
            role_code="ARTISAN",
            preferred_language="hi"
        ),
        db=db
    )
    artisan_user = db.query(User).filter(User.email == "heritage.master@craftlens.org").first()
    artisan_user.artisan_profile.verification_level = "GOVT_ID_VERIFIED"
    db.commit()

    # 2. Create Heritage Product
    prod_res = apply_catalog_to_product(
        payload=ApplyCatalogIn(
            title="Authentic Madhubani Handpainted Tree of Life",
            summary="Painted on handmade cowdung treated paper with natural twig brushes and vegetable dyes.",
            primary_material="Natural Mineral Pigments & Handmade Paper",
            technique="Madhubani Kachni Line Art",
            category_slug="traditional-painting",
            source_language="hi"
        ),
        db=db,
        current_user=artisan_user
    )
    product_id = prod_res.data["product_id"]

    # 3. Record Provenance
    prov_payload = ProvenanceCreateIn(
        product_id=product_id,
        batch_code="MDB-2026-B01",
        raw_materials_source="Locally sourced cowdung treated paper and soot/indigo pigments from Jitwarpur village",
        craft_technique_details="Drawn freehand using bamboo nib and cotton swab coloring."
    )
    prov_res = record_craft_provenance(provenance_in=prov_payload, db=db, current_user=artisan_user)
    assert prov_res.success is True
    assert prov_res.data.maker_signature_hash is not None
    assert len(prov_res.data.maker_signature_hash) == 64  # SHA256 length

    # 4. Generate Product QR Code
    qr_res = generate_product_qr(product_id=product_id, db=db, current_user=artisan_user)
    assert qr_res.success is True
    qr_data = qr_res.data
    assert qr_data.qr_code_hash is not None
    assert qr_data.qr_image_url.endswith(".png")
    assert qr_data.scan_count == 0

    # 5. Customer scans QR code -> Public Verification
    verify_res = verify_heritage_qr(qr_hash=qr_data.qr_code_hash, db=db)
    assert verify_res.success is True
    story = verify_res.data
    assert story.product_title == "Authentic Madhubani Handpainted Tree of Life"
    assert story.artisan_name == "Padma Shri Artisan"
    assert story.verification_level == "GOVT_ID_VERIFIED"
    assert story.batch_code == "MDB-2026-B01"
    assert story.maker_signature_hash == prov_res.data.maker_signature_hash
    assert story.verified_genuine is True
    assert story.scan_count == 1  # Incremented on scan
