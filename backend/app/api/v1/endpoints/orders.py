import json
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_role
from app.core.upload_security import sanitize_text
from app.db.session import get_db
from app.models import (
    ArtisanProfile,
    AuditLog,
    Buyer,
    Inventory,
    Order,
    OrderItem,
    Payment,
    ProductVariant,
    Review,
    Shipment,
    StockMovement,
    User,
)
from app.schemas.common import APIResponse
from app.schemas.marketplace import (
    DisputeResolveIn,
    OrderCreateIn,
    OrderDisputeIn,
    OrderOut,
    OrderRefundIn,
    OrderReviewCreateIn,
    OrderTransitionIn,
    ReviewOut,
)
from app.services.commerce_providers import (
    RazorpayPaymentProvider,
    build_gst_invoice,
    get_shipping_provider,
    notification_provider,
    validate_order_transition,
)

router = APIRouter()
razorpay_provider = RazorpayPaymentProvider()


def _restock_order_items(db: Session, order: Order, note: str) -> None:
    """Returns inventory back to stock on cancellation or return."""
    for item in order.items:
        inv = db.query(Inventory).filter(Inventory.product_variant_id == item.product_variant_id).first()
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
        if inv:
            inv.quantity_on_hand += item.quantity
            if variant:
                variant.stock_quantity = inv.quantity_on_hand
            db.add(
                StockMovement(
                    inventory_id=inv.id,
                    quantity_change=item.quantity,
                    movement_type="RETURN_RESTOCK",
                    notes=note,
                )
            )


def _authorize_order_participant(db: Session, order: Order, current_user: User) -> tuple[bool, bool, bool]:
    roles = [r.code for r in current_user.roles]
    is_admin = "ADMIN" in roles
    is_buyer_owner = bool(order.buyer and order.buyer.user_id == current_user.id)
    artisan = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    is_item_artisan = bool(artisan and any(it.artisan_id == artisan.id for it in order.items))
    if not (is_admin or is_buyer_owner or is_item_artisan):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access this order",
        )
    return is_admin, is_buyer_owner, is_item_artisan


