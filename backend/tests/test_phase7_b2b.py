import pytest

from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.b2b import (
    accept_quotation_and_generate_po,
    get_artisan_incoming_rfqs,
    submit_artisan_quotation,
    submit_request_for_quotation,
)
from app.api.v1.endpoints.voice import apply_catalog_to_product
from app.models import Product, PurchaseOrder, PurchaseRequest, Quotation, User
from app.schemas.b2b import PurchaseRequestCreate, QuotationCreate
from app.schemas.user import UserRegister
from app.schemas.voice import ApplyCatalogIn


def test_b2b_rfq_and_purchase_order_flow(db):
    from tests.conftest import create_test_artisan

    # 1. Register Artisan
    artisan_user = create_test_artisan(
        db=db,
        email="b2b.artisan@craftlens.org",
        password="ArtisanPass#123",
        full_name="Brass Metal Artisan",
    )

    # Create craft product
    prod_res = apply_catalog_to_product(
        payload=ApplyCatalogIn(
            title="Bastar Dhokra Brass Diya Sculpture",
            summary="Ancient 4000-year-old lost-wax bell metal casting",
            primary_material="Brass & Bell Metal",
            technique="Lost Wax Dhokra Casting",
            category_slug="metal-brassware",
            source_language="hi",
        ),
        db=db,
        current_user=artisan_user,
    )
    product_id = prod_res.data["product_id"]

    # 2. Register Wholesale Buyer
    buyer_reg = register_user(
        user_in=UserRegister(
            email="boutique.procure@fabindia-mock.com",
            password="BuyerPass#123",
            full_name="Ananya Corporate Retailer",
            role_code="WHOLESALE_BUYER",
        ),
        db=db,
    )
    buyer_user = db.query(User).filter(User.email == "boutique.procure@fabindia-mock.com").first()

    # 3. Buyer submits RFQ for 50 pieces
    rfq_payload = PurchaseRequestCreate(
        product_id=product_id,
        target_quantity=50,
        target_unit_price=1200.0,
        specifications="Custom gift packaging with artisan story card inside each box",
    )
    rfq_res = submit_request_for_quotation(rfq_in=rfq_payload, db=db, current_user=buyer_user)
    assert rfq_res.success is True
    rfq_id = rfq_res.data.id
    assert rfq_res.data.target_quantity == 50
    assert rfq_res.data.status == "OPEN"

    # 4. Artisan views incoming RFQ
    artisan_rfqs = get_artisan_incoming_rfqs(db=db, current_user=artisan_user)
    assert len(artisan_rfqs.data) >= 1

    # 5. Artisan responds with formal Quotation (₹1150/unit, 20 days lead time)
    quote_payload = QuotationCreate(
        purchase_request_id=rfq_id,
        quoted_unit_price=1150.0,
        lead_time_days=20,
        terms_conditions="Handmade batch production. Delivery within 20 working days.",
    )
    quote_res = submit_artisan_quotation(quote_in=quote_payload, db=db, current_user=artisan_user)
    assert quote_res.success is True
    quotation_id = quote_res.data.id
    assert quote_res.data.total_amount == 50 * 1150.0  # 57,500.0
    assert quote_res.data.status == "PENDING"

    # 6. Buyer accepts quotation -> Generates Purchase Order (PO)
    po_res = accept_quotation_and_generate_po(quotation_id=quotation_id, db=db, current_user=buyer_user)
    assert po_res.success is True
    po_data = po_res.data
    assert po_data.po_number.startswith("PO-")
    assert po_data.status == "ISSUED"
    assert len(po_data.milestone_schedule) == 3

    # Verify PO in database
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_data.id).first()
    assert po is not None
    assert po.quotation.status == "ACCEPTED"
    assert po.quotation.purchase_request.status == "ACCEPTED"
