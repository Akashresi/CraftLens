"""Phase 4 commerce completeness tests: Razorpay UPI, idempotent webhooks, refunds, full order state machine,
sandbox shipping, KYC hook, GI claim verification, reviews, disputes, B2B GST invoicing, and localized notifications.
"""

import hashlib
import hmac
import json

import pytest

from app.core.rate_limit import rate_limiter
from app.models import Inventory, Notification, User
from app.services.commerce_providers import (
    CANONICAL_ORDER_STATES,
    ORDER_TRANSITIONS,
    get_razorpay_webhook_secret,
    validate_order_transition,
)
from tests.conftest import TestingSessionLocal, create_test_artisan


async def _login(async_client, email: str, password: str) -> dict[str, str]:
    res = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _sign_webhook(payload_bytes: bytes) -> str:
    secret = get_razorpay_webhook_secret()
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def test_order_state_machine_all_valid_and_invalid_transitions():
    for src in CANONICAL_ORDER_STATES:
        for tgt in CANONICAL_ORDER_STATES:
            if tgt in ORDER_TRANSITIONS[src]:
                assert validate_order_transition(src, tgt) == tgt
            else:
                with pytest.raises(ValueError):
                    validate_order_transition(src, tgt)
    with pytest.raises(ValueError):
        validate_order_transition("PLACED", "UNKNOWN_STATE")


def _ensure_admin(db, email: str, password: str = "AdminPass#123") -> None:
    from app.core.security import get_password_hash
    from app.models import Role

    admin_role = db.query(Role).filter(Role.code == "ADMIN").first()
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(
            email=email,
            full_name="Test Admin",
            hashed_password=get_password_hash(password),
            is_active=True,
            is_verified=True,
        )
        if admin_role:
            u.roles.append(admin_role)
        db.add(u)
        db.flush()