@router.post("/checkout", response_model=APIResponse[OrderOut])
def create_order_checkout(
    order_in: OrderCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Executes atomic checkout transaction with stock deduction, Razorpay/UPI initialization
    (PLACED awaiting webhook) or Sandbox immediate confirmation (CONFIRMED).
    """
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        buyer = Buyer(user_id=current_user.id, buyer_type=order_in.order_type)
        db.add(buyer)
        db.flush()

    if not order_in.items:
        raise HTTPException(status_code=400, detail="Cannot create empty order")

    subtotal = 0.0
    order_items_to_create = []

    for item in order_in.items:
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail=f"Variant {item.variant_id} not found")

        inv = db.query(Inventory).filter(Inventory.product_variant_id == variant.id).first()
        if not inv or inv.quantity_on_hand < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{variant.title}'. Available: {inv.quantity_on_hand if inv else 0}",
            )

        unit_price = float(
            variant.price_wholesale
            if order_in.order_type == "WHOLESALE" and item.quantity >= variant.min_wholesale_qty
            else variant.price_retail
        )
        line_total = round(unit_price * item.quantity, 2)
        subtotal += line_total

        inv.quantity_on_hand -= item.quantity
        variant.stock_quantity = inv.quantity_on_hand
        db.add(
            StockMovement(
                inventory_id=inv.id,
                quantity_change=-item.quantity,
                movement_type="SALE_DEDUCT",
                notes="Order checkout deduction",
            )
        )

        order_items_to_create.append(
            {
                "variant_id": variant.id,
                "artisan_id": variant.product.artisan_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": line_total,
            }
        )

    shipping_fee = 0.0 if subtotal >= 1000.0 else 100.0
    total_amount = round(subtotal + shipping_fee, 2)
    order_num = f"ORD-{datetime.now(UTC).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    is_razorpay = order_in.payment_method.upper() in {"RAZORPAY", "RAZORPAY_UPI", "UPI"}

    new_order = Order(
        order_number=order_num,
        buyer_id=buyer.id,
        order_type=order_in.order_type,
        subtotal=subtotal,
        discount=0.0,
        tax=0.0,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        status="PLACED" if is_razorpay else "CONFIRMED",
        payout_status="PENDING" if is_razorpay else "ELIGIBLE",
        gst_invoice_number=f"INV-{order_num}",
        delivery_address=order_in.delivery_address,
    )
    db.add(new_order)
    db.flush()

    for oi in order_items_to_create:
        db.add(
            OrderItem(
                order_id=new_order.id,
                product_variant_id=oi["variant_id"],
                artisan_id=oi["artisan_id"],
                quantity=oi["quantity"],
                unit_price=oi["unit_price"],
                total_price=oi["total_price"],
            )
        )

    upi_intent_uri = None
    if is_razorpay:
        rzp = razorpay_provider.create_upi_order(
            amount_inr=total_amount,
            receipt=order_num,
            upi_vpa=order_in.upi_vpa,
        )
        upi_intent_uri = rzp["upi_intent_uri"]
        payment = Payment(
            order_id=new_order.id,
            payment_gateway="RAZORPAY_UPI",
            transaction_ref=f"TXN-{str(uuid.uuid4())[:12].upper()}",
            gateway_order_id=rzp["gateway_order_id"],
            upi_vpa=order_in.upi_vpa or "craftlens@icici",
            amount=total_amount,
            currency="INR",
            status="INITIATED",
            webhook_event_ids=[],
        )
        shipment_status = "PENDING_PAYMENT"
    else:
        payment = Payment(
            order_id=new_order.id,
            payment_gateway=order_in.payment_method,
            transaction_ref=f"TXN-{str(uuid.uuid4())[:12].upper()}",
            gateway_order_id=f"order_sbx_{uuid.uuid4().hex[:12]}",
            amount=total_amount,
            currency="INR",
            status="SUCCESS",
            paid_at=datetime.now(UTC),
            webhook_event_ids=[],
        )
        shipment_status = "MANIFESTED"

    db.add(payment)
    db.add(
        Shipment(
            order_id=new_order.id,
            shipping_provider="SHIPROCKET_SANDBOX",
            carrier="India Post / Delhivery (Sandbox)",
            tracking_number=f"IN-{datetime.now(UTC).strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}",
            status=shipment_status,
        )
    )

    notification_provider.dispatch(
        db=db,
        user_id=current_user.id,
        language=current_user.preferred_language,
        event="ORDER_PLACED",
        ref=order_num,
        amount=total_amount,
    )

    db.commit()
    db.refresh(new_order)

    out = OrderOut.model_validate(new_order)
    out.upi_intent_uri = upi_intent_uri
    return APIResponse(
        success=True,
        message=(
            "Order placed; complete Razorpay UPI payment to confirm"
            if is_razorpay
            else "Order placed successfully and payment verified"
        ),
        data=out,
    )


@router.post("/webhooks/razorpay", response_model=APIResponse[dict])
async def razorpay_payment_webhook(request: Request, db: Session = Depends(get_db)):
    """Idempotent Razorpay webhook receiver verified via X-Razorpay-Signature HMAC-SHA256."""
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not razorpay_provider.verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Malformed webhook JSON") from exc

    event_id = str(request.headers.get("X-Razorpay-Event-Id") or payload.get("event_id") or "")
    event_type = str(payload.get("event", ""))
    pay_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    gateway_order_id = pay_entity.get("order_id")
    gateway_payment_id = pay_entity.get("id")

    if not gateway_order_id:
        raise HTTPException(status_code=400, detail="Missing payment.entity.order_id")

    payment = db.query(Payment).filter(Payment.gateway_order_id == gateway_order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment order not found")

    seen_events = list(payment.webhook_event_ids or [])
    if event_id and event_id in seen_events:
        return APIResponse(
            success=True,
            message="Duplicate webhook event ignored idempotently",
            data={"duplicate_ignored": True, "order_id": payment.order_id, "order_status": payment.order.status},
        )

    if event_type == "payment.captured":
        payment.status = "SUCCESS"
        payment.gateway_payment_id = gateway_payment_id or payment.gateway_payment_id
        payment.paid_at = datetime.now(UTC)
        if payment.order.status == "PLACED":
            payment.order.status = validate_order_transition(payment.order.status, "PAID")
            payment.order.payout_status = "ELIGIBLE"
            if payment.order.shipment:
                payment.order.shipment.status = "MANIFESTED"
    elif event_type == "payment.failed":
        payment.status = "FAILED"

    if event_id:
        seen_events.append(event_id)
        payment.webhook_event_ids = seen_events

    db.add(
        AuditLog(
            user_id=payment.order.buyer.user_id if payment.order.buyer else None,
            action="PAYMENT_WEBHOOK_PROCESSED",
            resource=f"order:{payment.order_id}",
            details={"event_type": event_type, "event_id": event_id, "gateway_order_id": gateway_order_id},
        )
    )
    db.commit()

    return APIResponse(
        success=True,
        message="Razorpay webhook processed",
        data={
            "duplicate_ignored": False,
            "order_id": payment.order_id,
            "order_status": payment.order.status,
            "payment_status": payment.status,
        },
    )


@router.get("/my-orders", response_model=APIResponse[list[OrderOut]])
def get_buyer_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves all past orders placed by the authenticated buyer."""
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        return APIResponse(success=True, message="No orders found", data=[])

    orders = db.query(Order).filter(Order.buyer_id == buyer.id).order_by(desc(Order.created_at)).all()
    return APIResponse(
        success=True,
        message="Buyer orders retrieved",
        data=[OrderOut.model_validate(o) for o in orders],
    )


@router.get("/artisan-orders", response_model=APIResponse[list[dict]])
def get_artisan_incoming_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Retrieves incoming customer orders containing items crafted by this artisan."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        return APIResponse(success=True, message="Artisan profile not found", data=[])

    items = db.query(OrderItem).filter(OrderItem.artisan_id == profile.id).order_by(desc(OrderItem.id)).all()

    results = []
    for it in items:
        results.append(
            {
                "order_id": it.order.id if it.order else None,
                "order_number": it.order.order_number if it.order else "N/A",
                "order_status": it.order.status if it.order else "PENDING",
                "payout_status": it.order.payout_status if it.order else "PENDING",
                "product_title": it.variant.product.title if it.variant and it.variant.product else "Craft Item",
                "variant_sku": it.variant.sku if it.variant else "SKU",
                "quantity": it.quantity,
                "unit_price": float(it.unit_price),
                "total_payout": float(it.total_price),
                "ordered_at": it.order.created_at.isoformat() if it.order else None,
            }
        )

    return APIResponse(
        success=True,
        message="Artisan incoming order items retrieved",
        data=results,
    )


@router.get("/{order_id}", response_model=APIResponse[OrderOut])
def get_order_detail(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves a single order only if owned by the buyer, an involved artisan, or admin (IDOR guard)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    _authorize_order_participant(db, order, current_user)

    return APIResponse(
        success=True,
        message="Order details retrieved",
        data=OrderOut.model_validate(order),
    )


@router.post("/{order_id}/transition", response_model=APIResponse[OrderOut])
def transition_order_state(
    order_id: str,
    payload: OrderTransitionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Advances an order through the validated state machine:
    PLACED -> PAID -> PACKED -> SHIPPED -> DELIVERED (releasing payout) | CANCELLED | RETURNED | DISPUTED.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    is_admin, is_buyer_owner, is_item_artisan = _authorize_order_participant(db, order, current_user)
    target = payload.target_status.strip().upper()

    # Role permission matrix per transition target
    if target in {"PACKED", "SHIPPED", "DELIVERED", "PAID"} and not (is_admin or is_item_artisan):
        raise HTTPException(status_code=403, detail="Only artisan or admin may advance fulfillment states")
    if target in {"CANCELLED", "RETURNED", "DISPUTED"} and not (is_admin or is_buyer_owner or is_item_artisan):
        raise HTTPException(status_code=403, detail="Not permitted to change order status")

    try:
        next_status = validate_order_transition(order.status, target)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    prev_status = order.status
    order.status = next_status

    if next_status == "SHIPPED":
        ship_res = get_shipping_provider().create_shipment(
            order_number=order.order_number,
            destination=order.delivery_address or {},
        )
        if not order.shipment:
            order.shipment = Shipment(order_id=order.id)
        order.shipment.shipping_provider = ship_res["provider"]
        order.shipment.carrier = payload.carrier or ship_res["carrier"]
        order.shipment.tracking_number = ship_res["tracking_number"]
        order.shipment.label_url = ship_res["label_url"]
        order.shipment.status = "IN_TRANSIT"
        order.shipment.shipped_at = datetime.now(UTC)

        if order.buyer and order.buyer.user:
            notification_provider.dispatch(
                db=db,
                user_id=order.buyer.user.id,
                language=order.buyer.user.preferred_language,
                event="ORDER_SHIPPED",
                ref=order.order_number,
                extra=f"{order.shipment.carrier} ({order.shipment.tracking_number})",
            )

    elif next_status == "DELIVERED":
        if order.shipment:
            order.shipment.status = "DELIVERED"
            order.shipment.delivered_at = datetime.now(UTC)
        order.payout_status = "RELEASED"
        order.payout_released_at = datetime.now(UTC)

        seen_artisans = set()
        for it in order.items:
            art = db.query(ArtisanProfile).filter(ArtisanProfile.id == it.artisan_id).first()
            if art and art.user and art.user.id not in seen_artisans:
                seen_artisans.add(art.user.id)
                notification_provider.dispatch(
                    db=db,
                    user_id=art.user.id,
                    language=art.user.preferred_language,
                    event="PAYOUT_RELEASED",
                    ref=order.order_number,
                    amount=float(order.subtotal),
                )

    elif next_status in {"CANCELLED", "RETURNED"} and prev_status not in {"CANCELLED", "RETURNED"}:
        _restock_order_items(db, order, f"Order {next_status.lower()}: {payload.notes or order.order_number}")

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="ORDER_STATE_TRANSITION",
            resource=f"order:{order.id}",
            details={"from": prev_status, "to": next_status, "notes": payload.notes},
        )
    )
    db.commit()
    db.refresh(order)

    return APIResponse(
        success=True,
        message=f"Order transitioned from {prev_status} to {next_status}",
        data=OrderOut.model_validate(order),
    )


@router.post("/{order_id}/refund", response_model=APIResponse[OrderOut])
def refund_order_payment(
    order_id: str,
    payload: OrderRefundIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Issues a Razorpay refund for a paid/cancelled/returned order and records audit trail."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    is_admin, is_buyer_owner, _ = _authorize_order_participant(db, order, current_user)
    if not (is_admin or is_buyer_owner):
        raise HTTPException(status_code=403, detail="Only buyer or admin may initiate refund")

    if not order.payment or order.payment.status == "REFUNDED":
        raise HTTPException(status_code=400, detail="Payment not eligible or already refunded")
    if order.status not in {"CANCELLED", "RETURNED", "PAID", "CONFIRMED", "DISPUTED"}:
        raise HTTPException(status_code=400, detail=f"Cannot refund order in status {order.status}")

    refund_amt = round(float(payload.amount or order.total_amount), 2)
    if refund_amt > float(order.total_amount):
        raise HTTPException(status_code=400, detail="Refund amount exceeds order total")

    rzp_res = razorpay_provider.issue_refund(order.payment.gateway_payment_id, refund_amt)
    order.payment.status = "REFUNDED"
    order.payment.refund_ref = rzp_res["refund_ref"]
    order.payment.refund_amount = refund_amt
    order.payment.refunded_at = datetime.now(UTC)

    if order.status in {"PAID", "CONFIRMED"}:
        order.status = validate_order_transition(order.status, "CANCELLED")
        _restock_order_items(db, order, f"Refund restock ({payload.reason})")

    order.payout_status = "HELD"
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="PAYMENT_REFUNDED",
            resource=f"order:{order.id}",
            details={
                "refund_ref": rzp_res["refund_ref"],
                "amount": refund_amt,
                "reason": sanitize_text(payload.reason),
            },
        )
    )
    db.commit()
    db.refresh(order)
    return APIResponse(success=True, message="Refund processed successfully", data=OrderOut.model_validate(order))


