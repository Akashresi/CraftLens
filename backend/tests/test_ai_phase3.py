"""Phase 3 AI quality verification tests: vision cropping, async studio queue, multilingual voice/listing, confirmation safety, and explainable pricing."""

import asyncio
import io
import struct
import wave

import cv2
import numpy as np

from app.core.rate_limit import rate_limiter
from app.models import AuditLog, PricingHistory, Product
from tests.conftest import TestingSessionLocal, create_test_artisan


def _png_bytes(img: np.ndarray) -> bytes:
    ok, enc = cv2.imencode(".png", img)
    assert ok
    return enc.tobytes()


def _wav_bytes() -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        frames = b"".join(struct.pack("<h", int(1000 * np.sin(2 * np.pi * 440 * i / 16000))) for i in range(4000))
        wf.writeframes(frames)
    return buf.getvalue()


async def _login(async_client, email: str, password: str) -> dict[str, str]:
    res = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def test_vision_quality_cropping_and_async_job_queue(async_client):
    rate_limiter.reset()
    db = TestingSessionLocal()
    try:
        create_test_artisan(db, "studio.a@craftlens.org", "Studio Artisan A")
        create_test_artisan(db, "studio.b@craftlens.org", "Studio Artisan B")
        db.commit()
    finally:
        db.close()

    headers_a = await _login(async_client, "studio.a@craftlens.org", "ArtisanPass#123")
    headers_b = await _login(async_client, "studio.b@craftlens.org", "ArtisanPass#123")

    # Balanced textured image -> valid framing
    rng = np.random.default_rng(7)
    balanced = np.full((240, 240, 3), 235, dtype=np.uint8)
    balanced[55:185, 55:185] = rng.integers(45, 195, size=(130, 130, 3), dtype=np.uint8)
    r_ok = await async_client.post(
        "/api/v1/studio/analyze",
        headers=headers_a,
        files={"file": ("craft.png", _png_bytes(balanced), "image/png")},
    )
    assert r_ok.status_code == 200, r_ok.text
    data_ok = r_ok.json()["data"]
    assert data_ok["is_cropped_at_edge"] is False
    assert data_ok["subject_coverage_ratio"] > 0.12

    # Edge-cropped textured image -> flagged as cropped at edge
    cropped = np.full((240, 240, 3), 240, dtype=np.uint8)
    cropped[1:239, 1:239] = rng.integers(40, 180, size=(238, 238, 3), dtype=np.uint8)
    r_crop = await async_client.post(
        "/api/v1/studio/analyze",
        headers=headers_a,
        files={"file": ("cropped.png", _png_bytes(cropped), "image/png")},
    )
    assert r_crop.status_code == 200
    assert r_crop.json()["data"]["is_cropped_at_edge"] is True

    # Async Studio Job enqueue + polling + IDOR check
    r_enqueue = await async_client.post(
        "/api/v1/studio/process-async",
        headers=headers_a,
        files={"file": ("craft.png", _png_bytes(balanced), "image/png")},
        data={"lifestyle_theme": "wood"},
    )
    assert r_enqueue.status_code == 200, r_enqueue.text
    job_id = r_enqueue.json()["data"]["job_id"]

    # Another artisan cannot poll job_id
    r_idor = await async_client.get(f"/api/v1/studio/jobs/{job_id}", headers=headers_b)
    assert r_idor.status_code == 403

    # Poll until completed
    final_status = None
    for _ in range(40):
        r_poll = await async_client.get(f"/api/v1/studio/jobs/{job_id}", headers=headers_a)
        assert r_poll.status_code == 200
        body = r_poll.json()["data"]
        final_status = body["status"]
        if final_status in {"COMPLETED", "FAILED"}:
            break
        await asyncio.sleep(0.05)

    assert final_status == "COMPLETED"
    assert body["result"]["white_bg_url"].endswith("_white.jpg")


