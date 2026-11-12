"""Phase 2 security hardening verification tests: rate limit, lockout, CSRF, upload safety, IDOR, Ed25519, DPDP."""

import io
from datetime import UTC, datetime

import pytest
from PIL import Image, ImageDraw

from app.core.config import settings
from app.core.rate_limit import rate_limiter
from app.models import AuditLog, Product, ProductQR, ProvenanceRecord, User
from app.services.heritage_service import verify_provenance_signature
from tests.conftest import TestingSessionLocal, create_test_artisan


def _jpeg_with_exif() -> bytes:
    img = Image.new("RGB", (180, 180), color=(235, 225, 210))
    draw = ImageDraw.Draw(img)
    draw.ellipse([30, 30, 150, 150], fill=(160, 90, 50))
    exif = Image.Exif()
    exif[0x010F] = "SecretPhoneMaker"
    exif[0x013B] = "Photographer GPS PII"
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


async def _login(async_client, email: str, password: str) -> dict[str, str]:
    res = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def test_security_headers_and_csrf_protection(async_client):
    rate_limiter.reset()
    r = await async_client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "DENY"
    assert "content-security-policy" in r.headers

    # Cookie-based mutation without CSRF token -> 403
    csrf_res = await async_client.get("/api/v1/auth/csrf-token")
    assert csrf_res.status_code == 200
    csrf_token = csrf_res.json()["data"]["csrf_token"]

    r_no_csrf = await async_client.post(
        "/api/v1/auth/refresh",
        cookies={"craftlens_session": "cookie-session-id", "craftlens_csrf": csrf_token},
        json={"refresh_token": "bad"},
    )
    assert r_no_csrf.status_code == 403
    assert "CSRF" in r_no_csrf.json()["detail"]

    # Matching double-submit CSRF header passes middleware and hits endpoint validation (401 invalid token)
    r_with_csrf = await async_client.post(
        "/api/v1/auth/refresh",
        cookies={"craftlens_session": "cookie-session-id", "craftlens_csrf": csrf_token},
        headers={"X-CSRF-Token": csrf_token},
        json={"refresh_token": "bad"},
    )
    assert r_with_csrf.status_code == 401


async def test_rate_limiting_and_account_lockout(async_client):
    rate_limiter.reset()
    email = "lockout.buyer@craftlens.org"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "ValidPassword#2026", "full_name": "Lockout User"},
    )

    # Trigger 5 failed logins -> account locked (423 on 6th attempt)
    for _ in range(settings.MAX_FAILED_LOGIN_ATTEMPTS):
        res = await async_client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": "WrongPassword!"},
        )
        assert res.status_code == 401

    locked_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "ValidPassword#2026"},
    )
    assert locked_res.status_code == 423

    # Trigger rate limit directly on login scope (>20 requests in 60s)
    rate_limiter.reset()
    for _ in range(20):
        await async_client.post(
            "/api/v1/auth/login",
            data={"username": "nobody@craftlens.org", "password": "bad"},
        )
    r_429 = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@craftlens.org", "password": "bad"},
    )
    assert r_429.status_code == 429


async def test_upload_validation_magic_bytes_eicar_exif_and_audio(async_client):
    rate_limiter.reset()
    headers = await _login(async_client, "artisan@craftlens.org", "Artisan@2026")

    # 1. HTML/Script disguised as JPEG -> rejected by magic bytes
    r_poly = await async_client.post(
        "/api/v1/studio/analyze",
        headers=headers,
        files={"file": ("evil.jpg", b"<html><script>alert(1)</script></html>", "image/jpeg")},
    )
    assert r_poly.status_code == 400
    assert "Unsupported or invalid image format" in r_poly.json()["detail"]

    # 2. EICAR antivirus signature -> rejected
    eicar = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    r_eicar = await async_client.post(
        "/api/v1/studio/analyze",
        headers=headers,
        files={"file": ("eicar.jpg", b"\xff\xd8\xff" + eicar, "image/jpeg")},
    )
    assert r_eicar.status_code == 400
    assert "malware" in r_eicar.json()["detail"].lower()

    # 3. Valid JPEG with EXIF PII -> accepted & EXIF stripped on saved output
    jpeg_bytes = _jpeg_with_exif()
    r_ok = await async_client.post(
        "/api/v1/studio/process",
        headers=headers,
        files={"file": ("../../etc/passwd.jpg", jpeg_bytes, "image/jpeg")},
        data={"lifestyle_theme": "wood"},
    )
    assert r_ok.status_code == 200
    orig_url = r_ok.json()["data"]["original_url"]
    assert orig_url.startswith("/uploads/original/")
    assert ".." not in orig_url
    saved_path = orig_url.lstrip("/")
    with Image.open(saved_path) as saved_img:
        assert len(saved_img.getexif()) == 0

    # 4. Bad audio container -> rejected
    r_audio = await async_client.post(
        "/api/v1/voice/transcribe",
        headers=headers,
        files={"file": ("fake.wav", b"NOT_AN_AUDIO_FILE", "audio/wav")},
        data={"language_code": "ta"},
    )
    assert r_audio.status_code == 400