@router.post("/{order_id}/dispute", response_model=APIResponse[OrderOut])
def open_order_dispute(
    order_id: str,
    payload: OrderDisputeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Buyer opens a dispute; holds artisan payout until Admin resolution."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    is_admin, is_buyer_owner, _ = _authorize_order_participant(db, order, current_user)
    if not (is_admin or is_buyer_owner):
        raise HTTPException(status_code=403, detail="Only the buyer or admin may raise a dispute")

    try:
        order.status = validate_order_transition(order.status, "DISPUTED")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    order.dispute_reason = sanitize_text(payload.reason)
    order.payout_status = "HELD"
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="ORDER_DISPUTE_OPENED",
            resource=f"order:{order.id}",
            details={"reason": order.dispute_reason},
        )
    )
    db.commit()
    db.refresh(order)
    return APIResponse(success=True, message="Order dispute submitted", data=OrderOut.model_validate(order))


@router.post("/admin/{order_id}/resolve-dispute", response_model=APIResponse[OrderOut])
def admin_resolve_dispute(
    order_id: str,
    payload: DisputeResolveIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Admin resolves an open order dispute to DELIVERED, RETURNED, CANCELLED, or PAID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "DISPUTED":
        raise HTTPException(status_code=400, detail="Order is not currently disputed")

    try:
        next_status = validate_order_transition(order.status, payload.resolution_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    order.status = next_status
    order.dispute_resolution = sanitize_text(payload.resolution_notes)
    if next_status == "DELIVERED":
        order.payout_status = "RELEASED"
        order.payout_released_at = datetime.now(UTC)
    elif next_status in {"CANCELLED", "RETURNED"}:
        _restock_order_items(db, order, f"Dispute resolved as {next_status}")
        order.payout_status = "HELD"

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="ORDER_DISPUTE_RESOLVED",
            resource=f"order:{order.id}",
            details={"resolution_status": next_status, "notes": order.dispute_resolution},
        )
    )
    db.commit()
    db.refresh(order)
    return APIResponse(success=True, message="Order dispute resolved", data=OrderOut.model_validate(order))