async def test_multilingual_voice_and_confirmation_safety(async_client):
    rate_limiter.reset()
    db = TestingSessionLocal()
    try:
        create_test_artisan(db, "voice.artisan@craftlens.org", "Voice Artisan")
        db.commit()
    finally:
        db.close()

    headers = await _login(async_client, "voice.artisan@craftlens.org", "ArtisanPass#123")

    # 1. ASR returns honest low-confidence fallback without silent fake score
    r_asr = await async_client.post(
        "/api/v1/voice/transcribe",
        headers=headers,
        files={"file": ("speech.wav", _wav_bytes(), "audio/wav")},
        data={"language_code": "ml"},
    )
    assert r_asr.status_code == 200, r_asr.text
    asr_data = r_asr.json()["data"]
    assert asr_data["detected_language"] == "ml"
    assert asr_data["confidence"] <= 0.3
    assert asr_data["needs_confirmation"] is True

    # 2. Extract listings in Tamil, Hindi, Marathi, Kannada
    samples = [
        ("ta", "இது கைத்தறி பட்டுப் புடவை", "handloom-textiles"),
        ("hi", "पीतल की मूर्ति ढोकरा कला", "metal-brassware"),
        ("mr", "वारली चित्रकला हाताने रंगवलेली", "traditional-painting"),
        ("kn", "ಚನ್ನಪಟ್ಟಣದ ಮರದ ಗೊಂಬೆ", "woodcraft-toys"),
    ]
    for lang, text, expected_cat in samples:
        r_gen = await async_client.post(
            "/api/v1/voice/generate-catalog",
            headers=headers,
            json={"transcript": text, "source_language": lang},
        )
        assert r_gen.status_code == 200, r_gen.text
        gen = r_gen.json()["data"]
        assert gen["suggested_category_slug"] == expected_cat
        assert gen["requires_artisan_confirmation"] is True
        assert gen["listing_status"] == "DRAFT_PREVIEW"
        assert len(gen["title_local"]) > 0

    # 3. Attempting to publish/save without explicit artisan confirmation fails (400)
    r_reject = await async_client.post(
        "/api/v1/voice/apply-to-product",
        headers=headers,
        json={
            "title": "Draft Craft",
            "summary": "Handmade craft",
            "primary_material": "Mulberry Silk",
            "technique": "Handloom Weaving",
            "category_slug": "handloom-textiles",
            "artisan_confirmed": False,
        },
    )
    assert r_reject.status_code == 400

    # 4. Confirmed draft persists as DRAFT (not auto-published ACTIVE)
    r_confirm = await async_client.post(
        "/api/v1/voice/apply-to-product",
        headers=headers,
        json={
            "title": "Verified Handwoven Silk Saree",
            "summary": "Pure silk saree crafted on pit loom",
            "primary_material": "Mulberry Silk",
            "technique": "Pit Loom Weaving",
            "category_slug": "handloom-textiles",
            "artisan_confirmed": True,
        },
    )
    assert r_confirm.status_code == 200, r_confirm.text
    product_id = r_confirm.json()["data"]["product_id"]

    db = TestingSessionLocal()
    try:
        prod = db.query(Product).filter(Product.id == product_id).first()
        assert prod is not None
        assert prod.status == "DRAFT"
    finally:
        db.close()

    # 5. Pricing calculation enforces regional floor + logs override
    r_calc = await async_client.post(
        "/api/v1/pricing/calculate",
        headers=headers,
        json={
            "material_cost": 500,
            "labor_hours": 10,
            "labor_hourly_rate": 100,
            "packaging_cost": 50,
            "transportation_cost": 50,
            "overhead_cost": 50,
            "heritage_rarity_score": 1.15,
            "region_state": "Kerala",
        },
    )
    assert r_calc.status_code == 200, r_calc.text
    calc = r_calc.json()["data"]
    assert calc["why_this_price"]["effective_hourly_wage_inr"] == 170.0
    assert calc["why_this_price"]["region_state"] == "Kerala"

    r_apply_price = await async_client.post(
        f"/api/v1/pricing/apply/{product_id}",
        headers=headers,
        json={
            "retail_price": calc["recommended_retail_price"] + 250.0,
            "wholesale_price": calc["recommended_wholesale_price"],
            "stock_quantity": 5,
            "recommended_retail_price": calc["recommended_retail_price"],
            "override_reason": "Festival demand adjustment",
        },
    )
    assert r_apply_price.status_code == 200, r_apply_price.text

    db = TestingSessionLocal()
    try:
        hist = db.query(PricingHistory).filter(PricingHistory.product_id == product_id).all()
        assert len(hist) >= 1
        audit = (
            db.query(AuditLog)
            .filter(AuditLog.action == "PRICE_OVERRIDE_LOGGED", AuditLog.resource == f"product:{product_id}")
            .first()
        )
        assert audit is not None
    finally:
        db.close()
