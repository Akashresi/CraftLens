import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_role
from app.db.session import get_db
from app.models import (
    ArtisanProfile,
    Buyer,
    Product,
    PurchaseOrder,
    PurchaseRequest,
    Quotation,
    User,
)
from app.schemas.b2b import (
    PurchaseOrderOut,
    PurchaseRequestCreate,
    PurchaseRequestOut,
    QuotationCreate,
    QuotationOut,
)
from app.schemas.common import APIResponse
from app.services.commerce_providers import build_gst_invoice

router = APIRouter()


@router.post("/rfq", response_model=APIResponse[PurchaseRequestOut])
def submit_request_for_quotation(
    rfq_in: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("WHOLESALE_BUYER")),
):
    """Submits a formal bulk RFQ with target quantity and custom specifications."""
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        buyer = Buyer(user_id=current_user.id, buyer_type="WHOLESALE")
        db.add(buyer)
        db.flush()

    product = db.query(Product).filter(Product.id == rfq_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    rfq = PurchaseRequest(
        buyer_id=buyer.id,
        product_id=product.id,
        target_quantity=rfq_in.target_quantity,
        target_unit_price=rfq_in.target_unit_price,
        required_delivery_date=rfq_in.required_delivery_date,
        specifications=rfq_in.specifications,
        status="OPEN",
    )
    db.add(rfq)
    db.commit()
    db.refresh(rfq)

    return APIResponse(
        success=True,
        message="Request for Quotation submitted to artisan",
        data=PurchaseRequestOut.model_validate(rfq),
    )


@router.get("/rfq/artisan", response_model=APIResponse[list[PurchaseRequestOut]])
def get_artisan_incoming_rfqs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Retrieves all open RFQs targeting products created by the authenticated artisan."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        return APIResponse(success=True, message="No RFQs found", data=[])

    rfqs = (
        db.query(PurchaseRequest)
        .join(Product)
        .filter(Product.artisan_id == profile.id)
        .order_by(desc(PurchaseRequest.created_at))
        .all()
    )
    return APIResponse(
        success=True,
        message="Artisan incoming RFQs retrieved",
        data=[PurchaseRequestOut.model_validate(r) for r in rfqs],
    )


@router.post("/quotation", response_model=APIResponse[QuotationOut])
def submit_artisan_quotation(
    quote_in: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Artisan responds to bulk RFQ with pricing, production lead time, and terms."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Artisan profile not found")

    rfq = db.query(PurchaseRequest).filter(PurchaseRequest.id == quote_in.purchase_request_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    rfq_product = db.query(Product).filter(Product.id == rfq.product_id).first()
    if not rfq_product or (
        rfq_product.artisan_id != profile.id and "ADMIN" not in [r.code for r in current_user.roles]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you can only quote on RFQs for your own products",
        )

    total_amount = round(float(quote_in.quoted_unit_price) * rfq.target_quantity, 2)

    quotation = Quotation(
        purchase_request_id=rfq.id,
        artisan_id=profile.id,
        quoted_unit_price=quote_in.quoted_unit_price,
        total_amount=total_amount,
        lead_time_days=quote_in.lead_time_days,
        terms_conditions=quote_in.terms_conditions,
        status="PENDING",
    )
    db.add(quotation)
    rfq.status = "RESPONDED"
    db.commit()
    db.refresh(quotation)

    return APIResponse(
        success=True,
        message="Quotation submitted to buyer",
        data=QuotationOut.model_validate(quotation),
    )


@router.post("/quotation/{quotation_id}/accept", response_model=APIResponse[PurchaseOrderOut])
def accept_quotation_and_generate_po(
    quotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("WHOLESALE_BUYER")),
):
    """Buyer accepts quotation, triggering formal Purchase Order (PO) creation
    with milestone payment and delivery schedule.
    """
    quote = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")

    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    roles = [r.code for r in current_user.roles]
    if "ADMIN" not in roles and (not buyer or quote.purchase_request.buyer_id != buyer.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you can only accept quotations for your own RFQ",
        )

    quote.status = "ACCEPTED"
    quote.purchase_request.status = "ACCEPTED"

    po_number = f"PO-{datetime.now(UTC).strftime('%Y%m')}-{str(uuid.uuid4())[:6].upper()}"

    milestones = [
        {"milestone": "Advance Deposit (Raw Materials)", "percent": 30, "status": "PENDING"},
        {"milestone": "Mid-Production Inspection", "percent": 40, "status": "UPCOMING"},
        {"milestone": "Final Dispatch & Delivery", "percent": 30, "status": "UPCOMING"},
    ]

    po = PurchaseOrder(
        quotation_id=quote.id,
        po_number=po_number,
        payment_terms="30% Advance, 40% Mid-Production, 30% on Dispatch",
        milestone_schedule=milestones,
        status="ISSUED",
    )
    db.add(po)
    db.commit()
    db.refresh(po)

    return APIResponse(
        success=True,
        message="Quotation accepted and Purchase Order issued",
        data=PurchaseOrderOut.model_validate(po),
    )


@router.get("/purchase-orders/{po_id}/gst-invoice", response_model=APIResponse[dict])
def get_b2b_gst_invoice(
    po_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generates a B2B GST Tax Invoice (CGST/SGST or IGST + HSN code) for an issued Purchase Order."""
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")

    quote = po.quotation
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    artisan = db.query(ArtisanProfile).filter(ArtisanProfile.id == quote.artisan_id).first()
    roles = [r.code for r in current_user.roles]
    is_admin = "ADMIN" in roles
    is_buyer = bool(buyer and quote.purchase_request.buyer_id == buyer.id)
    is_artisan = bool(artisan and artisan.user_id == current_user.id)
    if not (is_admin or is_buyer or is_artisan):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this PO invoice")

    seller_name = artisan.user.full_name if artisan and artisan.user else "Artisan Supplier"
    seller_state = artisan.state if artisan and artisan.state else "Uttar Pradesh"
    po_buyer = quote.purchase_request.buyer
    biz = po_buyer.business_profile if po_buyer else None
    buyer_name = (biz.company_name if biz else None) or (
        po_buyer.user.full_name if po_buyer.user else "Wholesale Buyer"
    )
    buyer_state = str(
        (po_buyer.default_billing_address or {}).get("state")
        or (po_buyer.default_shipping_address or {}).get("state")
        or "Maharashtra"
    )

    invoice = build_gst_invoice(
        invoice_number=f"GST-{po.po_number}",
        doc_ref=po.po_number,
        seller_name=seller_name,
        seller_state=seller_state,
        buyer_name=buyer_name,
        buyer_state=buyer_state,
        taxable_subtotal=float(quote.total_amount),
        shipping_fee=0.0,
        gst_rate_percent=float(po.gst_rate_percent),
        hsn_code=po.hsn_code,
        buyer_gstin=po.buyer_gstin or (biz.gst_number if biz else None),
        seller_gstin=po.seller_gstin,
    )
    return APIResponse(success=True, message="B2B GST invoice generated", data=invoice)
