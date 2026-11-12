"""HTTP integration tests covering every FastAPI router including error and auth failure paths."""

import io

from PIL import Image, ImageDraw


def _make_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (200, 200), color=(245, 240, 230))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 160, 160], fill=(180, 95, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


async def _login_headers(async_client, email: str, password: str) -> dict[str, str]:
    res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_root_and_health_endpoints(async_client):
    r_root = await async_client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "operational"

    r_health = await async_client.get("/api/v1/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"


async def test_auth_login_refresh_and_failures(async_client):
    r_bad = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "admin@craftlens.org", "password": "WrongPassword!"},
    )
    assert r_bad.status_code == 401

    r_ok = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "artisan@craftlens.org", "password": "Artisan@2026"},
    )
    assert r_ok.status_code == 200
    tokens = r_ok.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    r_ref = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r_ref.status_code == 200
    assert "access_token" in r_ref.json()

    r_ref_bad = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r_ref_bad.status_code == 401

    r_ref_garbage = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-jwt"})
    assert r_ref_garbage.status_code == 401

    assert (await async_client.get("/api/v1/auth/me")).status_code == 401
    assert (await async_client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})).status_code == 401


async def test_users_and_buyers_http_flows(async_client):
    email = "http.buyer@craftlens.org"
    r_reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "BuyerPassword#123",
            "full_name": "HTTP Buyer",
            "preferred_language": "en",
        },
    )
    assert r_reg.status_code == 200

    r_dup = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "BuyerPassword#123",
            "full_name": "Duplicate",
        },
    )
    assert r_dup.status_code == 400

    headers = await _login_headers(async_client, email, "BuyerPassword#123")

    assert (await async_client.get("/api/v1/users/me", headers=headers)).status_code == 200
    r_upd = await async_client.put(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": "Updated HTTP Buyer", "preferred_language": "hi"},
    )
    assert r_upd.status_code == 200
    assert r_upd.json()["data"]["full_name"] == "Updated HTTP Buyer"

    r_pw_bad = await async_client.put(
        "/api/v1/users/me/password",
        headers=headers,
        json={"current_password": "Wrong", "new_password": "NewPassword#123"},
    )
    assert r_pw_bad.status_code == 400

    r_pw_ok = await async_client.put(
        "/api/v1/users/me/password",
        headers=headers,
        json={"current_password": "BuyerPassword#123", "new_password": "NewPassword#123"},
    )
    assert r_pw_ok.status_code == 200

    assert (await async_client.get("/api/v1/buyers/me", headers=headers)).status_code == 200
    assert (
        await async_client.put(
            "/api/v1/buyers/me",
            headers=headers,
            json={"default_shipping_address": {"city": "Jaipur"}},
        )
    ).status_code == 200
    assert (
        await async_client.put(
            "/api/v1/buyers/me/business",
            headers=headers,
            json={"company_name": "Test Co"},
        )
    ).status_code == 403