async def test_idor_cross_user_isolation(async_client):
    rate_limiter.reset()
    # Artisan A logs in & creates product
    artisan_a_headers = await _login(async_client, "artisan@craftlens.org", "Artisan@2026")
    r_prod = await async_client.post(
        "/api/v1/voice/apply-to-product",
        headers=artisan_a_headers,
        json={
            "title": "Artisan A Terracotta Lamp",
            "summary": "Handmade lamp crafted in Vilachery.",
            "primary_material": "Clay",
            "technique": "Wheel throwing",
            "category_slug": "terracotta-pottery",
            "source_language": "en",
        },
    )
    assert r_prod.status_code == 200
    product_id = r_prod.json()["data"]["product_id"]

    # Create Artisan B
    db = TestingSessionLocal()
    try:
        create_test_artisan(db, email="artisan.b@craftlens.org", full_name="Artisan B", password="ArtisanB#2026")
    finally:
        db.close()

    artisan_b_headers = await _login(async_client, "artisan.b@craftlens.org", "ArtisanB#2026")

    # Artisan B CANNOT price, record provenance, generate QR, or revoke Artisan A's product -> 403
    assert (
        await async_client.post(
            f"/api/v1/pricing/apply/{product_id}",
            headers=artisan_b_headers,
            json={"retail_price": 1.0, "wholesale_price": 1.0, "stock_quantity": 10},
        )
    ).status_code == 403

    assert (
        await async_client.post(
            "/api/v1/heritage/provenance",
            headers=artisan_b_headers,
            json={
                "product_id": product_id,
                "batch_code": "HIJACK-01",
                "raw_materials_source": "Fake",
                "craft_technique_details": "Hijack attempt",
            },
        )
    ).status_code == 403

    assert (
        await async_client.post(f"/api/v1/heritage/generate-qr/{product_id}", headers=artisan_b_headers)
    ).status_code == 403

    assert (
        await async_client.post(
            f"/api/v1/heritage/revoke/{product_id}",
            headers=artisan_b_headers,
            json={"reason": "Unauthorized revoke attempt"},
        )
    ).status_code == 403

    # Artisan A prices product, Buyer A places order, Buyer B gets 403 on GET /orders/{id}
    assert (
        await async_client.post(
            f"/api/v1/pricing/apply/{product_id}",
            headers=artisan_a_headers,
            json={"retail_price": 500.0, "wholesale_price": 400.0, "stock_quantity": 10},
        )
    ).status_code == 200

    db = TestingSessionLocal()
    try:
        prod = db.query(Product).filter(Product.id == product_id).first()
        variant_id = prod.variants[0].id
    finally:
        db.close()

    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "buyer.a@craftlens.org", "password": "BuyerPass#2026", "full_name": "Buyer A"},
    )
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "buyer.b@craftlens.org", "password": "BuyerPass#2026", "full_name": "Buyer B"},
    )
    buyer_a_headers = await _login(async_client, "buyer.a@craftlens.org", "BuyerPass#2026")
    buyer_b_headers = await _login(async_client, "buyer.b@craftlens.org", "BuyerPass#2026")

    r_order = await async_client.post(
        "/api/v1/orders/checkout",
        headers=buyer_a_headers,
        json={
            "items": [{"variant_id": variant_id, "quantity": 1}],
            "order_type": "RETAIL",
            "delivery_address": {"city": "Chennai"},
        },
    )
    assert r_order.status_code == 200
    order_id = r_order.json()["data"]["id"]

    assert (await async_client.get(f"/api/v1/orders/{order_id}", headers=buyer_a_headers)).status_code == 200
    assert (await async_client.get(f"/api/v1/orders/{order_id}", headers=buyer_b_headers)).status_code == 403

    # SQL injection search payload returns safe empty result set (no 500 / leak)
    r_sqli = await async_client.get("/api/v1/marketplace/products?search=' OR '1'='1' --")
    assert r_sqli.status_code == 200
    assert r_sqli.json()["data"]["total"] == 0