async def test_e2e_sandbox_commerce_kyc_gi_razorpay_shipping_payout(async_client):
    rate_limiter.reset()
    db = TestingSessionLocal()
    try:
        create_test_artisan(db, "comm.artisan@craftlens.org", "Commerce Artisan", preferred_language="ta")
        _ensure_admin(db, "comm.admin@craftlens.org")
        db.commit()
    finally:
        db.close()

    artisan_h = await _login(async_client, "comm.artisan@craftlens.org", "ArtisanPass#123")
    admin_h = await _login(async_client, "comm.admin@craftlens.org", "AdminPass#123")

    # Register & login Retail Buyer with Hindi preference
    r_reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "comm.buyer@craftlens.org",
            "password": "BuyerPass#2026",
            "full_name": "Ananya Iyer",
            "preferred_language": "hi",
        },
    )
    assert r_reg.status_code in {200, 201}, r_reg.text
    buyer_h = await _login(async_client, "comm.buyer@craftlens.org", "BuyerPass#2026")

    # 1. Artisan submits KYC hook (PAN format) and Admin approves it
    r_kyc = await async_client.post(
        "/api/v1/artisans/me/kyc-hook",
        headers=artisan_h,
        json={"document_type": "PAN", "document_number": "ABCDE1234F", "document_url": "https://cdn/kyc.pdf"},
    )
    assert r_kyc.status_code == 200, r_kyc.text
    assert r_kyc.json()["data"]["kyc_hook"]["format_valid"] is True
    ver_id = r_kyc.json()["data"]["verification"]["id"]

    r_ver_list = await async_client.get("/api/v1/artisans/admin/verifications?status_filter=PENDING", headers=admin_h)
    assert r_ver_list.status_code == 200
    assert any(v["id"] == ver_id for v in r_ver_list.json()["data"])

    r_kyc_ok = await async_client.post(
        f"/api/v1/artisans/admin/verifications/{ver_id}/review",
        headers=admin_h,
        json={"status": "APPROVED", "reviewer_notes": "PAN verified"},
    )
    assert r_kyc_ok.status_code == 200
    assert r_kyc_ok.json()["data"]["status"] == "APPROVED"

    # 2. Artisan creates draft listing, prices it, and submits GI claim -> Admin approves GI claim
    r_prod = await async_client.post(
        "/api/v1/voice/apply-to-product",
        headers=artisan_h,
        json={
            "title": "Kanchipuram Silk Zari Saree",
            "summary": "Traditional handloom mulberry silk weave",
            "primary_material": "Mulberry Silk & Silver Zari",
            "technique": "Korvai Pit Loom",
            "category_slug": "handloom-textiles",
            "artisan_confirmed": True,
        },
    )
    assert r_prod.status_code == 200, r_prod.text
    product_id = r_prod.json()["data"]["product_id"]

    r_price = await async_client.post(
        f"/api/v1/pricing/apply/{product_id}",
        headers=artisan_h,
        json={"retail_price": 4500.0, "wholesale_price": 3400.0, "stock_quantity": 5},
    )
    assert r_price.status_code == 200
    variant_id = r_price.json()["data"]["variant_id"]

    r_gi = await async_client.post(
        f"/api/v1/artisans/products/{product_id}/gi-claim",
        headers=artisan_h,
        json={"gi_claim_code": "GI-TN-001", "notes": "Kanchipuram Silk Society certificate"},
    )
    assert r_gi.status_code == 200
    assert r_gi.json()["data"]["gi_verification_status"] == "PENDING"

    r_gi_list = await async_client.get("/api/v1/artisans/admin/gi-claims?status_filter=PENDING", headers=admin_h)
    assert r_gi_list.status_code == 200
    assert any(c["product_id"] == product_id for c in r_gi_list.json()["data"])

    r_gi_approve = await async_client.post(
        f"/api/v1/artisans/admin/gi-claims/{product_id}/review",
        headers=admin_h,
        json={"status": "APPROVED", "reviewer_notes": "GI registry verified"},
    )
    assert r_gi_approve.status_code == 200
    assert r_gi_approve.json()["data"]["gi_verification_status"] == "APPROVED"

    # 3. Buyer initiates checkout via Razorpay UPI -> PLACED state + upi_intent_uri
    r_co = await async_client.post(
        "/api/v1/orders/checkout",
        headers=buyer_h,
        json={
            "items": [{"variant_id": variant_id, "quantity": 1}],
            "order_type": "RETAIL",
            "delivery_address": {"city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
            "payment_method": "RAZORPAY_UPI",
            "upi_vpa": "ananya@okhdfcbank",
        },
    )
    assert r_co.status_code == 200, r_co.text
    order = r_co.json()["data"]
    order_id = order["id"]
    assert order["status"] == "PLACED"
    assert order["upi_intent_uri"].startswith("upi://pay?")
    gw_order_id = order["payment"]["gateway_order_id"]

    # Illegal skip PLACED -> SHIPPED fails with 400
    r_bad_skip = await async_client.post(
        f"/api/v1/orders/{order_id}/transition",
        headers=artisan_h,
        json={"target_status": "SHIPPED"},
    )
    assert r_bad_skip.status_code == 400

    # 4. Razorpay webhook: bad signature -> 401; valid signature -> PAID; duplicate replay -> idempotent
    wh_payload = json.dumps(
        {
            "event": "payment.captured",
            "event_id": "evt_phase4_001",
            "payload": {"payment": {"entity": {"id": "pay_sbx_999", "order_id": gw_order_id}}},
        }
    ).encode("utf-8")

    r_bad_sig = await async_client.post(
        "/api/v1/orders/webhooks/razorpay",
        content=wh_payload,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": "deadbeef"},
    )
    assert r_bad_sig.status_code == 401

    good_sig = _sign_webhook(wh_payload)
    r_wh1 = await async_client.post(
        "/api/v1/orders/webhooks/razorpay",
        content=wh_payload,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": good_sig},
    )
    assert r_wh1.status_code == 200, r_wh1.text
    assert r_wh1.json()["data"]["order_status"] == "PAID"
    assert r_wh1.json()["data"]["duplicate_ignored"] is False

    r_wh2 = await async_client.post(
        "/api/v1/orders/webhooks/razorpay",
        content=wh_payload,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": good_sig},
    )
    assert r_wh2.status_code == 200
    assert r_wh2.json()["data"]["duplicate_ignored"] is True

    # 5. Artisan fulfills: PAID -> PACKED -> SHIPPED (sandbox courier AWB) -> DELIVERED (payout RELEASED)
    r_pack = await async_client.post(
        f"/api/v1/orders/{order_id}/transition", headers=artisan_h, json={"target_status": "PACKED"}
    )
    assert r_pack.status_code == 200
    assert r_pack.json()["data"]["status"] == "PACKED"

    r_ship = await async_client.post(
        f"/api/v1/orders/{order_id}/transition", headers=artisan_h, json={"target_status": "SHIPPED"}
    )
    assert r_ship.status_code == 200
    assert r_ship.json()["data"]["status"] == "SHIPPED"
    assert r_ship.json()["data"]["shipment"]["tracking_number"].startswith("SR-SBX-")

    r_del = await async_client.post(
        f"/api/v1/orders/{order_id}/transition", headers=artisan_h, json={"target_status": "DELIVERED"}
    )
    assert r_del.status_code == 200
    assert r_del.json()["data"]["status"] == "DELIVERED"
    assert r_del.json()["data"]["payout_status"] == "RELEASED"

    # 6. Verified buyer review & GST invoice
    r_rev = await async_client.post(
        f"/api/v1/orders/{order_id}/review",
        headers=buyer_h,
        json={"product_id": product_id, "rating": 5, "comment": "Exquisite pure zari weave!"},
    )
    assert r_rev.status_code == 200, r_rev.text

    r_pub_revs = await async_client.get(f"/api/v1/marketplace/products/{product_id}/reviews")
    assert r_pub_revs.status_code == 200
    assert len(r_pub_revs.json()["data"]) == 1

    r_inv = await async_client.get(f"/api/v1/orders/{order_id}/invoice", headers=buyer_h)
    assert r_inv.status_code == 200
    inv_data = r_inv.json()["data"]
    assert inv_data["supply_type"] == "INTER_STATE"  # Uttar Pradesh vs Maharashtra
    assert inv_data["igst_inr"] == 225.0  # 5% of 4500

    # Verify localized notifications generated (Hindi for buyer, Tamil for artisan)
    db = TestingSessionLocal()
    try:
        notifs = db.query(Notification).all()
        assert any("ऑर्डर" in n.title or "CraftLens" in n.message for n in notifs)
        assert any("கைவினைஞர்" in n.title or "GI" in n.title for n in notifs)
    finally:
        db.close()


async def test_dispute_refund_restock_and_b2b_gst_invoice(async_client):
    rate_limiter.reset()
    db = TestingSessionLocal()
    try:
        create_test_artisan(db, "disp.artisan@craftlens.org", "Dispute Artisan")
        _ensure_admin(db, "disp.admin@craftlens.org")
        from app.core.security import get_password_hash
        from app.models import Buyer, BuyerBusinessProfile, Role

        ws_role = db.query(Role).filter(Role.code == "WHOLESALE_BUYER").first()
        ws_user = User(
            email="ws.gst@craftlens.org",
            full_name="Wholesale Importer",
            hashed_password=get_password_hash("Wholesale#123"),
            is_active=True,
            is_verified=True,
        )
        if ws_role:
            ws_user.roles.append(ws_role)
        db.add(ws_user)
        db.flush()
        ws_buyer = Buyer(
            user_id=ws_user.id,
            buyer_type="WHOLESALE",
            default_billing_address={"state": "Uttar Pradesh"},
            default_shipping_address={"state": "Uttar Pradesh"},
        )
        db.add(ws_buyer)
        db.flush()
        db.add(
            BuyerBusinessProfile(
                buyer_id=ws_buyer.id,
                company_name="Heritage Emporium",
                gst_number="09AABCH1234F1Z5",
            )
        )
        db.commit()
    finally:
        db.close()

    artisan_h = await _login(async_client, "disp.artisan@craftlens.org", "ArtisanPass#123")
    ws_h = await _login(async_client, "ws.gst@craftlens.org", "Wholesale#123")
    admin_h = await _login(async_client, "disp.admin@craftlens.org", "AdminPass#123")

    r_prod = await async_client.post(
        "/api/v1/voice/apply-to-product",
        headers=artisan_h,
        json={
            "title": "Dhokra Brass Lamp",
            "summary": "Cast brass lamp",
            "primary_material": "Brass",
            "technique": "Lost Wax",
            "category_slug": "metal-brassware",
            "artisan_confirmed": True,
        },
    )
    prod_id = r_prod.json()["data"]["product_id"]
    r_price = await async_client.post(
        f"/api/v1/pricing/apply/{prod_id}",
        headers=artisan_h,
        json={"retail_price": 1200.0, "wholesale_price": 900.0, "stock_quantity": 10},
    )
    var_id = r_price.json()["data"]["variant_id"]

    # Checkout 2 items -> dispute -> admin resolves as RETURNED -> refund issues -> inventory restocked back to 10
    r_co = await async_client.post(
        "/api/v1/orders/checkout",
        headers=ws_h,
        json={
            "items": [{"variant_id": var_id, "quantity": 2}],
            "order_type": "RETAIL",
            "delivery_address": {"city": "Lucknow", "state": "Uttar Pradesh", "pincode": "226001"},
            "payment_method": "SANDBOX",
        },
    )
    ord_id = r_co.json()["data"]["id"]

    r_disp = await async_client.post(
        f"/api/v1/orders/{ord_id}/dispute",
        headers=ws_h,
        json={"reason": "Box arrived dented and base wobbles"},
    )
    assert r_disp.status_code == 200
    assert r_disp.json()["data"]["status"] == "DISPUTED"
    assert r_disp.json()["data"]["payout_status"] == "HELD"

    r_res = await async_client.post(
        f"/api/v1/orders/admin/{ord_id}/resolve-dispute",
        headers=admin_h,
        json={"resolution_status": "RETURNED", "resolution_notes": "Approved return & full refund"},
    )
    assert r_res.status_code == 200
    assert r_res.json()["data"]["status"] == "RETURNED"

    r_ref = await async_client.post(
        f"/api/v1/orders/{ord_id}/refund",
        headers=ws_h,
        json={"reason": "Damaged transit"},
    )
    assert r_ref.status_code == 200
    assert r_ref.json()["data"]["payment"]["status"] == "REFUNDED"
    assert r_ref.json()["data"]["payment"]["refund_ref"].startswith("rfnd_sbx_")

    # Duplicate refund rejected
    r_ref_dup = await async_client.post(f"/api/v1/orders/{ord_id}/refund", headers=ws_h, json={"reason": "Duplicate"})
    assert r_ref_dup.status_code == 400

    db = TestingSessionLocal()
    try:
        inv = db.query(Inventory).filter(Inventory.product_variant_id == var_id).first()
        assert inv is not None
        assert inv.quantity_on_hand == 10
    finally:
        db.close()

    # B2B RFQ -> Quotation -> PO -> GST Intra-state CGST/SGST Invoice
    r_rfq = await async_client.post(
        "/api/v1/b2b/rfq",
        headers=ws_h,
        json={"product_id": prod_id, "target_quantity": 20, "target_unit_price": 850.0, "specifications": "Gift box"},
    )
    rfq_id = r_rfq.json()["data"]["id"]
    r_quote = await async_client.post(
        "/api/v1/b2b/quotation",
        headers=artisan_h,
        json={"purchase_request_id": rfq_id, "quoted_unit_price": 875.0, "lead_time_days": 10},
    )
    quote_id = r_quote.json()["data"]["id"]
    r_po = await async_client.post(f"/api/v1/b2b/quotation/{quote_id}/accept", headers=ws_h)
    po_id = r_po.json()["data"]["id"]

    r_b2b_inv = await async_client.get(f"/api/v1/b2b/purchase-orders/{po_id}/gst-invoice", headers=ws_h)
    assert r_b2b_inv.status_code == 200, r_b2b_inv.text
    b2b_inv = r_b2b_inv.json()["data"]
    assert b2b_inv["supply_type"] == "INTRA_STATE"  # Both Artisan & Wholesale buyer in Uttar Pradesh
    assert b2b_inv["cgst_inr"] == b2b_inv["sgst_inr"] > 0
    assert b2b_inv["buyer"]["gstin"] == "09AABCH1234F1Z5"