async def test_artisan_studio_voice_pricing_marketplace_http(async_client):
    headers = await _login_headers(async_client, "artisan@craftlens.org", "Artisan@2026")
    buyer_headers = await _login_headers(async_client, "http.buyer@craftlens.org", "NewPassword#123")

    assert (await async_client.get("/api/v1/artisans/me", headers=headers)).status_code == 200
    assert (await async_client.get("/api/v1/artisans/nonexistent-id")).status_code == 404

    jpeg = _make_jpeg_bytes()
    r_empty = await async_client.post(
        "/api/v1/studio/analyze",
        headers=headers,
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert r_empty.status_code == 400

    r_analyze = await async_client.post(
        "/api/v1/studio/analyze",
        headers=headers,
        files={"file": ("craft.jpg", jpeg, "image/jpeg")},
    )
    assert r_analyze.status_code == 200

    r_process = await async_client.post(
        "/api/v1/studio/process",
        headers=headers,
        files={"file": ("craft.jpg", jpeg, "image/jpeg")},
        data={"lifestyle_theme": "wood"},
    )
    assert r_process.status_code == 200

    assert (
        await async_client.post(
            "/api/v1/studio/analyze",
            headers=buyer_headers,
            files={"file": ("craft.jpg", jpeg, "image/jpeg")},
        )
    ).status_code == 403

    r_tr_empty = await async_client.post(
        "/api/v1/voice/transcribe",
        headers=headers,
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert r_tr_empty.status_code == 400

    r_tr = await async_client.post(
        "/api/v1/voice/transcribe",
        headers=headers,
        files={"file": ("voice.wav", b"RIFF0000WAVEfmt ", "audio/wav")},
        data={"language_code": "ta"},
    )
    assert r_tr.status_code == 200

    r_cat = await async_client.post(
        "/api/v1/voice/generate-catalog",
        headers=headers,
        json={"transcript": "Handmade Kanchipuram silk saree", "source_language": "en"},
    )
    assert r_cat.status_code == 200

    r_price = await async_client.post(
        "/api/v1/pricing/calculate",
        headers=headers,
        json={"material_cost": 500, "labor_hours": 4, "labor_hourly_rate": 150},
    )
    assert r_price.status_code == 200
    assert (
        await async_client.post(
            "/api/v1/pricing/apply/nonexistent-id",
            headers=headers,
            json={"retail_price": 1000, "wholesale_price": 800, "stock_quantity": 5},
        )
    ).status_code == 404

    assert (await async_client.get("/api/v1/marketplace/categories")).status_code == 200
    assert (await async_client.get("/api/v1/marketplace/products?search=silk")).status_code == 200
    assert (await async_client.get("/api/v1/marketplace/products/does-not-exist")).status_code == 404

    assert (
        await async_client.post(
            "/api/v1/orders/checkout",
            headers=buyer_headers,
            json={"items": [], "order_type": "RETAIL", "delivery_address": {"city": "Chennai"}},
        )
    ).status_code == 400
    assert (await async_client.get("/api/v1/orders/my-orders", headers=buyer_headers)).status_code == 200
    assert (await async_client.get("/api/v1/orders/artisan-orders", headers=headers)).status_code == 200

    assert (await async_client.get("/api/v1/heritage/verify/unknown-hash")).status_code == 404
    assert (
        await async_client.post(
            "/api/v1/heritage/provenance",
            headers=headers,
            json={
                "product_id": "missing",
                "batch_code": "BATCH-001",
                "raw_materials_source": "Clay",
                "craft_technique_details": "Hand thrown",
            },
        )
    ).status_code == 404
    assert (await async_client.post("/api/v1/heritage/generate-qr/missing", headers=headers)).status_code == 404

    assert (await async_client.get("/api/v1/business/metrics", headers=headers)).status_code == 200
    assert (
        await async_client.post(
            "/api/v1/business/ask-assistant",
            headers=headers,
            json={"query": "How much revenue did I earn?"},
        )
    ).status_code == 200
    assert (
        await async_client.post(
            "/api/v1/business/marketing-copy",
            headers=headers,
            json={"product_title": "Silk Saree", "craft_technique": "Korvai", "platform": "INSTAGRAM"},
        )
    ).status_code == 200
    assert (await async_client.get("/api/v1/business/metrics", headers=buyer_headers)).status_code == 403

    assert (
        await async_client.post(
            "/api/v1/compliance/consent",
            headers=buyer_headers,
            json={"consent_type": "DPDP_PRIVACY_POLICY", "granted": True},
        )
    ).status_code == 200
    assert (await async_client.get("/api/v1/compliance/consent", headers=buyer_headers)).status_code == 200

    assert (await async_client.get("/api/v1/artisan-applications/me", headers=buyer_headers)).status_code == 200
    admin_headers = await _login_headers(async_client, "admin@craftlens.org", "CraftLensAdmin@2026")
    assert (
        await async_client.post(
            "/api/v1/artisan-applications/admin/missing-id/approve",
            headers=admin_headers,
            json={},
        )
    ).status_code == 404