async def test_ed25519_provenance_verification_and_revocation(async_client):
    rate_limiter.reset()
    artisan_headers = await _login(async_client, "artisan@craftlens.org", "Artisan@2026")

    r_pub = await async_client.get("/api/v1/heritage/public-key")
    assert r_pub.status_code == 200
    assert r_pub.json()["data"]["algorithm"] == "Ed25519"
    assert "BEGIN PUBLIC KEY" in r_pub.json()["data"]["public_key_pem"]

    r_prod = await async_client.post(
        "/api/v1/voice/apply-to-product",
        headers=artisan_headers,
        json={
            "title": "Ed25519 Provenance Silk Shawl",
            "summary": "Pure handwoven silk shawl",
            "primary_material": "Silk",
            "technique": "Handloom",
            "category_slug": "handloom-textiles",
            "source_language": "en",
        },
    )
    product_id = r_prod.json()["data"]["product_id"]

    r_prov = await async_client.post(
        "/api/v1/heritage/provenance",
        headers=artisan_headers,
        json={
            "product_id": product_id,
            "batch_code": "ED25519-B01",
            "raw_materials_source": "Mulberry Silk Farm, Kanchipuram",
            "craft_technique_details": "Throw-shuttle pit loom weaving",
        },
    )
    assert r_prov.status_code == 200
    prov_data = r_prov.json()["data"]
    assert verify_provenance_signature(prov_data["signed_payload"], prov_data["signature_ed25519"]) is True
    assert verify_provenance_signature(prov_data["signed_payload"] + "tamper", prov_data["signature_ed25519"]) is False

    r_qr = await async_client.post(f"/api/v1/heritage/generate-qr/{product_id}", headers=artisan_headers)
    assert r_qr.status_code == 200
    qr_hash = r_qr.json()["data"]["qr_code_hash"]

    r_verify = await async_client.get(f"/api/v1/heritage/verify/{qr_hash}")
    assert r_verify.status_code == 200
    assert r_verify.json()["data"]["signature_valid"] is True
    assert r_verify.json()["data"]["revoked"] is False
    assert r_verify.json()["data"]["verified_genuine"] is True

    # Revoke and re-verify
    r_rev = await async_client.post(
        f"/api/v1/heritage/revoke/{product_id}",
        headers=artisan_headers,
        json={"reason": "Batch recalled due to dye defect"},
    )
    assert r_rev.status_code == 200

    r_verify_after = await async_client.get(f"/api/v1/heritage/verify/{qr_hash}")
    assert r_verify_after.status_code == 200
    assert r_verify_after.json()["data"]["revoked"] is True
    assert r_verify_after.json()["data"]["verified_genuine"] is False


async def test_dpdp_act_full_lifecycle_and_immutable_audit_log(async_client):
    rate_limiter.reset()
    email = "dpdp.citizen@craftlens.org"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "CitizenPass#2026", "full_name": "DPDP Citizen"},
    )
    headers = await _login(async_client, email, "CitizenPass#2026")

    # 1. Consent grant & withdraw
    assert (
        await async_client.post(
            "/api/v1/compliance/consent",
            headers=headers,
            json={"consent_type": "ANALYTICS", "granted": True},
        )
    ).status_code == 200

    r_wd = await async_client.post("/api/v1/compliance/consent/ANALYTICS/withdraw", headers=headers)
    assert r_wd.status_code == 200
    assert r_wd.json()["data"]["granted"] is False
    assert r_wd.json()["data"]["withdrawn_at"] is not None

    # 2. Grievance contact & ticket submission
    r_contact = await async_client.get("/api/v1/compliance/grievance-contact")
    assert r_contact.status_code == 200
    assert r_contact.json()["data"]["email"]

    r_griev = await async_client.post(
        "/api/v1/compliance/grievance",
        headers=headers,
        json={"subject": "Data correction request", "description": "Please review my saved profile details."},
    )
    assert r_griev.status_code == 200
    assert len((await async_client.get("/api/v1/compliance/grievance", headers=headers)).json()["data"]) >= 1

    # 3. Data export
    r_exp = await async_client.get("/api/v1/compliance/export-my-data", headers=headers)
    assert r_exp.status_code == 200
    assert r_exp.json()["data"]["user"]["email"] == email

    # 4. Data erasure / anonymization
    r_erase = await async_client.post("/api/v1/compliance/erase-my-data", headers=headers)
    assert r_erase.status_code == 200
    assert r_erase.json()["data"]["status"] == "ANONYMIZED"

    # Erased user can no longer authenticate with old email or inactive account
    r_after = await async_client.get("/api/v1/compliance/export-my-data", headers=headers)
    assert r_after.status_code == 400

    # 5. AuditLog cannot be updated or deleted via ORM
    db = TestingSessionLocal()
    try:
        log = db.query(AuditLog).first()
        assert log is not None
        log.action = "TAMPERED"
        with pytest.raises(ValueError, match="append-only"):
            db.commit()
        db.rollback()

        log2 = db.query(AuditLog).first()
        db.delete(log2)
        with pytest.raises(ValueError, match="immutable"):
            db.commit()
        db.rollback()
    finally:
        db.close()
