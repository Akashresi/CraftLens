"""Phase 5 backend idempotency verification for mobile offline sync retries."""

from app.core.rate_limit import rate_limiter
from app.models import Product
from tests.conftest import TestingSessionLocal, create_test_artisan


async def test_offline_mobile_sync_idempotency_replay(async_client):
    rate_limiter.reset()
    db = TestingSessionLocal()
    try:
        create_test_artisan(db, "mobile.sync@craftlens.org", "Mobile Sync Artisan")
        db.commit()
    finally:
        db.close()

    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "mobile.sync@craftlens.org", "password": "ArtisanPass#123"},
    )
    assert login.status_code == 200
    headers = {
        "Authorization": f"Bearer {login.json()['access_token']}",
        "X-Idempotency-Key": "idem-mobile-draft-42",
    }
    payload = {
        "title": "Offline Synced Terracotta Lamp",
        "summary": "Captured offline in village studio",
        "primary_material": "Alluvial Clay",
        "technique": "Wheel Throwing",
        "category_slug": "terracotta-pottery",
        "source_language": "ta",
        "artisan_confirmed": True,
    }

    r1 = await async_client.post("/api/v1/voice/apply-to-product", headers=headers, json=payload)
    assert r1.status_code == 200, r1.text
    assert r1.json()["data"]["idempotent_replay"] is False
    prod_id_1 = r1.json()["data"]["product_id"]

    # Retry with exact same X-Idempotency-Key after flaky network -> replays same product_id, zero duplicates
    r2 = await async_client.post("/api/v1/voice/apply-to-product", headers=headers, json=payload)
    assert r2.status_code == 200, r2.text
    assert r2.json()["data"]["idempotent_replay"] is True
    assert r2.json()["data"]["product_id"] == prod_id_1

    db = TestingSessionLocal()
    try:
        matches = db.query(Product).filter(Product.title == "Offline Synced Terracotta Lamp").all()
        assert len(matches) == 1
    finally:
        db.close()