@router.post("/{order_id}/review", response_model=APIResponse[ReviewOut])
def create_verified_order_review(
    order_id: str,
    payload: OrderReviewCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Allows buyer to leave a verified-purchase product review on their paid/delivered order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.buyer or order.buyer.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the purchasing buyer can review this order")
    if order.status not in {"DELIVERED", "PAID", "CONFIRMED"}:
        raise HTTPException(status_code=400, detail="Order must be paid or delivered before submitting a review")

    matching_item = next(
        (it for it in order.items if it.variant and it.variant.product_id == payload.product_id),
        None,
    )
    if not matching_item:
        raise HTTPException(status_code=400, detail="Product was not part of this order")

    review = Review(
        product_id=payload.product_id,
        order_item_id=matching_item.id,
        buyer_id=order.buyer_id,
        rating=payload.rating,
        comment=sanitize_text(payload.comment) if payload.comment else None,
        is_verified_purchase=True,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return APIResponse(success=True, message="Review published", data=ReviewOut.model_validate(review))


@router.get("/{order_id}/invoice", response_model=APIResponse[dict])
def get_order_gst_invoice(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generates a GST tax invoice breakdown (CGST+SGST intra-state or IGST inter-state) for an order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    _authorize_order_participant(db, order, current_user)

    first_artisan = (
        db.query(ArtisanProfile).filter(ArtisanProfile.id == order.items[0].artisan_id).first() if order.items else None
    )
    seller_name = first_artisan.user.full_name if first_artisan and first_artisan.user else "CraftLens Artisan"
    seller_state = first_artisan.state if first_artisan and first_artisan.state else "Tamil Nadu"
    buyer_name = order.buyer.user.full_name if order.buyer and order.buyer.user else "Buyer"
    buyer_state = str((order.delivery_address or {}).get("state") or seller_state)

    invoice = build_gst_invoice(
        invoice_number=order.gst_invoice_number or f"INV-{order.order_number}",
        doc_ref=order.order_number,
        seller_name=seller_name,
        seller_state=seller_state,
        buyer_name=buyer_name,
        buyer_state=buyer_state,
        taxable_subtotal=float(order.subtotal),
        shipping_fee=float(order.shipping_fee),
        buyer_gstin=(order.buyer.business_profile.gst_number if order.buyer and order.buyer.business_profile else None),
    )
    return APIResponse(success=True, message="GST invoice generated", data=invoice)
